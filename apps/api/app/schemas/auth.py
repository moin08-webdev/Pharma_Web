import uuid
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.domain.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole
    active: bool


class PharmacyResponse(BaseModel):
    id: uuid.UUID
    name: str
    timezone: str
    currency: str
    demo_mode: bool
    expiry_buffer_days: int
    settings_version: int


class SessionContextResponse(BaseModel):
    user: UserResponse
    pharmacy: PharmacyResponse
    csrf_token: str
    permissions: List[str]
