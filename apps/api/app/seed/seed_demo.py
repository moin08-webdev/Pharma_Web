import asyncio
import uuid
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
from app.db.session import async_session_factory
from app.models.identity import Pharmacy, User
from app.models.catalog import Ingredient, Formulation, FormulationComponent, Product, PriceObservation
from app.models.inventory import InventoryBatch, StockMovement
from app.models.sources import DataSource
from app.models.prescriptions import Prescription, PrescriptionLine
from app.domain.enums import (
    UserRole,
    DatasetKind,
    PriceKind,
    BatchStatus,
    StockMovementReason,
    PrescriptionStatus,
    LineConfirmationState,
    DataSourceKind,
)
from app.domain.signatures import build_canonical_component, compute_formulation_signature
from app.core.security import hash_password
from app.core.config import settings


async def seed() -> None:
    async with async_session_factory() as db:
        # 1. Pharmacy
        p_res = await db.execute(select(Pharmacy).where(Pharmacy.name == "PharmaBridge Demo Pharmacy"))
        pharmacy = p_res.scalar_one_or_none()
        if not pharmacy:
            pharmacy = Pharmacy(
                name="PharmaBridge Demo Pharmacy",
                timezone=settings.PHARMACY_TIMEZONE,
                currency="INR",
                demo_mode=True,
                expiry_buffer_days=settings.EXPIRY_BUFFER_DAYS,
            )
            db.add(pharmacy)
            await db.flush()
            print(f"[Seed] Created Demo Pharmacy: {pharmacy.id}")
        else:
            print(f"[Seed] Found existing Demo Pharmacy: {pharmacy.id}")

        pharmacy_id = pharmacy.id

        # 2. Staff Accounts
        users_data = [
            ("admin@pharmabridge.demo", settings.DEMO_ADMIN_PASSWORD, UserRole.ADMIN),
            ("pharmacist@pharmabridge.demo", settings.DEMO_PHARMACIST_PASSWORD, UserRole.PHARMACIST),
            ("assistant@pharmabridge.demo", settings.DEMO_ASSISTANT_PASSWORD, UserRole.ASSISTANT),
        ]

        for email, pwd, role in users_data:
            u_res = await db.execute(select(User).where(User.normalized_email == email))
            user = u_res.scalar_one_or_none()
            if not user:
                user = User(
                    pharmacy_id=pharmacy_id,
                    normalized_email=email,
                    password_hash=hash_password(pwd),
                    role=role,
                    active=True,
                )
                db.add(user)
                print(f"[Seed] Created user {email} with role {role.value}")
        await db.flush()

        # 3. Data Source
        ds_res = await db.execute(
            select(DataSource).where(DataSource.pharmacy_id == pharmacy_id, DataSource.name == "Demo Catalog Source")
        )
        data_source = ds_res.scalar_one_or_none()
        if not data_source:
            data_source = DataSource(
                pharmacy_id=pharmacy_id,
                name="Demo Catalog Source",
                kind=DataSourceKind.MANUAL_CSV,
                configured_status="active",
                allowed_usage_note="Demonstration dataset strictly for testing and validation.",
                last_success_at=datetime.now(timezone.utc),
            )
            db.add(data_source)
            await db.flush()

        # 4. Ingredients
        ingredients_map = {}
        raw_ingredients = [
            "paracetamol",
            "amoxicillin",
            "clavulanic_acid",
            "metformin",
            "metformin_hydrochloride",
            "amlodipine",
            "pantoprazole",
            "atorvastatin",
            "cetirizine",
            "telmisartan",
        ]
        for ing_name in raw_ingredients:
            ing_res = await db.execute(
                select(Ingredient).where(Ingredient.pharmacy_id == pharmacy_id, Ingredient.canonical_name == ing_name)
            )
            ing = ing_res.scalar_one_or_none()
            if not ing:
                ing = Ingredient(
                    pharmacy_id=pharmacy_id,
                    canonical_name=ing_name,
                    salt_identity=None,
                    approved_aliases=[ing_name],
                )
                db.add(ing)
                await db.flush()
            ingredients_map[ing_name] = ing

        # 5. Formulations & Products
        # Helper to create product with formulation, prices and batches
        today = date.today()

        async def create_product(
            brand_name: str,
            manufacturer: str,
            code: str,
            dosage_form: str,
            route: str,
            release_type: str,
            components_spec: list,
            pack_quantity: int,
            dispensing_unit: str,
            pack_break_allowed: bool,
            mrp_paise: int,
            selling_paise: int,
            batches_spec: list,
        ):
            prod_res = await db.execute(
                select(Product).where(Product.pharmacy_id == pharmacy_id, Product.source_product_code == code)
            )
            existing_prod = prod_res.scalar_one_or_none()
            if existing_prod:
                for b_spec in batches_spec:
                    batch_res = await db.execute(
                        select(InventoryBatch).where(
                            InventoryBatch.pharmacy_id == pharmacy_id,
                            InventoryBatch.product_id == existing_prod.id,
                            InventoryBatch.batch_number == b_spec["batch_no"],
                        )
                    )
                    b = batch_res.scalar_one_or_none()
                    if b and b.quantity_on_hand < b_spec["qty"]:
                        b.quantity_on_hand = b_spec["qty"]
                        b.status = b_spec.get("status", BatchStatus.ACTIVE)
                await db.flush()
                return existing_prod

            # Build canonical signature
            canonical_comps = [
                build_canonical_component(
                    ingredient_name=cs["ing"],
                    strength_numerator=Decimal(str(cs["num"])),
                    numerator_unit=cs["unit"],
                    component_release_type=release_type,
                )
                for cs in components_spec
            ]
            sig_str, sig_hash = compute_formulation_signature(
                dosage_form=dosage_form,
                route=route,
                release_type=release_type,
                components=canonical_comps,
            )

            # Check existing formulation
            f_res = await db.execute(
                select(Formulation).where(
                    Formulation.pharmacy_id == pharmacy_id, Formulation.signature_hash == sig_hash
                )
            )
            formulation = f_res.scalar_one_or_none()
            if not formulation:
                formulation = Formulation(
                    pharmacy_id=pharmacy_id,
                    dosage_form=dosage_form,
                    route=route,
                    release_type=release_type,
                    complete_signature=sig_str,
                    signature_hash=sig_hash,
                    review_status="reviewed",
                    reviewed_at=datetime.now(timezone.utc),
                    revision=1,
                )
                db.add(formulation)
                await db.flush()

                for cs in components_spec:
                    fc = FormulationComponent(
                        pharmacy_id=pharmacy_id,
                        formulation_id=formulation.id,
                        ingredient_id=ingredients_map[cs["ing"]].id,
                        strength_numerator=Decimal(str(cs["num"])),
                        numerator_unit=cs["unit"],
                        denominator_amount=Decimal("1.0"),
                        denominator_unit="unit",
                        component_release_type=release_type,
                    )
                    db.add(fc)
                await db.flush()

            prod = Product(
                pharmacy_id=pharmacy_id,
                source_id=data_source.id,
                source_product_code=code,
                brand_name=brand_name,
                manufacturer=manufacturer,
                formulation_id=formulation.id,
                pack_quantity=pack_quantity,
                dispensing_unit=dispensing_unit,
                pack_break_allowed=pack_break_allowed,
                dataset_kind=DatasetKind.DEMO,
                active=True,
                revision=1,
                provenance="Synthetic demo dataset",
            )
            db.add(prod)
            await db.flush()

            # Price observations
            po_mrp = PriceObservation(
                pharmacy_id=pharmacy_id,
                product_id=prod.id,
                price_kind=PriceKind.MRP,
                pack_price_paise=mrp_paise,
                pack_quantity=pack_quantity,
                currency="INR",
                observed_at=datetime.now(timezone.utc),
                effective_at=datetime.now(timezone.utc),
            )
            po_sell = PriceObservation(
                pharmacy_id=pharmacy_id,
                product_id=prod.id,
                price_kind=PriceKind.SELLING_PRICE,
                pack_price_paise=selling_paise,
                pack_quantity=pack_quantity,
                currency="INR",
                observed_at=datetime.now(timezone.utc),
                effective_at=datetime.now(timezone.utc),
            )
            db.add(po_mrp)
            db.add(po_sell)
            await db.flush()

            # Batches
            for b_spec in batches_spec:
                batch = InventoryBatch(
                    pharmacy_id=pharmacy_id,
                    product_id=prod.id,
                    batch_number=b_spec["batch_no"],
                    quantity_on_hand=b_spec["qty"],
                    quantity_unit=dispensing_unit,
                    expires_on=b_spec["expires_on"],
                    mrp_pack_paise=mrp_paise,
                    selling_pack_paise=selling_paise,
                    status=b_spec.get("status", BatchStatus.ACTIVE),
                    version=1,
                    received_at=datetime.now(timezone.utc) - timedelta(days=10),
                )
                db.add(batch)
                await db.flush()

                mv = StockMovement(
                    pharmacy_id=pharmacy_id,
                    batch_id=batch.id,
                    delta_units=b_spec["qty"],
                    reason=StockMovementReason.RECEIPT,
                    created_at=datetime.now(timezone.utc) - timedelta(days=10),
                )
                db.add(mv)

            return prod

        # SCENARIO 1: Brand A (INR 30 for 15 tablets) & matching Product B (INR 10 for 10 tablets)
        brand_a = await create_product(
            brand_name="Brand A Paracetamol",
            manufacturer="Demo Pharma Ltd",
            code="DEMO-A-500",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "paracetamol", "num": 500, "unit": "mg"}],
            pack_quantity=15,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=3000,
            selling_paise=3000,
            batches_spec=[
                {"batch_no": "BA-2026-01", "qty": 500, "expires_on": today + timedelta(days=365)},
            ],
        )

        product_b = await create_product(
            brand_name="Product B Generic Paracetamol",
            manufacturer="Affordable Generics India",
            code="DEMO-B-500",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "paracetamol", "num": 500, "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=False,  # Whole pack comparison test
            mrp_paise=1000,
            selling_paise=1000,
            batches_spec=[
                {"batch_no": "PB-2026-01", "qty": 500, "expires_on": today + timedelta(days=180)},
                {"batch_no": "PB-2026-02", "qty": 500, "expires_on": today + timedelta(days=400)},
            ],
        )

        # SCENARIO 2: Ambiguous Amlo (2.5mg vs 5mg)
        await create_product(
            brand_name="DemoAmlo 2.5",
            manufacturer="Demo Labs",
            code="DEMO-AMLO-25",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "amlodipine", "num": Decimal("2.5"), "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=2500,
            selling_paise=2200,
            batches_spec=[{"batch_no": "AM-25-01", "qty": 100, "expires_on": today + timedelta(days=300)}],
        )

        await create_product(
            brand_name="DemoAmlo 5",
            manufacturer="Demo Labs",
            code="DEMO-AMLO-50",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "amlodipine", "num": Decimal("5.0"), "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=4500,
            selling_paise=4000,
            batches_spec=[{"batch_no": "AM-50-01", "qty": 100, "expires_on": today + timedelta(days=300)}],
        )

        # SCENARIO 3: Release type mismatch (Metformin IR vs Metformin ER)
        metformin_ir = await create_product(
            brand_name="DemoMetformin IR 500",
            manufacturer="Demo Health",
            code="DEMO-MET-IR",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "metformin", "num": 500, "unit": "mg"}],
            pack_quantity=20,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=3500,
            selling_paise=3000,
            batches_spec=[{"batch_no": "MET-IR-01", "qty": 100, "expires_on": today + timedelta(days=250)}],
        )

        await create_product(
            brand_name="DemoMetformin ER 500",
            manufacturer="Demo Health",
            code="DEMO-MET-ER",
            dosage_form="tablet",
            route="oral",
            release_type="extended_release",
            components_spec=[{"ing": "metformin", "num": 500, "unit": "mg"}],
            pack_quantity=20,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=4000,
            selling_paise=3800,
            batches_spec=[{"batch_no": "MET-ER-01", "qty": 100, "expires_on": today + timedelta(days=250)}],
        )

        # SCENARIO 4: Combination (Amoxicillin + Clavulanic Acid vs Amox alone)
        await create_product(
            brand_name="DemoAugmentin 625",
            manufacturer="Demo Therapeutics",
            code="DEMO-AUG-625",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[
                {"ing": "amoxicillin", "num": 500, "unit": "mg"},
                {"ing": "clavulanic_acid", "num": 125, "unit": "mg"},
            ],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=15000,
            selling_paise=14000,
            batches_spec=[{"batch_no": "AUG-01", "qty": 60, "expires_on": today + timedelta(days=200)}],
        )

        await create_product(
            brand_name="DemoAmox 500",
            manufacturer="Demo Therapeutics",
            code="DEMO-AMOX-500",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "amoxicillin", "num": 500, "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=7000,
            selling_paise=6500,
            batches_spec=[{"batch_no": "AMOX-01", "qty": 80, "expires_on": today + timedelta(days=200)}],
        )

        # SCENARIO 5: Stock shortage / expired / quarantined (Pantoprazole 40mg)
        await create_product(
            brand_name="DemoPantop 40",
            manufacturer="Demo Gastro",
            code="DEMO-PAN-40",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "pantoprazole", "num": 40, "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=8500,
            selling_paise=8000,
            batches_spec=[
                {"batch_no": "PAN-SHORT-01", "qty": 5, "expires_on": today + timedelta(days=120), "status": BatchStatus.ACTIVE},
                {"batch_no": "PAN-EXP-02", "qty": 50, "expires_on": today - timedelta(days=10), "status": BatchStatus.EXPIRED},
                {"batch_no": "PAN-QUAR-03", "qty": 50, "expires_on": today + timedelta(days=200), "status": BatchStatus.QUARANTINE},
            ],
        )

        # 6. Sample Prescriptions
        # Create a sample prescription for walkthrough demo:
        # Line 1: Brand A Paracetamol (qty: 15) -> candidate Product B available at 50% / 33.33% savings!
        # Line 2: DemoAmlo (ambiguous / user confirmed DemoAmlo 5, qty: 10)
        # Line 3: DemoMetformin IR 500 (qty: 20)
        sample_rx_res = await db.execute(
            select(Prescription).where(
                Prescription.pharmacy_id == pharmacy_id,
                Prescription.optional_patient_reference == "SAMPLE-DEMO-001",
            )
        )
        sample_rx = sample_rx_res.scalar_one_or_none()
        if not sample_rx:
            admin_user = (await db.execute(select(User).where(User.normalized_email == "admin@pharmabridge.demo"))).scalar_one()
            sample_rx = Prescription(
                pharmacy_id=pharmacy_id,
                optional_patient_reference="SAMPLE-DEMO-001",
                status=PrescriptionStatus.NEEDS_CONFIRMATION,
                revision=1,
                created_by=admin_user.id,
            )
            db.add(sample_rx)
            await db.flush()

            l1 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=sample_rx.id,
                raw_name="Brand A Paracetamol 500mg",
                raw_strength="500 mg",
                selected_product_id=brand_a.id,
                requested_quantity=15,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={"source": "sample_fixture", "text": "Brand A Paracetamol 500mg 15 tabs"},
            )
            l2 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=sample_rx.id,
                raw_name="Amlo",
                raw_strength="5 mg",
                selected_product_id=None,  # Ambiguous, needs confirmation!
                requested_quantity=10,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.UNCONFIRMED,
                evidence_json={"source": "sample_fixture", "text": "Amlo 10 tabs (strength unverified)"},
            )
            l3 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=sample_rx.id,
                raw_name="Metformin 500mg IR",
                raw_strength="500 mg",
                selected_product_id=metformin_ir.id,
                requested_quantity=20,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={"source": "sample_fixture", "text": "Metformin 500mg IR 20 tabs"},
            )
            db.add_all([l1, l2, l3])

        await db.commit()
        print("[Seed] Seed data successfully committed.")


if __name__ == "__main__":
    asyncio.run(seed())
