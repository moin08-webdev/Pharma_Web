import React from "react";
import { ShieldCheck, Layers } from "lucide-react";

export function SourceBadge({ kind }: { kind: "DEMO" | "VERIFIED" | string }) {
  if (kind === "DEMO") {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200 rounded">
        <Layers className="w-3 h-3 text-slate-500" />
        DEMO
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 rounded">
      <ShieldCheck className="w-3 h-3" />
      VERIFIED
    </span>
  );
}
