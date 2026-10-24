# PharmaBridge

**AI-Assisted Prescription Fulfilment Workspace for Indian Community Pharmacies**

PharmaBridge is an end-to-end clinical pharmacy workstation designed for Indian pharmacies. It streamlines the dispensing pipeline from paper/digital prescription intake to formulation equivalence matching, transparent pack economics, mandatory pharmacist clinical approval, and atomic FEFO (First-Expired, First-Out) inventory deduction.

---

## 🌟 Key Highlights & Engineering Guarantees

1. **Strict Active-Ingredient Equivalence**:
   - Formulation matching preserves canonical salt identities, release profiles (Immediate Release vs Extended Release), dosage forms, and routes.
   - Rejects partial multi-ingredient combination subsets and flagged high-risk narrow-therapeutic-index drugs.
2. **Whole-Pack Economics & Accurate Math**:
   - Dispensing logic respects pack constraints (`pack_break_allowed: false` forces whole-pack increments).
   - Computes real baseline vs. alternative costs with exact paise arithmetic (`Decimal`, zero floating-point imprecision).
   - Demonstrates **33.33% real savings** for Brand A (₹30 for 15 tablets) vs. Product B generic (₹10/pack of 10 = ₹20 for 2 packs).
3. **Mandatory Pharmacist Clinical Review Gate**:
   - Role-based permissions strictly enforced (`PHARMACIST`, `ASSISTANT`, `ADMIN`).
   - Only licensed Pharmacists can approve candidate substitutions and finalize orders. Assistants are blocked with explicit UI warnings and 403 API guards.
4. **FEFO Inventory & Transactional Safety**:
   - Allocates earliest-expiring, unquarantined, active stock first.
   - Finalizes orders atomically using PostgreSQL row-level locks (`SELECT ... FOR UPDATE`) with idempotency keys.
   - Stock movements are recorded in an append-only ledger.
5. **Resilient Local-First Design**:
   - Full workspace operates with synthetic demo fixtures and local PostgreSQL even if external vision/OCR providers are offline.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: 3.12+ (or via `uv`)
- **Node.js**: v20+ & **pnpm**: v9+
- **PostgreSQL**: 16+ or 17+ (running on `localhost:5432`)

### 2. Services Startup

#### A. Database
PostgreSQL is configured on port `5432` with user `pharmabridge` and database `pharmabridge`:
```powershell
# If using the portable PostgreSQL instance located at C:\Users\moins\.local\pgsql:
& "C:\Users\moins\.local\pgsql\pgsql\bin\postgres.exe" -D "C:\Users\moins\.local\pgsql\data"
```

#### B. Backend API (FastAPI)
```powershell
cd apps/api
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- API Endpoint: `http://127.0.0.1:8000`
- Swagger Interactive Docs: `http://127.0.0.1:8000/docs`

#### C. Frontend Web Workspace (React 19 + Vite)
```powershell
cd apps/web
pnpm dev --host 127.0.0.1 --port 5173
```
- Web Application: `http://127.0.0.1:5173`

---

## 👥 Demo Staff Credentials

The system comes pre-seeded with 3 realistic pharmacy staff accounts:

| Role | Email Address | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Pharmacist** | `pharmacist@pharmabridge.demo` | `DemoPharmacistPass123!` | Full clinical approval, substitution selection, and order finalization |
| **Assistant** | `assistant@pharmabridge.demo` | `DemoAssistantPass123!` | Intake, drafting, catalog viewing; blocked from approval & finalization |
| **Admin** | `admin@pharmabridge.demo` | `DemoAdminPass123!` | Pharmacy settings, staff role management, retention policies |

> *Tip: The Login screen includes one-click demo account auto-fill buttons for instant testing.*

---

## 🧪 Testing & Verification

### Run End-to-End Browser Tests (Playwright)
Executes the full dispensing flow, clinical gates, and responsive UI across Desktop, Tablet, and Mobile:
```powershell
pnpm exec playwright test -c tests/e2e/playwright.config.ts
```
*(All 12 Playwright tests pass in ~7 seconds).*

