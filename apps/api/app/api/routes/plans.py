import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_and_pharmacy
from app.services.planning import (
    create_plan,
    get_plan,
    update_plan_line_selection,
    generate_quote,
    submit_plan_for_review,
)
from app.services.approvals import approve_or_reject_plan
from app.schemas.plans import (
    CreatePlanRequest,
    PlanResponse,
    UpdatePlanLineSelectionRequest,
    QuoteResponse,
    ApprovalRequest,
)

router = APIRouter()


@router.post("", response_model=PlanResponse, status_code=201)
async def create_new_plan(
    data: CreatePlanRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    user, pharmacy, _ = ctx
    return await create_plan(db, pharmacy.id, user.id, data.prescription_id)


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_single_plan(
    plan_id: uuid.UUID,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await get_plan(db, pharmacy.id, plan_id)


@router.patch("/{plan_id}/lines/{line_id}", response_model=PlanResponse)
async def update_line_selection(
    plan_id: uuid.UUID,
    line_id: uuid.UUID,
    data: UpdatePlanLineSelectionRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await update_plan_line_selection(db, pharmacy.id, plan_id, line_id, data)


@router.post("/{plan_id}/quotes", response_model=PlanResponse)
async def regenerate_quote_for_plan(
    plan_id: uuid.UUID,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    plan_resp = await get_plan(db, pharmacy.id, plan_id)
    # Fetch plan entity and generate quote
    from app.models.planning import Plan
    from sqlalchemy import select
    p_res = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = p_res.scalar_one()
    await generate_quote(db, pharmacy.id, plan)
    await db.commit()
    return await get_plan(db, pharmacy.id, plan_id)


@router.post("/{plan_id}/submit", response_model=PlanResponse)
async def submit_for_review(
    plan_id: uuid.UUID,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    return await submit_plan_for_review(db, pharmacy.id, plan_id)


@router.post("/{plan_id}/approvals", response_model=PlanResponse)
async def approve_plan(
    plan_id: uuid.UUID,
    data: ApprovalRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    user, pharmacy, _ = ctx
    return await approve_or_reject_plan(db, pharmacy.id, user, plan_id, data)
