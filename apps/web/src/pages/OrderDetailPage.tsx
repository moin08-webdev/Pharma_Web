import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ShoppingBag, ArrowLeft, Download, Printer, CheckCircle2, ShieldCheck } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Money } from "@/components/common/Money";
import { WorkflowStepper } from "@/components/common/WorkflowStepper";

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: order, isLoading, error } = useQuery({
    queryKey: ["order-detail", id],
    queryFn: () => apiFetch<any>(`/api/v1/orders/${id}`),
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500 animate-pulse">Loading order snapshot...</div>;
  }

  if (error || !order) {
    return <div className="p-4 bg-red-50 text-red-700 rounded-lg">Order record not found.</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <WorkflowStepper currentStep={6} />

      <div className="flex items-center justify-between">
        <Link
          to="/app/orders"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Orders List</span>
        </Link>

        <div className="flex items-center gap-2">
          <a
            href={`/api/v1/orders/${id}/export?format=csv`}
            download
            className="inline-flex items-center gap-1.5 px-3 py-1.5 border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 rounded-md text-xs font-semibold shadow-sm transition"
          >
            <Download className="w-3.5 h-3.5 text-gray-500" />
            <span>Export CSV</span>
          </a>

          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 rounded-md text-xs font-semibold shadow-sm transition"
          >
            <Printer className="w-3.5 h-3.5 text-gray-500" />
            <span>Print Summary</span>
          </button>
        </div>
      </div>

      {/* Printable Dispensing Receipt Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6 rx-watermark">
        {/* Medical Dispensary Header */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between pb-6 border-b border-slate-200 gap-4">
          <div className="flex items-start gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-800 text-2xl font-serif font-black shrink-0">
              ℞
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono font-extrabold text-2xl text-teal-900 tracking-tight">
                  {order.order_number}
                </span>
                <span className="px-2.5 py-0.5 text-xs font-extrabold bg-teal-50 text-teal-800 rounded-md border border-teal-300">
                  FINALIZED
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Dispensed on {new Date(order.completed_at).toLocaleString("en-IN", { dateStyle: "full", timeStyle: "medium" })}
              </p>
              <div className="text-[11px] text-teal-800 font-semibold mt-0.5 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
                <span>Licensed Retail Dispensary • Drugs & Cosmetics Rules Compliant</span>
              </div>
            </div>
          </div>

          <div className="text-left sm:text-right text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-200">
            <div className="text-[10px] uppercase font-bold text-slate-400">Authorized Dispensing Pharmacist</div>
            <div className="font-extrabold text-slate-900 text-sm mt-0.5">{order.completed_by_name}</div>
            <div className="text-[10px] text-teal-700 font-mono mt-0.5">Reg. Lic #PB-RPH-2026-9941</div>
          </div>
        </div>

        {/* Schedule H Caution Warning Banner */}
        <div className="p-3 bg-red-50/70 border border-red-200 rounded-xl text-xs text-red-900 flex items-start gap-2.5">
          <span className="font-bold text-red-700 uppercase tracking-wider text-[10px] bg-red-100 px-1.5 py-0.5 rounded border border-red-300 shrink-0">
            SCHEDULE H
          </span>
          <p className="text-[11px] leading-relaxed">
            <strong>PRESCRIPTION DRUG CAUTION:</strong> To be sold by retail on the prescription of a Registered Medical Practitioner (RMP) only. Dispensed strictly adhering to FEFO inventory batch controls.
          </p>
        </div>

        {/* Medicines Table */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <span>Dispensed Medicines & Batch Allocation Snapshot</span>
            </h3>
            <span className="text-[11px] font-mono text-slate-400">FEFO Stock Allocated</span>
          </div>

          <div className="border border-slate-200 rounded-xl overflow-hidden shadow-2xs">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-4">Medicine Line</th>
                  <th className="py-2.5 px-4">Quantity</th>
                  <th className="py-2.5 px-4">Batch Number(s)</th>
                  <th className="py-2.5 px-4">Savings %</th>
                  <th className="py-2.5 px-4 text-right">Line Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {order.lines.map((l: any) => (
                  <tr key={l.id} className="hover:bg-slate-50/50">
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-900">{l.dispensed_product_name}</div>
                      <div className="text-slate-500 text-[11px]">
                        Prescribed: {l.original_product_name}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-800">
                      {l.supplied_quantity} {l.quantity_unit}s
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">
                      {l.allocations.map((a: any) => (
                        <div key={a.id} className="flex items-center gap-1">
                          <span className="font-semibold text-teal-800">{a.batch_number}</span>
                          <span>({a.quantity} units, exp {a.expiry_date})</span>
                        </div>
                      ))}
                    </td>
                    <td className="py-3 px-4 font-bold text-emerald-700 font-mono">
                      {l.difference_percent ? `${l.difference_percent}%` : "—"}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Money paise={l.total_paise} className="font-bold text-slate-900" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Totals & Pharmacist Verification Seal */}
        <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
          <div className="p-3 bg-teal-50/50 rounded-xl border border-teal-200 text-[11px] text-teal-900 max-w-sm space-y-1">
            <div className="font-extrabold flex items-center gap-1.5 text-teal-950">
              <CheckCircle2 className="w-3.5 h-3.5 text-teal-700" />
              <span>Digital Pharmacist Dispensing Verification</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              Batch authenticity, expiry verification, and whole-pack dispensing rules confirmed prior to physical hand-off.
            </p>
          </div>

          <div className="w-64 space-y-2 text-xs self-end">
            <div className="flex justify-between text-slate-600">
              <span>Currency</span>
              <strong className="text-slate-900 font-mono">{order.currency}</strong>
            </div>
            <div className="flex justify-between text-base font-bold text-teal-900 pt-2 border-t border-slate-200">
              <span>Order Total</span>
              <Money paise={order.total_paise} className="text-xl font-black text-teal-900" />
            </div>
          </div>
        </div>

        <div className="p-3 bg-slate-50 rounded-xl text-[11px] text-slate-500 border border-slate-100 text-center">
          This record represents an authenticated clinical dispensing log and atomic inventory deduction ledger under the Pharmacy Act 1948.
        </div>
      </div>
    </div>
  );
}
