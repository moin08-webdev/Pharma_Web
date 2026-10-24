from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    PHARMACIST = "PHARMACIST"
    ASSISTANT = "ASSISTANT"


class PrescriptionStatus(str, Enum):
    DRAFT = "draft"
    EXTRACTING = "extracting"
    NEEDS_CONFIRMATION = "needs_confirmation"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PlanState(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    FINALIZED = "finalized"


class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobType(str, Enum):
    EXTRACT_PRESCRIPTION = "extract_prescription"
    IMPORT_CATALOG = "import_catalog"
    CLEANUP_UPLOADS = "cleanup_uploads"
    REFRESH_SOURCES = "refresh_sources"


class DatasetKind(str, Enum):
    DEMO = "DEMO"
    VERIFIED = "VERIFIED"


class MatchOutcome(str, Enum):
    EXACT_FORMULATION_CANDIDATE = "EXACT_FORMULATION_CANDIDATE"
    AMBIGUOUS_PRODUCT = "AMBIGUOUS_PRODUCT"
    INCOMPLETE_FORMULATION = "INCOMPLETE_FORMULATION"
    STRENGTH_MISMATCH = "STRENGTH_MISMATCH"
    INGREDIENT_SET_MISMATCH = "INGREDIENT_SET_MISMATCH"
    FORM_ROUTE_RELEASE_MISMATCH = "FORM_ROUTE_RELEASE_MISMATCH"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    NO_REVIEWED_MATCH = "NO_REVIEWED_MATCH"


class PriceKind(str, Enum):
    MRP = "mrp"
    SELLING_PRICE = "selling_price"
    ACQUISITION = "acquisition"


class BatchStatus(str, Enum):
    ACTIVE = "active"
    QUARANTINE = "quarantine"
    RECALLED = "recalled"
    EXPIRED = "expired"


class StockMovementReason(str, Enum):
    RECEIPT = "receipt"
    DISPENSE = "dispense"
    ADJUSTMENT = "adjustment"
    QUARANTINE_MOVE = "quarantine_move"
    EXPIRED_WRITE_OFF = "expired_write_off"


class ApprovalDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class LineConfirmationState(str, Enum):
    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class DataSourceKind(str, Enum):
    PMBI = "PMBI"
    ABDM = "ABDM"
    MANUAL_CSV = "MANUAL_CSV"


class ImportRunState(str, Enum):
    STAGED = "staged"
    VALIDATING = "validating"
    VALIDATED = "validated"
    ACTIVE = "active"
    FAILED = "failed"
