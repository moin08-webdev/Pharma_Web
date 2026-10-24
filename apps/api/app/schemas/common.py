from typing import Generic, TypeVar, List, Optional, Dict, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    next_cursor: Optional[str] = None


class StandardErrorDetail(BaseModel):
    code: str
    message: str
    field_errors: Dict[str, str] = Field(default_factory=dict)
    request_id: str
    details: Dict[str, Any] = Field(default_factory=dict)


class StandardErrorResponse(BaseModel):
    error: StandardErrorDetail
