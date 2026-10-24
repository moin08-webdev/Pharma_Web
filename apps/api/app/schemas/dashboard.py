from pydantic import BaseModel
from typing import List


class ActionItem(BaseModel):
    id: str
    type: str  # e.g. "needs_review", "pending_approval", "low_stock"
    title: str
    description: str
    href: str
    created_at: str


class DashboardStatsResponse(BaseModel):
    pending_prescriptions_count: int
    pending_approvals_count: int
    completed_orders_today_count: int
    low_stock_alerts_count: int
    expiring_soon_alerts_count: int
    action_queue: List[ActionItem]
