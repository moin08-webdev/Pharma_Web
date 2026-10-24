import React from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  TrendingDown,
  Layers,
  Sparkles,
  FileText,
  Clock,
  Package,
} from "lucide-react";
import { useSession } from "@/features/auth/hooks";
import { AppLogo } from "@/components/common/AppLogo";

export function LandingPage() {
  const { data: session } = useSession();

  return (
    <div className="min-h-screen bg-[#F6F8F9] flex flex-col justify-between">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <AppLogo size="md" showTagline={true} />

          <div className="flex items-center gap-3">
            {session ? (
              <Link
                to="/app"
                className="px-4 py-2 text-sm font-bold bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-lg shadow-sm transition flex items-center gap-1.5"
              >
                <span>Go to Workspace</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 text-sm font-bold bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-lg shadow-sm transition"
              >
                Sign In to Workspace
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-4 py-12 text-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 text-xs font-bold bg-teal-50 text-[#0F766E] border border-teal-200 rounded-full mb-6">
          <Sparkles className="w-3.5 h-3.5 text-teal-600" />
          <span>SHARKFORGE 2026 • AI Pharmacy Workspace</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight leading-tight">
          AI Help for Everyday Pharmacy Work
        </h1>

        <p className="mt-3 text-lg sm:text-xl text-teal-800 font-semibold max-w-2xl mx-auto">
          Helps pharmacists check medicines, compare costs, and manage stock.
        </p>

        <p className="mt-2 text-sm text-gray-600 max-w-xl mx-auto leading-relaxed">
          From prescription intake to formulation matching, transparent whole-pack patient savings, and FEFO inventory deduction.
        </p>

        <div className="mt-8 flex justify-center gap-4">
          <Link
            to={session ? "/app" : "/login"}
            className="flex items-center gap-2 px-6 py-3.5 text-base font-bold bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-xl shadow-md transition"
          >
            <span>Open Pharmacy Workspace</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        {/* 6-Step Visual Workflow Banner (from PPT Slide 03) */}
        <div className="mt-16 text-left">
          <div className="text-center mb-6">
            <span className="text-xs font-bold text-teal-800 uppercase tracking-wider bg-teal-50 px-3 py-1 rounded-full border border-teal-200">
              How the App Works
            </span>
            <h2 className="text-2xl font-bold text-gray-900 mt-2">
              Six Simple Steps from Prescription to Order
            </h2>
            <p className="text-xs text-gray-500 mt-1">
              AI reads the text. Pharmacists review and approve before moving ahead.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
            {[
              { num: "01", title: "Add Prescription", desc: "Upload a file or type the details." },
              { num: "02", title: "Check the Details", desc: "Confirm unclear names or strengths." },
              { num: "03", title: "Compare Options", desc: "See stock and full-pack prices." },
              { num: "04", title: "Pharmacist Approval", desc: "Review and approve the plan." },
              { num: "05", title: "Complete Order", desc: "Save order and update stock." },
              { num: "06", title: "Keep a Record", desc: "Save receipt & stock changes." },
            ].map((st) => (
              <div key={st.num} className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="text-xs font-extrabold text-[#0F766E] font-mono mb-1">{st.num}</div>
                  <h3 className="font-bold text-sm text-gray-900 leading-snug">{st.title}</h3>
                </div>
                <p className="text-xs text-gray-500 mt-2 leading-relaxed">{st.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 2 Showcase Highlights: Pack Savings & FEFO Expiry (from PPT Slides 05 & 06) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12 text-left">
          {/* Highlight 1: What the patient pays */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 flex items-center gap-1">
                  <TrendingDown className="w-3.5 h-3.5 text-emerald-700" />
                  <span>What the Patient Pays</span>
                </span>
                <span className="text-xs font-extrabold text-emerald-700 font-mono">
                  33.33% Less to Pay
                </span>
              </div>
              <h3 className="text-base font-bold text-gray-900">
                Transparent Whole-Pack Economics
              </h3>
              <p className="text-xs text-gray-600 mt-1">
                Sample prices for 15 tablets. Only full packs can be sold.
              </p>

              <div className="mt-4 grid grid-cols-2 gap-3">
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-200 text-xs">
                  <div className="text-gray-500 font-medium">Brand A Prescribed</div>
                  <div className="font-bold text-gray-900 text-sm mt-0.5">₹30 in total</div>
                  <div className="text-gray-500 mt-1">1 pack of 15 tablets</div>
                </div>
                <div className="p-3 bg-teal-50/60 rounded-xl border border-teal-200 text-xs">
                  <div className="text-teal-800 font-bold">Option B Generic</div>
                  <div className="font-bold text-teal-900 text-sm mt-0.5">₹20 in total</div>
                  <div className="text-emerald-700 font-semibold mt-1">₹10 saved • 5 extra tabs</div>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-gray-100 text-[11px] text-gray-500 flex items-center justify-between">
              <span>Exact Decimal paise arithmetic (zero drift)</span>
              <strong className="text-teal-800">No hidden pill math</strong>
            </div>
          </div>

          {/* Highlight 2: Using stock before it expires */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-teal-800 bg-teal-50 px-2.5 py-1 rounded-full border border-teal-200 flex items-center gap-1">
                  <Layers className="w-3.5 h-3.5 text-teal-700" />
                  <span>FEFO Inventory Engine</span>
                </span>
                <span className="text-xs font-semibold text-gray-500">
                  Earliest Expiry First
                </span>
              </div>
              <h3 className="text-base font-bold text-gray-900">
                Using Stock Before It Expires
              </h3>
              <p className="text-xs text-gray-600 mt-1">
                Batches are allocated in order of earliest valid expiration date.
              </p>

              <div className="mt-4 space-y-2 text-xs">
                <div className="flex items-center justify-between p-2 rounded-lg bg-red-50/70 border border-red-100 text-red-900">
                  <span className="font-semibold">Batch A (Expired)</span>
                  <span className="text-red-700 font-bold">BLOCKED from dispensing</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900">
                  <span className="font-bold">Batch B (Expires first)</span>
                  <span className="font-bold text-emerald-800">Prioritized for order</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-gray-50 border border-gray-200 text-gray-700">
                  <span>Batch C (Expires later)</span>
                  <span className="text-gray-500">Reserved for future</span>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-gray-100 text-[11px] text-gray-500 flex items-center justify-between">
              <span>PostgreSQL row locks (`SELECT ... FOR UPDATE`)</span>
              <strong className="text-teal-800">Double-dispense protected</strong>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6 text-center text-xs text-gray-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <AppLogo size="sm" showTagline={false} />
          <div>AI-assisted prescription fulfilment workspace for Indian pharmacies.</div>
          <div className="text-gray-400">Production-Grade Release v1.0 MVP</div>
        </div>
      </footer>
    </div>
  );
}
