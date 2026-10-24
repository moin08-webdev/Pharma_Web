import React from "react";
import { Sparkles, ShieldCheck } from "lucide-react";

export function SourceBadge({ kind }: { kind: "DEMO" | "VERIFIED" | string }) {
  if (kind === "DEMO") {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold bg-purple-50 text-purple-700 border border-purple-200 rounded">
        <Sparkles className="w-3 h-3" />
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
