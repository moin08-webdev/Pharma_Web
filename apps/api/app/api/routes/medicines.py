import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_and_pharmacy
from app.services.catalog import search_products, get_product_detail, get_candidates_for_product
from app.schemas.medicines import ProductListItem, ProductDetailResponse, CandidatesResponse

router = APIRouter()


@router.get("", response_model=List[ProductListItem])
async def list_medicines(
    q: Optional[str] = Query(default=None),
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await search_products(db, pharmacy.id, query=q)


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_single_medicine(
    product_id: uuid.UUID,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await get_product_detail(db, pharmacy.id, product_id)


@router.get("/{product_id}/candidates", response_model=CandidatesResponse)
async def get_medicine_candidates(
    product_id: uuid.UUID,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await get_candidates_for_product(db, pharmacy.id, product_id)
