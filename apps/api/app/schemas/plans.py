import uuid
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.domain.enums import PlanState, ApprovalDecision, DatasetKind


class CreatePlanRequest(BaseModel):
    prescription_id: uuid.UUID


class UpdatePlanLineSelectionRequest(BaseModel):
    selected_product_id: uuid.UUID
    selection_reason: str = "candidate_selected"
    authorization_required: bool = False
    authorization_reference: Optional[str] = None
    expected_plan_version: int


class QuoteAllocationItem(BaseModel):
    batch_id: uuid.UUID
    batch_number: str
    quantity: int
    expires_on: str
    mrp_pack_paise: int
    selling_pack_paise: int
    unit_price_paise: int


class QuoteLineItem(BaseModel):
    prescription_line_id: uuid.UUID
    original_product_id: uuid.UUID
    original_brand_name: str
    selected_product_id: uuid.UUID
    selected_brand_name: str
    requested_units: int
    supplied_units: int
    excess_units: int
    packs_needed: int
    unit_dispensing: bool
    baseline_line_paise: Optional[int] = None
    selected_line_paise: Optional[int] = None
    difference_percent: Optional[str] = None
    allocations: List[QuoteAllocationItem] = Field(default_factory=list)
    shortage_units: int = 0
    authorization_required: bool = False
    authorization_reference: Optional[str] = None
    notes: Optional[str] = None


class QuoteCoverage(BaseModel):
    requested_lines: int
    fulfilled_lines: int
    comparable_lines: int


class QuoteTotals(BaseModel):
    currency: str = "INR"
    baseline_total_paise: Optional[int] = None
    selected_total_paise: Optional[int] = None
    comparable_subset_baseline_paise: Optional[int] = None
    comparable_subset_selected_paise: Optional[int] = None
    comparable_subset_difference_percent: Optional[str] = None
    comparison_basis: str


class QuoteBlocker(BaseModel):
    code: str
    message: str
    line_id: Optional[uuid.UUID] = None


class QuoteResponse(BaseModel):
    quote_id: uuid.UUID
    plan_id: uuid.UUID
    plan_version: int
    prescription_revision: int
    dataset_kind: DatasetKind
    expires_at: str
    coverage: QuoteCoverage
    finalizable: bool
    blockers: List[QuoteBlocker] = Field(default_factory=list)
    totals: QuoteTotals
    lines: List[QuoteLineItem]


class PlanLineResponse(BaseModel):
    id: uuid.UUID
    prescription_line_id: uuid.UUID
    selected_product_id: uuid.UUID
    selected_brand_name: str
    selection_reason: str
    authorization_required: bool
    authorization_reference: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: uuid.UUID
    decision: ApprovalDecision
    actor_id: uuid.UUID
    actor_name: str
    actor_role: str
    reason: Optional[str] = None
    authorization_reference: Optional[str] = None
    created_at: str


class PlanResponse(BaseModel):
    id: uuid.UUID
    prescription_id: uuid.UUID
    prescription_revision: int
    version: int
    state: PlanState
    created_at: str
    lines: List[PlanLineResponse]
    current_quote: Optional[QuoteResponse] = None
    approval: Optional[ApprovalResponse] = None


class ApprovalRequest(BaseModel):
    quote_id: uuid.UUID
    decision: ApprovalDecision
    reason: Optional[str] = None
    authorization_reference: Optional[str] = None
