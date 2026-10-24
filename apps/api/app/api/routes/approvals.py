import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_and_pharmacy
from app.models.planning import Plan
from app.services.planning import get_plan
from app.schemas.plans import PlanResponse
from app.domain.enums import PlanState

router = APIRouter()


@router.get("", response_model=List[PlanResponse])
async def list_approvals(
    state: Optional[str] = Query(default=None),
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    stmt = select(Plan).where(Plan.pharmacy_id == pharmacy.id)
    if state:
        stmt = stmt.where(Plan.state == state)
    else:
        stmt = stmt.where(Plan.state.in_([PlanState.PENDING_REVIEW, PlanState.APPROVED, PlanState.REJECTED]))

    stmt = stmt.order_by(Plan.created_at.desc()).limit(50)
    res = await db.execute(stmt)
    plans = res.scalars().all()

    items = []
    for p in plans:
        items.append(await get_plan(db, pharmacy.id, p.id))
    return items
