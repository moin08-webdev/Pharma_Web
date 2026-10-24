import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orders import Order, OrderLine, OrderAllocation
from app.models.planning import Plan, Quote, Approval
from app.models.prescriptions import Prescription
from app.models.inventory import InventoryBatch, StockMovement
from app.models.audit import IdempotencyRecord, AuditEvent
from app.models.identity import User
from app.domain.enums import PrescriptionStatus, PlanState, ApprovalDecision, BatchStatus, StockMovementReason
from app.core.permissions import require_pharmacist
from app.core.errors import NotFoundException, ConflictException, QuoteStaleException, InsufficientStockException
from app.schemas.orders import (
    FinalizeOrderRequest,
    OrderDetailResponse,
    OrderListItem,
    OrderLineItem,
    OrderAllocationItem,
)


def compute_request_hash(data: Dict[str, Any]) -> str:
    canonical = json.dumps(data, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def finalize_order(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    user: User,
    data: FinalizeOrderRequest,
    idempotency_key: str,
) -> OrderDetailResponse:
    # 1. Permission check: only PHARMACIST can finalize
    require_pharmacist(user)

    request_payload_dict = {
        "quote_id": str(data.quote_id),
        "approval_id": str(data.approval_id),
    }
    req_hash = compute_request_hash(request_payload_dict)

    # 2. Check Idempotency Record
    idem_stmt = select(IdempotencyRecord).where(
        IdempotencyRecord.pharmacy_id == pharmacy_id,
        IdempotencyRecord.operation == "finalize_order",
        IdempotencyRecord.key == idempotency_key,
    )
    idem_res = await db.execute(idem_stmt)
    existing_record = idem_res.scalar_one_or_none()

    if existing_record:
        if existing_record.request_hash == req_hash:
            return OrderDetailResponse(**existing_record.response_json)
        else:
            raise ConflictException(
                "Idempotency key reuse detected with different request payload."
            )

    now = datetime.now(timezone.utc)

    # 3. Lock Quote with FOR UPDATE
    q_stmt = select(Quote).where(
        Quote.pharmacy_id == pharmacy_id, Quote.id == data.quote_id
    ).with_for_update()
    q_res = await db.execute(q_stmt)
    quote = q_res.scalar_one_or_none()
    if not quote:
        raise NotFoundException("Quote not found.")

    if quote.consumed_at is not None:
        raise ConflictException("This quote has already been consumed by an order.")

    if quote.expires_at < now:
        raise QuoteStaleException("Quote has expired. Refresh plan and review again.")

    # Lock Approval
    appr_stmt = select(Approval).where(
        Approval.pharmacy_id == pharmacy_id,
        Approval.id == data.approval_id,
        Approval.quote_id == quote.id,
    ).with_for_update()
    appr_res = await db.execute(appr_stmt)
    approval = appr_res.scalar_one_or_none()
    if not approval or approval.decision != ApprovalDecision.APPROVED:
        raise ConflictException("Active pharmacist approval required for this quote.")

    # Lock Plan
    plan_stmt = select(Plan).where(
        Plan.pharmacy_id == pharmacy_id, Plan.id == quote.plan_id
    ).with_for_update()
    plan_res = await db.execute(plan_stmt)
    plan = plan_res.scalar_one_or_none()
    if not plan or plan.state != PlanState.APPROVED or plan.version != quote.plan_version:
        raise QuoteStaleException("Plan has been modified or is no longer approved. Re-review required.")

    # Lock Prescription
    rx_stmt = select(Prescription).where(
        Prescription.pharmacy_id == pharmacy_id, Prescription.id == plan.prescription_id
    ).with_for_update()
    rx_res = await db.execute(rx_stmt)
    rx = rx_res.scalar_one_or_none()
    if not rx or rx.status != PrescriptionStatus.CONFIRMED or rx.revision != quote.prescription_revision:
        raise QuoteStaleException("Prescription has been modified after quote was created.")

    # Check if this prescription already has an order
    existing_order_res = await db.execute(
        select(Order).where(Order.prescription_id == rx.id)
    )
    if existing_order_res.scalar_one_or_none():
        raise ConflictException("An order has already been finalized for this prescription.")

    quote_payload = quote.immutable_payload_json
    quote_lines = quote_payload.get("lines", [])

    # Gather all batch IDs allocated in the quote
    batch_allocations: Dict[uuid.UUID, int] = {}
    for ql in quote_lines:
        for alloc in ql.get("allocations", []):
            b_id = uuid.UUID(alloc["batch_id"])
            batch_allocations[b_id] = batch_allocations.get(b_id, 0) + alloc["quantity"]

    sorted_batch_ids = sorted(batch_allocations.keys())

    # Lock all batches in stable order to prevent deadlocks
    b_stmt = select(InventoryBatch).where(
        InventoryBatch.pharmacy_id == pharmacy_id,
        InventoryBatch.id.in_(sorted_batch_ids),
    ).order_by(InventoryBatch.id).with_for_update()
    b_res = await db.execute(b_stmt)
    locked_batches = {b.id: b for b in b_res.scalars().all()}

    # Verify inventory eligibility and quantities
    for b_id, needed_qty in batch_allocations.items():
        batch = locked_batches.get(b_id)
        if not batch:
            raise QuoteStaleException("Allocated batch no longer exists.")
        if batch.status != BatchStatus.ACTIVE:
            raise QuoteStaleException(f"Batch {batch.batch_number} is no longer active (status: {batch.status}).")
        if batch.quantity_on_hand < needed_qty:
            raise InsufficientStockException(
                f"Insufficient stock in batch {batch.batch_number}. Available: {batch.quantity_on_hand}, required: {needed_qty}."
            )

    # Calculate total and generate order number
    count_res = await db.execute(select(func.count(Order.id)).where(Order.pharmacy_id == pharmacy_id))
    order_seq = count_res.scalar_one() + 1
    order_num = f"ORD-{now.year}-{order_seq:05d}"

    total_paise = sum(
        ql.get("selected_line_paise", 0) for ql in quote_lines if ql.get("selected_line_paise") is not None
    )

    order = Order(
        pharmacy_id=pharmacy_id,
        prescription_id=rx.id,
        quote_id=quote.id,
        approval_id=approval.id,
        order_number=order_num,
        total_paise=total_paise,
        currency="INR",
        completed_by=user.id,
        completed_at=now,
    )
    db.add(order)
    await db.flush()

    order_line_responses: List[OrderLineItem] = []

    # Apply batch deductions and create order lines
    for ql in quote_lines:
        orig_snapshot = {
            "product_id": ql["original_product_id"],
            "brand_name": ql["original_brand_name"],
            "baseline_line_paise": ql.get("baseline_line_paise"),
        }
        disp_snapshot = {
            "product_id": ql["selected_product_id"],
            "brand_name": ql["selected_brand_name"],
            "selected_line_paise": ql.get("selected_line_paise"),
        }
        comp_snapshot = {
            "difference_percent": ql.get("difference_percent"),
            "excess_units": ql.get("excess_units", 0),
            "packs_needed": ql.get("packs_needed", 1),
        }

        ol = OrderLine(
            pharmacy_id=pharmacy_id,
            order_id=order.id,
            original_product_snapshot=orig_snapshot,
            dispensed_product_snapshot=disp_snapshot,
            requested_quantity=ql["requested_units"],
            supplied_quantity=ql["supplied_units"],
            quantity_unit="tablet",
            total_paise=ql.get("selected_line_paise", 0),
            comparison_snapshot=comp_snapshot,
        )
        db.add(ol)
        await db.flush()

        alloc_items: List[OrderAllocationItem] = []
        for alloc in ql.get("allocations", []):
            b_id = uuid.UUID(alloc["batch_id"])
            qty = alloc["quantity"]
            batch = locked_batches[b_id]

            # Deduct stock
            batch.quantity_on_hand -= qty
            batch.version += 1

            # Ledger movement
            mv = StockMovement(
                pharmacy_id=pharmacy_id,
                batch_id=batch.id,
                delta_units=-qty,
                reason=StockMovementReason.DISPENSE,
                reference_type="order",
                reference_id=order.id,
                actor_id=user.id,
                created_at=now,
            )
            db.add(mv)

            oa = OrderAllocation(
                pharmacy_id=pharmacy_id,
                order_line_id=ol.id,
                batch_id=batch.id,
                batch_number_snapshot=batch.batch_number,
                quantity=qty,
                price_snapshot={
                    "selling_pack_paise": batch.selling_pack_paise,
                    "mrp_pack_paise": batch.mrp_pack_paise,
                    "unit_price_paise": alloc["unit_price_paise"],
                },
                expiry_snapshot=batch.expires_on.isoformat(),
            )
            db.add(oa)
            await db.flush()

            alloc_items.append(
                OrderAllocationItem(
                    id=oa.id,
                    batch_number=batch.batch_number,
                    quantity=qty,
                    expiry_date=batch.expires_on.isoformat(),
                    mrp_pack_paise=batch.mrp_pack_paise,
                    selling_pack_paise=batch.selling_pack_paise,
                )
            )

        order_line_responses.append(
            OrderLineItem(
                id=ol.id,
                original_product_name=ql["original_brand_name"],
                dispensed_product_name=ql["selected_brand_name"],
                requested_quantity=ql["requested_units"],
                supplied_quantity=ql["supplied_units"],
                quantity_unit="tablet",
                total_paise=ql.get("selected_line_paise", 0),
                difference_percent=ql.get("difference_percent"),
                allocations=alloc_items,
            )
        )

    # Finalize state transitions
    quote.consumed_at = now
    plan.state = PlanState.FINALIZED
    rx.status = PrescriptionStatus.COMPLETED

    # Record Audit Event
    audit_evt = AuditEvent(
        pharmacy_id=pharmacy_id,
        actor_id=user.id,
        event_type="order.finalized",
        entity_type="order",
        entity_id=order.id,
        before_version=quote.plan_version,
        after_version=quote.plan_version,
        minimal_metadata={
            "order_number": order_num,
            "total_paise": total_paise,
            "prescription_id": str(rx.id),
        },
        timestamp=now,
    )
    db.add(audit_evt)

    result_response = OrderDetailResponse(
        id=order.id,
        order_number=order_num,
        prescription_id=rx.id,
        quote_id=quote.id,
        approval_id=approval.id,
        total_paise=total_paise,
        currency="INR",
        completed_by_name=user.normalized_email.split("@")[0].capitalize(),
        completed_at=now.isoformat(),
        comparison_basis="synthetic_demo_selling_prices",
        lines=order_line_responses,
    )

    # Record Idempotency Result
    idem_rec = IdempotencyRecord(
        pharmacy_id=pharmacy_id,
        operation="finalize_order",
        key=idempotency_key,
        request_hash=req_hash,
        response_status=200,
        response_json=result_response.model_dump(mode="json"),
        created_at=now,
    )
    db.add(idem_rec)

    # Commit atomic transaction
    await db.commit()

    return result_response


async def list_orders(
    db: AsyncSession, pharmacy_id: uuid.UUID, limit: int = 50
) -> List[OrderListItem]:
    stmt = (
        select(Order)
        .options(selectinload(Order.lines))
        .where(Order.pharmacy_id == pharmacy_id)
        .order_by(Order.completed_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    orders = res.scalars().all()

    return [
        OrderListItem(
            id=o.id,
            order_number=o.order_number,
            prescription_id=o.prescription_id,
            total_paise=o.total_paise,
            currency=o.currency,
            completed_at=o.completed_at.isoformat(),
            item_count=len(o.lines),
        )
        for o in orders
    ]


async def get_order_detail(
    db: AsyncSession, pharmacy_id: uuid.UUID, order_id: uuid.UUID
) -> OrderDetailResponse:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.lines).selectinload(OrderLine.allocations),
            selectinload(Order.completed_by),
        )
        .where(Order.pharmacy_id == pharmacy_id, Order.id == order_id)
    )
    # Join with User for completer name
    u_stmt = select(Order, User).join(User, Order.completed_by == User.id).where(
        Order.pharmacy_id == pharmacy_id, Order.id == order_id
    ).options(
        selectinload(Order.lines).selectinload(OrderLine.allocations)
    )
    res = await db.execute(u_stmt)
    row = res.first()
    if not row:
        raise NotFoundException("Order not found.")

    order, user = row

    lines_resp = [
        OrderLineItem(
            id=ol.id,
            original_product_name=ol.original_product_snapshot.get("brand_name", "Unknown"),
            dispensed_product_name=ol.dispensed_product_snapshot.get("brand_name", "Unknown"),
            requested_quantity=ol.requested_quantity,
            supplied_quantity=ol.supplied_quantity,
            quantity_unit=ol.quantity_unit,
            total_paise=ol.total_paise,
            difference_percent=ol.comparison_snapshot.get("difference_percent") if ol.comparison_snapshot else None,
            allocations=[
                OrderAllocationItem(
                    id=oa.id,
                    batch_number=oa.batch_number_snapshot,
                    quantity=oa.quantity,
                    expiry_date=oa.expiry_snapshot,
                    mrp_pack_paise=oa.price_snapshot.get("mrp_pack_paise", 0),
                    selling_pack_paise=oa.price_snapshot.get("selling_pack_paise", 0),
                )
                for oa in ol.allocations
            ],
        )
        for ol in order.lines
    ]

    return OrderDetailResponse(
        id=order.id,
        order_number=order.order_number,
        prescription_id=order.prescription_id,
        quote_id=order.quote_id,
        approval_id=order.approval_id,
        total_paise=order.total_paise,
        currency=order.currency,
        completed_by_name=user.normalized_email.split("@")[0].capitalize(),
        completed_at=order.completed_at.isoformat(),
        comparison_basis="synthetic_demo_selling_prices",
        lines=lines_resp,
    )
