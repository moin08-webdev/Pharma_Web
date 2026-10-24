import secrets
import hashlib
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=2,
    memory_cost=19456,
    parallelism=1,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(hash_str: str, password: str) -> bool:
    try:
        return ph.verify(hash_str, password)
    except (VerifyMismatchError, Exception):
        return False


def generate_session_token() -> str:
    """Generate a cryptographically secure 256-bit (32 bytes) hex session token."""
    return secrets.token_hex(32)


def hash_token(token: str) -> str:
    """Store only sha256 hash of session token in database."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_csrf_secret() -> str:
    return secrets.token_urlsafe(32)
