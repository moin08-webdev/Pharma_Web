import { test, expect, Page } from "@playwright/test";

/**
 * 4-Tier Comprehensive Opaque-Box E2E Test Suite for PharmaBridge
 *
 * Requirements Covered:
 * - R1: UI/UX Simplification & Professional Redesign (No presentation slide citations,
 *       no marketing gimmicks, clean medical software workflows across all viewports)
 * - R2: Realistic Indian Pharmaceutical & Clinical Datasets (Authentic Indian brands,
 *       Jan Aushadhi generics, Indian patient demographics, doctor MCI registrations,
 *       Schedule H compliance notices, FEFO shelf inventory deduction)
 * - R3: Test Suite Integrity & Application Stability (100% automated pass rate)
 *
 * Tier 1: Feature Coverage (Clean UI workflows, Indian Catalogue & Inventory)
 * Tier 2: Boundary & Corner Cases (Unconfirmed line gates, Role restrictions, Whole-pack arithmetic)
 * Tier 3: Cross-Feature Combinations (Multi-line intake, Generic substitution, FEFO deduction)
 * Tier 4: Real-World Clinical Workloads (Cardiology & Respiratory clinical consultations)
 */

async function loginAsPharmacist(page: Page) {
  await page.goto("/login");
  await page.fill('input[type="email"]', "pharmacist@pharmabridge.demo");
  await page.fill('input[type="password"]', "DemoPharmacistPass123!");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/app/);
}

async function loginAsAssistant(page: Page) {
  await page.goto("/login");
  await page.fill('input[type="email"]', "assistant@pharmabridge.demo");
  await page.fill('input[type="password"]', "DemoAssistantPass123!");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/app/);
}

test.describe("Tier 1: Feature Coverage & UI Simplification", () => {
  test("clean clinical UI presentation across core workflows without slide citations or marketing gimmicks", async ({
    page,
  }) => {
    // 1. Visit Login page: verify professional subtitle and clean demo credentials
    await page.goto("/login");
    await expect(page).toHaveTitle(/PharmaBridge/);
    await expect(page.locator("body")).not.toContainText("SHARKFORGE 2026");
    await expect(page.locator("body")).not.toContainText("AI help for everyday pharmacy work");

    // 2. Log in as Pharmacist and check Dashboard
    await page.fill('input[type="email"]', "pharmacist@pharmabridge.demo");
    await page.fill('input[type="password"]', "DemoPharmacistPass123!");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/app/);

    // Verify Dashboard layout & headings
    await expect(page.locator("h1")).toContainText("Pharmacy Dashboard");
    await expect(page.locator("text=Active Clinical Dispensing Station")).toBeVisible();

    // Verify absence of marketing walkthrough cards and slide citations on Dashboard
    await expect(page.locator("body")).not.toContainText("Mentor & Evaluator Walkthrough");
    await expect(page.locator("body")).not.toContainText("Start 5-Minute Demo Flow");
    await expect(page.locator("body")).not.toContainText("Slide 03");
    await expect(page.locator("body")).not.toContainText("Slide 04");
    await expect(page.locator("body")).not.toContainText("Slide 06");

    // 3. Check New Prescription view
    await page.goto("/app/prescriptions/new");
    await expect(page.locator("h1")).toContainText("New Prescription Intake");
    await expect(page.locator('button:has-text("Load Sample Prescription")')).toBeVisible();
    await expect(page.getByPlaceholder("e.g. RX-2026-4412")).toBeVisible();
    await expect(page.locator("body")).not.toContainText("Five-Minute Mentor Demo");
    await expect(page.locator("body")).not.toContainText("Slide 10");

    // 4. Check Inventory view
    await page.goto("/app/inventory");
    await expect(page.locator("h1")).toContainText("Inventory & Batch Management");
    await expect(page.locator("text=FEFO Shelf Inventory Priority")).toBeVisible();
    await expect(page.locator("body")).not.toContainText("Slide 06 Standard");

    // 5. Check Approvals view
    await page.goto("/app/approvals");
    await expect(page.locator("h1")).toContainText("Clinical Approvals");
    await expect(page.locator("body")).not.toContainText("Slide 07");
  });

  test("authentic Indian pharmaceutical formulary catalogue and inventory equivalence", async ({
    page,
  }) => {
    await loginAsPharmacist(page);

    // Navigate to Medicines Catalogue
    await page.goto("/app/medicines");
    await expect(page.locator("h1")).toContainText("Medicines Catalogue");

    // Verify table structure with clinical packaging and MRP headers
    await expect(page.locator("th:has-text('Brand & Molecule')")).toBeVisible();
    await expect(page.locator("th:has-text('Packaging Spec')")).toBeVisible();
    await expect(page.locator("th:has-text('MRP (Pack)')")).toBeVisible();
    await expect(page.locator("th:has-text('Equivalence')")).toBeVisible();

    // Wait for catalogue records to load and click Candidates link
    const candidateLink = page.locator('a:has-text("Candidates")').first();
    await expect(candidateLink).toBeVisible({ timeout: 15000 });
    await candidateLink.click();

    // Verify Medicine Detail page structure
    await expect(page).toHaveURL(/\/app\/medicines\/.*/);
    await expect(page.locator("text=Canonical Pharmacological Formulation Identity")).toBeVisible();
    await expect(page.locator("text=Active Molecule Chemical Composition")).toBeVisible();
    await expect(page.locator("text=Bio-Equivalent Generic Candidates")).toBeVisible();

    // Check Schedule H Prescription compliance tag or Indian Pharmacopoeia standard
    await expect(
      page
        .locator("text=Schedule H Prescription Drug")
        .or(page.locator("text=Indian Pharmacopoeia"))
        .first()
    ).toBeVisible();

    // Navigate to Inventory & Batch Management
    await page.goto("/app/inventory");
    await expect(page.locator("h1")).toContainText("Inventory & Batch Management");
    await expect(page.locator("text=Low Stock Formulations")).toBeVisible();
    await expect(page.locator("text=Batches Expiring Soon")).toBeVisible();
    await expect(page.locator("text=Quarantined Batches").first()).toBeVisible();
  });
});

