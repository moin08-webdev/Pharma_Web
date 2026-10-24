import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.domain.enums import BatchStatus, StockMovementReason, DatasetKind


class InventoryBatchItem(BaseModel):
    id: uuid.UUID
    batch_number: str
    quantity_on_hand: int
    quantity_unit: str
    expires_on: str
    expiry_precision: str
    mrp_pack_paise: int
    selling_pack_paise: int
    status: BatchStatus
    version: int
    received_at: str


class InventoryProductItem(BaseModel):
    product_id: uuid.UUID
    brand_name: str
    manufacturer: str
    dataset_kind: DatasetKind
    pack_quantity: int
    dispensing_unit: str
    total_quantity_on_hand: int
    active_batches_count: int
    nearest_expiry: Optional[str] = None
    is_low_stock: bool = False
    has_quarantine: bool = False


class StockReceiptRequest(BaseModel):
    product_id: uuid.UUID
    batch_number: str
    quantity_units: int = Field(gt=0)
    quantity_unit: str = "tablet"
    expires_on: date
    mrp_pack_paise: int = Field(gt=0)
    selling_pack_paise: int = Field(gt=0)


class StockAdjustmentRequest(BaseModel):
    batch_id: uuid.UUID
    delta_units: int
    reason: StockMovementReason
    expected_version: int
    note: Optional[str] = None


class InventoryAlertsResponse(BaseModel):
    low_stock_products_count: int
    expiring_soon_batches_count: int
    quarantined_batches_count: int
    expired_batches_count: int
