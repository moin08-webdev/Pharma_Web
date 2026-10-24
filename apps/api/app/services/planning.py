import math
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.planning import Plan, PlanLine, Quote, Approval
from app.models.prescriptions import Prescription, PrescriptionLine
from app.models.catalog import Product, PriceObservation
from app.models.identity import Pharmacy, User
from app.domain.enums import PrescriptionStatus, PlanState, ApprovalDecision, PriceKind
from app.domain.money import calculate_percent_difference
from app.domain.quantities import calculate_pack_breakdown
from app.services.allocation import allocate_batches_fefo
from app.core.config import settings
from app.core.errors import NotFoundException, ConflictException
from app.schemas.plans import (
    QuoteResponse,
    QuoteLineItem,
    QuoteAllocationItem,
    QuoteCoverage,
    QuoteTotals,
    QuoteBlocker,
    PlanResponse,
    PlanLineResponse,
    ApprovalResponse,
    UpdatePlanLineSelectionRequest,
)


async def generate_quote(
    db: AsyncSession, pharmacy_id: uuid.UUID, plan: Plan
) -> Quote:
    # Fetch prescription lines
    rx_stmt = (
        select(Prescription)
        .options(
            selectinload(Prescription.lines).selectinload(PrescriptionLine.selected_product).selectinload(Product.price_observations)
        )
        .where(Prescription.pharmacy_id == pharmacy_id, Prescription.id == plan.prescription_id)
    )
    rx_res = await db.execute(rx_stmt)
    rx = rx_res.scalar_one()

    # Fetch pharmacy settings
    p_stmt = select(Pharmacy).where(Pharmacy.id == pharmacy_id)
    p_res = await db.execute(p_stmt)
    pharmacy = p_res.scalar_one()

    # Query plan lines explicitly to avoid lazy loading in async
    pl_stmt = select(PlanLine).where(
        PlanLine.pharmacy_id == pharmacy_id, PlanLine.plan_id == plan.id
    )
    pl_res = await db.execute(pl_stmt)
    plan_lines = pl_res.scalars().all()
    plan_lines_map = {pl.prescription_line_id: pl for pl in plan_lines}

    quote_lines: List[QuoteLineItem] = []
    blockers: List[QuoteBlocker] = []

    total_baseline_paise = 0
    total_selected_paise = 0
    has_full_baseline = True
    has_full_selected = True

    comparable_baseline = 0
    comparable_selected = 0
    comparable_count = 0
    fulfilled_count = 0

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=settings.QUOTE_TTL_SECONDS)

    for rx_line in rx.lines:
        orig_prod = rx_line.selected_product
        if not orig_prod:
            continue

        pl = plan_lines_map.get(rx_line.id)
        selected_prod_id = pl.selected_product_id if pl else orig_prod.id
        auth_req = pl.authorization_required if pl else False
        auth_ref = pl.authorization_reference if pl else None

        # Fetch selected product
        sp_stmt = (
            select(Product)
            .options(selectinload(Product.price_observations))
            .where(Product.pharmacy_id == pharmacy_id, Product.id == selected_prod_id)
        )
        sp_res = await db.execute(sp_stmt)
        selected_prod = sp_res.scalar_one()

        # Baseline pack price (from original product)
        baseline_pack_price = None
        for po in orig_prod.price_observations:
            if po.price_kind in (PriceKind.MRP, PriceKind.SELLING_PRICE):
                baseline_pack_price = po.pack_price_paise
                break

        # Calculate baseline line cost
        baseline_cost = None
        if baseline_pack_price is not None:
            _, _, _, b_cost = calculate_pack_breakdown(
                requested_units=rx_line.requested_quantity,
                pack_quantity=orig_prod.pack_quantity,
                pack_price_paise=baseline_pack_price,
                pack_break_allowed=orig_prod.pack_break_allowed,
            )
            baseline_cost = b_cost
            total_baseline_paise += b_cost
        else:
            has_full_baseline = False

        # Allocate batches for selected product using FEFO
        allocations, supplied_units, excess_units, packs_needed, shortage = await allocate_batches_fefo(
            db=db,
            pharmacy_id=pharmacy_id,
            product=selected_prod,
            requested_units=rx_line.requested_quantity,
            course_end_date=rx_line.optional_course_end_date,
            expiry_buffer_days=pharmacy.expiry_buffer_days,
        )

        selected_cost = None
        if shortage > 0:
            blockers.append(
                QuoteBlocker(
                    code="INSUFFICIENT_STOCK",
                    message=f"Shortage of {shortage} units for {selected_prod.brand_name}",
                    line_id=rx_line.id,
                )
            )
            has_full_selected = False
        else:
            fulfilled_count += 1
            # Calculate total cost from allocations
            line_cost = sum(a.quantity * a.unit_price_paise for a in allocations)
            selected_cost = line_cost
            total_selected_paise += line_cost

        if auth_req and not auth_ref:
            blockers.append(
                QuoteBlocker(
                    code="AUTHORIZATION_REQUIRED",
                    message=f"Prescriber authorization reference missing for {selected_prod.brand_name}",
                    line_id=rx_line.id,
                )
            )

        line_diff_pct = None
        if baseline_cost is not None and selected_cost is not None:
            diff = calculate_percent_difference(baseline_cost, selected_cost)
            if diff is not None:
                line_diff_pct = f"{diff:.2f}"
                comparable_baseline += baseline_cost
                comparable_selected += selected_cost
                comparable_count += 1

        quote_lines.append(
            QuoteLineItem(
                prescription_line_id=rx_line.id,
                original_product_id=orig_prod.id,
                original_brand_name=orig_prod.brand_name,
                selected_product_id=selected_prod.id,
                selected_brand_name=selected_prod.brand_name,
                requested_units=rx_line.requested_quantity,
                supplied_units=supplied_units,
                excess_units=excess_units,
                packs_needed=packs_needed,
                unit_dispensing=selected_prod.pack_break_allowed,
                baseline_line_paise=baseline_cost,
                selected_line_paise=selected_cost,
                difference_percent=line_diff_pct,
                allocations=allocations,
                shortage_units=shortage,
                authorization_required=auth_req,
                authorization_reference=auth_ref,
            )
        )

    # Calculate overall difference for comparable subset
    comparable_diff_pct = None
    if comparable_count > 0 and comparable_baseline > 0:
        c_diff = calculate_percent_difference(comparable_baseline, comparable_selected)
        if c_diff is not None:
            comparable_diff_pct = f"{c_diff:.2f}"

    req_lines = len(rx.lines)
    coverage = QuoteCoverage(
        requested_lines=req_lines,
        fulfilled_lines=fulfilled_count,
        comparable_lines=comparable_count,
    )

    finalizable = (fulfilled_count == req_lines) and (len(blockers) == 0)

    totals = QuoteTotals(
        currency="INR",
        baseline_total_paise=total_baseline_paise if has_full_baseline else None,
        selected_total_paise=total_selected_paise if has_full_selected else None,
        comparable_subset_baseline_paise=comparable_baseline if comparable_count > 0 else None,
        comparable_subset_selected_paise=comparable_selected if comparable_count > 0 else None,
        comparable_subset_difference_percent=comparable_diff_pct,
        comparison_basis="synthetic_demo_selling_prices",
    )

    quote_id = uuid.uuid4()
    first_prod = rx.lines[0].selected_product if rx.lines else None
    d_kind_val = "DEMO"
    if first_prod and first_prod.dataset_kind:
        d_kind_val = first_prod.dataset_kind.value if hasattr(first_prod.dataset_kind, "value") else str(first_prod.dataset_kind)

    payload = {
        "quote_id": str(quote_id),
        "plan_id": str(plan.id),
        "plan_version": plan.version,
        "prescription_revision": rx.revision,
        "dataset_kind": d_kind_val,
        "expires_at": expires_at.isoformat(),
        "coverage": coverage.model_dump(mode="json"),
        "finalizable": finalizable,
        "blockers": [b.model_dump(mode="json") for b in blockers],
        "totals": totals.model_dump(mode="json"),
        "lines": [l.model_dump(mode="json") for l in quote_lines],
    }

    quote = Quote(
        id=quote_id,
        pharmacy_id=pharmacy_id,
        plan_id=plan.id,
        plan_version=plan.version,
        prescription_revision=rx.revision,
        rules_version=1,
        settings_version=pharmacy.settings_version,
        immutable_payload_json=payload,
        created_at=now,
        expires_at=expires_at,
    )
    db.add(quote)
    plan.current_quote_id = quote_id
    await db.flush()
    return quote


