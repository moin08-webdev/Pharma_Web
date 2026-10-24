import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Integer, BigInteger, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.domain.enums import PrescriptionStatus, LineConfirmationState
from app.models.catalog import Product


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    optional_patient_reference: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[PrescriptionStatus] = mapped_column(String(32), default=PrescriptionStatus.DRAFT, nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    documents: Mapped[list["PrescriptionDocument"]] = relationship(back_populates="prescription", cascade="all, delete-orphan")
    lines: Mapped[list["PrescriptionLine"]] = relationship(back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionDocument(Base):
    __tablename__ = "prescription_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    prescription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False, index=True)
    private_storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), default="prescription.png", nullable=False)
    media_type: Mapped[str] = mapped_column(String(64), nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    extraction_provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    retention_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    prescription: Mapped[Prescription] = relationship(back_populates="documents")


class PrescriptionLine(Base):
    __tablename__ = "prescription_lines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    prescription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False, index=True)
    raw_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    raw_strength: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    evidence_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    selected_product_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    requested_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    quantity_unit: Mapped[str] = mapped_column(String(32), default="tablet", nullable=False)
    optional_course_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    confirmation_state: Mapped[LineConfirmationState] = mapped_column(
        String(32), default=LineConfirmationState.UNCONFIRMED, nullable=False
    )

    prescription: Mapped[Prescription] = relationship(back_populates="lines")
    selected_product: Mapped[Optional[Product]] = relationship()
