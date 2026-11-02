import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Pill, ShieldCheck, AlertCircle, Package, CheckCircle2 } from "lucide-react";
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

      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6 rx-watermark">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between pb-6 border-b border-slate-200 gap-4">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-800 text-2xl font-serif font-black shrink-0">
              ℞
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-slate-900">{product.brand_name}</h1>
                <SourceBadge kind={product.dataset_kind} />
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Manufacturer: {product.manufacturer} • Source Code: {product.source_product_code} • Indian Pharmacopoeia
              </p>
              <div className="flex items-center gap-2 mt-2 text-[11px] text-teal-800 font-semibold">
                <span className="px-2 py-0.5 bg-teal-50 rounded border border-teal-200">Schedule H Prescription Drug</span>
                <span className="px-2 py-0.5 bg-slate-100 rounded border border-slate-200 text-slate-600">Store Below 25°C</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 bg-slate-50 px-4 py-3 rounded-xl border border-slate-200">
            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Available Shelf Stock</div>
              <div className="text-lg font-extrabold text-teal-900 font-mono">
                {product.stock_available} {product.dispensing_unit}s
              </div>
            </div>
          </div>
        </div>

        {/* Formulation Details */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-teal-700" />
            <span>Canonical Pharmacological Formulation Identity</span>
          </h3>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-2.5 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-500 text-[11px]">Pharmaceutical Dosage Form: </span>
                <div className="text-slate-900 font-bold capitalize mt-0.5">{product.formulation.dosage_form}</div>
              </div>
              <div className="p-2.5 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-500 text-[11px]">Administration Route: </span>
                <div className="text-slate-900 font-bold capitalize mt-0.5">{product.formulation.route}</div>
              </div>
              <div className="p-2.5 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-500 text-[11px]">Release Kinetic Profile: </span>
                <div className="text-slate-900 font-bold capitalize mt-0.5">
                  {product.formulation.release_type.replace("_", " ")}
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-200">
              <div className="text-xs font-semibold text-slate-700 mb-1.5">Active Molecule Chemical Composition:</div>
              <ul className="list-disc pl-5 text-xs text-slate-600 space-y-1">
                {product.formulation.components.map((c: any, idx: number) => (
                  <li key={idx}>
                    <strong className="text-slate-900">{c.ingredient}</strong> — {c.strength} {c.unit} ({c.release})
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Eligible Candidates Comparison */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center justify-between">
            <span>Bio-Equivalent Generic Candidates ({candidates?.eligible_candidates?.length || 0})</span>
            <span className="text-[11px] text-teal-800 font-normal">Identical active ingredient & strength</span>
          </h3>

          {!candidates || candidates.eligible_candidates.length === 0 ? (
            <div className="p-4 bg-slate-50 rounded-xl text-xs text-slate-500 border border-slate-200 text-center">
              No alternate generic formulations strictly match this product's canonical signature in local inventory.
            </div>
          ) : (
            <div className="border border-slate-200 rounded-xl overflow-hidden shadow-2xs">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-4">Candidate Brand</th>
                    <th className="py-2.5 px-4">Manufacturer</th>
                    <th className="py-2.5 px-4">Pack MRP</th>
                    <th className="py-2.5 px-4">Local Stock</th>
                    <th className="py-2.5 px-4">Equivalence Outcome</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {candidates.eligible_candidates.map((cand: any) => (
                    <tr key={cand.product_id} className="hover:bg-slate-50/70">
                      <td className="py-3 px-4 font-bold text-slate-900">
                        {cand.brand_name}
                      </td>
                      <td className="py-3 px-4 text-slate-600">{cand.manufacturer}</td>
                      <td className="py-3 px-4 font-semibold text-slate-800">
                        <Money paise={cand.pack_price_paise} />
                      </td>
                      <td className="py-3 px-4 text-teal-800 font-semibold font-mono">
                        {cand.available_stock_units} units
                      </td>
                      <td className="py-3 px-4 text-emerald-800 font-semibold flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                        <span>{cand.match_reason}</span>
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
