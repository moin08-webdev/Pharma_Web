import uuid
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from app.domain.enums import UserRole


class PharmacySettingsResponse(BaseModel):
    id: uuid.UUID
    name: str
    timezone: str
    currency: str
    demo_mode: bool
    expiry_buffer_days: int
    settings_version: int
    allowed_origins: List[str]
    vision_provider: str
    external_vision_enabled: bool


class UpdatePharmacySettingsRequest(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    expiry_buffer_days: Optional[int] = Field(default=None, ge=0, le=365)
    expected_version: int


class StaffUserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole
    active: bool
    created_at: str


class StaffCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole


class StaffUpdateRequest(BaseModel):
    role: Optional[UserRole] = None
    active: Optional[bool] = None
