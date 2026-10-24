import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, FilePlus, Sparkles, AlertCircle, ArrowRight, CheckCircle2 } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { WorkflowStepper } from "@/components/common/WorkflowStepper";
import { loadDemoSamplePrescription } from "@/lib/demo-helper";

export function NewPrescriptionPage() {
  const [patientRef, setPatientRef] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleManualCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    try {
      const rx = await apiFetch<any>("/api/v1/prescriptions", {
        method: "POST",
        body: JSON.stringify({ optional_patient_reference: patientRef || null }),
      });

      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        await apiFetch(`/api/v1/prescriptions/${rx.id}/documents`, {
          method: "POST",
          body: formData,
        });
      }

      navigate(`/app/prescriptions/${rx.id}/review`);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to create prescription.");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      await loadDemoSamplePrescription(navigate);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load sample prescription.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <WorkflowStepper currentStep={1} />

      <PageHeader
        title="New Prescription Intake"
        description="Step 1 of 6: Upload a prescription file for OCR extraction, or enter medicine lines manually"
      />

      {errorMsg && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Demo Quick-Start Callout (from PPT Slide 10) */}
      <div className="p-5 bg-gradient-to-r from-purple-50 via-teal-50 to-emerald-50 border border-purple-200 rounded-2xl shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 font-bold text-purple-900 text-sm">
            <Sparkles className="w-4 h-4 text-purple-700" />
            <span>Five-Minute Mentor Demo: Instant Sample Prescription</span>
          </div>
          <p className="text-xs text-purple-800 mt-1 max-w-xl leading-relaxed">
            Quick-start the test scenario: Brand A Paracetamol 500mg (15 tabs) and ambiguous Amlo 5mg. Demonstrates ₹30 vs ₹20 whole-pack savings and clinical review gates.
          </p>
        </div>
        <button
          onClick={handleLoadSample}
          disabled={loading}
          className="px-4 py-2.5 bg-purple-700 hover:bg-purple-800 text-white rounded-xl text-xs font-bold shadow-sm transition shrink-0 disabled:opacity-50 flex items-center gap-1.5"
        >
          <span>Load Sample Prescription</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Document Upload Box */}
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-gray-900 mb-1 flex items-center gap-2">
              <Upload className="w-4 h-4 text-[#0F766E]" />
              <span>Option A: Upload Prescription File</span>
            </h3>
            <p className="text-xs text-gray-500 mb-4">
              Accepted formats: PNG, JPEG, PDF (max 10 MiB, up to 5 pages). Stored securely on private volume.
            </p>

            <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-teal-500 transition cursor-pointer relative bg-gray-50/50">
              <input
                type="file"
                accept="image/png,image/jpeg,application/pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-xs font-semibold text-gray-700">
                {file ? file.name : "Click to select or drag & drop prescription file"}
              </p>
              <p className="text-[11px] text-gray-400 mt-1">
                {file ? `${(file.size / 1024).toFixed(1)} KB` : "JPEG, PNG, or PDF"}
              </p>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-gray-100 text-[11px] text-gray-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-teal-600 shrink-0" />
            <span>Files are stored locally; automatic 24h retention cleanup.</span>
          </div>
        </div>

        {/* Patient Reference & Manual Start */}
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs flex flex-col justify-between">
          <form onSubmit={handleManualCreate} className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-1 flex items-center gap-2">
                <FilePlus className="w-4 h-4 text-[#0F766E]" />
                <span>Option B: Direct / Manual Intake</span>
              </h3>
              <p className="text-xs text-gray-500 mb-4">
                Assign an optional local patient reference or identifier for records.
              </p>

              <label className="block text-xs font-semibold text-gray-700 mb-1">
                Patient Reference / Prescription Number (Optional)
              </label>
              <input
                type="text"
                value={patientRef}
                onChange={(e) => setPatientRef(e.target.value)}
                placeholder="e.g. RX-2026-4412"
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-[#0F766E] focus:border-[#0F766E]"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-lg text-xs font-bold shadow-sm transition disabled:opacity-50"
            >
              <span>{loading ? "Creating Draft..." : "Create & Review Lines (Step 2)"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="mt-4 pt-3 border-t border-gray-100 text-[11px] text-gray-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-teal-600 shrink-0" />
            <span>Manual entry is always available even if OCR is offline.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
