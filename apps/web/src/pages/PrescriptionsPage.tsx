import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { PlusCircle, FileText, ArrowRight, Search } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";

interface PrescriptionItem {
  id: string;
  optional_patient_reference: string | null;
  status: string;
  revision: number;
  line_count: number;
  created_at: string;
}

export function PrescriptionsPage() {
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const { data: prescriptions, isLoading, error } = useQuery({
    queryKey: ["prescriptions-list"],
    queryFn: () => apiFetch<PrescriptionItem[]>("/api/v1/prescriptions"),
  });

  const filtered = prescriptions?.filter((rx) => {
    if (filterStatus === "all") return true;
    return rx.status.toLowerCase() === filterStatus.toLowerCase();
  });

  return (
    <div>
      <PageHeader
        title="Prescriptions"
        description="Prescription intake, digital confirmation, and formulation planning"
        action={
          <Link
            to="/app/prescriptions/new"
            className="flex items-center gap-2 px-4 py-2 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-md text-sm font-medium shadow-sm transition"
          >
            <PlusCircle className="w-4 h-4" />
            <span>New Prescription</span>
          </Link>
        }
      />

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-4 border-b border-gray-200 pb-2">
        {["all", "draft", "needs_confirmation", "confirmed", "completed"].map((st) => (
          <button
            key={st}
            onClick={() => setFilterStatus(st)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md capitalize transition ${
              filterStatus === st
                ? "bg-[#0F766E] text-white shadow-sm"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            {st.replace("_", " ")}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-sm text-gray-500 animate-pulse">
          Loading prescriptions...
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">
          Failed to load prescriptions.
        </div>
      ) : filtered && filtered.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-gray-800">No prescriptions found</h3>
          <p className="text-sm text-gray-500 mt-1 mb-4">
            Upload an image or manually enter medicine items to start dispensing.
          </p>
          <Link
            to="/app/prescriptions/new"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-md text-sm font-medium"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Create First Prescription</span>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-600 font-semibold border-b border-gray-200">
                <tr>
                  <th className="py-3 px-4">Prescription Reference</th>
                  <th className="py-3 px-4">Medicines</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Revision</th>
                  <th className="py-3 px-4">Date Created</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered?.map((rx) => {
                  const targetUrl =
                    rx.status === "confirmed" || rx.status === "completed"
                      ? `/app/prescriptions/${rx.id}/plan`
                      : `/app/prescriptions/${rx.id}/review`;

                  return (
                    <tr key={rx.id} className="hover:bg-gray-50/80 transition">
                      <td className="py-3 px-4 font-semibold text-gray-900">
                        {rx.optional_patient_reference || (
                          <span className="text-gray-400 italic">No Reference</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-gray-700">
                        {rx.line_count} line{rx.line_count === 1 ? "" : "s"}
                      </td>
                      <td className="py-3 px-4">
                        <StatusBadge status={rx.status} />
                      </td>
                      <td className="py-3 px-4 text-gray-500 font-mono text-xs">
                        v{rx.revision}
                      </td>
                      <td className="py-3 px-4 text-gray-500 text-xs">
                        {new Date(rx.created_at).toLocaleString("en-IN", {
                          dateStyle: "medium",
                          timeStyle: "short",
                        })}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link
                          to={targetUrl}
                          className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold bg-gray-100 hover:bg-[#E6F4F2] hover:text-[#0F766E] text-gray-700 rounded transition"
                        >
                          <span>{rx.status === "confirmed" ? "Open Plan" : "Review"}</span>
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
