import { test, expect } from "@playwright/test";

test.describe("Responsive Layout & Navigation", () => {
  test("responsive viewport rendering without global horizontal overflow", async ({ page }) => {
    // Log in
    await page.goto("/login");
    await page.fill('input[type="email"]', "pharmacist@pharmabridge.demo");
    await page.fill('input[type="password"]', "DemoPharmacistPass123!");
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/app/);

    const routes = ["/app", "/app/prescriptions", "/app/medicines", "/app/inventory", "/app/orders"];

    for (const route of routes) {
      await page.goto(route);
      await page.waitForLoadState("domcontentloaded");

      // Verify no global horizontal overflow
      const overflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });
      expect(overflow).toBe(false);
    }
  });
});
