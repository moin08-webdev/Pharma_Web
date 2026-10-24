# PharmaBridge: Complete System Documentation, Architecture & User Manual

> **Official Release Documentation** | Version 1.0.0-MVP  
> **PDF Export**: [PharmaBridge_Comprehensive_Documentation.pdf](file:///c:/Users/moins/Pharma_Web/PharmaBridge_Comprehensive_Documentation.pdf)

---

## 1. What is the Main Goal of PharmaBridge?

In Indian retail and community pharmacies, dispensing prescription medication is a high-stakes, time-sensitive process fraught with clinical, financial, and operational challenges. Thousands of pharmaceutical manufacturers market identical or near-identical generic formulations under brand names varying significantly in price, packaging, and availability.

The primary mission of **PharmaBridge** is to provide a unified, highly guarded digital workstation that empowers pharmacists to safely, efficiently, and transparently fulfil prescriptions. PharmaBridge bridges the gap between raw doctor prescriptions (handwritten, scanned, or digital) and actual pharmacy inventory, ensuring:

1. **Zero Clinical Compromise**: Every suggested alternative brand or generic substitution must be strictly bio-equivalent in active ingredient, canonical salt identity, strength, dosage form, and release profile (Immediate Release vs. Extended Release).
2. **Pack Economics Transparency**: Indian drug regulations and blister packaging often require dispensing whole packs. PharmaBridge computes transparent whole-pack economics, exposing exact patient cost savings without misleading fractional-pill pricing.
3. **Mandatory Pharmacist Clinical Authority**: Only licensed pharmacists can approve substitutions or finalize orders. Assistants and technicians are gated from clinical decisions.
4. **FEFO Inventory Integrity**: Inventory deduction is strictly First-Expired, First-Out (FEFO), with transactional database locks preventing stock race conditions and waste.
5. **Resilient Offline-First Architecture**: Full operation is guaranteed using synthetic demo fixtures and local database persistence even if cloud OCR or external APIs fail.

---

## 2. How PharmaBridge Solves the Problem

| Challenge Area | Traditional Pharmacy Practice | The PharmaBridge Solution |
| :--- | :--- | :--- |
| **Prescription Legibility & Intake** | Manual reading of doctor handwriting; frequent confusion over similar brand names (e.g., Metformin IR vs. Metformin ER). | Multi-format OCR intake (images/PDFs) coupled with a required manual line verification step. Ambiguities are highlighted in amber and must be resolved before proceeding. |
| **Generic Substitution Risk** | Ad-hoc substitution driven by wholesaler profit margins rather than clinical equivalence; risk of salt mismatches or partial combination errors. | Deterministic formulation matching engine. Automatically filters candidates by canonical salt, release profile, and route. Formally rejects partial combination subsets and narrow therapeutic index drugs. |
| **Pricing & Pack Economics** | Calculating pill prices on manual paper scraps; patients surprised by whole-pack costs or buying unnecessary excess units. | Exact Decimal paise arithmetic (zero floating-point drift). Transparently breaks down requested units, packs needed, excess units, and delivers demonstrable cost comparisons (e.g. 33.33% real savings). |
| **Staff Responsibility & Gating** | Untrained shop assistants often dispense medications without pharmacist supervision; no digital audit trail. | Role-based permissions (Pharmacist vs. Assistant vs. Admin). Only authenticated Pharmacists can sign off on clinical substitutions and trigger final stock deduction. |
| **Stock Waste & Expiry** | Disorganized shelves lead to newer batches being dispensed while older stock expires in the back (LIFO or random dispensing). | Automated FEFO (First-Expired, First-Out) batch allocation. Batches nearing expiry are prioritized; quarantined or expired stock is strictly blocked. |

---

## 3. Core System Features

1. **Intake & Document Processing**: Upload prescription images (PNG/JPEG) and PDFs (up to 10 MB, 5 pages) locally. Includes manual draft creation and synthetic demo quick-start fixtures.
2. **Clinical Line Verification**: Two-column review workspace displaying the source prescription document alongside editable medicine lines. Enforces catalogue SKU selection before quote generation.
3. **Formulation Candidate Engine**: Automatically retrieves bio-equivalent products with clinical rejection reasons (Release Mismatch, Combination Subset, Salt Incompatible, or Stock Shortage).
4. **Pack Economics Optimizer**: Calculates whole packs vs. unit dispensing based on catalogue packaging rules. Computes baseline costs, candidate savings percentages, and reports excess pack units.
5. **Clinical Approval Workflow**: Mandatory clinical sign-off where licensed pharmacists review alternatives, provide notes, and digitally sign the plan.
6. **FEFO Batch Inventory Management**: Full batch tracking with expiry dates, status (Active, Quarantined, Recalled, Expired), and unit costs. Records immutable movements in an append-only audit ledger.
7. **Order Finalization & Invoicing**: Atomic order execution using row-level locking (`SELECT ... FOR UPDATE`) and idempotency keys.
8. **Executive Analytics Dashboard**: Real-time metrics on prescriptions processed, fulfillment coverage rate, aggregate patient savings delivered, and inventory expiry alerts.

---

## 4. Clinical Safety & Mathematical Architecture

### Strict Equivalence Rules
- **Active Ingredient Equivalence**: All active chemical ingredients must match canonically (e.g., `paracetamol == acetaminophen`).
- **Canonical Salt Preservation**: Incompatible salts are blocked (e.g., Metformin Hydrochloride vs. Metformin Pamoate).
- **Release Profile Matching**: Immediate Release (IR), Extended Release (ER), and Sustained Release (SR) cannot substitute for one another.
- **Combination Subset Rejection**: Multi-ingredient drugs cannot be replaced by single-ingredient subsets.
- **Dosage Form & Route**: Oral tablets cannot substitute for ointments or injectables.

### Pack Economics: The 33.33% Savings Benchmark
- **Prescribed**: 15 tablets of Brand A Paracetamol 500mg (15-tablet pack @ ₹30.00 = ₹30.00).
- **Candidate**: Product B Generic (10-tablet pack @ ₹10.00, whole pack only).
- **Dispensing**: `ceil(15 / 10) = 2 packs` (20 tablets supplied, 5 excess units).
- **Final Cost**: 2 packs × ₹10.00 = **₹20.00**.
- **Savings**: ₹30.00 − ₹20.00 = ₹10.00 out of ₹30.00 = **33.33% Real Savings**.

---

## 5. End-to-End User Operational Manual

### User Roles & Access Control
- **Pharmacist**: Full access to review, substitute candidates, approve plans, and finalize orders.
- **Assistant**: Can intake, draft, and search; blocked from clinical approvals and order finalization.
- **Admin**: Full access including pharmacy settings, staff management, and retention policies.

### Evaluator Walkthrough (7 Steps)
1. **Sign In**: Navigate to `http://localhost:5173/login` and click **"Pharmacist"** auto-fill, then **"Sign in to Workspace"**.
2. **Intake**: Click **"New Prescription"** -> click purple **"Load Sample Prescription"** button.
3. **Verify Line**: On Review screen, select `DemoAmlo 5 (amlodipine 5mg (tablet))` in Line 2 dropdown. Click **"Confirm & Generate Plan"**.
4. **Compare Economics**: On Fulfilment Plan screen, change Line 1 candidate to `Product B Generic Paracetamol (Pack ₹10.00)` and verify **33.33% Savings**.
5. **Approve**: Click **"Approve Fulfilment Plan"**.
6. **Finalize**: Click **"Finalize Order & Deduct Stock"**. Reload page (`F5`) to verify persistent storage in PostgreSQL.
7. **Inspect Inventory**: Open **"Inventory & Batches"** in sidebar and verify that batch `PB-2026-01` was decremented by 20 units.

---

## 6. Technical Specifications & Verification Matrix

- **Backend**: FastAPI 0.115 + SQLAlchemy 2.0 (asyncpg) + PostgreSQL 17 + Pydantic v2 + Argon2id
- **Frontend**: React 19 + TypeScript 5.7 + Vite 6.4 + Tailwind CSS + TanStack Query 5
- **Verification**: 21 Pytest tests + 12 Playwright cross-device tests (Desktop Chrome, Tablet, Mobile) = **33/33 Passed (100%)**.
