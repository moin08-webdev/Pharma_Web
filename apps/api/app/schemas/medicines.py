import uuid
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.domain.enums import DatasetKind, MatchOutcome


class ComponentSchema(BaseModel):
    ingredient: str
    strength: str
    unit: str
    release: str


class FormulationSchema(BaseModel):
    id: uuid.UUID
    dosage_form: str
    route: str
    release_type: str
    complete_signature: str
    components: List[ComponentSchema]


class PriceObservationSchema(BaseModel):
    id: uuid.UUID
    price_kind: str
    pack_price_paise: int
    pack_quantity: int
    currency: str
    observed_at: str


class ProductListItem(BaseModel):
    id: uuid.UUID
    brand_name: str
    manufacturer: str
    source_product_code: str
    pack_quantity: int
    dispensing_unit: str
    pack_break_allowed: bool
    dataset_kind: DatasetKind
    mrp_pack_paise: Optional[int] = None
    formulation_summary: str
    dosage_form: str
    route: str
    release_type: str


class ProductDetailResponse(BaseModel):
    id: uuid.UUID
    brand_name: str
    manufacturer: str
    source_product_code: str
    pack_quantity: int
    dispensing_unit: str
    pack_break_allowed: bool
    dataset_kind: DatasetKind
    active: bool
    revision: int
    formulation: FormulationSchema
    latest_prices: List[PriceObservationSchema]
    stock_available: int


class CandidateItem(BaseModel):
    product_id: uuid.UUID
    brand_name: str
    manufacturer: str
    pack_quantity: int
    dispensing_unit: str
    pack_break_allowed: bool
    dataset_kind: DatasetKind
    outcome: MatchOutcome
    match_reason: str
    pack_price_paise: Optional[int] = None
    available_stock_units: int = 0
    is_local_stock_confirmed: bool = False
    requires_authorization: bool = False


class RejectedCandidateItem(BaseModel):
    product_id: uuid.UUID
    brand_name: str
    outcome: MatchOutcome
    rejection_reason: str


class CandidatesResponse(BaseModel):
    prescribed_product_id: uuid.UUID
    eligible_candidates: List[CandidateItem]
    rejected_alternatives: List[RejectedCandidateItem]
