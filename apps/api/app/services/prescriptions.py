import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prescriptions import Prescription, PrescriptionLine, PrescriptionDocument
from app.models.catalog import Product
from app.models.planning import Plan
from app.domain.enums import PrescriptionStatus, LineConfirmationState, PlanState
from app.domain.state_transitions import can_transition_prescription
from app.core.errors import NotFoundException, ConflictException
from app.schemas.prescriptions import (
    CreatePrescriptionRequest,
    BulkLinesUpdateRequest,
    PrescriptionResponse,
    PrescriptionLineResponse,
    PrescriptionDocumentResponse,
    PrescriptionListItem,
)


async def create_prescription(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    actor_id: uuid.UUID,
    data: CreatePrescriptionRequest,
) -> Prescription:
    now = datetime.now(timezone.utc)
    rx = Prescription(
        pharmacy_id=pharmacy_id,
        optional_patient_reference=data.optional_patient_reference,
        status=PrescriptionStatus.DRAFT,
        revision=1,
        created_by=actor_id,
        created_at=now,
    )
    db.add(rx)
    await db.commit()
    await db.refresh(rx)
    return rx


async def get_prescription(
    db: AsyncSession, pharmacy_id: uuid.UUID, prescription_id: uuid.UUID
) -> PrescriptionResponse:
    stmt = (
        select(Prescription)
        .options(
            selectinload(Prescription.lines).selectinload(PrescriptionLine.selected_product),
            selectinload(Prescription.documents),
        )
        .where(Prescription.pharmacy_id == pharmacy_id, Prescription.id == prescription_id)
    )
    res = await db.execute(stmt)
    rx = res.scalar_one_or_none()
    if not rx:
        raise NotFoundException("Prescription not found.")

    lines_resp = [
        PrescriptionLineResponse(
            id=line.id,
            raw_name=line.raw_name,
            raw_strength=line.raw_strength,
            selected_product_id=line.selected_product_id,
            selected_product_name=line.selected_product.brand_name if line.selected_product else None,
            requested_quantity=line.requested_quantity,
            quantity_unit=line.quantity_unit,
            optional_course_end_date=line.optional_course_end_date.isoformat() if line.optional_course_end_date else None,
            confirmation_state=line.confirmation_state,
            evidence_json=line.evidence_json,
        )
        for line in rx.lines
    ]

    docs_resp = [
        PrescriptionDocumentResponse(
            id=doc.id,
            file_name=doc.file_name,
            media_type=doc.media_type,
            byte_size=doc.byte_size,
            page_count=doc.page_count,
            created_at=doc.created_at.isoformat(),
            extraction_provider=doc.extraction_provider,
        )
        for doc in rx.documents
    ]

    return PrescriptionResponse(
        id=rx.id,
        optional_patient_reference=rx.optional_patient_reference,
        status=rx.status,
        revision=rx.revision,
        created_at=rx.created_at.isoformat(),
        confirmed_at=rx.confirmed_at.isoformat() if rx.confirmed_at else None,
        lines=lines_resp,
        documents=docs_resp,
    )


async def list_prescriptions(
    db: AsyncSession, pharmacy_id: uuid.UUID, limit: int = 50
) -> List[PrescriptionListItem]:
    stmt = (
        select(Prescription)
        .options(selectinload(Prescription.lines))
        .where(Prescription.pharmacy_id == pharmacy_id)
        .order_by(Prescription.created_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    prescriptions = res.scalars().all()

    return [
        PrescriptionListItem(
            id=rx.id,
            optional_patient_reference=rx.optional_patient_reference,
            status=rx.status,
            revision=rx.revision,
            line_count=len(rx.lines),
            created_at=rx.created_at.isoformat(),
        )
        for rx in prescriptions
    ]


async def update_prescription_lines(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    prescription_id: uuid.UUID,
    data: BulkLinesUpdateRequest,
) -> PrescriptionResponse:
    stmt = (
        select(Prescription)
        .options(selectinload(Prescription.lines))
        .where(Prescription.pharmacy_id == pharmacy_id, Prescription.id == prescription_id)
    )
    res = await db.execute(stmt)
    rx = res.scalar_one_or_none()
    if not rx:
        raise NotFoundException("Prescription not found.")

    if rx.status == PrescriptionStatus.COMPLETED:
        raise ConflictException("Completed prescriptions cannot be modified.")

    if rx.revision != data.expected_revision:
        raise ConflictException(
            f"Prescription revision mismatch. Expected {data.expected_revision}, current is {rx.revision}."
        )

    # Invalidate existing lines
    for line in list(rx.lines):
        await db.delete(line)
    rx.lines.clear()

    # Add new lines
    for l_in in data.lines:
        new_line = PrescriptionLine(
            id=l_in.id or uuid.uuid4(),
            pharmacy_id=pharmacy_id,
            prescription_id=rx.id,
            raw_name=l_in.raw_name,
            raw_strength=l_in.raw_strength,
            selected_product_id=l_in.selected_product_id,
            requested_quantity=l_in.requested_quantity,
            quantity_unit=l_in.quantity_unit,
            optional_course_end_date=l_in.optional_course_end_date,
            confirmation_state=l_in.confirmation_state,
            evidence_json=l_in.evidence_json,
        )
        db.add(new_line)
        rx.lines.append(new_line)

    # Increment revision and transition state if needed
    rx.revision += 1
    if rx.status == PrescriptionStatus.CONFIRMED:
        # Field edits invalidate confirmation
        rx.status = PrescriptionStatus.NEEDS_CONFIRMATION
        rx.confirmed_at = None

    # Invalidate any existing plans for this prescription
    await db.execute(
        update(Plan)
        .where(Plan.prescription_id == rx.id, Plan.state.in_([PlanState.DRAFT, PlanState.PENDING_REVIEW, PlanState.APPROVED]))
        .values(state=PlanState.SUPERSEDED)
    )

    await db.commit()
    return await get_prescription(db, pharmacy_id, prescription_id)


async def confirm_prescription(
    db: AsyncSession, pharmacy_id: uuid.UUID, prescription_id: uuid.UUID
) -> PrescriptionResponse:
    stmt = (
        select(Prescription)
        .options(selectinload(Prescription.lines))
        .where(Prescription.pharmacy_id == pharmacy_id, Prescription.id == prescription_id)
    )
    res = await db.execute(stmt)
    rx = res.scalar_one_or_none()
    if not rx:
        raise NotFoundException("Prescription not found.")

    if not rx.lines:
        raise ConflictException("Cannot confirm prescription without any medicine lines.")

    # All lines must be confirmed and have selected_product_id
    for line in rx.lines:
        if not line.selected_product_id:
            raise ConflictException(f"Line '{line.raw_name or 'unnamed'}' requires a selected catalogue product.")
        line.confirmation_state = LineConfirmationState.CONFIRMED

    rx.status = PrescriptionStatus.CONFIRMED
    rx.confirmed_at = datetime.now(timezone.utc)
    rx.revision += 1

    await db.commit()
    return await get_prescription(db, pharmacy_id, prescription_id)
