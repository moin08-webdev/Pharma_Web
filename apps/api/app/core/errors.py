import uuid
from typing import Optional, Dict, Any
from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        field_errors: Optional[Dict[str, str]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.field_errors = field_errors or {}
        super().__init__(message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(code="NOT_FOUND", message=message, status_code=404)


class ConflictException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(code="CONFLICT", message=message, status_code=409, details=details)


class QuoteStaleException(AppException):
    def __init__(
        self,
        message: str = "Stock or pricing changed after this plan was reviewed. Refresh the plan and review it again.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code="QUOTE_STALE",
            message=message,
            status_code=409,
            details=details or {"refresh_required": True},
        )


class InsufficientStockException(AppException):
    def __init__(
        self,
        message: str = "Insufficient stock available for the selected medicines.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code="INSUFFICIENT_STOCK",
            message=message,
            status_code=409,
            details=details or {},
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "field_errors": exc.field_errors,
                "request_id": request_id,
                "details": exc.details,
            }
        },
    )
