import math
import uuid
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.inventory import InventoryBatch
from app.models.catalog import Product
from app.domain.enums import BatchStatus
from app.schemas.plans import QuoteAllocationItem


async def allocate_batches_fefo(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    product: Product,
    requested_units: int,
    course_end_date: Optional[date] = None,
    expiry_buffer_days: int = 30,
) -> Tuple[List[QuoteAllocationItem], int, int, int, int]:
    """Allocate stock using FEFO.
    
    Returns:
        allocations: List[QuoteAllocationItem]
        supplied_units: int
        excess_units: int
        packs_needed: int
        shortage_units: int
    """
    today = date.today()
    min_expiry = today + timedelta(days=expiry_buffer_days)
    if course_end_date and course_end_date > min_expiry:
        min_expiry = course_end_date

    # Fetch eligible active batches ordered by earliest expiry
    stmt = (
        select(InventoryBatch)
        .where(
            InventoryBatch.pharmacy_id == pharmacy_id,
            InventoryBatch.product_id == product.id,
            InventoryBatch.status == BatchStatus.ACTIVE,
            InventoryBatch.quantity_on_hand > 0,
            InventoryBatch.expires_on >= min_expiry,
        )
        .order_by(InventoryBatch.expires_on.asc(), InventoryBatch.received_at.asc())
    )
    res = await db.execute(stmt)
    batches = res.scalars().all()

    pack_qty = product.pack_quantity
    pack_break = product.pack_break_allowed

    if pack_break:
        target_units = requested_units
        packs_needed = math.ceil(requested_units / pack_qty)
        supplied_units = requested_units
        excess_units = 0
    else:
        packs_needed = math.ceil(requested_units / pack_qty)
        target_units = packs_needed * pack_qty
        supplied_units = target_units
        excess_units = target_units - requested_units

    remaining_needed = target_units
    allocations: List[QuoteAllocationItem] = []

    for b in batches:
        if remaining_needed <= 0:
            break

        take = min(b.quantity_on_hand, remaining_needed)
        # Unit price calculated from pack selling price
        unit_price = int(
            (Decimal(b.selling_pack_paise) / Decimal(pack_qty)).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )

        allocations.append(
            QuoteAllocationItem(
                batch_id=b.id,
                batch_number=b.batch_number,
                quantity=take,
                expires_on=b.expires_on.isoformat(),
                mrp_pack_paise=b.mrp_pack_paise,
                selling_pack_paise=b.selling_pack_paise,
                unit_price_paise=unit_price,
            )
        )
        remaining_needed -= take

    shortage = remaining_needed if remaining_needed > 0 else 0
    return allocations, supplied_units, excess_units, packs_needed, shortage
