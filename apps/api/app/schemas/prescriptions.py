import uuid
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.domain.enums import PrescriptionStatus, LineConfirmationState


class PrescriptionLineInput(BaseModel):
    id: Optional[uuid.UUID] = None
    raw_name: Optional[str] = None
    raw_strength: Optional[str] = None
    selected_product_id: Optional[uuid.UUID] = None
    requested_quantity: int = Field(default=1, gt=0)
    quantity_unit: str = "tablet"
    optional_course_end_date: Optional[date] = None
    confirmation_state: LineConfirmationState = LineConfirmationState.UNCONFIRMED
    evidence_json: Optional[Dict[str, Any]] = None


class CreatePrescriptionRequest(BaseModel):
    optional_patient_reference: Optional[str] = None
    sample_fixture_key: Optional[str] = None  # Explicit sample fixture loading


class BulkLinesUpdateRequest(BaseModel):
    expected_revision: int
    lines: List[PrescriptionLineInput]


class PrescriptionLineResponse(BaseModel):
    id: uuid.UUID
    raw_name: Optional[str] = None
    raw_strength: Optional[str] = None
    selected_product_id: Optional[uuid.UUID] = None
    selected_product_name: Optional[str] = None
    requested_quantity: int
    quantity_unit: str
    optional_course_end_date: Optional[str] = None
    confirmation_state: LineConfirmationState
    evidence_json: Optional[Dict[str, Any]] = None


class PrescriptionDocumentResponse(BaseModel):
    id: uuid.UUID
    file_name: str
    media_type: str
    byte_size: int
    page_count: int
    created_at: str
    extraction_provider: Optional[str] = None


class PrescriptionResponse(BaseModel):
    id: uuid.UUID
    optional_patient_reference: Optional[str] = None
    status: PrescriptionStatus
    revision: int
    created_at: str
    confirmed_at: Optional[str] = None
    lines: List[PrescriptionLineResponse]
    documents: List[PrescriptionDocumentResponse]


class PrescriptionListItem(BaseModel):
    id: uuid.UUID
    optional_patient_reference: Optional[str] = None
    status: PrescriptionStatus
    revision: int
    line_count: int
    created_at: str
