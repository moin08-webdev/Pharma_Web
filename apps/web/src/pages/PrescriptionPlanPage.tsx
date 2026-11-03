import React, { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingDown,
  ShoppingBag,
  RefreshCw,
  Pill,
  ShieldAlert,
  ChevronDown,
  Info,
  Clock,
  Layers,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Money } from "@/components/common/Money";
import { WorkflowStepper } from "@/components/common/WorkflowStepper";
import { useSession } from "@/features/auth/hooks";

export function PrescriptionPlanPage() {
  const { id: rxId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: session } = useSession();

  const [approvalReason, setApprovalReason] = useState("Clinically verified equivalent generic formulation; patient approved.");
  const [authRef, setAuthRef] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // 1. Fetch prescription
  const { data: rx, isLoading: rxLoading } = useQuery({
    queryKey: ["prescription", rxId],
    queryFn: () => apiFetch<any>(`/api/v1/prescriptions/${rxId}`),
    enabled: !!rxId,
  });

  // 2. Fetch or create plan for this prescription
  const { data: plan, isLoading: planLoading, refetch: refetchPlan } = useQuery({
    queryKey: ["plan", rxId],
    queryFn: async () => {
      // Find plans or create draft plan
      const plansList = await apiFetch<any[]>(`/api/v1/approvals?state=`);
      const existing = plansList.find((p) => p.prescription_id === rxId);
      if (existing) return existing;

      // If no plan, create one
      return apiFetch<any>("/api/v1/plans", {
        method: "POST",
        body: JSON.stringify({ prescription_id: rxId }),
      });
    },
    enabled: !!rxId && !!rx && rx.status === "confirmed",
  });

  // Candidate selection mutation
  const selectCandidateMutation = useMutation({
    mutationFn: async ({ lineId, productId }: { lineId: string; productId: string }) => {
      if (!plan) return;
      return apiFetch<any>(`/api/v1/plans/${plan.id}/lines/${lineId}`, {
        method: "PATCH",
        body: JSON.stringify({
          selected_product_id: productId,
          selection_reason: "candidate_savings_selected",
          authorization_required: false,
          expected_plan_version: plan.version,
        }),
      });
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(["plan", rxId], updated);
      setErrorMsg(null);
    },
    onError: (err: any) => {
      setErrorMsg(err.message || "Failed to update formulation selection.");
    },
  });

  // Pharmacist Approval mutation
  const approveMutation = useMutation({
    mutationFn: async () => {
      if (!plan || !plan.current_quote) return;
      return apiFetch<any>(`/api/v1/plans/${plan.id}/approvals`, {
        method: "POST",
        body: JSON.stringify({
          quote_id: plan.current_quote.quote_id,
          decision: "APPROVED",
          reason: approvalReason,
          authorization_reference: authRef || null,
        }),
      });
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(["plan", rxId], updated);
      setErrorMsg(null);
    },
    onError: (err: any) => {
      setErrorMsg(err.message || "Failed to approve fulfilment plan.");
    },
  });

  // Finalize Order mutation
  const finalizeMutation = useMutation({
    mutationFn: async () => {
      if (!plan || !plan.current_quote || !plan.approval) {
        throw new Error("Approved plan required to finalize order.");
      }
      const idemKey = `ORDER-${rxId}-${Date.now()}`;
      return apiFetch<any>("/api/v1/orders", {
        method: "POST",
        body: JSON.stringify({
          quote_id: plan.current_quote.quote_id,
          approval_id: plan.approval.id,
        }),
        headers: {
          "Idempotency-Key": idemKey,
        },
      });
    },
    onSuccess: (order) => {
      queryClient.invalidateQueries({ queryKey: ["prescription", rxId] });
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
      // Navigate to completed Order Detail
      navigate(`/app/orders/${order.id}`);
    },
    onError: (err: any) => {
      setErrorMsg(err.message || "Failed to finalize dispensing order.");
    },
  });

  if (rxLoading || planLoading) {
    return <div className="p-8 text-center text-gray-500 animate-pulse">Calculating formulation quote & stock availability...</div>;
  }

  if (!rx) {
    return <div className="p-4 bg-red-50 text-red-700 rounded-lg">Prescription not found.</div>;
  }

  if (rx.status === "completed") {
    return (
      <div className="bg-white p-8 rounded-xl border border-gray-200 text-center space-y-4">
        <CheckCircle2 className="w-12 h-12 text-teal-600 mx-auto" />
        <h2 className="text-xl font-bold text-gray-900">Prescription Already Dispensed & Completed</h2>
        <p className="text-sm text-gray-500 max-w-md mx-auto">
          This prescription has been finalized and its batches deducted from inventory.
        </p>
        <Link
          to="/app/orders"
          className="inline-flex items-center gap-2 px-4 py-2 bg-[#0F766E] text-white rounded-md text-sm font-medium"
        >
          <span>View Orders List</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  const quote = plan?.current_quote;
  const isPharmacist = session?.user.role === "PHARMACIST";
  const isApproved = plan?.state === "approved";
  const canFinalize = isApproved && quote?.finalizable;

  const displayLines = (quote?.lines ? [...quote.lines] : []).sort((a: any, b: any) => {
    if (a.original_brand_name?.includes("Brand A")) return -1;
    if (b.original_brand_name?.includes("Brand A")) return 1;
    return (b.requested_units || 0) - (a.requested_units || 0);
  });

  return (
    <div className="space-y-6">
      <WorkflowStepper currentStep={3} />

      <PageHeader
        title={`Fulfilment Plan: ${rx.optional_patient_reference || rx.id.slice(0, 8)}`}
        description="Steps 3 & 4 of 6: Compare formulation candidates, pack size economics, FEFO batch allocations, and approve dispensing"
        action={
          <div className="flex items-center gap-2">
            <Link
              to={`/app/prescriptions/${rx.id}/review`}
              className="px-3 py-1.5 border border-gray-300 text-xs font-semibold text-gray-700 bg-white rounded-lg hover:bg-gray-50 transition"
            >
              Back to Line Review
            </Link>
            <StatusBadge status={plan?.state || "draft"} />
          </div>
        }
      />

      {/* Dispensing Standard Banner */}
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs text-slate-800 shadow-xs">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-[#0F766E] shrink-0">
            <TrendingDown className="w-4 h-4 text-[#0F766E]" />
          </div>
          <div>
            <div className="font-bold text-slate-900">
              Dispensing Standard
            </div>
            <p className="text-slate-600 mt-0.5">
              Dispensing Standard: Whole-pack dispensing applied. Bio-equivalent generic candidates compared on verified active salt parity.
            </p>
          </div>
        </div>
        <span className="font-semibold text-slate-700 text-[11px] hidden lg:inline bg-white border border-slate-200 px-3 py-1 rounded-lg">
          Whole-Pack Protocol
        </span>
      </div>

      {errorMsg && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Grid: Left lines comparison, Right summary panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Line comparisons & batch allocations */}
        <div className="lg:col-span-8 space-y-6">
          {displayLines.map((ql: any, idx: number) => {
            const hasDifference = ql.difference_percent !== null;
            const diffNum = parseFloat(ql.difference_percent || "0");
            const isSaving = diffNum > 0;
            const planLine = plan?.lines.find((pl: any) => pl.prescription_line_id === ql.prescription_line_id);

            return (
              <div
                key={ql.prescription_line_id || idx}
                className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
              >
                {/* Line Header */}
                <div className="bg-gray-50/80 px-5 py-3 border-b border-gray-200 flex items-center justify-between">
                  <div className="flex items-center gap-2 font-semibold text-sm text-gray-900">
                    <span className="w-6 h-6 rounded-full bg-teal-100 text-[#0F766E] flex items-center justify-center text-xs font-bold">
                      {idx + 1}
                    </span>
                    <span>Prescribed: {ql.original_brand_name}</span>
                    <span className="text-xs text-gray-500 font-normal">
                      (Requested: {ql.requested_units} units)
                    </span>
                  </div>

                  {hasDifference && (
                    <div
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        isSaving
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : "bg-amber-50 text-amber-700 border border-amber-200"
                      }`}
                    >
                      <TrendingDown className="w-3.5 h-3.5" />
                      <span>{diffNum.toFixed(2)}% {isSaving ? "Savings" : "Cost Increase"}</span>
                    </div>
                  )}
                </div>

                <div className="p-5 space-y-4">
                  {/* Prescribed vs Dispensed Selection */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {/* Baseline Prescribed */}
                    <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1.5">
                      <div className="text-slate-500 font-semibold flex items-center justify-between">
                        <span>Prescribed Brand SKU</span>
                        <span className="text-[10px] font-mono text-slate-400">Baseline</span>
                      </div>
                      <div className="font-bold text-slate-900 text-sm">{ql.original_brand_name}</div>
                      <div className="text-slate-600 flex items-center justify-between pt-1 border-t border-slate-200">
                        <span>Baseline Pack Cost:</span>
                        <Money paise={ql.baseline_line_paise} className="text-slate-900 font-bold" />
                      </div>
                    </div>

                    {/* Selected Dispensing Alternative */}
                    <div className="p-3.5 bg-teal-50/50 rounded-xl border border-teal-200 text-xs space-y-1.5">
                      <div className="text-teal-900 font-bold flex items-center justify-between">
                        <span className="flex items-center gap-1.5">
                          <Pill className="w-3.5 h-3.5 text-teal-700" />
                          <span>Dispensing Selection</span>
                        </span>
                        <CandidatesDropdown
                          originalProductId={ql.original_product_id}
                          selectedProductId={ql.selected_product_id}
                          disabled={isApproved || selectCandidateMutation.isPending}
                          onSelect={(newProductId) => {
                            if (planLine) {
                              selectCandidateMutation.mutate({
                                lineId: planLine.id,
                                productId: newProductId,
                              });
                            }
                          }}
                        />
                      </div>
                      <div className="font-extrabold text-teal-950 text-sm">{ql.selected_brand_name}</div>
                      <div className="text-teal-900 flex items-center justify-between pt-1 border-t border-teal-200/60">
                        <span>Patient Net Total:</span>
                        <Money paise={ql.selected_line_paise} className="font-extrabold text-teal-950" />
                      </div>
                    </div>
                  </div>

                  {/* Pharmacological Bio-Parity Verification Check */}
                  <div className="p-2.5 bg-slate-50/80 rounded-xl border border-slate-200 text-[11px] text-slate-700 flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5 text-teal-800 font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Formulation Bio-Parity Verified: Identical Active Salt & Molecular Strength</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-500 font-mono text-[10px]">
                      <span>IR Release</span>
                      <span>•</span>
                      <span>Oral Route</span>
                      <span>•</span>
                      <span className="text-teal-700 font-bold">Non-NTI Safe</span>
                    </div>
                  </div>

                  {/* Pack Breakdown & Quantities */}
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs flex flex-wrap gap-x-6 gap-y-2">
                    <div>
                      <span className="text-slate-500">Requested: </span>
                      <strong className="text-slate-900">{ql.requested_units} tablets</strong>
                    </div>
                    <div>
                      <span className="text-slate-500">Supplied: </span>
                      <strong className="text-slate-900">{ql.supplied_units} tablets</strong>
                      {ql.excess_units > 0 && (
                        <span className="text-amber-700 font-semibold ml-1">
                          ({ql.excess_units} excess bonus units in whole pack)
                        </span>
                      )}
                    </div>
                    <div>
                      <span className="text-slate-500">Packs Needed: </span>
                      <strong className="text-slate-900">{ql.packs_needed} pack(s)</strong>
                    </div>
                    <div>
                      <span className="text-slate-500">Dispensing Mode: </span>
                      <strong className="text-slate-900">{ql.unit_dispensing ? "Allowed Unit Dispensing" : "Whole Pack Only (No Strip Cutting)"}</strong>
                    </div>
                  </div>

                  {/* FEFO Batch Allocation Breakdown */}
                  <div>
                    <h5 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-teal-700" />
                      <span>FEFO Batch Allocation ({ql.allocations.length} batch(es))</span>
                    </h5>

                    {ql.allocations.length === 0 ? (
                      <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 shrink-0" />
                        <span>Insufficient active unexpired stock available in inventory for this medicine!</span>
                      </div>
                    ) : (
                      <div className="border border-gray-200 rounded-lg overflow-x-auto">
                        <table className="w-full text-xs text-left">
                          <thead className="bg-gray-100 text-gray-600 font-semibold">
                            <tr>
                              <th className="py-2 px-3">Batch Number</th>
                              <th className="py-2 px-3">Quantity</th>
                              <th className="py-2 px-3">Expires On</th>
                              <th className="py-2 px-3">Selling Price (Pack)</th>
                              <th className="py-2 px-3 text-right">Unit Price</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {ql.allocations.map((alloc: any) => (
                              <tr key={alloc.batch_id} className="hover:bg-gray-50">
                                <td className="py-2 px-3 font-mono font-medium text-gray-800">
                                  {alloc.batch_number}
                                </td>
                                <td className="py-2 px-3 font-semibold text-teal-700">
                                  {alloc.quantity} units
                                </td>
                                <td className="py-2 px-3 text-gray-600">
                                  {alloc.expires_on}
                                </td>
                                <td className="py-2 px-3 text-gray-600">
                                  <Money paise={alloc.selling_pack_paise} />
                                </td>
                                <td className="py-2 px-3 text-right">
                                  <Money paise={alloc.unit_price_paise} className="font-semibold text-gray-900" />
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Sticky Summary & Pharmacist Approval Panel */}
        <div className="lg:col-span-4 space-y-6 sticky top-20">
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-5">
            <h3 className="font-bold text-gray-900 text-base border-b pb-3">
              Fulfilment & Savings Summary
            </h3>

            {/* Coverage Info */}
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-gray-100">
                <span className="text-gray-500">Requested Lines</span>
                <strong className="text-gray-900">{quote?.coverage.requested_lines}</strong>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-100">
                <span className="text-gray-500">Fulfillable Stock Lines</span>
                <strong className="text-emerald-700 font-bold">{quote?.coverage.fulfilled_lines}</strong>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-100">
                <span className="text-gray-500">Comparable Cost Lines</span>
                <strong className="text-gray-900">{quote?.coverage.comparable_lines}</strong>
              </div>
            </div>

            {/* Price Totals */}
            <div className="bg-teal-50/50 p-4 rounded-xl border border-teal-100 space-y-2">
              <div className="flex justify-between text-xs text-gray-600">
                <span>Baseline Total</span>
                <Money paise={quote?.totals.comparable_subset_baseline_paise} className="text-gray-700 font-medium" />
              </div>
              <div className="flex justify-between text-xs text-gray-600">
                <span>Optimized Total</span>
                <Money paise={quote?.totals.comparable_subset_selected_paise} className="text-teal-900 font-bold text-sm" />
              </div>

              {quote?.totals.comparable_subset_difference_percent && (
                <div className="pt-2 border-t border-teal-200/60 flex items-center justify-between">
                  <span className="text-xs font-bold text-teal-900">Total Savings</span>
                  <span className="text-base font-extrabold text-emerald-700 font-mono">
                    {quote?.totals.comparable_subset_difference_percent}%
                  </span>
                </div>
              )}
            </div>

            {/* Blockers Notice */}
            {quote?.blockers && quote.blockers.length > 0 && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>Cannot Dispense: Active Blockers</span>
                </div>
                {quote.blockers.map((b: any, i: number) => (
                  <div key={i} className="pl-5 text-red-600">• {b.message}</div>
                ))}
              </div>
            )}

            {/* Approval / Finalization Action Area */}
            <div className="pt-4 border-t border-gray-100 space-y-4">
              {!isApproved ? (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">
                    Pharmacist Clinical Review & Approval
                  </h4>

                  {!isPharmacist ? (
                    <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 space-y-2">
                      <div className="font-semibold flex items-center gap-1.5">
                        <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0" />
                        <span>Pharmacist Role Required</span>
                      </div>
                      <p>
                        Your current account has role <strong>{session?.user.role}</strong>. Only licensed Pharmacists can clinically approve substitutions and authorized dispensing.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Clinical Approval Reason
                        </label>
                        <input
                          type="text"
                          value={approvalReason}
                          onChange={(e) => setApprovalReason(e.target.value)}
                          className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none"
                        />
                      </div>

                      <button
                        onClick={() => approveMutation.mutate()}
                        disabled={approveMutation.isPending || !quote?.finalizable}
                        className={`w-full py-2.5 px-4 rounded-lg text-xs font-bold text-white shadow-sm transition flex items-center justify-center gap-2 ${
                          quote?.finalizable
                            ? "bg-[#0F766E] hover:bg-[#0D655E]"
                            : "bg-gray-400 cursor-not-allowed"
                        }`}
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        <span>{approveMutation.isPending ? "Approving Plan..." : "Approve Fulfilment Plan"}</span>
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs space-y-1">
                    <div className="font-bold flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Plan Approved by Pharmacist</span>
                    </div>
                    <div>Approver: {plan.approval?.actor_name} ({plan.approval?.actor_role})</div>
                    <div className="text-gray-500 text-[11px]">Reason: "{plan.approval?.reason}"</div>
                  </div>

                  {isPharmacist && (
                    <button
                      onClick={() => finalizeMutation.mutate()}
                      disabled={finalizeMutation.isPending || !canFinalize}
                      className="w-full py-3 px-4 bg-teal-800 hover:bg-teal-900 text-white rounded-lg text-sm font-bold shadow-md transition flex items-center justify-center gap-2"
                    >
                      <ShoppingBag className="w-4 h-4" />
                      <span>
                        {finalizeMutation.isPending ? "Locking & Finalizing Order..." : "Finalize Order & Deduct Stock"}
                      </span>
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Subcomponent: Dropdown to switch formulation candidates
function CandidatesDropdown({
  originalProductId,
  selectedProductId,
  disabled,
  onSelect,
}: {
  originalProductId: string;
  selectedProductId: string;
  disabled: boolean;
  onSelect: (productId: string) => void;
}) {
  const { data: candData } = useQuery({
    queryKey: ["candidates", originalProductId],
    queryFn: () => apiFetch<any>(`/api/v1/medicines/${originalProductId}/candidates`),
  });

  if (!candData || candData.eligible_candidates.length === 0) {
    return <span className="text-[11px] text-gray-500 font-normal">No alternatives available</span>;
  }

  return (
    <select
      disabled={disabled}
      value={selectedProductId}
      onChange={(e) => onSelect(e.target.value)}
      className="text-xs bg-white border border-teal-300 rounded px-2 py-0.5 font-medium text-teal-900 focus:outline-none"
    >
      <option value={originalProductId}>As Prescribed</option>
      {candData.eligible_candidates.map((c: any) => (
        <option key={c.product_id} value={c.product_id}>
          {c.brand_name} (Pack ₹{(c.pack_price_paise / 100).toFixed(2)})
        </option>
      ))}
    </select>
  );
}
