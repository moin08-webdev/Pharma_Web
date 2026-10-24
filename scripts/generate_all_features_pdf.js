const path = require("path");
const fs = require("fs");
const { chromium } = require("@playwright/test");

async function generateAllFeaturesPDF() {
  const htmlPath = path.resolve(__dirname, "../docs/all_features_deck.html");
  const outputPath = path.resolve(__dirname, "../PharmaBridge_All_Features_Presentation_Slides.pdf");

  console.log(`Reading all features HTML from: ${htmlPath}`);
  console.log(`Generating 22-slide PDF at: ${outputPath}`);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1920, height: 1080 },
  });

  const fileUrl = `file://${htmlPath.replace(/\\/g, "/")}`;
  await page.goto(fileUrl, { waitUntil: "networkidle" });

  await page.pdf({
    path: outputPath,
    width: "16in",
    height: "9in",
    printBackground: true,
    margin: { top: 0, bottom: 0, left: 0, right: 0 },
  });

  await browser.close();
  console.log(`Slide PDF created successfully: ${outputPath} (${fs.statSync(outputPath).size} bytes)`);
}

generateAllFeaturesPDF().catch((err) => {
  console.error("Error generating slide PDF:", err);
  process.exit(1);
});
