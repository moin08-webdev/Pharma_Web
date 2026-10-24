const path = require("path");
const fs = require("fs");
const { chromium } = require("@playwright/test");

async function generatePDF() {
  const htmlPath = path.resolve(__dirname, "../docs/PharmaBridge_Comprehensive_Documentation.html");
  const outputPath = path.resolve(__dirname, "../PharmaBridge_Comprehensive_Documentation.pdf");

  console.log(`Reading HTML from: ${htmlPath}`);
  console.log(`Generating PDF at: ${outputPath}`);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Load the local HTML file
  const fileUrl = `file://${htmlPath.replace(/\\/g, "/")}`;
  await page.goto(fileUrl, { waitUntil: "networkidle" });

  // Generate PDF
  await page.pdf({
    path: outputPath,
    format: "A4",
    printBackground: true,
    margin: {
      top: "14mm",
      bottom: "14mm",
      left: "14mm",
      right: "14mm",
    },
    displayHeaderFooter: true,
    headerTemplate: `<div style="font-size: 8pt; color: #94a3b8; width: 100%; text-align: right; padding-right: 14mm; font-family: sans-serif;">PharmaBridge Clinical Workspace Documentation</div>`,
    footerTemplate: `<div style="font-size: 8pt; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; padding-left: 14mm; padding-right: 14mm; font-family: sans-serif;"><span>PharmaBridge v1.0 MVP</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`,
  });

  await browser.close();
  console.log(`PDF successfully created: ${outputPath} (${fs.statSync(outputPath).size} bytes)`);
}

generatePDF().catch((err) => {
  console.error("Error generating PDF:", err);
  process.exit(1);
});
