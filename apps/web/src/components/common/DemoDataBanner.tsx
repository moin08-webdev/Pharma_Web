import React from "react";
import { AlertCircle } from "lucide-react";

export function DemoDataBanner() {
  return (
    <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-xs text-amber-900 flex items-center justify-between">
      <div className="flex items-center gap-2 max-w-5xl mx-auto w-full">
        <AlertCircle className="w-4 h-4 text-amber-700 shrink-0" />
        <span>
          <strong>DEMONSTRATION WORKSPACE:</strong> Medicines, formulations, stock, and prices are synthetic demonstration fixtures and do not represent actual commercial or clinical recommendations.
        </span>
      </div>
    </div>
  );
}
