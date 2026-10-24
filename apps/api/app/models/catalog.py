import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.domain.enums import DatasetKind, PriceKind


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    standardized_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    salt_identity: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_aliases: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)


class Formulation(Base):
    __tablename__ = "formulations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    dosage_form: Mapped[str] = mapped_column(String(64), nullable=False)
    route: Mapped[str] = mapped_column(String(64), default="oral", nullable=False)
    release_type: Mapped[str] = mapped_column(String(64), default="immediate_release", nullable=False)
    complete_signature: Mapped[str] = mapped_column(Text, nullable=False)
    signature_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    review_status: Mapped[str] = mapped_column(String(32), default="reviewed", nullable=False)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    substitution_policy: Mapped[Optional[str]] = mapped_column(String(64), default="permitted", nullable=True)

    components: Mapped[list["FormulationComponent"]] = relationship(back_populates="formulation", cascade="all, delete-orphan")
    products: Mapped[list["Product"]] = relationship(back_populates="formulation")


class FormulationComponent(Base):
    __tablename__ = "formulation_components"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    formulation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("formulations.id"), nullable=False, index=True)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ingredients.id"), nullable=False, index=True)
    strength_numerator: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    numerator_unit: Mapped[str] = mapped_column(String(32), nullable=False)
    denominator_amount: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("1.0"), nullable=False)
    denominator_unit: Mapped[str] = mapped_column(String(32), default="unit", nullable=False)
    strength_basis: Mapped[str] = mapped_column(String(64), default="active_moiety", nullable=False)
    component_release_type: Mapped[str] = mapped_column(String(64), default="immediate_release", nullable=False)

    formulation: Mapped[Formulation] = relationship(back_populates="components")
    ingredient: Mapped[Ingredient] = relationship()


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    source_product_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    formulation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("formulations.id"), nullable=False, index=True)
    pack_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    dispensing_unit: Mapped[str] = mapped_column(String(32), default="tablet", nullable=False)
    pack_break_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dataset_kind: Mapped[DatasetKind] = mapped_column(String(32), default=DatasetKind.DEMO, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    provenance: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    formulation: Mapped[Formulation] = relationship(back_populates="products")
    price_observations: Mapped[list["PriceObservation"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class PriceObservation(Base):
    __tablename__ = "price_observations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pharmacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=False, index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    price_kind: Mapped[PriceKind] = mapped_column(String(32), default=PriceKind.MRP, nullable=False)
    pack_price_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    pack_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    source_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="verified", nullable=False)

    product: Mapped[Product] = relationship(back_populates="price_observations")
