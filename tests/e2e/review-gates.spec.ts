import { test, expect } from "@playwright/test";

test.describe("Clinical Review Gates & Permission Enforcement", () => {
  test("assistant account cannot approve substitutions or finalize orders", async ({ page }) => {
    // 1. Log in as Assistant
    await page.goto("/login");
    await page.fill('input[type="email"]', "assistant@pharmabridge.demo");
    await page.fill('input[type="password"]', "DemoAssistantPass123!");
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/app/);

    // 2. Open any active plan or create one
    await page.goto("/app/approvals");
    await expect(page.locator("h1")).toContainText("Clinical Approvals");

    const reviewLinks = page.locator('a:has-text("Review Plan")');
    const count = await reviewLinks.count();
    if (count > 0) {
      await reviewLinks.first().click();

      // Assistant should see the role warning
      await expect(page.locator("text=Pharmacist Role Required")).toBeVisible();
      // Approve button must not exist or be disabled
      await expect(page.locator('button:has-text("Approve Fulfilment Plan")')).toHaveCount(0);
    }
  });

  test("unconfirmed lines block prescription plan generation", async ({ page }) => {
    // Log in as Pharmacist
    await page.goto("/login");
    await page.fill('input[type="email"]', "pharmacist@pharmabridge.demo");
    await page.fill('input[type="password"]', "DemoPharmacistPass123!");
    await page.click('button[type="submit"]');

    // Wait until logged in
    await expect(page).toHaveURL(/\/app/);

    // Create a new draft
    await page.goto("/app/prescriptions/new");
    await expect(page.locator("h1")).toContainText("New Prescription Intake");
    await page.getByPlaceholder("e.g. RX-2026-4412").fill("UNCONFIRMED-TEST");
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/app\/prescriptions\/.*\/review/);

    // Add unconfirmed line
    await page.click('button:has-text("Add Line")');

    // Confirm button should be disabled because no SKU is selected
    const confirmBtn = page.locator('button:has-text("Confirm & Generate Plan")');
    await expect(confirmBtn).toBeDisabled();
    await expect(page.locator("text=Ambiguous: Catalogue Selection Required")).toBeVisible();
  });
});
