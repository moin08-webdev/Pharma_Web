import React from "react";
import { Check, Upload, CheckCircle2, TrendingUp, ShieldCheck, ShoppingBag, Receipt } from "lucide-react";

export interface WorkflowStepperProps {
  currentStep: 1 | 2 | 3 | 4 | 5 | 6;
  className?: string;
}

const STEPS = [
  { step: 1, title: "Add Prescription", subtitle: "Upload or type details", icon: Upload },
  { step: 2, title: "Check Details", subtitle: "Confirm names & strengths", icon: CheckCircle2 },
  { step: 3, title: "Compare Options", subtitle: "Stock & full-pack prices", icon: TrendingUp },
  { step: 4, title: "Pharmacist Approval", subtitle: "Review & approve plan", icon: ShieldCheck },
  { step: 5, title: "Complete Order", subtitle: "Save order & update stock", icon: ShoppingBag },
  { step: 6, title: "Keep a Record", subtitle: "Receipt & stock ledger", icon: Receipt },
];

export function WorkflowStepper({ currentStep, className = "" }: WorkflowStepperProps) {
  return (
    <div className={`bg-white border border-gray-200 rounded-xl p-4 shadow-sm mb-6 ${className}`}>
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
            6-Step Pharmacy Workflow
          </span>
          <span className="text-xs text-gray-500">
            Step {currentStep} of 6: <strong>{STEPS[currentStep - 1].title}</strong>
          </span>
        </div>
        <span className="text-xs text-gray-400 font-medium hidden sm:inline">
          {STEPS[currentStep - 1].subtitle}
        </span>
      </div>

      {/* Stepper Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {STEPS.map((s) => {
          const isDone = s.step < currentStep;
          const isCurrent = s.step === currentStep;
          const Icon = s.icon;

          return (
            <div
              key={s.step}
              className={`flex items-center gap-2 p-2 rounded-lg text-xs transition border ${
                isCurrent
                  ? "bg-teal-50/80 border-teal-300 text-teal-900 font-semibold shadow-xs"
                  : isDone
                  ? "bg-emerald-50/40 border-emerald-200 text-emerald-800"
                  : "bg-gray-50/60 border-gray-100 text-gray-400"
              }`}
            >
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 text-[11px] font-bold ${
                  isCurrent
                    ? "bg-[#0F766E] text-white"
                    : isDone
                    ? "bg-emerald-600 text-white"
                    : "bg-gray-200 text-gray-500"
                }`}
              >
                {isDone ? <Check className="w-3.5 h-3.5" /> : s.step}
              </div>
              <div className="min-w-0 flex-1 truncate">
                <div className="truncate font-medium">{s.title}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
