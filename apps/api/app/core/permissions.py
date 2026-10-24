from app.domain.enums import UserRole
from app.core.errors import ForbiddenException
from app.models.identity import User


def check_role(user: User, allowed_roles: list[UserRole]) -> None:
    if user.role not in allowed_roles:
        raise ForbiddenException(
            f"Role '{user.role}' is not authorized. Required: {[r.value for r in allowed_roles]}"
        )


def require_pharmacist(user: User) -> None:
    """Enforce clinical role: only PHARMACIST can approve plans or finalize orders."""
    if user.role != UserRole.PHARMACIST:
        raise ForbiddenException("Only registered Pharmacists are authorized to approve plans or finalize orders.")


def require_admin(user: User) -> None:
    """Enforce admin role for staff management, data sources and settings."""
    if user.role != UserRole.ADMIN:
        raise ForbiddenException("Administrator privileges required.")
