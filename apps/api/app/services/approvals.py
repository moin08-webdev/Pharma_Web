import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.planning import Plan, Quote, Approval
from app.models.identity import User
from app.domain.enums import PlanState, ApprovalDecision, UserRole
from app.core.permissions import require_pharmacist
from app.core.errors import NotFoundException, ConflictException, ForbiddenException, QuoteStaleException
from app.schemas.plans import ApprovalRequest, PlanResponse
from app.services.planning import get_plan


async def approve_or_reject_plan(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    user: User,
    plan_id: uuid.UUID,
    data: ApprovalRequest,
) -> PlanResponse:
    # 1. Enforce pharmacist permission
    require_pharmacist(user)

    # 2. Fetch plan
    stmt = select(Plan).where(Plan.pharmacy_id == pharmacy_id, Plan.id == plan_id)
    res = await db.execute(stmt)
    plan = res.scalar_one_or_none()
    if not plan:
        raise NotFoundException("Plan not found.")

    # 3. Fetch quote
    q_stmt = select(Quote).where(
        Quote.pharmacy_id == pharmacy_id, Quote.id == data.quote_id, Quote.plan_id == plan.id
    )
    q_res = await db.execute(q_stmt)
    quote = q_res.scalar_one_or_none()
    if not quote:
        raise NotFoundException("Quote not found.")

    now = datetime.now(timezone.utc)
    if quote.expires_at < now:
        raise QuoteStaleException("Quote has expired (5-minute TTL reached). Refresh quote before approving.")

    if quote.consumed_at is not None:
        raise ConflictException("Quote has already been consumed by an order.")

    payload = quote.immutable_payload_json

    if data.decision == ApprovalDecision.APPROVED:
        # Check blockers
        if not payload.get("finalizable", False):
            blockers = payload.get("blockers", [])
            msg = "Plan cannot be approved due to active blockers: " + ", ".join(
                b.get("message", b.get("code")) for b in blockers
            )
            raise ConflictException(msg)

        plan.state = PlanState.APPROVED
    else:
        plan.state = PlanState.REJECTED

    # Create approval record bound to exact quote_id
    approval = Approval(
        pharmacy_id=pharmacy_id,
        quote_id=quote.id,
        decision=data.decision,
        actor_id=user.id,
        reason=data.reason,
        authorization_reference=data.authorization_reference,
        created_at=now,
    )
    db.add(approval)
    await db.commit()

    return await get_plan(db, pharmacy_id, plan_id)
