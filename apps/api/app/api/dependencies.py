import uuid
from typing import Tuple, Optional
from fastapi import Request, Depends, Header, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.models.identity import User, Pharmacy, Session
from app.services.auth import validate_session
from app.core.errors import UnauthorizedException, ForbiddenException
from app.domain.enums import UserRole


async def get_db() -> AsyncSession:
    async for session in get_db_session():
        yield session


async def get_current_user_and_pharmacy(
    request: Request,
    db: AsyncSession = Depends(get_db),
    pharmabridge_session: Optional[str] = Cookie(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Tuple[User, Pharmacy, Session]:
    token = pharmabridge_session
    if not token and authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        raise UnauthorizedException("Authentication session required.")

    return await validate_session(db, token)


async def get_current_user(
    auth_ctx: Tuple[User, Pharmacy, Session] = Depends(get_current_user_and_pharmacy)
) -> User:
    return auth_ctx[0]


async def get_current_pharmacy(
    auth_ctx: Tuple[User, Pharmacy, Session] = Depends(get_current_user_and_pharmacy)
) -> Pharmacy:
    return auth_ctx[1]


def require_role(roles: list[UserRole]):
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenException(
                f"Action not permitted for role '{user.role}'. Required: {[r.value for r in roles]}"
            )
        return user

    return role_checker
