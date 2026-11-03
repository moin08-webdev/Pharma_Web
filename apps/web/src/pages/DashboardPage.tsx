import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  FileText,
  ClipboardCheck,
  ShoppingBag,
  AlertTriangle,
  ArrowRight,
  PlusCircle,
  PackageCheck,
  Search,
  Layers,
  ShieldCheck,
  CheckCircle2,
  Stethoscope,
  Pill,
  Activity,
  AlertCircle,
  Clock,
  Scale,
  FlaskConical,
  Package,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";

interface DashboardStats {
  pending_prescriptions_count: number;
  pending_approvals_count: number;
  completed_orders_today_count: number;
  low_stock_alerts_count: number;
  expiring_soon_alerts_count: number;
  action_queue: Array<{
    id: string;
    type: string;
    title: string;
    description: string;
    href: string;
    created_at: string;
  }>;
}

export function DashboardPage() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () => apiFetch<DashboardStats>("/api/v1/dashboard"),
    refetchInterval: 10000,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Pharmacy Dashboard"
        description="Prescription fulfilment operations, pending clinical reviews, and dispensary inventory health"
        action={
          <div className="flex items-center gap-2">
            <Link
              to="/app/prescriptions/new"
              className="flex items-center gap-1.5 px-3.5 py-2 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-lg text-xs font-bold shadow-xs transition"
            >
              <PlusCircle className="w-4 h-4" />
              <span>+ New Prescription</span>
            </Link>
          </div>
        }
      />

      {/* Clinical Dispensary Live Status Header */}
      <div className="bg-slate-900 text-white rounded-xl p-3.5 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-slate-800 rounded-lg border border-slate-700">
            <Stethoscope className="w-4 h-4 text-teal-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-xs tracking-tight">Active Clinical Dispensing Station</span>
              <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 bg-emerald-950 text-emerald-400 rounded border border-emerald-800">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                ONLINE
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Indian Pharmacopoeia (IP) formulation equivalence rules & Schedule H/H1 clinical audit enforcement active.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-[11px] text-slate-300 shrink-0 font-medium">
          <span className="px-2.5 py-1 bg-slate-800 rounded-md border border-slate-700 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-400" />
            <span>R.Ph. Gate Enforced</span>
          </span>
          <span className="px-2.5 py-1 bg-slate-800 rounded-md border border-slate-700 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-teal-400" />
            <span>FEFO Stock Rotation</span>
          </span>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-200 rounded-xl" />
          ))}
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200 text-sm">
          Failed to load dashboard statistics.
        </div>
      ) : stats ? (
        <>
          {/* Key Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link
              to="/app/prescriptions"
              className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs hover:border-teal-400 hover:shadow-sm transition group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Pending Prescriptions
                </span>
                <div className="p-2.5 bg-amber-50 text-amber-700 rounded-xl group-hover:scale-105 transition">
                  <FileText className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-slate-900">
                {stats.pending_prescriptions_count}
              </div>
              <p className="mt-1 text-xs text-slate-500 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-amber-600" />
                <span>Drafts awaiting line confirmation</span>
              </p>
            </Link>

            <Link
              to="/app/approvals"
              className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs hover:border-teal-400 hover:shadow-sm transition group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Pending Approvals
                </span>
                <div className="p-2.5 bg-teal-50 text-[#0F766E] rounded-xl group-hover:scale-105 transition">
                  <ClipboardCheck className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-slate-900">
                {stats.pending_approvals_count}
              </div>
              <p className="mt-1 text-xs text-slate-500 flex items-center gap-1.5">
                <Stethoscope className="w-3.5 h-3.5 text-teal-600" />
                <span>Pharmacist sign-off required</span>
              </p>
            </Link>

            <Link
              to="/app/orders"
              className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs hover:border-teal-400 hover:shadow-sm transition group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Dispensed Today
                </span>
                <div className="p-2.5 bg-emerald-50 text-emerald-700 rounded-xl group-hover:scale-105 transition">
                  <ShoppingBag className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-slate-900">
                {stats.completed_orders_today_count}
              </div>
              <p className="mt-1 text-xs text-slate-500 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Completed order transactions</span>
              </p>
            </Link>

            <Link
              to="/app/inventory"
              className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs hover:border-teal-400 hover:shadow-sm transition group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Stock Expiry Alerts
                </span>
                <div className="p-2.5 bg-rose-50 text-rose-700 rounded-xl group-hover:scale-105 transition">
                  <AlertTriangle className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-slate-900">
                {stats.low_stock_alerts_count}
              </div>
              <p className="mt-1 text-xs text-slate-500 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                <span>{stats.expiring_soon_alerts_count} batch(es) nearing expiry (FEFO)</span>
              </p>
            </Link>
          </div>

          {/* Primary Viewport Focus: Immediate Action Queue & Quick Nav */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
              <h2 className="text-sm font-bold text-slate-900 mb-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ClipboardCheck className="w-4 h-4 text-teal-700" />
                  <span>Immediate Action Queue</span>
                </div>
                <span className="text-xs font-normal text-slate-400">Live dispensary feed</span>
              </h2>

              {stats.action_queue.length === 0 ? (
                <div className="p-8 text-center border-2 border-dashed border-slate-200 rounded-xl">
                  <PackageCheck className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-slate-900">All prescription queues are clear!</p>
                  <p className="text-xs text-slate-500 mt-1">
                    No prescriptions or fulfilment plans currently pending review. Click "+ New Prescription" above to begin.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {stats.action_queue.map((act) => (
                    <div key={act.id} className="py-3 flex items-center justify-between gap-4">
                      <div>
                        <h4 className="text-xs font-bold text-slate-900">{act.title}</h4>
                        <p className="text-xs text-slate-600 mt-0.5">{act.description}</p>
                      </div>
                      <Link
                        to={act.href}
                        className="flex items-center gap-1 text-xs font-bold text-[#0F766E] hover:underline shrink-0 px-2.5 py-1 bg-teal-50 rounded-lg border border-teal-200"
                      >
                        <span>Review</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Actions Panel */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-teal-700" />
                  <span>Quick Navigation</span>
                </h3>
                <div className="space-y-2.5">
                  <Link
                    to="/app/prescriptions/new"
                    className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-teal-50 hover:border-teal-300 transition text-xs font-semibold text-slate-800"
                  >
                    <span>Create Prescription Draft</span>
                    <PlusCircle className="w-4 h-4 text-[#0F766E]" />
                  </Link>

                  <Link
                    to="/app/medicines"
                    className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-teal-50 hover:border-teal-300 transition text-xs font-semibold text-slate-800"
                  >
                    <span>Drug Formulary Catalogue</span>
                    <Search className="w-4 h-4 text-slate-600" />
                  </Link>

                  <Link
                    to="/app/inventory"
                    className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-teal-50 hover:border-teal-300 transition text-xs font-semibold text-slate-800"
                  >
                    <span>Inventory & FEFO Batches</span>
                    <ArrowRight className="w-4 h-4 text-slate-600" />
                  </Link>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
                Logged in as <strong>Registered Pharmacist / Staff</strong> • Scoped strictly to active dispensary.
              </div>
            </div>
          </div>

          {/* Clinical Reference Standards: Formulation Verification & FEFO Stock Rotation */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Guide 1: Formulation Verification Standards */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <span className="text-xs font-bold text-teal-900 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-teal-700" />
                  <span>Medicine Formulation Verification</span>
                </span>
                <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Must match 100%
                </span>
              </div>
              <p className="text-xs text-slate-600">
                Details must strictly match before candidate formulation comparison:
              </p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100 text-slate-700 flex items-center gap-2">
                  <FlaskConical className="w-3.5 h-3.5 text-teal-700 shrink-0" />
                  <span><strong>Active ingredient & salt</strong></span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100 text-slate-700 flex items-center gap-2">
                  <Scale className="w-3.5 h-3.5 text-teal-700 shrink-0" />
                  <span><strong>Strength (e.g. 500 mg)</strong></span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100 text-slate-700 flex items-center gap-2">
                  <Pill className="w-3.5 h-3.5 text-teal-700 shrink-0" />
                  <span><strong>Form (tablet, liquid)</strong></span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100 text-slate-700 flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5 text-teal-700 shrink-0" />
                  <span><strong>Release speed (IR vs ER)</strong></span>
                </div>
              </div>
              <div className="p-3 bg-amber-50/80 rounded-xl border border-amber-200 text-[11px] text-amber-900 leading-relaxed flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <strong>Safety Pause Enforced:</strong> Dose mismatches (500mg vs 650mg), release kinetic variations (Fast IR vs Sustained ER), or missing active combination salts (A+B vs A) are automatically rejected.
                </div>
              </div>
            </div>

            {/* Guide 2: Inventory Dispensing Priority (FEFO) */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <span className="text-xs font-bold text-teal-900 flex items-center gap-1.5">
                  <Layers className="w-4 h-4 text-teal-700" />
                  <span>Inventory Dispensing Priority (FEFO)</span>
                </span>
                <span className="text-[11px] font-bold text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
                  Earliest Expiry First
                </span>
              </div>
              <p className="text-xs text-slate-600">
                Automated FEFO inventory priority ensures older shelf stock is dispensed first:
              </p>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-2 rounded-lg bg-red-50/70 border border-red-200 text-red-900 text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-600"></span>
                    <span><strong>Batch A</strong> (Expired or Quarantined)</span>
                  </div>
                  <strong className="text-red-700 uppercase tracking-wider text-[10px]">BLOCKED: Cannot dispense</strong>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-emerald-50 border border-emerald-300 text-emerald-900 text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-600"></span>
                    <span><strong>Batch B</strong> (Earliest valid expiry)</span>
                  </div>
                  <strong className="text-emerald-800 uppercase tracking-wider text-[10px]">PRIORITIZED: Dispensed first</strong>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-slate-400"></span>
                    <span><strong>Batch C</strong> (Later expiry date)</span>
                  </div>
                  <span className="text-slate-500">Reserved for subsequent orders</span>
                </div>
              </div>
            </div>
          </div>

          {/* 6-Step Clinical Dispensing Workflow Overview */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
            <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2">
              <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-teal-600" />
                <span>Dispensary Protocol • 6 Steps from Prescription to Order</span>
              </span>
              <span className="text-xs text-slate-400">Digital intake • Registered pharmacist verification & approval required</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              {[
                { num: "01", title: "Add Prescription", desc: "Upload file or type details", icon: FileText },
                { num: "02", title: "Check Details", desc: "Confirm unclear names & strength", icon: Stethoscope },
                { num: "03", title: "Compare Options", desc: "See stock & full-pack prices", icon: Pill },
                { num: "04", title: "Pharmacist Approval", desc: "Review & approve plan", icon: ShieldCheck },
                { num: "05", title: "Complete Order", desc: "Save order & update stock", icon: Package },
                { num: "06", title: "Keep a Record", desc: "Save receipt & stock changes", icon: ShoppingBag },
              ].map((st) => {
                const IconComponent = st.icon;
                return (
                  <div key={st.num} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs hover:border-teal-300 transition">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-teal-700 text-[11px]">{st.num}</span>
                      <IconComponent className="w-3.5 h-3.5 text-teal-700" />
                    </div>
                    <div className="font-semibold text-slate-900 mt-1 truncate">{st.title}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5 line-clamp-1">{st.desc}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