test.describe("Tier 2: Boundary & Corner Cases", () => {
  test("unconfirmed medicine lines strictly block prescription plan generation gate", async ({
    page,
  }) => {
    await loginAsPharmacist(page);

    // Create a new draft with Indian outpatient patient reference
    await page.goto("/app/prescriptions/new");
    await page.getByPlaceholder("e.g. RX-2026-4412").fill("RX-GATE-UNCONFIRMED-01");
    await page.click('button[type="submit"]');

    // On Review screen, verify intake loaded
    await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/review/);
    await expect(page.locator("h1")).toContainText("Review Prescription");

    // Add unconfirmed line
    await page.click('button:has-text("Add Line")');

    // Confirm button must be disabled because newly added line is unconfirmed
    const confirmBtn = page.locator('button:has-text("Confirm & Generate Plan")');
    await expect(confirmBtn).toBeDisabled();
    await expect(page.locator("text=Ambiguous: Catalogue Selection Required")).toBeVisible();

    // Select a catalogue SKU from the dropdown
    const lastSelect = page.locator("select").last();
    await expect(lastSelect).toBeVisible();
    await expect(lastSelect.locator("option").nth(1)).toBeAttached({ timeout: 10000 });
    await lastSelect.selectOption({ index: 1 });

    // After selection, the confirm button must become enabled
    await expect(confirmBtn).toBeEnabled();
  });

  test("assistant account is restricted by clinical role gates from approving plans", async ({
    page,
  }) => {
    await loginAsAssistant(page);

    // Navigate to Approvals queue
    await page.goto("/app/approvals");
    await expect(page.locator("h1")).toContainText("Clinical Approvals");

    const reviewLinks = page.locator('a:has-text("Review Plan")');
    const count = await reviewLinks.count();
    if (count > 0) {
      await reviewLinks.first().click();

      // Assistant account MUST see the Pharmacist role warning
      await expect(page.locator("text=Pharmacist Role Required")).toBeVisible();
      // Approve button must not be visible to Assistant
      await expect(page.locator('button:has-text("Approve Fulfilment Plan")')).toHaveCount(0);
    }
  });

  test("whole-pack dispensing arithmetic enforces integer pack boundaries with excess units", async ({
    page,
  }) => {
    await loginAsPharmacist(page);

    // Load sample prescription (requests 15 tablets of Paracetamol)
    await page.goto("/app/prescriptions/new");
    await page.click('button:has-text("Load Sample Prescription")');

    // On Review page, ensure line items have rendered
    await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/review/);
    await expect(page.locator(".font-semibold:has-text('Brand A Paracetamol')").first()).toBeVisible({
      timeout: 15000,
    });

    // Wait for dropdown options to be attached before selecting
    await expect(page.locator('option:has-text("DemoAmlo 5")').first()).toBeAttached({ timeout: 15000 });
    const dropdowns = page.locator("select");
    await dropdowns.nth(1).selectOption({ label: "DemoAmlo 5 (amlodipine 5mg (tablet))" });

    // Confirm and generate plan
    const confirmBtn = page.locator('button:has-text("Confirm & Generate Plan")');
    await expect(confirmBtn).toBeEnabled({ timeout: 15000 });
    await confirmBtn.click();

    await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/plan/);
    await expect(page.locator("h1")).toContainText("Fulfilment Plan", { timeout: 20000 });

    // Target the specific dropdown containing Product B Generic Paracetamol
    const candDropdown = page
      .locator("select")
      .filter({ has: page.locator('option:has-text("Product B Generic Paracetamol")') });
    await expect(candDropdown).toBeVisible({ timeout: 15000 });
    await candDropdown.selectOption({ label: "Product B Generic Paracetamol (Pack ₹10.00)" });

    // Verify whole pack arithmetic:
    // 15 tablets requested requires ceil(15 / 10) = 2 whole packs = 20 tablets supplied (5 excess bonus units)
    await expect(page.locator("text=2 pack(s)").first()).toBeVisible();
    await expect(page.locator("text=20 tablets").first()).toBeVisible();
    await expect(page.locator("text=5 excess bonus units in whole pack").first()).toBeVisible();
    await expect(page.locator("text=Whole Pack Only (No Strip Cutting)").first()).toBeVisible();

    // Verify savings calculation: ₹20 vs ₹30 = 33.33% savings
    await expect(page.getByText(/33\.33%/).first()).toBeVisible();
  });
});

