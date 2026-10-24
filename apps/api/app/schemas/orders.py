import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class FinalizeOrderRequest(BaseModel):
    quote_id: uuid.UUID
    approval_id: uuid.UUID


class OrderAllocationItem(BaseModel):
    id: uuid.UUID
    batch_number: str
    quantity: int
    expiry_date: str
    mrp_pack_paise: int
    selling_pack_paise: int


class OrderLineItem(BaseModel):
    id: uuid.UUID
    original_product_name: str
    dispensed_product_name: str
    requested_quantity: int
    supplied_quantity: int
    quantity_unit: str
    total_paise: int
    difference_percent: Optional[str] = None
    allocations: List[OrderAllocationItem]


class OrderDetailResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    prescription_id: uuid.UUID
    quote_id: uuid.UUID
    approval_id: uuid.UUID
    total_paise: int
    currency: str
    completed_by_name: str
    completed_at: str
    comparison_basis: str
    lines: List[OrderLineItem]


class OrderListItem(BaseModel):
    id: uuid.UUID
    order_number: str
    prescription_id: uuid.UUID
    total_paise: int
    currency: str
    completed_at: str
    item_count: int
