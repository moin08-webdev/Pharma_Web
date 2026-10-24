import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_and_pharmacy
from app.services.inventory import (
    list_inventory,
    get_product_batches,
    receive_stock,
    adjust_stock,
    get_inventory_alerts,
)
from app.schemas.inventory import (
    InventoryProductItem,
    InventoryBatchItem,
    StockReceiptRequest,
    StockAdjustmentRequest,
    InventoryAlertsResponse,
)

router = APIRouter()


@router.get("", response_model=List[InventoryProductItem])
async def get_inventory(
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await list_inventory(db, pharmacy.id)


@router.get("/alerts", response_model=InventoryAlertsResponse)
async def get_alerts(
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await get_inventory_alerts(db, pharmacy.id, pharmacy.expiry_buffer_days)


@router.get("/{product_id}", response_model=List[InventoryBatchItem])
async def get_batches(
    product_id: uuid.UUID,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await get_product_batches(db, pharmacy.id, product_id)


@router.post("/receipts", response_model=InventoryBatchItem, status_code=201)
async def receive_new_stock(
    data: StockReceiptRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    user, pharmacy, _ = ctx
    return await receive_stock(db, pharmacy.id, user.id, data)


@router.post("/adjustments", response_model=InventoryBatchItem)
async def adjust_batch(
    data: StockAdjustmentRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    user, pharmacy, _ = ctx
    return await adjust_stock(db, pharmacy.id, user.id, data)