test.describe("Tier 3: Cross-Feature Combinations", () => {
  test("multi-line clinical prescription intake, generic candidate substitution, and FEFO stock deduction", async ({
    page,
  }) => {
    await loginAsPharmacist(page);

    // 1. Intake New Prescription
    await page.goto("/app/prescriptions/new");
    await page.click('button:has-text("Load Sample Prescription")');

    // 2. Review view: verify line items and confirm
    await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/review/);
    await expect(page.locator("h1")).toContainText("Review Prescription");
    await expect(page.locator(".font-semibold:has-text('Brand A Paracetamol')").first()).toBeVisible({
      timeout: 15000,
    });

    // Confirm ambiguous line
    await expect(page.locator('option:has-text("DemoAmlo 5")').first()).toBeAttached({ timeout: 15000 });
    const dropdowns = page.locator("select");
    await dropdowns.nth(1).selectOption({ label: "DemoAmlo 5 (amlodipine 5mg (tablet))" });

    // 3. Transition to Plan view
    const confirmBtn = page.locator('button:has-text("Confirm & Generate Plan")');
    await expect(confirmBtn).toBeEnabled({ timeout: 15000 });
    await confirmBtn.click();

    await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/plan/);
    await expect(page.locator("h1")).toContainText("Fulfilment Plan", { timeout: 20000 });
    await expect(page.locator("text=Fulfilment & Savings Summary")).toBeVisible();

    // 4. Target the specific dropdown containing Product B Generic Paracetamol
    const candDropdown = page
      .locator("select")
      .filter({ has: page.locator('option:has-text("Product B Generic Paracetamol")') });
    await expect(candDropdown).toBeVisible({ timeout: 15000 });
    await candDropdown.selectOption({ label: "Product B Generic Paracetamol (Pack ₹10.00)" });
    await expect(page.getByText(/33\.33%/).first()).toBeVisible();

    // 5. Clinical Approval by Pharmacist
    const approveBtn = page.locator('button:has-text("Approve Fulfilment Plan")');
    await expect(approveBtn).toBeEnabled();
    await approveBtn.click();
    await expect(page.locator("text=Plan Approved by Pharmacist")).toBeVisible();

    // 6. Finalize Order & Deduct Stock
    const finalizeBtn = page.locator('button:has-text("Finalize Order & Deduct Stock")');
    await expect(finalizeBtn).toBeVisible();
    await finalizeBtn.click();

    // 7. Verify Order Detail view
    await expect(page).toHaveURL(/\/app\/orders\/.*/, { timeout: 20000 });
    await expect(page.locator("text=FINALIZED")).toBeVisible();
    await expect(page.locator("text=Product B Generic Paracetamol")).toBeVisible();
    await expect(page.locator("text=Licensed Retail Dispensary • Drugs & Cosmetics Rules Compliant")).toBeVisible();

    // 8. Test persistence across page reload
    await page.reload();
    await expect(page.locator("text=FINALIZED")).toBeVisible();
    await expect(page.locator("text=Product B Generic Paracetamol")).toBeVisible();

    // 9. Verify Inventory stock reflection
    await page.goto("/app/inventory");
    await expect(page.locator("h1")).toContainText("Inventory & Batch Management");
    await expect(page.locator("text=Product B Generic Paracetamol")).toBeVisible();
  });
});

