import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_and_pharmacy
from app.services.orders import finalize_order, list_orders, get_order_detail
from app.schemas.orders import FinalizeOrderRequest, OrderDetailResponse, OrderListItem

router = APIRouter()


@router.post("", response_model=OrderDetailResponse, status_code=201)
async def finalize_new_order(
    data: FinalizeOrderRequest,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    user, pharmacy, _ = ctx
    key = idempotency_key or str(uuid.uuid4())
    return await finalize_order(db, pharmacy.id, user, data, key)


@router.get("", response_model=List[OrderListItem])
async def get_all_orders(
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await list_orders(db, pharmacy.id)


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_single_order(
    order_id: uuid.UUID,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await get_order_detail(db, pharmacy.id, order_id)


@router.get("/{order_id}/export")
async def export_order(
    order_id: uuid.UUID,
    format: str = "csv",
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    order = await get_order_detail(db, pharmacy.id, order_id)

    # Generate CSV lines
    csv_rows = [
        "Order Number,Date,Prescribed Medicine,Dispensed Medicine,Quantity,Unit,Line Total (Paise),Line Total (INR),Difference %",
    ]
    for line in order.lines:
        line_inr = f"{line.total_paise / 100:.2f}"
        diff = line.difference_percent or "0.00"
        csv_rows.append(
            f'"{order.order_number}","{order.completed_at}","{line.original_product_name}","{line.dispensed_product_name}",{line.supplied_quantity},"{line.quantity_unit}",{line.total_paise},{line_inr},"{diff}"'
        )

    content = "\n".join(csv_rows)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="dispensing_{order.order_number}.csv"'},
    )
