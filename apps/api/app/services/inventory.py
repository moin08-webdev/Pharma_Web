import uuid
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventory import InventoryBatch, StockMovement
from app.models.catalog import Product, PriceObservation
from app.domain.enums import BatchStatus, StockMovementReason, PriceKind
from app.core.errors import NotFoundException, ConflictException
from app.schemas.inventory import (
    InventoryProductItem,
    InventoryBatchItem,
    StockReceiptRequest,
    StockAdjustmentRequest,
    InventoryAlertsResponse,
)


async def list_inventory(
    db: AsyncSession, pharmacy_id: uuid.UUID, limit: int = 50
) -> List[InventoryProductItem]:
    # Group batches by product
    stmt = (
        select(Product)
        .where(Product.pharmacy_id == pharmacy_id, Product.active == True)
        .order_by(Product.brand_name)
        .limit(limit)
    )
    res = await db.execute(stmt)
    products = res.scalars().all()

    items = []
    today = date.today()

    for p in products:
        b_stmt = select(InventoryBatch).where(
            InventoryBatch.pharmacy_id == pharmacy_id,
            InventoryBatch.product_id == p.id,
        )
        b_res = await db.execute(b_stmt)
        batches = b_res.scalars().all()

        total_qty = sum(b.quantity_on_hand for b in batches if b.status == BatchStatus.ACTIVE)
        active_count = sum(1 for b in batches if b.status == BatchStatus.ACTIVE)
        has_quarantine = any(b.status == BatchStatus.QUARANTINE for b in batches)

        active_expiries = [b.expires_on for b in batches if b.status == BatchStatus.ACTIVE and b.quantity_on_hand > 0]
        nearest_exp = min(active_expiries).isoformat() if active_expiries else None

        items.append(
            InventoryProductItem(
                product_id=p.id,
                brand_name=p.brand_name,
                manufacturer=p.manufacturer,
                dataset_kind=p.dataset_kind,
                pack_quantity=p.pack_quantity,
                dispensing_unit=p.dispensing_unit,
                total_quantity_on_hand=total_qty,
                active_batches_count=active_count,
                nearest_expiry=nearest_exp,
                is_low_stock=(total_qty < 20),
                has_quarantine=has_quarantine,
            )
        )
    return items


async def get_product_batches(
    db: AsyncSession, pharmacy_id: uuid.UUID, product_id: uuid.UUID
) -> List[InventoryBatchItem]:
    stmt = (
        select(InventoryBatch)
        .where(
            InventoryBatch.pharmacy_id == pharmacy_id,
            InventoryBatch.product_id == product_id,
        )
        .order_by(InventoryBatch.expires_on.asc())
    )
    res = await db.execute(stmt)
    batches = res.scalars().all()

    return [
        InventoryBatchItem(
            id=b.id,
            batch_number=b.batch_number,
            quantity_on_hand=b.quantity_on_hand,
            quantity_unit=b.quantity_unit,
            expires_on=b.expires_on.isoformat(),
            expiry_precision=b.expiry_precision,
            mrp_pack_paise=b.mrp_pack_paise,
            selling_pack_paise=b.selling_pack_paise,
            status=b.status,
            version=b.version,
            received_at=b.received_at.isoformat(),
        )
        for b in batches
    ]


async def receive_stock(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    actor_id: uuid.UUID,
    data: StockReceiptRequest,
) -> InventoryBatchItem:
    # Verify product exists
    p_res = await db.execute(
        select(Product).where(Product.pharmacy_id == pharmacy_id, Product.id == data.product_id)
    )
    product = p_res.scalar_one_or_none()
    if not product:
        raise NotFoundException("Product not found.")

    now = datetime.now(timezone.utc)

    # Check if batch with this number already exists
    b_res = await db.execute(
        select(InventoryBatch).where(
            InventoryBatch.pharmacy_id == pharmacy_id,
            InventoryBatch.product_id == data.product_id,
            InventoryBatch.batch_number == data.batch_number,
        )
    )
    batch = b_res.scalar_one_or_none()

    if batch:
        batch.quantity_on_hand += data.quantity_units
        batch.mrp_pack_paise = data.mrp_pack_paise
        batch.selling_pack_paise = data.selling_pack_paise
        batch.expires_on = data.expires_on
        batch.version += 1
    else:
        batch = InventoryBatch(
            pharmacy_id=pharmacy_id,
            product_id=data.product_id,
            batch_number=data.batch_number,
            quantity_on_hand=data.quantity_units,
            quantity_unit=data.quantity_unit,
            expires_on=data.expires_on,
            expiry_precision="day",
            mrp_pack_paise=data.mrp_pack_paise,
            selling_pack_paise=data.selling_pack_paise,
            status=BatchStatus.ACTIVE,
            version=1,
            received_at=now,
        )
        db.add(batch)
        await db.flush()

    # Record stock movement
    movement = StockMovement(
        pharmacy_id=pharmacy_id,
        batch_id=batch.id,
        delta_units=data.quantity_units,
        reason=StockMovementReason.RECEIPT,
        actor_id=actor_id,
        created_at=now,
    )
    db.add(movement)
    await db.commit()
    await db.refresh(batch)

    return InventoryBatchItem(
        id=batch.id,
        batch_number=batch.batch_number,
        quantity_on_hand=batch.quantity_on_hand,
        quantity_unit=batch.quantity_unit,
        expires_on=batch.expires_on.isoformat(),
        expiry_precision=batch.expiry_precision,
        mrp_pack_paise=batch.mrp_pack_paise,
        selling_pack_paise=batch.selling_pack_paise,
        status=batch.status,
        version=batch.version,
        received_at=batch.received_at.isoformat(),
    )