async def create_plan(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    actor_id: uuid.UUID,
    prescription_id: uuid.UUID,
) -> PlanResponse:
    # Fetch confirmed prescription
    stmt = (
        select(Prescription)
        .options(selectinload(Prescription.lines))
        .where(Prescription.pharmacy_id == pharmacy_id, Prescription.id == prescription_id)
    )
    res = await db.execute(stmt)
    rx = res.scalar_one_or_none()
    if not rx:
        raise NotFoundException("Prescription not found.")

    if rx.status != PrescriptionStatus.CONFIRMED:
        raise ConflictException("Prescription must be confirmed before creating a fulfilment plan.")

    # Supersede any active existing plan for this prescription
    await db.execute(
        update(Plan)
        .where(Plan.prescription_id == rx.id, Plan.state.in_([PlanState.DRAFT, PlanState.PENDING_REVIEW, PlanState.APPROVED]))
        .values(state=PlanState.SUPERSEDED)
    )

    now = datetime.now(timezone.utc)
    plan = Plan(
        pharmacy_id=pharmacy_id,
        prescription_id=rx.id,
        prescription_revision=rx.revision,
        version=1,
        state=PlanState.DRAFT,
        created_by=actor_id,
        created_at=now,
    )
    db.add(plan)
    await db.flush()

    # Create plan lines matching confirmed prescription lines
    for line in rx.lines:
        pl = PlanLine(
            pharmacy_id=pharmacy_id,
            plan_id=plan.id,
            prescription_line_id=line.id,
            selected_product_id=line.selected_product_id,
            selection_reason="as_prescribed",
            authorization_required=False,
        )
        db.add(pl)
    await db.flush()

    # Generate initial quote
    quote = await generate_quote(db, pharmacy_id, plan)
    await db.commit()

    return await get_plan(db, pharmacy_id, plan.id)


