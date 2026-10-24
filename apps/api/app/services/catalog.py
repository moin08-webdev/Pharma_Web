import uuid
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.catalog import Product, Formulation, FormulationComponent, Ingredient, PriceObservation
from app.models.inventory import InventoryBatch
from app.domain.enums import BatchStatus, MatchOutcome, PriceKind, DatasetKind
from app.domain.matching_rules import evaluate_formulation_match
from app.core.errors import NotFoundException
from app.schemas.medicines import (
    ProductListItem,
    ProductDetailResponse,
    FormulationSchema,
    ComponentSchema,
    PriceObservationSchema,
    CandidatesResponse,
    CandidateItem,
    RejectedCandidateItem,
)


def format_formulation_summary(formulation: Formulation) -> str:
    comps = [
        f"{c.ingredient.canonical_name} {c.strength_numerator.normalize():f}{c.numerator_unit}"
        for c in formulation.components
    ]
    return f"{', '.join(comps)} ({formulation.dosage_form})"


async def search_products(
    db: AsyncSession,
    pharmacy_id: uuid.UUID,
    query: Optional[str] = None,
    dataset_kind: Optional[DatasetKind] = None,
    limit: int = 50,
) -> List[ProductListItem]:
    stmt = (
        select(Product)
        .options(
            selectinload(Product.formulation).selectinload(Formulation.components).selectinload(FormulationComponent.ingredient),
            selectinload(Product.price_observations),
        )
        .where(Product.pharmacy_id == pharmacy_id, Product.active == True)
    )

    if dataset_kind:
        stmt = stmt.where(Product.dataset_kind == dataset_kind)

    if query:
        q = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                Product.brand_name.ilike(q),
                Product.source_product_code.ilike(q),
                Product.manufacturer.ilike(q),
            )
        )

    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    products = res.scalars().all()

    items = []
    for p in products:
        mrp = None
        for po in p.price_observations:
            if po.price_kind == PriceKind.MRP:
                mrp = po.pack_price_paise
                break

        summary = format_formulation_summary(p.formulation)
        items.append(
            ProductListItem(
                id=p.id,
                brand_name=p.brand_name,
                manufacturer=p.manufacturer,
                source_product_code=p.source_product_code,
                pack_quantity=p.pack_quantity,
                dispensing_unit=p.dispensing_unit,
                pack_break_allowed=p.pack_break_allowed,
                dataset_kind=p.dataset_kind,
                mrp_pack_paise=mrp,
                formulation_summary=summary,
                dosage_form=p.formulation.dosage_form,
                route=p.formulation.route,
                release_type=p.formulation.release_type,
            )
        )
    return items


async def get_product_detail(
    db: AsyncSession, pharmacy_id: uuid.UUID, product_id: uuid.UUID
) -> ProductDetailResponse:
    stmt = (
        select(Product)
        .options(
            selectinload(Product.formulation).selectinload(Formulation.components).selectinload(FormulationComponent.ingredient),
            selectinload(Product.price_observations),
        )
        .where(Product.pharmacy_id == pharmacy_id, Product.id == product_id)
    )
    res = await db.execute(stmt)
    product = res.scalar_one_or_none()
    if not product:
        raise NotFoundException("Product not found.")

    # Calculate current available stock
    stock_stmt = (
        select(func.coalesce(func.sum(InventoryBatch.quantity_on_hand), 0))
        .where(
            InventoryBatch.pharmacy_id == pharmacy_id,
            InventoryBatch.product_id == product_id,
            InventoryBatch.status == BatchStatus.ACTIVE,
        )
    )
    stock_res = await db.execute(stock_stmt)
    total_stock = stock_res.scalar_one()

    comp_schemas = [
        ComponentSchema(
            ingredient=c.ingredient.canonical_name,
            strength=str(c.strength_numerator),
            unit=c.numerator_unit,
            release=c.component_release_type,
        )
        for c in product.formulation.components
    ]

    form_schema = FormulationSchema(
        id=product.formulation.id,
        dosage_form=product.formulation.dosage_form,
        route=product.formulation.route,
        release_type=product.formulation.release_type,
        complete_signature=product.formulation.complete_signature,
        components=comp_schemas,
    )

    prices = [
        PriceObservationSchema(
            id=po.id,
            price_kind=po.price_kind.value if hasattr(po.price_kind, "value") else str(po.price_kind),
            pack_price_paise=po.pack_price_paise,
            pack_quantity=po.pack_quantity,
            currency=po.currency,
            observed_at=po.observed_at.isoformat(),
        )
        for po in product.price_observations
    ]

    return ProductDetailResponse(
        id=product.id,
        brand_name=product.brand_name,
        manufacturer=product.manufacturer,
        source_product_code=product.source_product_code,
        pack_quantity=product.pack_quantity,
        dispensing_unit=product.dispensing_unit,
        pack_break_allowed=product.pack_break_allowed,
        dataset_kind=product.dataset_kind,
        active=product.active,
        revision=product.revision,
        formulation=form_schema,
        latest_prices=prices,
        stock_available=int(total_stock),
    )