### Run Backend Tests (Pytest)
Executes 21 unit and integration tests covering matching rules, paise pricing, and API transitions:
```powershell
cd apps/api
uv run pytest
```
*(All 21 backend tests pass in ~3 seconds).*

For complete test logs and matrix results, see [`docs/test-results.md`](docs/test-results.md).  
For runtime technology versions, see [`docs/technology-versions.md`](docs/technology-versions.md).

---

## 📋 Evaluator Walkthrough Script

Follow these steps to experience the complete dispensing flow:

1. **Sign In**:
   - Open `http://localhost:5173/login`.
   - Click the **"Pharmacist"** quick-fill button, then click **"Sign in to Workspace"**.
2. **Intake Prescription**:
   - Navigate to **"New Prescription"** in the top navigation bar.
   - Click the purple **"Load Sample Prescription"** button. This automatically loads a synthetic test prescription with two lines:
     - *Line 1*: Brand A Paracetamol 500mg (15 tablets).
     - *Line 2*: Amlo 5mg (ambiguous strength requiring catalogue resolution).
3. **Review & Confirm**:
   - On the Review page, note that Line 1 is pre-confirmed, while Line 2 shows an amber *"Ambiguous: Catalogue Selection Required"* badge.
   - In the Line 2 dropdown, select `DemoAmlo 5 (amlodipine 5mg (tablet))`.
   - Click **"Confirm & Generate Plan"**.
4. **Compare Formulation Candidates & Pack Savings**:
   - On the Fulfilment Plan screen, inspect the baseline quote.
   - Under Line 1, open the **"Dispensing Selection"** dropdown and select `Product B Generic Paracetamol (Pack ₹10.00)`.
   - Observe the updated calculation: because Product B is sold in 10-tablet whole packs, 2 packs (20 tablets, with 5 excess) cost ₹20.00 compared to ₹30.00 for Brand A, delivering **33.33% Savings**.
5. **Clinical Approval**:
   - In the right-hand panel, click **"Approve Fulfilment Plan"**.
   - Note the confirmation badge displaying the approving pharmacist's name, role, and timestamp.
6. **Finalize Order & FEFO Stock Deduction**:
   - Click **"Finalize Order & Deduct Stock"**.
   - The order moves to `FINALIZED` and displays the deducted batch details.
   - Reload the page to confirm persistent storage in PostgreSQL.
7. **Inspect Inventory**:
   - Navigate to **"Inventory & Batches"** in the sidebar.
   - Verify that Product B's earliest-expiring batch (`PB-2026-01`) has been decremented by exactly 20 units.

---

## 🏗️ Project Architecture

```
Pharma_Web/
├── apps/
│   ├── api/                     # FastAPI Asynchronous REST Backend
│   │   ├── app/
│   │   │   ├── api/routes/      # Auth, Prescriptions, Plans, Orders, Catalog, Inventory
│   │   │   ├── domain/          # Matching rules, state transitions, money & quantities
│   │   │   ├── models/          # SQLAlchemy async models (PostgreSQL)
│   │   │   ├── schemas/         # Pydantic v2 validation models
│   │   │   ├── seed/            # Demo data fixtures (Brand A, Product B, Staff accounts)
│   │   │   └── services/        # Business logic: planning, approvals, transactions
│   │   └── tests/               # Unit & integration pytest suite
│   │
│   └── web/                     # React 19 + TypeScript + Vite Workspace
│       ├── src/
│       │   ├── components/      # UI components, layout, status badges, navbar
│       │   ├── pages/           # Review, Plan, Approvals, Orders, Inventory, Search
│       │   └── lib/             # API client & auth session hooks
│       └── tailwind.config.js
│
├── docs/                        # Technology versions and verification logs
│   ├── technology-versions.md
│   └── test-results.md
│
├── tests/e2e/                   # Playwright E2E browser tests (Chromium, Tablet, Mobile)
└── README.md
```
