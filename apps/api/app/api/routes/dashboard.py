from datetime import datetime, date, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_and_pharmacy
from app.models.prescriptions import Prescription
from app.models.planning import Plan
from app.models.orders import Order
from app.domain.enums import PrescriptionStatus, PlanState
from app.services.inventory import get_inventory_alerts
from app.schemas.dashboard import DashboardStatsResponse, ActionItem

router = APIRouter()


@router.get("", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx

    # Pending prescriptions
    rx_res = await db.execute(
        select(func.count(Prescription.id)).where(
            Prescription.pharmacy_id == pharmacy.id,
            Prescription.status.in_([PrescriptionStatus.DRAFT, PrescriptionStatus.NEEDS_CONFIRMATION]),
        )
    )
    pending_rx = int(rx_res.scalar_one())

    # Pending approvals
    appr_res = await db.execute(
        select(func.count(Plan.id)).where(
            Plan.pharmacy_id == pharmacy.id,
            Plan.state == PlanState.PENDING_REVIEW,
        )
    )
    pending_appr = int(appr_res.scalar_one())

    # Completed orders today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    ord_res = await db.execute(
        select(func.count(Order.id)).where(
            Order.pharmacy_id == pharmacy.id,
            Order.completed_at >= today_start,
        )
    )
    orders_today = int(ord_res.scalar_one())

    # Inventory alerts
    inv_alerts = await get_inventory_alerts(db, pharmacy.id, pharmacy.expiry_buffer_days)

    actions = []
    if pending_appr > 0:
        actions.append(
            ActionItem(
                id="act-appr",
                type="pending_approval",
                title=f"{pending_appr} Fulfilment Plan(s) Awaiting Review",
                description="Pharmacist review and clinical authorization verification required.",
                href="/app/approvals",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        )
    if pending_rx > 0:
        actions.append(
            ActionItem(
                id="act-rx",
                type="needs_review",
                title=f"{pending_rx} Draft Prescription(s) Need Confirmation",
                description="Review extracted medicine lines, verify strengths and confirm quantities.",
                href="/app/prescriptions",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        )
    if inv_alerts.low_stock_products_count > 0:
        actions.append(
            ActionItem(
                id="act-stock",
                type="low_stock",
                title=f"{inv_alerts.low_stock_products_count} Product(s) Below Minimum Stock",
                description="Inventory level is low. Check batch balances and prepare stock receipt.",
                href="/app/inventory",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        )

    return DashboardStatsResponse(
        pending_prescriptions_count=pending_rx,
        pending_approvals_count=pending_appr,
        completed_orders_today_count=orders_today,
        low_stock_alerts_count=inv_alerts.low_stock_products_count,
        expiring_soon_alerts_count=inv_alerts.expiring_soon_batches_count,
        action_queue=actions,
    )