async def get_candidates_for_product(
    db: AsyncSession, pharmacy_id: uuid.UUID, product_id: uuid.UUID
) -> CandidatesResponse:
    target = await get_product_detail(db, pharmacy_id, product_id)

    # Extract target formulation dictionary for domain rule evaluation
    p_dict = {
        "form": target.formulation.dosage_form,
        "route": target.formulation.route,
        "release": target.formulation.release_type,
        "components": [
            {
                "ingredient": c.ingredient,
                "strength": c.strength,
                "unit": c.unit,
                "release": c.release,
            }
            for c in target.formulation.components
        ],
    }

    # Fetch all candidate products with the same dataset_kind
    stmt = (
        select(Product)
        .options(
            selectinload(Product.formulation).selectinload(Formulation.components).selectinload(FormulationComponent.ingredient),
            selectinload(Product.price_observations),
        )
        .where(
            Product.pharmacy_id == pharmacy_id,
            Product.dataset_kind == target.dataset_kind,
            Product.active == True,
        )
    )
    res = await db.execute(stmt)
    candidates_pool = res.scalars().all()

    eligible: List[CandidateItem] = []
    rejected: List[RejectedCandidateItem] = []

    for cand in candidates_pool:
        if cand.id == product_id:
            continue

        c_dict = {
            "form": cand.formulation.dosage_form,
            "route": cand.formulation.route,
            "release": cand.formulation.release_type,
            "components": [
                {
                    "ingredient": c.ingredient.canonical_name,
                    "strength": str(c.strength_numerator),
                    "unit": c.numerator_unit,
                    "release": c.component_release_type,
                }
                for c in cand.formulation.components
            ],
        }

        outcome, reason = evaluate_formulation_match(p_dict, c_dict)

        if outcome == MatchOutcome.EXACT_FORMULATION_CANDIDATE:
            # Query active stock
            stock_stmt = (
                select(func.coalesce(func.sum(InventoryBatch.quantity_on_hand), 0))
                .where(
                    InventoryBatch.pharmacy_id == pharmacy_id,
                    InventoryBatch.product_id == cand.id,
                    InventoryBatch.status == BatchStatus.ACTIVE,
                )
            )
            s_res = await db.execute(stock_stmt)
            stock = int(s_res.scalar_one())

            # Find price
            price_paise = None
            for po in cand.price_observations:
                if po.price_kind in (PriceKind.SELLING_PRICE, PriceKind.MRP):
                    price_paise = po.pack_price_paise
                    break

            eligible.append(
                CandidateItem(
                    product_id=cand.id,
                    brand_name=cand.brand_name,
                    manufacturer=cand.manufacturer,
                    pack_quantity=cand.pack_quantity,
                    dispensing_unit=cand.dispensing_unit,
                    pack_break_allowed=cand.pack_break_allowed,
                    dataset_kind=cand.dataset_kind,
                    outcome=outcome,
                    match_reason=reason,
                    pack_price_paise=price_paise,
                    available_stock_units=stock,
                    is_local_stock_confirmed=(stock > 0),
                    requires_authorization=False,
                )
            )
        else:
            rejected.append(
                RejectedCandidateItem(
                    product_id=cand.id,
                    brand_name=cand.brand_name,
                    outcome=outcome,
                    rejection_reason=reason,
                )
            )

    return CandidatesResponse(
        prescribed_product_id=product_id,
        eligible_candidates=eligible,
        rejected_alternatives=rejected,
    )
