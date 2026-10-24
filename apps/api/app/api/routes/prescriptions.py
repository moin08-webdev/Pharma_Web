import os
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_and_pharmacy
from app.models.identity import User, Pharmacy
from app.models.prescriptions import PrescriptionDocument
from app.services.prescriptions import (
    create_prescription,
    get_prescription,
    list_prescriptions,
    update_prescription_lines,
    confirm_prescription,
)
from app.schemas.prescriptions import (
    CreatePrescriptionRequest,
    BulkLinesUpdateRequest,
    PrescriptionResponse,
    PrescriptionListItem,
    PrescriptionDocumentResponse,
)
from app.core.config import settings

router = APIRouter()


@router.post("", response_model=PrescriptionResponse, status_code=201)
async def create_new_prescription(
    data: CreatePrescriptionRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    user, pharmacy, _ = ctx
    rx = await create_prescription(db, pharmacy.id, user.id, data)
    return await get_prescription(db, pharmacy.id, rx.id)


@router.get("", response_model=List[PrescriptionListItem])
async def get_all_prescriptions(
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await list_prescriptions(db, pharmacy.id)


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_single_prescription(
    prescription_id: uuid.UUID,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await get_prescription(db, pharmacy.id, prescription_id)


@router.put("/{prescription_id}/lines", response_model=PrescriptionResponse)
async def update_lines(
    prescription_id: uuid.UUID,
    data: BulkLinesUpdateRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await update_prescription_lines(db, pharmacy.id, prescription_id, data)


@router.post("/{prescription_id}/confirm", response_model=PrescriptionResponse)
async def confirm(
    prescription_id: uuid.UUID,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await confirm_prescription(db, pharmacy.id, prescription_id)


@router.post("/{prescription_id}/documents", status_code=202)
async def upload_document(
    prescription_id: uuid.UUID,
    file: UploadFile = File(...),
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    user, pharmacy, _ = ctx
    # Validate prescription exists
    await get_prescription(db, pharmacy.id, prescription_id)

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds maximum permitted size of 10 MiB")

    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    media_type = file.content_type or "application/octet-stream"
    if media_type not in allowed_types:
        raise HTTPException(status_code=422, detail="Unsupported file format. Please upload JPEG, PNG, or PDF.")

    sha = hashlib.sha256(content).hexdigest()
    storage_key = f"{pharmacy.id}/{prescription_id}_{uuid.uuid4().hex[:8]}_{file.filename}"
    full_path = os.path.join(settings.UPLOAD_DIRECTORY, storage_key)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(content)

    now = datetime.now(timezone.utc)
    retention_deadline = now + timedelta(hours=settings.UPLOAD_RETENTION_HOURS)

    doc = PrescriptionDocument(
        pharmacy_id=pharmacy.id,
        prescription_id=prescription_id,
        private_storage_key=storage_key,
        file_name=file.filename or "prescription_doc",
        media_type=media_type,
        byte_size=len(content),
        sha256=sha,
        page_count=1,
        extraction_provider="local_tesseract",
        retention_deadline=retention_deadline,
        created_at=now,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return {
        "document_id": str(doc.id),
        "prescription_id": str(prescription_id),
        "file_name": doc.file_name,
        "byte_size": doc.byte_size,
        "status": "uploaded",
    }
