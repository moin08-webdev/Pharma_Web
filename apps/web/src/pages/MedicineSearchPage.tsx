import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Search, ArrowRight, Pill, Layers } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { SourceBadge } from "@/components/common/SourceBadge";
import { Money } from "@/components/common/Money";

export function MedicineSearchPage() {
  const [query, setQuery] = useState("");

  const { data: medicines, isLoading } = useQuery({
    queryKey: ["medicines-search", query],
    queryFn: () => apiFetch<any[]>(`/api/v1/medicines?q=${encodeURIComponent(query)}`),
  });

  return (
    <div>
      <PageHeader
        title="Medicines Catalogue"
        description="Search active medicines, reviewed active ingredients, strengths, and local availability"
      />

      {/* Search Input */}
      <div className="mb-6 max-w-lg relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by brand name, active molecule, code, or manufacturer..."
          className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-[#0F766E] focus:border-[#0F766E] bg-white shadow-2xs"
        />
      </div>

      {isLoading ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-sm text-slate-500 animate-pulse">
          Searching clinical formulary catalogue...
        </div>
      ) : medicines && medicines.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <Pill className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No matching medicines found in formulary</h3>
          <p className="text-sm text-slate-500 mt-1">Try searching by brand name, active ingredient, or source code.</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Brand & Molecule</th>
                  <th className="py-3 px-4">Formulation Identity</th>
                  <th className="py-3 px-4">Packaging Spec</th>
                  <th className="py-3 px-4">MRP (Pack)</th>
                  <th className="py-3 px-4">Provenance</th>
                  <th className="py-3 px-4 text-right">Equivalence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {medicines?.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-md bg-teal-50 border border-teal-200 text-teal-800 flex items-center justify-center text-[10px] font-serif font-bold shrink-0">
                          ℞
                        </span>
                        <div>
                          <div className="font-bold text-slate-900">{m.brand_name}</div>
                          <div className="text-slate-400 text-xs">{m.manufacturer} • {m.source_product_code}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-700">
                      <div className="font-medium text-slate-900">{m.formulation_summary}</div>
                      <div className="text-slate-400 text-xs capitalize flex items-center gap-1.5 mt-0.5">
                        <span className="px-1.5 py-0.2 bg-slate-100 rounded text-[10px] text-slate-600 font-medium">
                          {m.dosage_form}
                        </span>
                        <span>•</span>
                        <span>{m.route}</span>
                        <span>•</span>
                        <span>{m.release_type.replace("_", " ")}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-600 text-xs">
                      <div className="font-semibold text-slate-800">
                        {m.pack_quantity} {m.dispensing_unit}s
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {m.pack_break_allowed ? (
                          <span className="text-teal-700 font-medium">Blister breakable</span>
                        ) : (
                          <span>Whole pack only</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-900">
                      <Money paise={m.mrp_pack_paise} />
                    </td>
                    <td className="py-3 px-4">
                      <SourceBadge kind={m.dataset_kind} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/app/medicines/${m.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-bold bg-slate-100 hover:bg-[#E6F4F2] hover:text-[#0F766E] text-slate-700 rounded-lg transition"
                      >
                        <span>Candidates</span>
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