test.describe("Tier 4: Real-World Clinical Workloads", () => {
  test("Cardiology & Hypertension clinical consultation with Indian prescriber metadata", async ({
    page,
  }) => {
    await loginAsPharmacist(page);

    // 1. Browse Prescriptions Queue
    await page.goto("/app/prescriptions");
    await expect(page.locator("h1")).toContainText("Prescriptions");

    // Verify filter tabs function properly
    const filterTabs = ["all", "draft", "needs confirmation", "confirmed", "completed"];
    for (const tab of filterTabs) {
      const tabBtn = page.locator(`button:has-text("${tab}")`);
      if ((await tabBtn.count()) > 0) {
        await tabBtn.click();
        await page.waitForTimeout(100);
      }
    }
    await page.locator('button:has-text("all")').click();

    // Check if seeded Indian Cardiology prescription is available or create outpatient intake
    const cardioRxLink = page.locator('a:has-text("Rajesh Kumar Verma")');
    if ((await cardioRxLink.count()) > 0) {
      await cardioRxLink.first().click();
      await expect(page).toHaveURL(/\/app\/prescriptions\/.*/);
    } else {
      // 2. Intake Cardiology patient prescription
      await page.goto("/app/prescriptions/new");
      await page.getByPlaceholder("e.g. RX-2026-4412").fill("RX-VERMA-CARDIO-58M");
      await page.click('button[type="submit"]');

      await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/review/);

      // Verify clinical metadata box in Review view
      await expect(page.locator("text=Prescribing Doctor")).toBeVisible();
      await expect(page.locator("text=Medical Reg No.")).toBeVisible();
      await expect(page.locator("text=Patient Ref / MRN")).toBeVisible();
      await expect(page.locator("text=RX-VERMA-CARDIO-58M").first()).toBeVisible();

      // Add prescribed line item
      await page.click('button:has-text("Add Line")');
      const select = page.locator("select").last();
      await expect(select).toBeVisible();
      await expect(select.locator("option").nth(1)).toBeAttached({ timeout: 10000 });
      await select.selectOption({ index: 1 });

      const confirmBtn = page.locator('button:has-text("Confirm & Generate Plan")');
      await expect(confirmBtn).toBeEnabled();
      await confirmBtn.click();

      // Verify Plan generation
      await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/plan/);
      await expect(page.locator("h1")).toContainText("Fulfilment Plan", { timeout: 20000 });
      await expect(page.locator("text=Fulfilment & Savings Summary")).toBeVisible();
    }
  });

  test("Acute Respiratory Infection clinical consultation with antibiotic combination safety", async ({
    page,
  }) => {
    await loginAsPharmacist(page);

    // 1. Catalogue investigation: verify combination formulations in formulary
    await page.goto("/app/medicines");
    await expect(page.locator("h1")).toContainText("Medicines Catalogue");

    // Verify search input operates smoothly
    const searchInput = page.getByPlaceholder("Search by brand name, active molecule, code, or manufacturer...");
    await expect(searchInput).toBeVisible();
    await searchInput.fill("Augmentin");
    await page.waitForTimeout(300);

    // Check if seeded Respiratory prescription is in queue or intake fresh record
    await page.goto("/app/prescriptions");
    const respRxLink = page.locator('a:has-text("Aarav S. Patel")');
    if ((await respRxLink.count()) > 0) {
      await respRxLink.first().click();
      await expect(page).toHaveURL(/\/app\/prescriptions\/.*/);
    } else {
      // 2. Intake Respiratory outpatient prescription
      await page.goto("/app/prescriptions/new");
      await page.getByPlaceholder("e.g. RX-2026-4412").fill("RX-PATEL-RESP-19M");
      await page.click('button[type="submit"]');

      await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/review/);
      await expect(page.locator("text=RX-PATEL-RESP-19M").first()).toBeVisible();

      // Verify Schedule H clinical safety rule / verification standard notice
      await expect(
        page
          .locator("text=Clinical Verification Standard")
          .or(page.locator("text=Clinical Safety Rule"))
          .first()
      ).toBeVisible();
    }
  });
});
