import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Package, PlusCircle, AlertTriangle, ShieldAlert, CheckCircle2, X, Clock } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { SourceBadge } from "@/components/common/SourceBadge";

interface InventoryProduct {
  product_id: string;
  brand_name: string;
  manufacturer: string;
  dataset_kind: "DEMO" | "VERIFIED";
  pack_quantity: number;
  dispensing_unit: string;
  total_quantity_on_hand: number;
  active_batches_count: number;
  nearest_expiry: string | null;
  is_low_stock: boolean;
  has_quarantine: boolean;
}

export function InventoryPage() {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);

  // Form state for stock receipt
  const [selectedProductId, setSelectedProductId] = useState("");
  const [batchNo, setBatchNo] = useState("");
  const [qty, setQty] = useState(100);
  const [expiry, setExpiry] = useState("2027-12-31");
  const [mrpPaise, setMrpPaise] = useState(1000);
  const [sellingPaise, setSellingPaise] = useState(1000);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: inventory, isLoading } = useQuery({
    queryKey: ["inventory-list"],
    queryFn: () => apiFetch<InventoryProduct[]>("/api/v1/inventory"),
  });

  const { data: alerts } = useQuery({
    queryKey: ["inventory-alerts"],
    queryFn: () => apiFetch<any>("/api/v1/inventory/alerts"),
  });

  const { data: medicines } = useQuery({
    queryKey: ["medicines-all"],
    queryFn: () => apiFetch<any[]>("/api/v1/medicines"),
  });

  const receiptMutation = useMutation({
    mutationFn: async () => {
      return apiFetch("/api/v1/inventory/receipts", {
        method: "POST",
        body: JSON.stringify({
          product_id: selectedProductId,
          batch_number: batchNo,
          quantity_units: qty,
          quantity_unit: "tablet",
          expires_on: expiry,
          mrp_pack_paise: mrpPaise,
          selling_pack_paise: sellingPaise,
        }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory-list"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-alerts"] });
      setModalOpen(false);
      setBatchNo("");
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.message || "Failed to receive stock batch.");
    },
  });

  const handleSubmitReceipt = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProductId || !batchNo) {
      setFormError("Please select a medicine and specify a batch number.");
      return;
    }
    receiptMutation.mutate();
  };

  return (
    <div>
      <PageHeader
        title="Inventory & Batch Management"
        description="Monitor physical batch quantities, FEFO expiry dates, and receive stock"
        action={
          <button
            onClick={() => {
              setModalOpen(true);
              if (medicines && medicines.length > 0) {
                setSelectedProductId(medicines[0].id);
              }
            }}
            className="flex items-center gap-2 px-4 py-2 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-md text-sm font-medium shadow-sm transition"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Receive New Stock</span>
          </button>
        }
      />

      {/* FEFO Shelf Inventory Priority Banner */}
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs text-slate-800 shadow-xs mb-6">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-[#0F766E] shrink-0">
            <Package className="w-4 h-4 text-[#0F766E]" />
          </div>
          <div>
            <div className="font-bold text-slate-900">
              FEFO Shelf Inventory Priority
            </div>
            <p className="text-slate-600 mt-0.5">
              The automated dispensing engine allocates earliest expiring active stock first. Expired or quarantined batches are strictly locked from counter fulfillment.
            </p>
          </div>
        </div>
        <span className="font-semibold text-slate-700 text-[11px] hidden sm:inline bg-white border border-slate-200 px-3 py-1 rounded-lg">
          First-Expired, First-Out (FEFO)
        </span>
      </div>

      {/* Alert Stats */}
      {alerts && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between hover:border-amber-300 transition">
            <div>
              <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                <span>Low Stock Formulations</span>
              </span>
              <div className="text-2xl font-extrabold text-slate-900 mt-1">
                {alerts.low_stock_products_count}
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">Re-order threshold alert</p>
            </div>
            <div className="p-3 bg-amber-50 text-amber-700 rounded-xl border border-amber-200">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between hover:border-rose-300 transition">
            <div>
              <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-rose-600" />
                <span>Batches Expiring Soon</span>
              </span>
              <div className="text-2xl font-extrabold text-slate-900 mt-1">
                {alerts.expiring_soon_batches_count}
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">Within 90-day buffer (FEFO priority)</p>
            </div>
            <div className="p-3 bg-rose-50 text-rose-700 rounded-xl border border-rose-200">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between hover:border-slate-300 transition">
            <div>
              <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-slate-600" />
                <span>Quarantined Batches</span>
              </span>
              <div className="text-2xl font-extrabold text-slate-900 mt-1">
                {alerts.quarantined_batches_count}
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">Isolated from dispensing</p>
            </div>
            <div className="p-3 bg-slate-100 text-slate-700 rounded-xl border border-slate-200">
              <Package className="w-5 h-5" />
            </div>
          </div>
        </div>
      )}

      {/* Inventory Table */}
      {isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-sm text-gray-500 animate-pulse">
          Loading inventory balances...
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-600 font-semibold border-b border-gray-200">
                <tr>
                  <th className="py-3 px-4">Medicine Product</th>
                  <th className="py-3 px-4">Usable Units on Hand</th>
                  <th className="py-3 px-4">Active Batches</th>
                  <th className="py-3 px-4">Nearest Expiry</th>
                  <th className="py-3 px-4">Dataset</th>
                  <th className="py-3 px-4">Alert Flags</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {inventory?.map((p) => (
                  <tr key={p.product_id} className="hover:bg-gray-50 transition">
                    <td className="py-3 px-4">
                      <div className="font-bold text-gray-900">{p.brand_name}</div>
                      <div className="text-gray-400 text-xs">
                        {p.manufacturer} • {p.pack_quantity} units/pack
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono font-bold text-base text-teal-800">
                        {p.total_quantity_on_hand}
                      </span>{" "}
                      <span className="text-xs text-gray-500">{p.dispensing_unit}s</span>
                    </td>
                    <td className="py-3 px-4 text-gray-700 font-medium">
                      {p.active_batches_count} batch(es)
                    </td>
                    <td className="py-3 px-4 text-gray-600 font-mono text-xs">
                      {p.nearest_expiry || "No active stock"}
                    </td>
                    <td className="py-3 px-4">
                      <SourceBadge kind={p.dataset_kind} />
                    </td>
                    <td className="py-3 px-4">
                      {p.is_low_stock && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 mr-2">
                          Low Stock
                        </span>
                      )}
                      {p.has_quarantine && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                          Quarantine
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Receive Stock Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-gray-200 max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="font-bold text-gray-900 text-base">Receive Inventory Stock</h3>
              <button onClick={() => setModalOpen(false)}>
                <X className="w-5 h-5 text-gray-500 hover:text-gray-800" />
              </button>
            </div>

            {formError && (
              <div className="p-2.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                {formError}
              </div>
            )}

            <form onSubmit={handleSubmitReceipt} className="space-y-3 text-xs">
              <div>
                <label className="block font-medium text-gray-700 mb-1">Select Medicine SKU</label>
                <select
                  value={selectedProductId}
                  onChange={(e) => setSelectedProductId(e.target.value)}
                  className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none"
                >
                  {medicines?.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.brand_name} ({m.source_product_code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-medium text-gray-700 mb-1">Batch Number</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. BATCH-2026-X9"
                  value={batchNo}
                  onChange={(e) => setBatchNo(e.target.value)}
                  className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Received Units</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={qty}
                    onChange={(e) => setQty(parseInt(e.target.value) || 1)}
                    className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none font-mono"
                  />
                </div>

                <div>
                  <label className="block font-medium text-gray-700 mb-1">Expiry Date</label>
                  <input
                    type="date"
                    required
                    value={expiry}
                    onChange={(e) => setExpiry(e.target.value)}
                    className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Pack MRP (Paise)</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={mrpPaise}
                    onChange={(e) => setMrpPaise(parseInt(e.target.value) || 0)}
                    className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none font-mono"
                  />
                  <span className="text-[10px] text-gray-400">₹{(mrpPaise / 100).toFixed(2)}</span>
                </div>

                <div>
                  <label className="block font-medium text-gray-700 mb-1">Selling Price (Paise)</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={sellingPaise}
                    onChange={(e) => setSellingPaise(parseInt(e.target.value) || 0)}
                    className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none font-mono"
                  />
                  <span className="text-[10px] text-gray-400">₹{(sellingPaise / 100).toFixed(2)}</span>
                </div>
              </div>

              <div className="pt-3 border-t flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-3 py-1.5 border border-gray-300 rounded text-xs text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={receiptMutation.isPending}
                  className="px-4 py-1.5 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded text-xs font-semibold shadow-sm transition"
                >
                  {receiptMutation.isPending ? "Recording..." : "Record Receipt"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
