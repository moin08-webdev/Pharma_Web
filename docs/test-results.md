# PharmaBridge Test Execution & Verification Report

This document reports the comprehensive verification results for PharmaBridge, covering backend unit and integration tests, domain pricing arithmetic, clinical permission gates, FEFO inventory allocation, and real-browser Playwright end-to-end tests across Desktop, Tablet, and Mobile viewports.

---

## 1. Executive Summary

| Test Category | Suite / Runner | Tests Executed | Passed | Failed | Execution Time |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Backend Unit & Integration** | Pytest 9.1.1 (`uv run pytest`) | 21 | 21 | 0 | 2.99s |
| **End-to-End Browser Tests** | Playwright Chromium (3 Viewports) | 12 | 12 | 0 | 7.8s |
| **Frontend Production Build** | TypeScript 5.7.3 + Vite 6.4.5 | 1 | 1 | 0 | 3.48s |
| **Total** | | **34** | **34** | **0** | **14.27s** |

---

## 2. Backend Pytest Suite (`apps/api/tests`)

Command: `& "C:\Users\moins\.local\bin\uv.exe" run pytest`
Result: `21 passed in 2.99s`

### Detailed Test Breakdown:
- **`tests/integration/test_auth_and_permissions.py` (3 tests)**:
  - `test_login_and_me_endpoint`: Verifies Argon2id password verification, session cookie issuance, and `/api/v1/auth/me` user context.
  - `test_pharmacist_can_approve_and_finalize`: Asserts that users with the `PHARMACIST` role can successfully approve substitutions and finalize orders.
  - `test_assistant_forbidden_from_approving_or_finalizing`: Confirms that `ASSISTANT` role attempts to approve or finalize are rejected with HTTP 403 Forbidden.
- **`tests/integration/test_prescription_to_order_api.py` (1 test)**:
  - `test_complete_prescription_to_order_flow`: Tests the full transactional backend pipeline:
    1. Prescription draft creation (`POST /api/v1/prescriptions`)
    2. Document metadata registration
    3. Bulk line updates with revision check (`PUT /api/v1/prescriptions/{id}/lines`)
    4. Prescription confirmation (`POST /api/v1/prescriptions/{id}/confirm`)
    5. Baseline quote generation with FEFO batch allocations
    6. Candidate substitution to Product B Generic Paracetamol
    7. Optimized quote calculation with 33.33% pack savings
    8. Pharmacist approval recording (`POST /api/v1/prescriptions/{id}/plan/approve`)
    9. Order finalization with `FOR UPDATE` inventory row locking (`POST /api/v1/orders`)
    10. Ledger stock deduction verification in `inventory_batches` and `stock_movements`.
- **`tests/unit/test_matching.py` (5 tests)**:
  - Exact active ingredient and strength equivalence.
  - Dosage form equivalence (tablet vs capsule).
  - Component release type mismatch rejection (Immediate Release vs Extended Release).
  - Salt identity and canonical normalization matching.
  - Multi-ingredient combination subset rejection (preventing partial matches).
- **`tests/unit/test_pricing.py` (5 tests)**:
  - Exact Decimal paise arithmetic (zero floating-point drift).
  - Whole pack vs unit dispensing quantity calculation.
  - Excess unit calculation when dispensing whole packs.
  - Accurate 33.33% savings computation between Brand A (₹30 for 15 tabs) and Product B (₹20 for 2 × 10 tab packs).
  - Multi-batch FEFO price aggregation.
- **`tests/unit/test_normalization.py` (4 tests)**:
  - Canonical drug name cleaning and normalization.
  - Standard unit conversions (e.g., grams to milligrams).
  - Salt suffix stripping while preserving base chemical identity.
  - Alias lookup and resolution.
- **`tests/unit/test_state_transitions.py` (3 tests)**:
  - Valid transitions for prescriptions (`draft` -> `needs_confirmation` -> `confirmed` -> `in_planning` -> `completed`).
  - Revision increments upon modification.
  - Invalidation of approval if prescription lines change post-approval.

