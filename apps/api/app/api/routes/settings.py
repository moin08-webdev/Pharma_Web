import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_and_pharmacy
from app.models.identity import User, Pharmacy
from app.domain.enums import UserRole
from app.core.permissions import require_admin
from app.core.security import hash_password
from app.core.errors import NotFoundException, ConflictException
from app.core.config import settings as app_settings
from app.schemas.settings import (
    PharmacySettingsResponse,
    UpdatePharmacySettingsRequest,
    StaffUserResponse,
    StaffCreateRequest,
    StaffUpdateRequest,
)

router = APIRouter()


@router.get("", response_model=PharmacySettingsResponse)
async def get_settings(
    ctx=Depends(get_current_user_and_pharmacy),
):
    _, pharmacy, _ = ctx
    return PharmacySettingsResponse(
        id=pharmacy.id,
        name=pharmacy.name,
        timezone=pharmacy.timezone,
        currency=pharmacy.currency,
        demo_mode=pharmacy.demo_mode,
        expiry_buffer_days=pharmacy.expiry_buffer_days,
        settings_version=pharmacy.settings_version,
        allowed_origins=app_settings.allowed_origins_list,
        vision_provider=app_settings.VISION_PROVIDER,
        external_vision_enabled=app_settings.EXTERNAL_VISION_ENABLED,
    )


@router.patch("", response_model=PharmacySettingsResponse)
async def update_settings(
    data: UpdatePharmacySettingsRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    user, pharmacy, _ = ctx
    require_admin(user)

    if pharmacy.settings_version != data.expected_version:
        raise ConflictException(
            f"Settings version mismatch. Expected {data.expected_version}, current is {pharmacy.settings_version}."
        )

    if data.name:
        pharmacy.name = data.name
    if data.timezone:
        pharmacy.timezone = data.timezone
    if data.expiry_buffer_days is not None:
        pharmacy.expiry_buffer_days = data.expiry_buffer_days

    pharmacy.settings_version += 1
    await db.commit()
    await db.refresh(pharmacy)

    return PharmacySettingsResponse(
        id=pharmacy.id,
        name=pharmacy.name,
        timezone=pharmacy.timezone,
        currency=pharmacy.currency,
        demo_mode=pharmacy.demo_mode,
        expiry_buffer_days=pharmacy.expiry_buffer_days,
        settings_version=pharmacy.settings_version,
        allowed_origins=app_settings.allowed_origins_list,
        vision_provider=app_settings.VISION_PROVIDER,
        external_vision_enabled=app_settings.EXTERNAL_VISION_ENABLED,
    )


@router.get("/staff", response_model=List[StaffUserResponse])
async def list_staff(
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    _, pharmacy, _ = ctx
    stmt = (
        select(User)
        .where(User.pharmacy_id == pharmacy.id)
        .order_by(User.created_at.asc())
    )
    res = await db.execute(stmt)
    users = res.scalars().all()

    return [
        StaffUserResponse(
            id=u.id,
            email=u.normalized_email,
            role=u.role,
            active=u.active,
            created_at=u.created_at.isoformat(),
        )
        for u in users
    ]


@router.post("/staff", response_model=StaffUserResponse, status_code=201)
async def create_staff(
    data: StaffCreateRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    admin_user, pharmacy, _ = ctx
    require_admin(admin_user)

    norm_email = data.email.strip().lower()
    existing_res = await db.execute(select(User).where(User.normalized_email == norm_email))
    if existing_res.scalar_one_or_none():
        raise ConflictException("A user with this email address already exists.")

    new_user = User(
        pharmacy_id=pharmacy.id,
        normalized_email=norm_email,
        password_hash=hash_password(data.password),
        role=data.role,
        active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return StaffUserResponse(
        id=new_user.id,
        email=new_user.normalized_email,
        role=new_user.role,
        active=new_user.active,
        created_at=new_user.created_at.isoformat(),
    )


@router.patch("/staff/{staff_id}", response_model=StaffUserResponse)
async def update_staff_member(
    staff_id: uuid.UUID,
    data: StaffUpdateRequest,
    ctx=Depends(get_current_user_and_pharmacy),
    db: AsyncSession = Depends(get_db),
):
    admin_user, pharmacy, _ = ctx
    require_admin(admin_user)

    res = await db.execute(
        select(User).where(User.pharmacy_id == pharmacy.id, User.id == staff_id)
    )
    user = res.scalar_one_or_none()
    if not user:
        raise NotFoundException("Staff member not found.")

    if data.role is not None:
        user.role = data.role
    if data.active is not None:
        user.active = data.active

    await db.commit()
    await db.refresh(user)

    return StaffUserResponse(
        id=user.id,
        email=user.normalized_email,
        role=user.role,
        active=user.active,
        created_at=user.created_at.isoformat(),
    )