async def adjust_stock(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    actor_id: uuid.UUID,
    data: StockAdjustmentRequest,
) -> InventoryBatchItem:
    res = await db.execute(
        select(InventoryBatch).where(
            InventoryBatch.pharmacy_id == pharmacy_id, InventoryBatch.id == data.batch_id
        )
    )
    batch = res.scalar_one_or_none()
    if not batch:
        raise NotFoundException("Batch not found.")

    if batch.version != data.expected_version:
        raise ConflictException("Batch version conflict. Please refresh and try again.")

    new_qty = batch.quantity_on_hand + data.delta_units
    if new_qty < 0:
        raise ConflictException("Quantity on hand cannot become negative.")

    batch.quantity_on_hand = new_qty
    batch.version += 1

    if data.reason == StockMovementReason.QUARANTINE_MOVE:
        batch.status = BatchStatus.QUARANTINE
    elif batch.status == BatchStatus.QUARANTINE and data.reason == StockMovementReason.ADJUSTMENT:
        batch.status = BatchStatus.ACTIVE

    now = datetime.now(timezone.utc)
    movement = StockMovement(
        pharmacy_id=pharmacy_id,
        batch_id=batch.id,
        delta_units=data.delta_units,
        reason=data.reason,
        actor_id=actor_id,
        created_at=now,
    )
    db.add(movement)
    await db.commit()
    await db.refresh(batch)

    return InventoryBatchItem(
        id=batch.id,
        batch_number=batch.batch_number,
        quantity_on_hand=batch.quantity_on_hand,
        quantity_unit=batch.quantity_unit,
        expires_on=batch.expires_on.isoformat(),
        expiry_precision=batch.expiry_precision,
        mrp_pack_paise=batch.mrp_pack_paise,
        selling_pack_paise=batch.selling_pack_paise,
        status=batch.status,
        version=batch.version,
        received_at=batch.received_at.isoformat(),
    )


async def get_inventory_alerts(
    db: AsyncSession, pharmacy_id: uuid.UUID, expiry_buffer_days: int = 30
) -> InventoryAlertsResponse:
    today = date.today()
    exp_threshold = today + timedelta(days=expiry_buffer_days)

    # Low stock
    all_prod = await list_inventory(db, pharmacy_id, limit=200)
    low_stock_count = sum(1 for p in all_prod if p.is_low_stock)

    # Expiring soon batches
    exp_res = await db.execute(
        select(func.count(InventoryBatch.id)).where(
            InventoryBatch.pharmacy_id == pharmacy_id,
            InventoryBatch.status == BatchStatus.ACTIVE,
            InventoryBatch.quantity_on_hand > 0,
            InventoryBatch.expires_on >= today,
            InventoryBatch.expires_on <= exp_threshold,
        )
    )
    expiring_soon = exp_res.scalar_one()

    # Expired batches
    expired_res = await db.execute(
        select(func.count(InventoryBatch.id)).where(
            InventoryBatch.pharmacy_id == pharmacy_id,
            InventoryBatch.quantity_on_hand > 0,
            InventoryBatch.expires_on < today,
        )
    )
    expired = expired_res.scalar_one()

    # Quarantined batches
    q_res = await db.execute(
        select(func.count(InventoryBatch.id)).where(
            InventoryBatch.pharmacy_id == pharmacy_id,
            InventoryBatch.status == BatchStatus.QUARANTINE,
        )
    )
    quarantine = q_res.scalar_one()

    return InventoryAlertsResponse(
        low_stock_products_count=low_stock_count,
        expiring_soon_batches_count=int(expiring_soon),
        quarantined_batches_count=int(quarantine),
        expired_batches_count=int(expired),
    )
