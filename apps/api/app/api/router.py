from fastapi import APIRouter
from app.api.routes import (
    health,
    auth,
    dashboard,
    prescriptions,
    medicines,
    plans,
    approvals,
    inventory,
    orders,
    settings,
)

api_router = APIRouter()

# Health endpoints mounted at root as well as /api/health
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# v1 routes
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
v1_router.include_router(prescriptions.router, prefix="/prescriptions", tags=["Prescriptions"])
v1_router.include_router(medicines.router, prefix="/medicines", tags=["Medicines"])
v1_router.include_router(plans.router, prefix="/plans", tags=["Plans"])
v1_router.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])
v1_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
v1_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
v1_router.include_router(settings.router, prefix="/settings", tags=["Settings"])

api_router.include_router(v1_router)
