import React from "react";
import { CheckCircle2, Clock, AlertTriangle, XCircle, FileText, CheckCheck } from "lucide-react";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  const norm = status.toLowerCase();
  const padding = size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-xs";

  switch (norm) {
    case "confirmed":
    case "approved":
    case "active":
      return (
        <span className={`inline-flex items-center gap-1 font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full ${padding}`}>
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span className="capitalize">{norm}</span>
        </span>
      );
    case "completed":
    case "finalized":
      return (
        <span className={`inline-flex items-center gap-1 font-medium bg-teal-50 text-teal-800 border border-teal-300 rounded-full ${padding}`}>
          <CheckCheck className="w-3.5 h-3.5" />
          <span className="capitalize">{norm}</span>
        </span>
      );
    case "pending_review":
    case "needs_confirmation":
    case "extracting":
      return (
        <span className={`inline-flex items-center gap-1 font-medium bg-amber-50 text-amber-800 border border-amber-300 rounded-full ${padding}`}>
          <Clock className="w-3.5 h-3.5" />
          <span className="capitalize">{norm.replace("_", " ")}</span>
        </span>
      );
    case "draft":
      return (
        <span className={`inline-flex items-center gap-1 font-medium bg-slate-100 text-slate-700 border border-slate-300 rounded-full ${padding}`}>
          <FileText className="w-3.5 h-3.5" />
          <span className="capitalize">{norm}</span>
        </span>
      );
    case "quarantine":
    case "expired":
    case "rejected":
    case "cancelled":
    case "superseded":
      return (
        <span className={`inline-flex items-center gap-1 font-medium bg-rose-50 text-rose-700 border border-rose-200 rounded-full ${padding}`}>
          <XCircle className="w-3.5 h-3.5" />
          <span className="capitalize">{norm}</span>
        </span>
      );
    default:
      return (
        <span className={`inline-flex items-center gap-1 font-medium bg-gray-100 text-gray-700 border border-gray-300 rounded-full ${padding}`}>
          <span>{status}</span>
        </span>
      );
  }
}
