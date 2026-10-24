import { apiFetch } from "@/lib/api";

export async function loadDemoSamplePrescription(navigate: (path: string) => void) {
  // 1. Create demonstration prescription
  const rx = await apiFetch<any>("/api/v1/prescriptions", {
    method: "POST",
    body: JSON.stringify({
      optional_patient_reference: `DEMO-RX-${Math.floor(1000 + Math.random() * 9000)}`,
    }),
  });

  // 2. Fetch Brand A medicine SKU
  const meds = await apiFetch<any[]>("/api/v1/medicines?q=Brand A");
  const brandA = meds[0];

  // 3. Populate 2 benchmark lines matching the PPT case studies:
  // Line 1: Brand A Paracetamol 500mg (15 tabs) -> for the ₹30 vs ₹20 (33.33% savings) comparison
  // Line 2: Amlo 5mg (ambiguous) -> to demonstrate ambiguity resolution before quoting
  await apiFetch(`/api/v1/prescriptions/${rx.id}/lines`, {
    method: "PUT",
    body: JSON.stringify({
      expected_revision: rx.revision,
      lines: [
        {
          raw_name: "Brand A Paracetamol 500mg",
          raw_strength: "500 mg",
          selected_product_id: brandA ? brandA.id : null,
          requested_quantity: 15,
          quantity_unit: "tablet",
          confirmation_state: "confirmed",
          evidence_json: { source: "sample_fixture", text: "Brand A Paracetamol 500mg - 15 tabs" },
        },
        {
          raw_name: "Amlo 5mg",
          raw_strength: "5 mg",
          selected_product_id: null, // Intentionally unconfirmed
          requested_quantity: 10,
          quantity_unit: "tablet",
          confirmation_state: "unconfirmed",
          evidence_json: { source: "sample_fixture", text: "Amlo 5mg - 10 tabs" },
        },
      ],
    }),
  });

  // Navigate straight to Step 2: Review & Line Confirmation
  navigate(`/app/prescriptions/${rx.id}/review`);
}
