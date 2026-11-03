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
from app.models.planning import Plan, PlanLine, Quote, Approval
from app.models.orders import Order, OrderLine, OrderAllocation
from app.domain.enums import (
    UserRole,
    DatasetKind,
    PriceKind,
    BatchStatus,
    StockMovementReason,
    PrescriptionStatus,
    LineConfirmationState,
    DataSourceKind,
    PlanState,
    ApprovalDecision,
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

        # Fetch staff user references for later prescription/order authoring
        admin_user = (
            await db.execute(select(User).where(User.normalized_email == "admin@pharmabridge.demo"))
        ).scalar_one()
        pharmacist_user = (
            await db.execute(select(User).where(User.normalized_email == "pharmacist@pharmabridge.demo"))
        ).scalar_one()

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
            "ibuprofen",
            "azithromycin",
            "domperidone",
            "fexofenadine",
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
            provenance: str = "Synthetic demo dataset",
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
                    elif not b:
                        batch = InventoryBatch(
                            pharmacy_id=pharmacy_id,
                            product_id=existing_prod.id,
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
                provenance=provenance,
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

        # =====================================================================
        # BENCHMARK PRODUCTS (Preserved for automated tests and E2E verification)
        # =====================================================================

        # Benchmark 1: Brand A Paracetamol (INR 30 for 15 tablets)
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
            provenance="Benchmark demo baseline",
        )

        # Benchmark 2: Product B Generic Paracetamol (INR 10 for 10 tablets, whole pack -> 33.33% savings)
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
            provenance="Benchmark demo baseline",
        )

        # Benchmark 3: DemoAmlo (2.5mg vs 5mg)
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
            provenance="Benchmark demo baseline",
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
            provenance="Benchmark demo baseline",
        )

        # Benchmark 4: Metformin IR vs Metformin ER (release type mismatch test)
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
            provenance="Benchmark demo baseline",
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
            provenance="Benchmark demo baseline",
        )

        # Benchmark 5: Combination vs Single (Amox + Clav vs Amox alone)
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
            provenance="Benchmark demo baseline",
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
            provenance="Benchmark demo baseline",
        )

        # Benchmark 6: Stock status demonstration (Pantoprazole 40mg with short, expired, quarantined batches)
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
            provenance="Benchmark demo baseline",
        )

        # =====================================================================
        # AUTHENTIC INDIAN PHARMACEUTICAL CATALOG (Requirement R2)
        # =====================================================================

        # Category 1: Analgesics / Antipyretics
        dolo_650 = await create_product(
            brand_name="Dolo 650",
            manufacturer="Micro Labs Ltd",
            code="MIC-DOLO-650",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "paracetamol", "num": 650, "unit": "mg"}],
            pack_quantity=15,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=3450,
            selling_paise=3200,
            batches_spec=[
                {"batch_no": "ML-24K091", "qty": 450, "expires_on": today + timedelta(days=420)},
                {"batch_no": "ML-24K092", "qty": 150, "expires_on": today + timedelta(days=600)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        await create_product(
            brand_name="Paracetamol IP 650mg",
            manufacturer="PMBI / Karnataka Antibiotics & Pharmaceuticals Ltd",
            code="PMBI-PCM-650",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "paracetamol", "num": 650, "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=False,  # Whole pack Jan Aushadhi packaging
            mrp_paise=1200,
            selling_paise=1000,
            batches_spec=[
                {"batch_no": "PMBI-2601", "qty": 600, "expires_on": today + timedelta(days=360)},
            ],
            provenance="PMBI Jan Aushadhi Generic",
        )

        await create_product(
            brand_name="Combiflam",
            manufacturer="Sanofi India Ltd",
            code="SAN-COMBI-400",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[
                {"ing": "paracetamol", "num": 325, "unit": "mg"},
                {"ing": "ibuprofen", "num": 400, "unit": "mg"},
            ],
            pack_quantity=20,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=4800,
            selling_paise=4500,
            batches_spec=[
                {"batch_no": "SAN-8812", "qty": 200, "expires_on": today + timedelta(days=300)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        # Category 2: Antibiotics
        aug_625_duo = await create_product(
            brand_name="Augmentin 625 Duo",
            manufacturer="GlaxoSmithKline Pharmaceuticals Ltd (GSK India)",
            code="GSK-AUG-625",
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
            mrp_paise=20400,
            selling_paise=19000,
            batches_spec=[
                {"batch_no": "GSK-24A101", "qty": 120, "expires_on": today + timedelta(days=280)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        await create_product(
            brand_name="Amoxyclav 625",
            manufacturer="Cipla Ltd",
            code="CIP-AMXCV-625",
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
            mrp_paise=7500,
            selling_paise=7000,
            batches_spec=[
                {"batch_no": "CIP-26042", "qty": 250, "expires_on": today + timedelta(days=340)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        await create_product(
            brand_name="Azithral 500",
            manufacturer="Alembic Pharmaceuticals Ltd",
            code="ALM-AZITH-500",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "azithromycin", "num": 500, "unit": "mg"}],
            pack_quantity=5,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=13200,
            selling_paise=12500,
            batches_spec=[
                {"batch_no": "ALM-5521", "qty": 100, "expires_on": today + timedelta(days=300)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        await create_product(
            brand_name="Azithromycin IP 500mg",
            manufacturer="Alkem Laboratories Ltd",
            code="ALK-AZI-500",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "azithromycin", "num": 500, "unit": "mg"}],
            pack_quantity=3,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=4500,
            selling_paise=4000,
            batches_spec=[
                {"batch_no": "ALK-8801", "qty": 150, "expires_on": today + timedelta(days=320)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        # Category 3: Gastroenterology
        pantocid_40 = await create_product(
            brand_name="Pantocid 40",
            manufacturer="Sun Pharmaceutical Industries Ltd",
            code="SUN-PANT-40",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "pantoprazole", "num": 40, "unit": "mg"}],
            pack_quantity=15,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=15500,
            selling_paise=14500,
            batches_spec=[
                {"batch_no": "SUN-88412", "qty": 300, "expires_on": today + timedelta(days=365)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        await create_product(
            brand_name="Pantoprazole IP 40mg",
            manufacturer="PMBI / Torrent Pharmaceuticals Ltd",
            code="PMBI-PAN-40",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "pantoprazole", "num": 40, "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=False,  # Whole pack Jan Aushadhi packaging
            mrp_paise=2800,
            selling_paise=2500,
            batches_spec=[
                {"batch_no": "PMBI-8819", "qty": 500, "expires_on": today + timedelta(days=400)},
            ],
            provenance="PMBI Jan Aushadhi Generic",
        )

        pan_d = await create_product(
            brand_name="Pan-D",
            manufacturer="Alkem Laboratories Ltd",
            code="ALK-PAND-CAP",
            dosage_form="capsule",
            route="oral",
            release_type="sustained_release",
            components_spec=[
                {"ing": "pantoprazole", "num": 40, "unit": "mg"},
                {"ing": "domperidone", "num": 30, "unit": "mg"},
            ],
            pack_quantity=15,
            dispensing_unit="capsule",
            pack_break_allowed=True,
            mrp_paise=19900,
            selling_paise=18500,
            batches_spec=[
                {"batch_no": "ALK-7612", "qty": 150, "expires_on": today + timedelta(days=250)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        # Category 4: Cardiology & Lipids
        telma_40 = await create_product(
            brand_name="Telma 40",
            manufacturer="Glenmark Pharmaceuticals Ltd",
            code="GLN-TEL-40",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "telmisartan", "num": 40, "unit": "mg"}],
            pack_quantity=30,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=22000,
            selling_paise=20500,
            batches_spec=[
                {"batch_no": "GLN-3319", "qty": 200, "expires_on": today + timedelta(days=365)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        await create_product(
            brand_name="Telmisartan IP 40mg",
            manufacturer="PMBI / Torrent Pharmaceuticals Ltd",
            code="PMBI-TEL-40",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "telmisartan", "num": 40, "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=False,  # Whole pack Jan Aushadhi packaging
            mrp_paise=1800,
            selling_paise=1600,
            batches_spec=[
                {"batch_no": "PMBI-4412", "qty": 500, "expires_on": today + timedelta(days=450)},
            ],
            provenance="PMBI Jan Aushadhi Generic",
        )

        amlong_5 = await create_product(
            brand_name="Amlong 5",
            manufacturer="Micro Labs Ltd",
            code="MIC-AMLO-5",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "amlodipine", "num": Decimal("5.0"), "unit": "mg"}],
            pack_quantity=15,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=5200,
            selling_paise=4800,
            batches_spec=[
                {"batch_no": "ML-8821", "qty": 250, "expires_on": today + timedelta(days=300)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        atorva_20 = await create_product(
            brand_name="Atorva 20",
            manufacturer="Zydus Lifesciences Ltd",
            code="ZYD-ATOR-20",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "atorvastatin", "num": 20, "unit": "mg"}],
            pack_quantity=15,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=26500,
            selling_paise=24500,
            batches_spec=[
                {"batch_no": "ZYD-9012", "qty": 200, "expires_on": today + timedelta(days=300)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        # Category 5: Diabetology
        glycomet_500 = await create_product(
            brand_name="Glycomet 500",
            manufacturer="USV Pvt Ltd",
            code="USV-GLYC-500",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "metformin", "num": 500, "unit": "mg"}],
            pack_quantity=20,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=4200,
            selling_paise=3800,
            batches_spec=[
                {"batch_no": "USV-5512", "qty": 400, "expires_on": today + timedelta(days=365)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        await create_product(
            brand_name="Metformin IP 500mg",
            manufacturer="PMBI / Mankind Pharma Ltd",
            code="PMBI-MET-500",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "metformin", "num": 500, "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=False,  # Whole pack Jan Aushadhi packaging
            mrp_paise=800,
            selling_paise=750,
            batches_spec=[
                {"batch_no": "PMBI-1102", "qty": 800, "expires_on": today + timedelta(days=400)},
            ],
            provenance="PMBI Jan Aushadhi Generic",
        )

        await create_product(
            brand_name="Glycomet-SR 500",
            manufacturer="USV Pvt Ltd",
            code="USV-GLYC-SR500",
            dosage_form="tablet",
            route="oral",
            release_type="extended_release",
            components_spec=[{"ing": "metformin", "num": 500, "unit": "mg"}],
            pack_quantity=20,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=4800,
            selling_paise=4400,
            batches_spec=[
                {"batch_no": "USV-7714", "qty": 200, "expires_on": today + timedelta(days=300)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        # Category 6: Allergy
        allegra_120 = await create_product(
            brand_name="Allegra 120",
            manufacturer="Sanofi India Ltd",
            code="SAN-ALLG-120",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "fexofenadine", "num": 120, "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=19800,
            selling_paise=18500,
            batches_spec=[
                {"batch_no": "SAN-7741", "qty": 150, "expires_on": today + timedelta(days=300)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        await create_product(
            brand_name="Fexofenadine IP 120mg",
            manufacturer="Cipla Ltd",
            code="CIP-FEXO-120",
            dosage_form="tablet",
            route="oral",
            release_type="immediate_release",
            components_spec=[{"ing": "fexofenadine", "num": 120, "unit": "mg"}],
            pack_quantity=10,
            dispensing_unit="tablet",
            pack_break_allowed=True,
            mrp_paise=6200,
            selling_paise=5800,
            batches_spec=[
                {"batch_no": "CIP-24019", "qty": 200, "expires_on": today + timedelta(days=350)},
            ],
            provenance="Authentic Indian Pharmaceutical Dataset",
        )

        # =====================================================================
        # REALISTIC CLINICAL PRESCRIPTIONS & WORKFLOWS (Requirement R2)
        # =====================================================================

        # 1. Baseline Walk-in OPD (SAMPLE-DEMO-001 preserved for automated tests)
        sample_rx_res = await db.execute(
            select(Prescription).where(
                Prescription.pharmacy_id == pharmacy_id,
                Prescription.optional_patient_reference == "SAMPLE-DEMO-001",
            )
        )
        sample_rx = sample_rx_res.scalar_one_or_none()
        if not sample_rx:
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

        # 2. Cardiology: Essential Hypertension & Mixed Dyslipidemia (Confirmed, ready for plan)
        rx2_res = await db.execute(
            select(Prescription).where(
                Prescription.pharmacy_id == pharmacy_id,
                Prescription.optional_patient_reference.like("%DEL-2026-8812%"),
            )
        )
        if not rx2_res.scalar_one_or_none():
            rx2 = Prescription(
                pharmacy_id=pharmacy_id,
                optional_patient_reference="Mr. Rajesh Kumar Verma (58/M) | MRN: DEL-2026-8812",
                status=PrescriptionStatus.CONFIRMED,
                revision=1,
                created_by=pharmacist_user.id,
                created_at=datetime.now(timezone.utc) - timedelta(hours=4),
                confirmed_at=datetime.now(timezone.utc) - timedelta(hours=3, minutes=45),
            )
            db.add(rx2)
            await db.flush()

            r2_l1 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx2.id,
                raw_name="Telma 40 (Telmisartan 40mg)",
                raw_strength="40 mg",
                selected_product_id=telma_40.id,
                requested_quantity=30,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. Suresh V. Nair, MD, DM (Cardiology)",
                    "doctor_registration": "MCI-2009-41235",
                    "clinic": "Fortis Escorts Heart Institute, Okhla Road, New Delhi",
                    "diagnosis": "Essential Hypertension with Mixed Dyslipidemia",
                    "sig": "1 tab OD morning after breakfast x 30 days",
                    "text": "Dr. Suresh V. Nair (MCI-2009-41235) | Fortis Escorts Heart Institute | Dx: Essential Hypertension | Sig: 1 tab OD morning after breakfast x 30 days",
                },
            )
            r2_l2 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx2.id,
                raw_name="Atorva 20 (Atorvastatin 20mg)",
                raw_strength="20 mg",
                selected_product_id=atorva_20.id,
                requested_quantity=30,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. Suresh V. Nair, MD, DM (Cardiology)",
                    "doctor_registration": "MCI-2009-41235",
                    "clinic": "Fortis Escorts Heart Institute, Okhla Road, New Delhi",
                    "diagnosis": "Essential Hypertension with Mixed Dyslipidemia",
                    "sig": "1 tab HS bedtime x 30 days",
                    "text": "Dr. Suresh V. Nair (MCI-2009-41235) | Fortis Escorts Heart Institute | Dx: Mixed Dyslipidemia | Sig: 1 tab HS bedtime x 30 days",
                },
            )
            r2_l3 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx2.id,
                raw_name="Amlong 5 (Amlodipine 5mg)",
                raw_strength="5 mg",
                selected_product_id=amlong_5.id,
                requested_quantity=30,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. Suresh V. Nair, MD, DM (Cardiology)",
                    "doctor_registration": "MCI-2009-41235",
                    "clinic": "Fortis Escorts Heart Institute, Okhla Road, New Delhi",
                    "diagnosis": "Essential Hypertension with Mixed Dyslipidemia",
                    "sig": "1 tab OD morning x 30 days",
                    "text": "Dr. Suresh V. Nair (MCI-2009-41235) | Fortis Escorts Heart Institute | Dx: Essential Hypertension | Sig: 1 tab OD morning x 30 days",
                },
            )
            db.add_all([r2_l1, r2_l2, r2_l3])

        # 3. Diabetology & Dyspepsia (Needs Confirmation with unconfirmed Amlodipine line)
        rx3_res = await db.execute(
            select(Prescription).where(
                Prescription.pharmacy_id == pharmacy_id,
                Prescription.optional_patient_reference.like("%BOM-2026-3401%"),
            )
        )
        if not rx3_res.scalar_one_or_none():
            rx3 = Prescription(
                pharmacy_id=pharmacy_id,
                optional_patient_reference="Mrs. Sunita Devi Sharma (52/F) | MRN: BOM-2026-3401",
                status=PrescriptionStatus.NEEDS_CONFIRMATION,
                revision=1,
                created_by=admin_user.id,
                created_at=datetime.now(timezone.utc) - timedelta(hours=3),
            )
            db.add(rx3)
            await db.flush()

            r3_l1 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx3.id,
                raw_name="Glycomet 500 (Metformin 500mg)",
                raw_strength="500 mg",
                selected_product_id=glycomet_500.id,
                requested_quantity=60,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. Ananya Mukherjee, MBBS, MD (Internal Med)",
                    "doctor_registration": "MMC-2012-08912",
                    "clinic": "Apollo Hospital, Navi Mumbai",
                    "diagnosis": "Type 2 Diabetes Mellitus with Non-Ulcer Dyspepsia",
                    "sig": "1 tab BD after lunch & dinner x 30 days",
                    "text": "Dr. Ananya Mukherjee (MMC-2012-08912) | Apollo Hospital | Dx: T2DM | Sig: 1 tab BD after lunch & dinner x 30 days",
                },
            )
            r3_l2 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx3.id,
                raw_name="Pantocid 40 (Pantoprazole 40mg)",
                raw_strength="40 mg",
                selected_product_id=pantocid_40.id,
                requested_quantity=15,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. Ananya Mukherjee, MBBS, MD (Internal Med)",
                    "doctor_registration": "MMC-2012-08912",
                    "clinic": "Apollo Hospital, Navi Mumbai",
                    "diagnosis": "Type 2 Diabetes Mellitus with Non-Ulcer Dyspepsia",
                    "sig": "1 tab OD empty stomach before breakfast x 15 days",
                    "text": "Dr. Ananya Mukherjee (MMC-2012-08912) | Apollo Hospital | Dx: Non-Ulcer Dyspepsia | Sig: 1 tab OD empty stomach before breakfast x 15 days",
                },
            )
            r3_l3 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx3.id,
                raw_name="Amlodipine",
                raw_strength="5 mg",
                selected_product_id=None,  # Ambiguous brand SKU, demonstrates pharmacist confirmation badge
                requested_quantity=30,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.UNCONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. Ananya Mukherjee, MBBS, MD (Internal Med)",
                    "doctor_registration": "MMC-2012-08912",
                    "clinic": "Apollo Hospital, Navi Mumbai",
                    "diagnosis": "Type 2 Diabetes Mellitus with Non-Ulcer Dyspepsia",
                    "sig": "1 tab OD morning (brand unselected - pharmacist confirmation required)",
                    "text": "Dr. Ananya Mukherjee (MMC-2012-08912) | Apollo Hospital | Dx: Mild Hypertension | Sig: Amlodipine 5mg 1 tab OD (Ambiguous brand)",
                },
            )
            db.add_all([r3_l1, r3_l2, r3_l3])

        # 4. Respiratory Infection & Pyrexia (Confirmed, acute outpatient care)
        rx4_res = await db.execute(
            select(Prescription).where(
                Prescription.pharmacy_id == pharmacy_id,
                Prescription.optional_patient_reference.like("%BLR-2026-1192%"),
            )
        )
        if not rx4_res.scalar_one_or_none():
            rx4 = Prescription(
                pharmacy_id=pharmacy_id,
                optional_patient_reference="Master Aarav S. Patel (19/M) | MRN: BLR-2026-1192",
                status=PrescriptionStatus.CONFIRMED,
                revision=1,
                created_by=pharmacist_user.id,
                created_at=datetime.now(timezone.utc) - timedelta(hours=2, minutes=30),
                confirmed_at=datetime.now(timezone.utc) - timedelta(hours=2, minutes=15),
            )
            db.add(rx4)
            await db.flush()

            r4_l1 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx4.id,
                raw_name="Augmentin 625 Duo (Amoxicillin 500mg + Clavulanate 125mg)",
                raw_strength="625 mg",
                selected_product_id=aug_625_duo.id,
                requested_quantity=10,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. K. R. Venkatesh, MBBS, DNB (Fam. Med.)",
                    "doctor_registration": "KMC-2015-77341",
                    "clinic": "Manipal Primary Care Clinic, Indiranagar, Bengaluru",
                    "diagnosis": "Acute Bacterial Upper Respiratory Tract Infection (URTI) with High Pyrexia",
                    "sig": "1 tab BD after food x 5 days",
                    "text": "Dr. K. R. Venkatesh (KMC-2015-77341) | Manipal Primary Care Clinic | Dx: Acute Bacterial URTI | Sig: 1 tab BD x 5 days",
                },
            )
            r4_l2 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx4.id,
                raw_name="Dolo 650 (Paracetamol 650mg)",
                raw_strength="650 mg",
                selected_product_id=dolo_650.id,
                requested_quantity=15,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. K. R. Venkatesh, MBBS, DNB (Fam. Med.)",
                    "doctor_registration": "KMC-2015-77341",
                    "clinic": "Manipal Primary Care Clinic, Indiranagar, Bengaluru",
                    "diagnosis": "Acute Bacterial Upper Respiratory Tract Infection (URTI) with High Pyrexia",
                    "sig": "1 tab TDS / SOS for fever > 100°F",
                    "text": "Dr. K. R. Venkatesh (KMC-2015-77341) | Manipal Primary Care Clinic | Dx: High Pyrexia | Sig: 1 tab TDS / SOS for fever",
                },
            )
            r4_l3 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx4.id,
                raw_name="Allegra 120 (Fexofenadine 120mg)",
                raw_strength="120 mg",
                selected_product_id=allegra_120.id,
                requested_quantity=10,
                quantity_unit="tablet",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. K. R. Venkatesh, MBBS, DNB (Fam. Med.)",
                    "doctor_registration": "KMC-2015-77341",
                    "clinic": "Manipal Primary Care Clinic, Indiranagar, Bengaluru",
                    "diagnosis": "Acute Bacterial Upper Respiratory Tract Infection (URTI) with High Pyrexia",
                    "sig": "1 tab OD at bedtime x 5 days",
                    "text": "Dr. K. R. Venkatesh (KMC-2015-77341) | Manipal Primary Care Clinic | Dx: Allergic Rhinitis / Rhinorrhea | Sig: 1 tab OD bedtime x 5 days",
                },
            )
            db.add_all([r4_l1, r4_l2, r4_l3])

        # 5. Gastroenterology / Acute Gastritis (Completed with order record)
        rx5_res = await db.execute(
            select(Prescription).where(
                Prescription.pharmacy_id == pharmacy_id,
                Prescription.optional_patient_reference.like("%KOL-2026-6218%"),
            )
        )
        if not rx5_res.scalar_one_or_none():
            rx5 = Prescription(
                pharmacy_id=pharmacy_id,
                optional_patient_reference="Ms. Priya Sen (29/F) | MRN: KOL-2026-6218",
                status=PrescriptionStatus.COMPLETED,
                revision=1,
                created_by=pharmacist_user.id,
                created_at=datetime.now(timezone.utc) - timedelta(hours=2),
                confirmed_at=datetime.now(timezone.utc) - timedelta(hours=1, minutes=55),
            )
            db.add(rx5)
            await db.flush()

            r5_l1 = PrescriptionLine(
                pharmacy_id=pharmacy_id,
                prescription_id=rx5.id,
                raw_name="Pan-D (Pantoprazole 40mg + Domperidone 30mg SR)",
                raw_strength="70 mg",
                selected_product_id=pan_d.id,
                requested_quantity=15,
                quantity_unit="capsule",
                confirmation_state=LineConfirmationState.CONFIRMED,
                evidence_json={
                    "doctor_name": "Dr. Debabrata Roy, MD (Gastroenterology)",
                    "doctor_registration": "WBMC-2014-55120",
                    "clinic": "AMRI Hospitals, Salt Lake, Kolkata",
                    "diagnosis": "Acute Erosive Gastritis & GERD",
                    "sig": "1 cap OD before breakfast x 15 days",
                    "text": "Dr. Debabrata Roy (WBMC-2014-55120) | AMRI Hospitals | Dx: Acute Erosive Gastritis & GERD | Sig: 1 cap OD before breakfast x 15 days",
                },
            )
            db.add(r5_l1)
            await db.flush()

            # Retrieve active batch for Pan-D
            pan_d_batch_res = await db.execute(
                select(InventoryBatch).where(
                    InventoryBatch.pharmacy_id == pharmacy_id,
                    InventoryBatch.product_id == pan_d.id,
                    InventoryBatch.batch_number == "ALK-7612",
                )
            )
            pan_d_batch = pan_d_batch_res.scalar_one()

            # Create finalized plan
            plan5 = Plan(
                pharmacy_id=pharmacy_id,
                prescription_id=rx5.id,
                prescription_revision=1,
                version=1,
                state=PlanState.FINALIZED,
                created_by=pharmacist_user.id,
                created_at=datetime.now(timezone.utc) - timedelta(hours=1, minutes=55),
            )
            db.add(plan5)
            await db.flush()

            pl5 = PlanLine(
                pharmacy_id=pharmacy_id,
                plan_id=plan5.id,
                prescription_line_id=r5_l1.id,
                selected_product_id=pan_d.id,
                selection_reason="as_prescribed",
                authorization_required=False,
            )
            db.add(pl5)
            await db.flush()

            # Create Quote
            quote_payload = {
                "quote_id": str(uuid.uuid4()),
                "plan_id": str(plan5.id),
                "plan_version": 1,
                "prescription_id": str(rx5.id),
                "lines": [
                    {
                        "prescription_line_id": str(r5_l1.id),
                        "original_product_id": str(pan_d.id),
                        "original_brand_name": "Pan-D",
                        "selected_product_id": str(pan_d.id),
                        "selected_brand_name": "Pan-D",
                        "requested_units": 15,
                        "supplied_units": 15,
                        "unit_dispensing": True,
                        "packs_needed": 1,
                        "excess_units": 0,
                        "baseline_line_paise": 18500,
                        "selected_line_paise": 18500,
                        "difference_paise": 0,
                        "difference_percent": "0.00",
                        "allocations": [
                            {
                                "batch_id": str(pan_d_batch.id),
                                "batch_number": pan_d_batch.batch_number,
                                "quantity": 15,
                                "unit_price_paise": 1233,
                                "line_total_paise": 18500,
                            }
                        ],
                    }
                ],
                "totals": {
                    "currency": "INR",
                    "baseline_total_paise": 18500,
                    "selected_total_paise": 18500,
                    "difference_paise": 0,
                    "comparable_subset_difference_percent": "0.00",
                    "pack_rounding_excess_units_total": 0,
                },
            }

            quote5 = Quote(
                pharmacy_id=pharmacy_id,
                plan_id=plan5.id,
                plan_version=1,
                prescription_revision=1,
                rules_version=1,
                settings_version=1,
                immutable_payload_json=quote_payload,
                created_at=datetime.now(timezone.utc) - timedelta(hours=1, minutes=55),
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                consumed_at=datetime.now(timezone.utc) - timedelta(hours=1, minutes=45),
            )
            db.add(quote5)
            await db.flush()

            plan5.current_quote_id = quote5.id

            # Create Approval
            appr5 = Approval(
                pharmacy_id=pharmacy_id,
                quote_id=quote5.id,
                decision=ApprovalDecision.APPROVED,
                actor_id=pharmacist_user.id,
                reason="Prescription verified and dispensed as prescribed by gastroenterologist.",
                created_at=datetime.now(timezone.utc) - timedelta(hours=1, minutes=50),
            )
            db.add(appr5)
            await db.flush()

            # Create Order
            ord_res = await db.execute(
                select(Order).where(Order.pharmacy_id == pharmacy_id, Order.order_number == "ORD-20261103-0042")
            )
            existing_ord = ord_res.scalar_one_or_none()
            if not existing_ord:
                order5 = Order(
                    pharmacy_id=pharmacy_id,
                    prescription_id=rx5.id,
                    quote_id=quote5.id,
                    approval_id=appr5.id,
                    order_number="ORD-20261103-0042",
                    total_paise=18500,
                    currency="INR",
                    completed_by=pharmacist_user.id,
                    completed_at=datetime.now(timezone.utc) - timedelta(hours=1, minutes=45),
                )
                db.add(order5)
                await db.flush()

                ol5 = OrderLine(
                    pharmacy_id=pharmacy_id,
                    order_id=order5.id,
                    original_product_snapshot={
                        "product_id": str(pan_d.id),
                        "brand_name": "Pan-D",
                        "baseline_line_paise": 18500,
                    },
                    dispensed_product_snapshot={
                        "product_id": str(pan_d.id),
                        "brand_name": "Pan-D",
                        "selected_line_paise": 18500,
                    },
                    requested_quantity=15,
                    supplied_quantity=15,
                    quantity_unit="capsule",
                    total_paise=18500,
                    comparison_snapshot={
                        "difference_percent": "0.00",
                        "excess_units": 0,
                        "packs_needed": 1,
                    },
                )
                db.add(ol5)
                await db.flush()

                oa5 = OrderAllocation(
                    pharmacy_id=pharmacy_id,
                    order_line_id=ol5.id,
                    batch_id=pan_d_batch.id,
                    batch_number_snapshot=pan_d_batch.batch_number,
                    quantity=15,
                    price_snapshot={
                        "selling_pack_paise": pan_d_batch.selling_pack_paise,
                        "mrp_pack_paise": pan_d_batch.mrp_pack_paise,
                        "unit_price_paise": 1233,
                    },
                    expiry_snapshot=pan_d_batch.expires_on.isoformat(),
                )
                db.add(oa5)
                await db.flush()

                # Deduct stock and register stock movement
                if pan_d_batch.quantity_on_hand >= 15:
                    pan_d_batch.quantity_on_hand -= 15
                    pan_d_batch.version += 1
                mv5 = StockMovement(
                    pharmacy_id=pharmacy_id,
                    batch_id=pan_d_batch.id,
                    delta_units=-15,
                    reason=StockMovementReason.DISPENSE,
                    reference_type="order",
                    reference_id=order5.id,
                    actor_id=pharmacist_user.id,
                    created_at=datetime.now(timezone.utc) - timedelta(hours=1, minutes=45),
                )
                db.add(mv5)

        await db.commit()
        print("[Seed] Seed data successfully committed.")


if __name__ == "__main__":
    asyncio.run(seed())