---

## 3. End-to-End Playwright Suite (`tests/e2e`)

Command: `pnpm exec playwright test -c tests/e2e/playwright.config.ts`
Result: `12 passed in 7.8s` across 3 device profiles:
1. **Desktop Chrome** (1440 × 900)
2. **Tablet** (Galaxy Tab S4: 768 × 1024)
3. **Mobile** (Pixel 7: 390 × 844)

### Detailed Test Scenarios:

#### A. Prescription-to-Order Real Flow (`prescription-to-order.spec.ts`)
- **Step 1**: Navigates to `/login` and signs in as `pharmacist@pharmabridge.demo`.
- **Step 2**: Navigates to `/app/prescriptions/new` and clicks *"Load Sample Prescription"* (demonstrating the sample evaluator workflow).
- **Step 3**: Navigates to `/app/prescriptions/{id}/review`:
  - Confirms Line 1 is pre-populated with Brand A Paracetamol 500mg (15 tabs).
  - Identifies Line 2 (Amlo 5mg) as ambiguous (`confirmation_state = unconfirmed`).
  - Selects matching catalogue SKU `DemoAmlo 5 (amlodipine 5mg (tablet))` from dropdown.
  - Clicks *"Confirm & Generate Plan"*.
- **Step 4**: Navigates to `/app/prescriptions/{id}/plan`:
  - Verifies baseline quote renders with initial cost.
  - Switches Brand A to equivalent generic candidate `Product B Generic Paracetamol (Pack ₹10.00)`.
  - Asserts that pack economics calculate **33.33% Savings** (Brand A ₹30 vs 2 packs of Product B ₹20).
  - Pharmacist enters review reason and clicks *"Approve Fulfilment Plan"*.
  - Verifies plan updates to *"Plan Approved by Pharmacist"*.
  - Clicks *"Finalize Order & Deduct Stock"*.
- **Step 5**: Order Confirmation & Backend Persistence:
  - Navigates to `/app/orders/{order_id}`.
  - Verifies order badge is `FINALIZED` and dispensed items include Product B.
  - **Browser Reload Test**: Hard page reload re-queries PostgreSQL backend, confirming persistent order state.
- **Step 6**: Inventory Verification:
  - Navigates to `/app/inventory`.
  - Confirms Product B batch stock was atomically decremented via FEFO ledger movements.

#### B. Clinical Review Gates & Permissions (`review-gates.spec.ts`)
- **Test 1**: Assistant role protection:
  - Logs in as `assistant@pharmabridge.demo`.
  - Navigates to `/app/approvals` and opens an active plan.
  - Asserts that the approval action is blocked: displays *"Pharmacist Role Required"* and hides/disables the approval trigger.
- **Test 2**: Unconfirmed prescription lines gate:
  - Pharmacist creates a draft and adds an unconfirmed medicine line without selecting a SKU.
  - Asserts that the *"Confirm & Generate Plan"* button is disabled and warns *"Ambiguous: Catalogue Selection Required"*, preventing premature quote generation.

#### C. Responsive Layout & Navigation (`responsive-navigation.spec.ts`)
- Tested across Desktop, Tablet, and Mobile viewports.
- Asserts that no horizontal scroll overflow exists (`scrollWidth <= clientWidth`).
- Verifies responsive navigation bar, collapsible side drawer, and legible tables on all device form factors.

---

## 4. Frontend Production Compilation

Command: `pnpm --filter @pharmabridge/web build`
Result: `tsc -b && vite build` succeeded in 3.48s.
Output bundles:
- `dist/index.html` (0.61 kB)
- `dist/assets/index-CanWRhtn.css` (25.40 kB / gzip: 5.28 kB)
- `dist/assets/index-CJapQeb0.js` (474.85 kB / gzip: 135.92 kB)
- Zero TypeScript type errors (`0 errors`).
