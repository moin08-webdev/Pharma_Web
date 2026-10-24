import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.identity import User, Session, Pharmacy, AuthThrottle
from app.core.security import verify_password, generate_session_token, hash_token, generate_csrf_secret
from app.core.config import settings
from app.core.errors import UnauthorizedException


async def check_throttle(db: AsyncSession, email: str) -> None:
    key_hash = hash_token(email.lower())
    now = datetime.now(timezone.utc)
    res = await db.execute(select(AuthThrottle).where(AuthThrottle.key_hash == key_hash))
    throttle = res.scalar_one_or_none()
    if throttle and throttle.blocked_until and throttle.blocked_until > now:
        raise UnauthorizedException("Too many failed login attempts. Account temporarily locked.")


async def record_login_attempt(db: AsyncSession, email: str, success: bool) -> None:
    key_hash = hash_token(email.lower())
    now = datetime.now(timezone.utc)
    res = await db.execute(select(AuthThrottle).where(AuthThrottle.key_hash == key_hash))
    throttle = res.scalar_one_or_none()
    if success:
        if throttle:
            await db.delete(throttle)
            await db.commit()
    else:
        if throttle:
            throttle.attempts += 1
            if throttle.attempts >= 5:
                throttle.blocked_until = now + timedelta(minutes=15)
        else:
            throttle = AuthThrottle(key_hash=key_hash, window_start=now, attempts=1)
            db.add(throttle)
        await db.commit()


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Tuple[User, Pharmacy, str, str]:
    normalized_email = email.strip().lower()
    await check_throttle(db, normalized_email)

    res = await db.execute(
        select(User).where(User.normalized_email == normalized_email, User.active == True)
    )
    user = res.scalar_one_or_none()

    if not user or not verify_password(user.password_hash, password):
        await record_login_attempt(db, normalized_email, success=False)
        raise UnauthorizedException("Invalid email or password.")

    await record_login_attempt(db, normalized_email, success=True)

    # Fetch user's pharmacy
    p_res = await db.execute(select(Pharmacy).where(Pharmacy.id == user.pharmacy_id))
    pharmacy = p_res.scalar_one()

    # Generate session token and CSRF secret
    raw_token = generate_session_token()
    token_h = hash_token(raw_token)
    csrf_secret = generate_csrf_secret()

    now = datetime.now(timezone.utc)
    abs_expires = now + timedelta(seconds=settings.SESSION_ABSOLUTE_TTL_SECONDS)

    new_session = Session(
        user_id=user.id,
        token_hash=token_h,
        csrf_secret=csrf_secret,
        created_at=now,
        last_seen_at=now,
        absolute_expires_at=abs_expires,
    )
    db.add(new_session)
    await db.commit()

    return user, pharmacy, raw_token, csrf_secret


async def validate_session(
    db: AsyncSession, raw_token: str
) -> Tuple[User, Pharmacy, Session]:
    token_h = hash_token(raw_token)
    now = datetime.now(timezone.utc)

    stmt = (
        select(Session, User, Pharmacy)
        .join(User, Session.user_id == User.id)
        .join(Pharmacy, User.pharmacy_id == Pharmacy.id)
        .where(Session.token_hash == token_h, Session.revoked_at.is_(None))
    )
    res = await db.execute(stmt)
    row = res.first()

    if not row:
        raise UnauthorizedException("Invalid or expired session.")

    session_obj, user, pharmacy = row

    if session_obj.absolute_expires_at < now:
        session_obj.revoked_at = now
        await db.commit()
        raise UnauthorizedException("Session expired (absolute lifetime reached).")

    idle_limit = session_obj.last_seen_at + timedelta(seconds=settings.SESSION_IDLE_TTL_SECONDS)
    if idle_limit < now:
        session_obj.revoked_at = now
        await db.commit()
        raise UnauthorizedException("Session expired (idle timeout).")

    # Update last_seen_at
    session_obj.last_seen_at = now
    await db.commit()

    return user, pharmacy, session_obj


async def revoke_session(db: AsyncSession, raw_token: str) -> None:
    token_h = hash_token(raw_token)
    now = datetime.now(timezone.utc)
    await db.execute(
        update(Session).where(Session.token_hash == token_h).values(revoked_at=now)
    )
    await db.commit()