async def get_plan(
    db: AsyncSession, pharmacy_id: uuid.UUID, plan_id: uuid.UUID
) -> PlanResponse:
    stmt = (
        select(Plan)
        .options(
            selectinload(Plan.lines).selectinload(PlanLine.selected_product),
            selectinload(Plan.quotes),
        )
        .where(Plan.pharmacy_id == pharmacy_id, Plan.id == plan_id)
    )
    res = await db.execute(stmt)
    plan = res.scalar_one_or_none()
    if not plan:
        raise NotFoundException("Plan not found.")

    lines_resp = [
        PlanLineResponse(
            id=pl.id,
            prescription_line_id=pl.prescription_line_id,
            selected_product_id=pl.selected_product_id,
            selected_brand_name=pl.selected_product.brand_name,
            selection_reason=pl.selection_reason,
            authorization_required=pl.authorization_required,
            authorization_reference=pl.authorization_reference,
        )
        for pl in plan.lines
    ]

    current_quote_resp = None
    if plan.current_quote_id:
        for q in plan.quotes:
            if q.id == plan.current_quote_id:
                # Payload is QuoteResponse
                current_quote_resp = QuoteResponse(**q.immutable_payload_json)
                break

    # Get active approval if exists
    appr_resp = None
    if plan.current_quote_id:
        a_res = await db.execute(
            select(Approval, User)
            .join(User, Approval.actor_id == User.id)
            .where(Approval.pharmacy_id == pharmacy_id, Approval.quote_id == plan.current_quote_id)
        )
        row = a_res.first()
        if row:
            appr, user = row
            appr_resp = ApprovalResponse(
                id=appr.id,
                decision=appr.decision,
                actor_id=appr.actor_id,
                actor_name=user.normalized_email.split("@")[0].capitalize(),
                actor_role=user.role.value if hasattr(user.role, "value") else str(user.role),
                reason=appr.reason,
                authorization_reference=appr.authorization_reference,
                created_at=appr.created_at.isoformat(),
            )

    return PlanResponse(
        id=plan.id,
        prescription_id=plan.prescription_id,
        prescription_revision=plan.prescription_revision,
        version=plan.version,
        state=plan.state,
        created_at=plan.created_at.isoformat(),
        lines=lines_resp,
        current_quote=current_quote_resp,
        approval=appr_resp,
    )


async def update_plan_line_selection(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    plan_id: uuid.UUID,
    line_id: uuid.UUID,
    data: UpdatePlanLineSelectionRequest,
) -> PlanResponse:
    stmt = (
        select(Plan)
        .options(selectinload(Plan.lines))
        .where(Plan.pharmacy_id == pharmacy_id, Plan.id == plan_id)
    )
    res = await db.execute(stmt)
    plan = res.scalar_one_or_none()
    if not plan:
        raise NotFoundException("Plan not found.")

    if plan.version != data.expected_plan_version:
        raise ConflictException(
            f"Plan version mismatch. Expected {data.expected_plan_version}, current is {plan.version}."
        )

    # Find the line
    target_line = None
    for pl in plan.lines:
        if pl.id == line_id:
            target_line = pl
            break
    if not target_line:
        raise NotFoundException("Plan line not found.")

    target_line.selected_product_id = data.selected_product_id
    target_line.selection_reason = data.selection_reason
    target_line.authorization_required = data.authorization_required
    target_line.authorization_reference = data.authorization_reference

    # Increment plan version and reset state to DRAFT if approved or pending
    plan.version += 1
    plan.state = PlanState.DRAFT

    # Re-generate quote
    await generate_quote(db, pharmacy_id, plan)
    await db.commit()

    return await get_plan(db, pharmacy_id, plan_id)


async def submit_plan_for_review(
    db: AsyncSession, pharmacy_id: uuid.UUID, plan_id: uuid.UUID
) -> PlanResponse:
    stmt = select(Plan).where(Plan.pharmacy_id == pharmacy_id, Plan.id == plan_id)
    res = await db.execute(stmt)
    plan = res.scalar_one_or_none()
    if not plan:
        raise NotFoundException("Plan not found.")

    if not plan.current_quote_id:
        await generate_quote(db, pharmacy_id, plan)

    plan.state = PlanState.PENDING_REVIEW
    await db.commit()

    return await get_plan(db, pharmacy_id, plan_id)
