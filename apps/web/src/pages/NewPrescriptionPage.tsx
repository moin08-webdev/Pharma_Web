import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Upload,
  FilePlus,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Stethoscope,
  Pill,
  ShieldCheck,
  FileCheck,
  User,
  Hash,
  AlertTriangle,
} from "lucide-react";
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
        description="Step 1 of 6: Clinical intake via digital scan upload or direct order entry pad"
      />

      {errorMsg && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Clinical Prescription Pad Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs rx-watermark flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-800 text-2xl font-serif font-black shrink-0">
            ℞
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-slate-900 text-sm tracking-tight">
                Prescription Triage & Verification Station
              </span>
              <span className="text-[10px] font-bold text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
                Formulary Ready
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Prescriptions are ingested under Indian Pharmacy Practice Regulations & DPDP Act 2023 private storage.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-[11px] text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
          <ShieldCheck className="w-4 h-4 text-teal-600 shrink-0" />
          <span>Zero cloud data leakage • Local encrypted volume</span>
        </div>
      </div>

      {/* Clinical Sample Quick-Loader */}
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white rounded-lg border border-slate-200">
            <FileCheck className="w-4 h-4 text-teal-700" />
          </div>
          <div>
            <div className="font-bold text-slate-900 text-xs">
              Clinical Benchmark Sample Prescription
            </div>
            <p className="text-slate-500 text-[11px] mt-0.5">
              Standard outpatient formulation regimen for clinical review and verification.
            </p>
          </div>
        </div>
        <button
          onClick={handleLoadSample}
          disabled={loading}
          className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 rounded-lg text-xs font-bold shadow-xs transition shrink-0 disabled:opacity-50 flex items-center gap-1.5"
        >
          <span>Load Sample Prescription</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Document Upload Box */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-1 flex items-center gap-2">
              <Upload className="w-4 h-4 text-[#0F766E]" />
              <span>Option A: Upload Prescription File</span>
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Accepted formats: PNG, JPEG, PDF (max 10 MiB, up to 5 pages). Stored securely on private volume.
            </p>

            <div className="border-2 border-dashed border-slate-300 rounded-2xl p-6 text-center hover:border-teal-500 hover:bg-teal-50/20 transition cursor-pointer relative bg-slate-50/50 group">
              <input
                type="file"
                accept="image/png,image/jpeg,application/pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div className="w-12 h-12 rounded-full bg-teal-50 border border-teal-200 flex items-center justify-center mx-auto mb-2 text-teal-700 group-hover:scale-105 transition">
                <Upload className="w-5 h-5" />
              </div>
              <p className="text-xs font-bold text-slate-800">
                {file ? file.name : "Click to select or drag & drop prescription file"}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                {file ? `${(file.size / 1024).toFixed(1)} KB` : "Supports doctor slips, clinic scans, and camera photos"}
              </p>
            </div>

            <div className="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-100 text-[11px] text-slate-600 space-y-1">
              <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                <FileCheck className="w-3.5 h-3.5 text-teal-600" />
                <span>Clinical Scan Guidelines:</span>
              </div>
              <p>• Ensure doctor's name, clinic header, and Rx signature are visible.</p>
              <p>• Plain legible text accelerates OCR drug name extraction.</p>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-teal-600 shrink-0" />
            <span>Files are stored locally; automatic 24h retention cleanup.</span>
          </div>
        </div>

        {/* Patient Reference & Manual Start */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <form onSubmit={handleManualCreate} className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 mb-1 flex items-center gap-2">
                <FilePlus className="w-4 h-4 text-[#0F766E]" />
                <span>Option B: Direct / Manual Intake</span>
              </h3>
              <p className="text-xs text-slate-500 mb-4">
                Assign an optional local patient reference or identifier for records.
              </p>

              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1.5">
                    <Hash className="w-3.5 h-3.5 text-teal-700" />
                    <span>Patient Reference / Prescription Number (Optional)</span>
                  </label>
                  <input
                    type="text"
                    value={patientRef}
                    onChange={(e) => setPatientRef(e.target.value)}
                    placeholder="e.g. RX-2026-4412"
                    className="block w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-mono focus:outline-none focus:ring-2 focus:ring-[#0F766E] focus:border-[#0F766E] bg-slate-50/50"
                  />
                  <p className="text-[10px] text-slate-400 mt-1">
                    MRN, doctor prescription number, or clinic token ID.
                  </p>
                </div>

                <div className="p-3 bg-teal-50/60 rounded-xl border border-teal-100 text-xs text-teal-900 flex items-start gap-2">
                  <Stethoscope className="w-4 h-4 text-teal-700 shrink-0 mt-0.5" />
                  <div>
                    <strong>Clinical Triage Note:</strong> In Step 2, you can verify each medication line side-by-side with dosage forms, strength metrics, and therapeutic regimens.
                  </div>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-xl text-xs font-bold shadow-xs transition disabled:opacity-50"
            >
              <span>{loading ? "Creating Draft..." : "Create & Review Lines (Step 2)"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-teal-600 shrink-0" />
            <span>Manual entry is always available even if OCR is offline.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
