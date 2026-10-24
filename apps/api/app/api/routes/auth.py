from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_and_pharmacy
from app.schemas.auth import LoginRequest, SessionContextResponse, UserResponse, PharmacyResponse
from app.services.auth import authenticate_user, revoke_session
from app.core.config import settings
from typing import Optional

router = APIRouter()


@router.post("/login", response_model=SessionContextResponse)
async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user, pharmacy, token, csrf = await authenticate_user(db, data.email, data.password)

    # Set HttpOnly session cookie
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=settings.SESSION_ABSOLUTE_TTL_SECONDS,
        path="/",
    )

    permissions = ["read:prescriptions", "write:prescriptions", "read:inventory"]
    if user.role in ("ADMIN", "PHARMACIST"):
        permissions.append("read:approvals")
    if user.role == "PHARMACIST":
        permissions.extend(["approve:plans", "finalize:orders"])
    if user.role == "ADMIN":
        permissions.extend(["manage:staff", "manage:settings", "manage:sources"])

    return SessionContextResponse(
        user=UserResponse(
            id=user.id,
            email=user.normalized_email,
            role=user.role,
            active=user.active,
        ),
        pharmacy=PharmacyResponse(
            id=pharmacy.id,
            name=pharmacy.name,
            timezone=pharmacy.timezone,
            currency=pharmacy.currency,
            demo_mode=pharmacy.demo_mode,
            expiry_buffer_days=pharmacy.expiry_buffer_days,
            settings_version=pharmacy.settings_version,
        ),
        csrf_token=csrf,
        permissions=permissions,
    )


@router.post("/logout")
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    pharmabridge_session: Optional[str] = Cookie(default=None),
):
    if pharmabridge_session:
        await revoke_session(db, pharmabridge_session)
    response.delete_cookie(key=settings.SESSION_COOKIE_NAME, path="/")
    return {"status": "logged_out"}


@router.get("/me", response_model=SessionContextResponse)
async def get_me(
    ctx=Depends(get_current_user_and_pharmacy),
):
    user, pharmacy, session_obj = ctx
    permissions = ["read:prescriptions", "write:prescriptions", "read:inventory"]
    if user.role in ("ADMIN", "PHARMACIST"):
        permissions.append("read:approvals")
    if user.role == "PHARMACIST":
        permissions.extend(["approve:plans", "finalize:orders"])
    if user.role == "ADMIN":
        permissions.extend(["manage:staff", "manage:settings", "manage:sources"])

    return SessionContextResponse(
        user=UserResponse(
            id=user.id,
            email=user.normalized_email,
            role=user.role,
            active=user.active,
        ),
        pharmacy=PharmacyResponse(
            id=pharmacy.id,
            name=pharmacy.name,
            timezone=pharmacy.timezone,
            currency=pharmacy.currency,
            demo_mode=pharmacy.demo_mode,
            expiry_buffer_days=pharmacy.expiry_buffer_days,
            settings_version=pharmacy.settings_version,
        ),
        csrf_token=session_obj.csrf_secret,
        permissions=permissions,
    )
