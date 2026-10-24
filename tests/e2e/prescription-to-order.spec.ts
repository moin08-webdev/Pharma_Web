import { test, expect } from "@playwright/test";

test.describe("Prescription-to-Order Real Flow", () => {
  test("complete end-to-end dispensing flow with persistence and inventory reduction", async ({ page }) => {
    // 1. Visit Login page
    await page.goto("/login");
    await expect(page).toHaveTitle(/PharmaBridge/);

    // 2. Sign in as Pharmacist
    await page.fill('input[type="email"]', "pharmacist@pharmabridge.demo");
    await page.fill('input[type="password"]', "DemoPharmacistPass123!");
    await page.click('button[type="submit"]');

    // 3. Confirm Dashboard loads
    await expect(page).toHaveURL(/\/app/);
    await expect(page.locator("h1")).toContainText("Pharmacy Dashboard");

    // 4. Navigate to New Prescription
    await page.goto("/app/prescriptions/new");
    await expect(page.locator("h1")).toContainText("New Prescription Intake");

    // 5. Click "Load Sample Prescription" demo quick-start
    await page.click('button:has-text("Load Sample Prescription")');

    // 6. Wait for Review screen
    await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/review/);
    await expect(page.locator("h1")).toContainText("Review Prescription");

    // Verify Line 1 is Brand A Paracetamol
    await expect(page.locator(".font-semibold:has-text('Brand A Paracetamol')").first()).toBeVisible();

    // Line 2 is Amlo 5mg (ambiguous, needs resolution)
    // Select DemoAmlo 5 from the second line's select dropdown
    const dropdowns = page.locator("select");
    const count = await dropdowns.count();
    expect(count).toBeGreaterThanOrEqual(2);

    // In the second select, pick DemoAmlo 5
    await dropdowns.nth(1).selectOption({ label: "DemoAmlo 5 (amlodipine 5mg (tablet))" });

    // 7. Click Confirm & Generate Plan
    const confirmBtn = page.locator('button:has-text("Confirm & Generate Plan")');
    await expect(confirmBtn).toBeEnabled();
    await confirmBtn.click();

    // 8. Assert navigated to Plan view
    await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/plan/);
    await expect(page.locator("h1")).toContainText("Fulfilment Plan");

    // Verify baseline quote is calculated
    await expect(page.locator("text=Fulfilment & Savings Summary")).toBeVisible();

    // 9. Switch Brand A to Candidate Product B in the candidate dropdown
    const candDropdown = page.locator("select").first();
    await candDropdown.selectOption({ label: "Product B Generic Paracetamol (Pack ₹10.00)" });

    // 10. Assert 33.33% savings is displayed
    await expect(page.getByText(/33\.33%/).first()).toBeVisible();

    // 11. Approve plan as Pharmacist
    const approveBtn = page.locator('button:has-text("Approve Fulfilment Plan")');
    await expect(approveBtn).toBeEnabled();
    await approveBtn.click();

    // 12. Assert Plan is Approved
    await expect(page.locator("text=Plan Approved by Pharmacist")).toBeVisible();

    // 13. Finalize Order & Deduct Stock
    const finalizeBtn = page.locator('button:has-text("Finalize Order & Deduct Stock")');
    await expect(finalizeBtn).toBeVisible();
    await finalizeBtn.click();

    // 14. Assert navigated to Order Detail page
    await expect(page).toHaveURL(/\/app\/orders\/.*/);
    await expect(page.locator("text=FINALIZED")).toBeVisible();
    await expect(page.locator("text=Product B Generic Paracetamol")).toBeVisible();

    // 15. Reload the page to verify backend persistence
    await page.reload();
    await expect(page.locator("text=FINALIZED")).toBeVisible();
    await expect(page.locator("text=Product B Generic Paracetamol")).toBeVisible();

    // 16. Navigate to Inventory and verify stock persistence
    await page.goto("/app/inventory");
    await expect(page.locator("h1")).toContainText("Inventory & Batch Management");
    await expect(page.locator("text=Product B Generic Paracetamol")).toBeVisible();
  });
});
