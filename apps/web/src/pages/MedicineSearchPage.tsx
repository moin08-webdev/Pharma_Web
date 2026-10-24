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
      <div className="mb-6 max-w-md relative">
        <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by brand name, code, or manufacturer..."
          className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-[#0F766E] focus:border-[#0F766E]"
        />
      </div>

      {isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-sm text-gray-500 animate-pulse">
          Searching catalogue...
        </div>
      ) : medicines && medicines.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Pill className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-gray-800">No matching medicines found</h3>
          <p className="text-sm text-gray-500 mt-1">Try searching by brand name or source code.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-600 font-semibold border-b border-gray-200">
                <tr>
                  <th className="py-3 px-4">Brand Name</th>
                  <th className="py-3 px-4">Formulation</th>
                  <th className="py-3 px-4">Pack Size</th>
                  <th className="py-3 px-4">MRP (Pack)</th>
                  <th className="py-3 px-4">Provenance</th>
                  <th className="py-3 px-4 text-right">Candidates</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {medicines?.map((m) => (
                  <tr key={m.id} className="hover:bg-gray-50 transition">
                    <td className="py-3 px-4">
                      <div className="font-bold text-gray-900">{m.brand_name}</div>
                      <div className="text-gray-400 text-xs">{m.manufacturer} • {m.source_product_code}</div>
                    </td>
                    <td className="py-3 px-4 text-gray-700">
                      <div>{m.formulation_summary}</div>
                      <div className="text-gray-400 text-xs capitalize">
                        {m.dosage_form} • {m.route} • {m.release_type.replace("_", " ")}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-600 text-xs">
                      {m.pack_quantity} {m.dispensing_unit}s
                      {m.pack_break_allowed && <span className="ml-1 text-teal-700 font-medium">(Breakable)</span>}
                    </td>
                    <td className="py-3 px-4 font-semibold text-gray-900">
                      <Money paise={m.mrp_pack_paise} />
                    </td>
                    <td className="py-3 px-4">
                      <SourceBadge kind={m.dataset_kind} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/app/medicines/${m.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold bg-gray-100 hover:bg-[#E6F4F2] hover:text-[#0F766E] text-gray-700 rounded transition"
                      >
                        <span>Details</span>
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
