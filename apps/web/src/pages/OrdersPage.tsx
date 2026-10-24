import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ShoppingBag, ArrowRight, Download, FileText } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Money } from "@/components/common/Money";

interface OrderItem {
  id: string;
  order_number: string;
  prescription_id: string;
  total_paise: number;
  currency: string;
  completed_at: string;
  item_count: number;
}

export function OrdersPage() {
  const { data: orders, isLoading, error } = useQuery({
    queryKey: ["orders-list"],
    queryFn: () => apiFetch<OrderItem[]>("/api/v1/orders"),
  });

  return (
    <div>
      <PageHeader
        title="Dispensed Orders"
        description="Immutable records of finalized prescription orders and stock deductions"
      />

      {isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-sm text-gray-500 animate-pulse">
          Loading orders...
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg">Failed to load orders.</div>
      ) : orders && orders.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <ShoppingBag className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-gray-800">No completed orders yet</h3>
          <p className="text-sm text-gray-500 mt-1">
            Finalized prescription plans will appear here after pharmacist approval.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-600 font-semibold border-b border-gray-200">
                <tr>
                  <th className="py-3 px-4">Order Number</th>
                  <th className="py-3 px-4">Dispensed Medicines</th>
                  <th className="py-3 px-4">Total Amount</th>
                  <th className="py-3 px-4">Dispensed At</th>
                  <th className="py-3 px-4 text-right">Receipt / Snapshot</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {orders?.map((ord) => (
                  <tr key={ord.id} className="hover:bg-gray-50 transition">
                    <td className="py-3 px-4 font-mono font-bold text-teal-800">
                      {ord.order_number}
                    </td>
                    <td className="py-3 px-4 text-gray-700">
                      {ord.item_count} medicine{ord.item_count === 1 ? "" : "s"}
                    </td>
                    <td className="py-3 px-4 font-semibold text-gray-900">
                      <Money paise={ord.total_paise} />
                    </td>
                    <td className="py-3 px-4 text-gray-500 text-xs">
                      {new Date(ord.completed_at).toLocaleString("en-IN", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/app/orders/${ord.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold bg-gray-100 hover:bg-[#E6F4F2] hover:text-[#0F766E] text-gray-700 rounded transition"
                      >
                        <span>View Snapshot</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
