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
      <div className="bg-white rounded-xl border border-gray-200 p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-gray-200 gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono font-extrabold text-2xl text-teal-800 tracking-tight">
                {order.order_number}
              </span>
              <span className="px-2 py-0.5 text-xs font-bold bg-teal-50 text-teal-800 rounded border border-teal-200">
                FINALIZED
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Dispensed on {new Date(order.completed_at).toLocaleString("en-IN", { dateStyle: "full", timeStyle: "medium" })}
            </p>
          </div>

          <div className="text-left sm:text-right text-xs text-gray-500">
            <div>Authorized Dispensing Pharmacist:</div>
            <div className="font-bold text-gray-900 text-sm mt-0.5">{order.completed_by_name}</div>
          </div>
        </div>

        {/* Medicines Table */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            Dispensed Medicines & Batch Allocation Snapshot
          </h3>
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-xs text-left">
              <thead className="bg-gray-50 text-gray-600 font-semibold border-b">
                <tr>
                  <th className="py-2.5 px-4">Medicine Line</th>
                  <th className="py-2.5 px-4">Quantity</th>
                  <th className="py-2.5 px-4">Batch Number(s)</th>
                  <th className="py-2.5 px-4">Savings %</th>
                  <th className="py-2.5 px-4 text-right">Line Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {order.lines.map((l: any) => (
                  <tr key={l.id} className="hover:bg-gray-50/50">
                    <td className="py-3 px-4">
                      <div className="font-bold text-gray-900">{l.dispensed_product_name}</div>
                      <div className="text-gray-400 text-[11px]">
                        Prescribed: {l.original_product_name}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-semibold text-gray-800">
                      {l.supplied_quantity} {l.quantity_unit}s
                    </td>
                    <td className="py-3 px-4 text-gray-600 font-mono">
                      {l.allocations.map((a: any) => (
                        <div key={a.id}>
                          {a.batch_number} ({a.quantity} units, exp {a.expiry_date})
                        </div>
                      ))}
                    </td>
                    <td className="py-3 px-4 font-semibold text-emerald-700 font-mono">
                      {l.difference_percent ? `${l.difference_percent}%` : "—"}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Money paise={l.total_paise} className="font-bold text-gray-900" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Totals */}
        <div className="pt-4 border-t border-gray-200 flex justify-end">
          <div className="w-64 space-y-2 text-xs">
            <div className="flex justify-between text-gray-600">
              <span>Currency</span>
              <strong className="text-gray-900">{order.currency}</strong>
            </div>
            <div className="flex justify-between text-base font-bold text-teal-900 pt-2 border-t">
              <span>Order Total</span>
              <Money paise={order.total_paise} className="text-lg font-black text-teal-900" />
            </div>
          </div>
        </div>

        <div className="p-3 bg-gray-50 rounded-lg text-[11px] text-gray-500 border border-gray-100 text-center">
          This record represents an internal dispensing log and operational inventory deduction snapshot. It does not constitute a certified tax invoice or legal diagnostic recommendation.
        </div>
      </div>
    </div>
  );
}
