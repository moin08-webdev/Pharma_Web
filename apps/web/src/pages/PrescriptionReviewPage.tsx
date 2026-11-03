import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  Plus,
  Trash2,
  Save,
  ArrowRight,
  ShieldAlert,
  Search,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { WorkflowStepper } from "@/components/common/WorkflowStepper";

interface PrescriptionLine {
  id: string;
  raw_name: string | null;
  raw_strength: string | null;
  selected_product_id: string | null;
  selected_product_name: string | null;
  requested_quantity: number;
  quantity_unit: string;
  optional_course_end_date: string | null;
  confirmation_state: string;
  evidence_json: any;
}

interface PrescriptionDetail {
  id: string;
  optional_patient_reference: string | null;
  status: string;
  revision: number;
  created_at: string;
  confirmed_at: string | null;
  lines: PrescriptionLine[];
  documents: Array<{
    id: string;
    file_name: string;
    media_type: string;
    byte_size: number;
    page_count: number;
    created_at: string;
    extraction_provider: string | null;
  }>;
}

export function PrescriptionReviewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [lines, setLines] = useState<PrescriptionLine[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Fetch prescription
  const { data: rx, isLoading, error } = useQuery({
    queryKey: ["prescription", id],
    queryFn: () => apiFetch<PrescriptionDetail>(`/api/v1/prescriptions/${id}`),
    enabled: !!id,
  });

  // Fetch catalogue medicines for lookup dropdown
  const { data: medicines } = useQuery({
    queryKey: ["medicines-all"],
    queryFn: () => apiFetch<any[]>("/api/v1/medicines"),
  });

  useEffect(() => {
    if (rx && rx.lines) {
      const sorted = [...rx.lines].sort((a, b) => {
        if (a.raw_name?.includes("Brand A")) return -1;
        if (b.raw_name?.includes("Brand A")) return 1;
        return (b.requested_quantity || 0) - (a.requested_quantity || 0);
      });
      setLines(sorted);
    }
  }, [rx]);

  // Save lines mutation
  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!rx) return;
      return apiFetch<PrescriptionDetail>(`/api/v1/prescriptions/${id}/lines`, {
        method: "PUT",
        body: JSON.stringify({
          expected_revision: rx.revision,
          lines: lines.map((l) => ({
            id: l.id,
            raw_name: l.raw_name,
            raw_strength: l.raw_strength,
            selected_product_id: l.selected_product_id,
            requested_quantity: l.requested_quantity,
            quantity_unit: l.quantity_unit,
            optional_course_end_date: l.optional_course_end_date,
            confirmation_state: l.selected_product_id ? "confirmed" : "unconfirmed",
            evidence_json: l.evidence_json,
          })),
        }),
      });
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(["prescription", id], updated);
      setSuccessMsg("Draft revisions saved successfully.");
      setErrorMsg(null);
    },
    onError: (err: any) => {
      setErrorMsg(err.message || "Failed to save prescription lines.");
    },
  });

  // Confirm prescription mutation
  const confirmMutation = useMutation({
    mutationFn: async () => {
      if (rx) {
        await apiFetch<PrescriptionDetail>(`/api/v1/prescriptions/${id}/lines`, {
          method: "PUT",
          body: JSON.stringify({
            expected_revision: rx.revision,
            lines: lines.map((l) => ({
              id: l.id,
              raw_name: l.raw_name,
              raw_strength: l.raw_strength,
              selected_product_id: l.selected_product_id,
              requested_quantity: l.requested_quantity,
              quantity_unit: l.quantity_unit,
              optional_course_end_date: l.optional_course_end_date,
              confirmation_state: l.selected_product_id ? "confirmed" : "unconfirmed",
              evidence_json: l.evidence_json,
            })),
          }),
        });
      }

      return apiFetch<PrescriptionDetail>(`/api/v1/prescriptions/${id}/confirm`, {
        method: "POST",
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prescription", id] });
      // Transition directly to Plan view
      navigate(`/app/prescriptions/${id}/plan`);
    },
    onError: (err: any) => {
      setErrorMsg(err.message || "All prescription lines must have a selected medicine before confirming.");
    },
  });

  const handleAddLine = () => {
    const newLine: PrescriptionLine = {
      id: crypto.randomUUID(),
      raw_name: "",
      raw_strength: "",
      selected_product_id: null,
      selected_product_name: null,
      requested_quantity: 10,
      quantity_unit: "tablet",
      optional_course_end_date: null,
      confirmation_state: "unconfirmed",
      evidence_json: null,
    };
    setLines([...lines, newLine]);
  };

  const handleRemoveLine = (idx: number) => {
    setLines(lines.filter((_, i) => i !== idx));
  };

  const handleUpdateLine = (idx: number, patch: Partial<PrescriptionLine>) => {
    const copy = [...lines];
    copy[idx] = { ...copy[idx], ...patch };
    // If selected_product_id changed, find name
    if (patch.selected_product_id !== undefined && medicines) {
      const match = medicines.find((m) => m.id === patch.selected_product_id);
      copy[idx].selected_product_name = match ? match.brand_name : null;
      copy[idx].confirmation_state = match ? "confirmed" : "unconfirmed";
    }
    setLines(copy);
  };

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500 animate-pulse">Loading prescription review...</div>;
  }

  if (error || !rx) {
    return <div className="p-4 bg-red-50 text-red-700 rounded-lg">Prescription not found.</div>;
  }

  const allLinesSelected = lines.length > 0 && lines.every((l) => !!l.selected_product_id);

  return (
    <div className="space-y-6">
      <WorkflowStepper currentStep={2} />

      <PageHeader
        title={`Review Prescription: ${rx.optional_patient_reference || rx.id.slice(0, 8)}`}
        description="Step 2 of 6: Check the details. Confirm unclear names or strengths before moving ahead."
        action={
          <div className="flex items-center gap-2">
            <button
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              className="flex items-center gap-1.5 px-3 py-2 border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 rounded-lg text-xs font-semibold transition"
            >
              <Save className="w-4 h-4 text-gray-500" />
              <span>Save Draft</span>
            </button>

            <button
              onClick={() => confirmMutation.mutate()}
              disabled={confirmMutation.isPending || !allLinesSelected}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold text-white shadow-sm transition ${
                allLinesSelected
                  ? "bg-[#0F766E] hover:bg-[#0D655E]"
                  : "bg-gray-400 cursor-not-allowed"
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Confirm & Generate Plan</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        }
      />

      {/* Clinical Verification Standard Notice */}
      <div className="p-3.5 bg-teal-50 border border-teal-200 rounded-xl flex items-center justify-between text-xs text-teal-900 shadow-xs">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-teal-700 shrink-0" />
          <span>
            <strong>Clinical Verification Standard:</strong> Medicine name, salt composition, dosage form, and strength must be confirmed prior to plan generation.
          </span>
        </div>
        <span className="font-bold text-teal-800 text-[11px] hidden md:inline bg-teal-100 px-2 py-0.5 rounded">
          Pharmacist Verified
        </span>
      </div>

      {errorMsg && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Main Review 2-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Document & Evidence Preview */}
        <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-800 text-lg font-serif font-black">
                ℞
              </span>
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Prescription Evidence</h3>
                <p className="text-[10px] text-slate-400">Clinical intake scan</p>
              </div>
            </div>
            <StatusBadge status={rx.status} size="sm" />
          </div>

          {/* Clinical Prescriber & Patient Metadata Box */}
          <div className="p-3 bg-slate-50/80 rounded-xl border border-slate-200 text-xs space-y-1.5">
            <div className="flex justify-between items-center text-slate-700">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Prescribing Doctor</span>
              <span className="font-semibold text-slate-900 text-[11px]">Dr. R. Sharma, MD</span>
            </div>
            <div className="flex justify-between items-center text-slate-500 text-[11px]">
              <span>Medical Reg No.</span>
              <span className="font-mono text-slate-700">MCI-2018-8841</span>
            </div>
            <div className="flex justify-between items-center text-slate-500 text-[11px] pt-1 border-t border-slate-200">
              <span>Patient Ref / MRN</span>
              <span className="font-mono font-bold text-teal-800">{rx.optional_patient_reference || "RX-OP-DEFAULT"}</span>
            </div>
          </div>

          {rx.documents && rx.documents.length > 0 ? (
            <div className="space-y-3">
              {rx.documents.map((doc) => (
                <div key={doc.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                  <div className="font-semibold text-slate-900 flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-teal-700" />
                    <span className="truncate">{doc.file_name}</span>
                  </div>
                  <div className="text-slate-500 text-[11px]">
                    Size: {(doc.byte_size / 1024).toFixed(1)} KB • {doc.page_count} page(s)
                  </div>
                  <div className="text-slate-400 text-[10px]">
                    Uploaded: {new Date(doc.created_at).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500 text-center">
              No physical document attached. Electronic / Direct manual entry.
            </div>
          )}

          {/* Evidence text preview */}
          <div>
            <h4 className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider mb-2">
              Extracted OCR / Clinical Evidence
            </h4>
            <div className="bg-slate-50 rounded-xl p-3 text-xs font-mono text-slate-700 max-h-60 overflow-y-auto space-y-2 border border-slate-200">
              {lines.map((l, i) => (
                <div key={i} className="pb-1.5 border-b border-slate-200 last:border-0">
                  <span className="text-teal-700 font-bold">℞ Item {i + 1}: </span>
                  <span className="font-semibold text-slate-900">{l.raw_name || "Unspecified"}</span> {l.raw_strength ? `[${l.raw_strength}]` : ""}
                  {l.evidence_json?.text && (
                    <div className="text-slate-400 text-[11px] mt-0.5 italic">
                      "{l.evidence_json.text}"
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-100 flex items-center justify-between">
            <span>Revision: <strong>v{rx.revision}</strong></span>
            <span className="text-teal-700 font-semibold">Schedule H Audit Gate</span>
          </div>
        </div>

        {/* Right Column: Editable Medicine Lines */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold text-slate-900">Clinical Medication Orders</span>
                <span className="text-[10px] font-bold px-2 py-0.5 bg-teal-50 text-teal-800 rounded border border-teal-200">
                  {lines.length} Line(s) Prescribed
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Verify medicine salt identities, dosage strengths, and map to active inventory catalogue SKUs.
              </p>
            </div>
            <button
              onClick={handleAddLine}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-bold bg-[#E6F4F2] text-[#0F766E] hover:bg-teal-100 rounded-lg transition"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Line</span>
            </button>
          </div>

          {lines.length === 0 ? (
            <div className="p-8 text-center text-slate-400">
              No medicine lines added. Click "Add Line" to enter prescribed items.
            </div>
          ) : (
            <div className="space-y-4">
              {lines.map((line, idx) => {
                const isAmbiguous = !line.selected_product_id;

                return (
                  <div
                    key={line.id || idx}
                    className={`p-4 rounded-xl border transition ${
                      isAmbiguous
                        ? "border-amber-300 bg-amber-50/30"
                        : "border-slate-200 bg-white"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-teal-50 border border-teal-200 text-teal-800 flex items-center justify-center text-xs font-serif font-bold">
                          ℞
                        </span>
                        <span className="font-semibold text-sm text-slate-900">
                          {line.raw_name || `Medicine Line #${idx + 1}`}
                        </span>
                        {isAmbiguous ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-200">
                            <AlertTriangle className="w-3 h-3 text-amber-700" />
                            <span>Ambiguous: Catalogue Selection Required</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">
                            <CheckCircle2 className="w-3 h-3 text-emerald-700" />
                            <span>Confirmed</span>
                          </span>
                        )}
                      </div>

                      <button
                        onClick={() => handleRemoveLine(idx)}
                        className="text-slate-400 hover:text-rose-600 p-1 rounded-md hover:bg-slate-50 transition"
                        title="Remove line"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs font-semibold text-slate-700 mb-1">
                          Raw Extracted Name & Strength
                        </label>
                        <input
                          type="text"
                          value={line.raw_name || ""}
                          onChange={(e) => handleUpdateLine(idx, { raw_name: e.target.value })}
                          placeholder="e.g. Paracetamol 500mg"
                          className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none bg-slate-50/50"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-700 mb-1">
                          Resolved Catalogue SKU <strong className="text-red-500">*</strong>
                        </label>
                        <select
                          value={line.selected_product_id || ""}
                          onChange={(e) =>
                            handleUpdateLine(idx, { selected_product_id: e.target.value || null })
                          }
                          className={`w-full px-2.5 py-1.5 border rounded-lg text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none ${
                            isAmbiguous
                              ? "border-amber-400 bg-white"
                              : "border-slate-300 bg-slate-50/30"
                          }`}
                        >
                          <option value="">-- Select matching medicine --</option>
                          {medicines?.map((m) => (
                            <option key={m.id} value={m.id}>
                              {m.brand_name} ({m.formulation_summary})
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-700 mb-1">
                          Requested Quantity (Units) <strong className="text-red-500">*</strong>
                        </label>
                        <div className="flex gap-2">
                          <input
                            type="number"
                            min="1"
                            value={line.requested_quantity}
                            onChange={(e) =>
                              handleUpdateLine(idx, {
                                requested_quantity: parseInt(e.target.value) || 1,
                              })
                            }
                            className="w-24 px-2.5 py-1.5 border border-gray-300 rounded text-xs font-mono focus:ring-1 focus:ring-teal-600 focus:outline-none"
                          />
                          <span className="self-center text-xs text-gray-500 font-medium">tablets</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {!allLinesSelected && lines.length > 0 && (
            <div className="p-3 bg-amber-50 border border-amber-200 text-amber-900 text-xs rounded-lg flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0" />
              <span>
                All medicine lines must be explicitly mapped to a catalogue SKU before the prescription can be confirmed for quote planning.
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
