import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  timeout: 45000,
  expect: {
    timeout: 10000,
  },
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "Desktop Chrome",
      use: { ...devices["Desktop Chrome"], browserName: "chromium", viewport: { width: 1440, height: 900 } },
    },
    {
      name: "Tablet",
      use: { ...devices["Galaxy Tab S4"], browserName: "chromium", viewport: { width: 768, height: 1024 } },
    },
    {
      name: "Mobile",
      use: { ...devices["Pixel 7"], browserName: "chromium", viewport: { width: 390, height: 844 } },
    },
  ],
});
