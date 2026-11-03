import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ClipboardCheck, ArrowRight, Clock, ShieldCheck } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Money } from "@/components/common/Money";

export function ApprovalsPage() {
  const { data: plans, isLoading, error } = useQuery({
    queryKey: ["approvals-list"],
    queryFn: () => apiFetch<any[]>("/api/v1/approvals"),
  });

  return (
    <div>
      <PageHeader
        title="Clinical Approvals & Review Queue"
        description="Pharmacist review queue for submitted formulation plans and substitution authorizations"
      />

      {/* Role Governance Standard */}
      <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs text-slate-800 shadow-xs mb-6">
        <div>
          <strong>Role Governance Standard:</strong> Dispensary assistants can intake and check details, but only registered <strong>Pharmacists</strong> can clinically approve medicine substitutions and authorize stock deduction.
        </div>
        <span className="font-semibold text-slate-700 text-[11px] hidden sm:inline bg-white border border-slate-200 px-2.5 py-0.5 rounded">
          Pharmacy Act 1948
        </span>
      </div>

      {isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-sm text-gray-500 animate-pulse">
          Loading approval queue...
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg">Failed to load approvals queue.</div>
      ) : plans && plans.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <ShieldCheck className="w-12 h-12 text-teal-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-gray-800">No plans awaiting approval</h3>
          <p className="text-sm text-gray-500 mt-1">
            All submitted fulfilment plans have been reviewed.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-600 font-semibold border-b border-gray-200">
                <tr>
                  <th className="py-3 px-4">Plan Reference</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Fulfilled Lines</th>
                  <th className="py-3 px-4">Plan Total</th>
                  <th className="py-3 px-4">Created Date</th>
                  <th className="py-3 px-4 text-right">Review Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {plans?.map((p) => {
                  const quote = p.current_quote;
                  return (
                    <tr key={p.id} className="hover:bg-gray-50 transition">
                      <td className="py-3 px-4 font-semibold text-gray-900">
                        Plan #{p.id.slice(0, 8)} (v{p.version})
                      </td>
                      <td className="py-3 px-4">
                        <StatusBadge status={p.state} />
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {quote ? `${quote.coverage.fulfilled_lines} of ${quote.coverage.requested_lines}` : "—"}
                      </td>
                      <td className="py-3 px-4 font-semibold text-gray-900">
                        <Money paise={quote?.totals.comparable_subset_selected_paise} />
                      </td>
                      <td className="py-3 px-4 text-gray-500 text-xs">
                        {new Date(p.created_at).toLocaleString("en-IN", {
                          dateStyle: "medium",
                          timeStyle: "short",
                        })}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link
                          to={`/app/prescriptions/${p.prescription_id}/plan`}
                          className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold bg-[#E6F4F2] text-[#0F766E] hover:bg-teal-100 rounded transition"
                        >
                          <span>Review Plan</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
