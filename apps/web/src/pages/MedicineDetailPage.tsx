import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Pill, ShieldCheck, AlertCircle, Package } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { SourceBadge } from "@/components/common/SourceBadge";
import { Money } from "@/components/common/Money";

export function MedicineDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: product, isLoading, error } = useQuery({
    queryKey: ["medicine-detail", id],
    queryFn: () => apiFetch<any>(`/api/v1/medicines/${id}`),
    enabled: !!id,
  });

  const { data: candidates } = useQuery({
    queryKey: ["medicine-candidates", id],
    queryFn: () => apiFetch<any>(`/api/v1/medicines/${id}/candidates`),
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500 animate-pulse">Loading medicine details...</div>;
  }

  if (error || !product) {
    return <div className="p-4 bg-red-50 text-red-700 rounded-lg">Medicine record not found.</div>;
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <Link
        to="/app/medicines"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Catalogue</span>
      </Link>

      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-gray-200 gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{product.brand_name}</h1>
              <SourceBadge kind={product.dataset_kind} />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Manufacturer: {product.manufacturer} • Code: {product.source_product_code}
            </p>
          </div>

          <div className="flex items-center gap-4 bg-gray-50 px-4 py-2.5 rounded-lg border">
            <div>
              <div className="text-[11px] font-semibold text-gray-500 uppercase">Available Stock</div>
              <div className="text-lg font-extrabold text-teal-800 font-mono">
                {product.stock_available} {product.dispensing_unit}s
              </div>
            </div>
          </div>
        </div>

        {/* Formulation Details */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            Canonical Formulation Identity
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 space-y-3">
            <div className="grid grid-cols-3 gap-4 text-xs">
              <div>
                <span className="text-gray-500">Dosage Form: </span>
                <strong className="text-gray-900 capitalize">{product.formulation.dosage_form}</strong>
              </div>
              <div>
                <span className="text-gray-500">Route: </span>
                <strong className="text-gray-900 capitalize">{product.formulation.route}</strong>
              </div>
              <div>
                <span className="text-gray-500">Release Type: </span>
                <strong className="text-gray-900 capitalize">
                  {product.formulation.release_type.replace("_", " ")}
                </strong>
              </div>
            </div>

            <div className="pt-2 border-t border-gray-200">
              <div className="text-xs font-semibold text-gray-700 mb-1">Active Ingredient Components:</div>
              <ul className="list-disc pl-5 text-xs text-gray-600 space-y-1">
                {product.formulation.components.map((c: any, idx: number) => (
                  <li key={idx}>
                    <strong>{c.ingredient}</strong> — {c.strength} {c.unit} ({c.release})
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Eligible Candidates Comparison */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            Strict Formulation Candidates ({candidates?.eligible_candidates?.length || 0})
          </h3>

          {!candidates || candidates.eligible_candidates.length === 0 ? (
            <div className="p-4 bg-gray-50 rounded-lg text-xs text-gray-500 border text-center">
              No alternate formulations strictly match this product's canonical signature.
            </div>
          ) : (
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="w-full text-xs text-left">
                <thead className="bg-gray-50 text-gray-600 font-semibold border-b">
                  <tr>
                    <th className="py-2.5 px-4">Candidate Brand</th>
                    <th className="py-2.5 px-4">Manufacturer</th>
                    <th className="py-2.5 px-4">Pack MRP</th>
                    <th className="py-2.5 px-4">Local Stock</th>
                    <th className="py-2.5 px-4">Match Outcome</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {candidates.eligible_candidates.map((cand: any) => (
                    <tr key={cand.product_id} className="hover:bg-gray-50">
                      <td className="py-3 px-4 font-bold text-gray-900">
                        {cand.brand_name}
                      </td>
                      <td className="py-3 px-4 text-gray-600">{cand.manufacturer}</td>
                      <td className="py-3 px-4 font-semibold text-gray-800">
                        <Money paise={cand.pack_price_paise} />
                      </td>
                      <td className="py-3 px-4 text-teal-700 font-semibold font-mono">
                        {cand.available_stock_units} units
                      </td>
                      <td className="py-3 px-4 text-emerald-700 font-medium">
                        {cand.match_reason}
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
}
