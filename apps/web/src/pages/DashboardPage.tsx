import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
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
  Sparkles,
  Layers,
  TrendingDown,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { loadDemoSamplePrescription } from "@/lib/demo-helper";

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
  const navigate = useNavigate();
  const [loadingDemo, setLoadingDemo] = useState(false);

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () => apiFetch<DashboardStats>("/api/v1/dashboard"),
    refetchInterval: 10000,
  });

  const handleStartDemo = async () => {
    setLoadingDemo(true);
    try {
      await loadDemoSamplePrescription(navigate);
    } catch (err) {
      console.error("Failed to load demo scenario:", err);
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Pharmacy Dashboard"
        description="Prescription fulfilment operations, pending reviews, and inventory health"
        action={
          <div className="flex items-center gap-2">
            <button
              onClick={handleStartDemo}
              disabled={loadingDemo}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-purple-700 hover:bg-purple-800 text-white rounded-lg text-xs font-bold shadow-sm transition disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4 text-purple-200" />
              <span>{loadingDemo ? "Loading Demo..." : "Start 5-Minute Demo Flow"}</span>
            </button>
            <Link
              to="/app/prescriptions/new"
              className="flex items-center gap-1.5 px-3.5 py-2 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-lg text-xs font-bold shadow-sm transition"
            >
              <PlusCircle className="w-4 h-4" />
              <span>+ New Prescription</span>
            </Link>
          </div>
        }
      />

      {/* 5-Minute Demo Walkthrough Card (from PPT Slide 10) */}
      <div className="p-5 bg-gradient-to-r from-purple-50 via-teal-50 to-emerald-50 border border-purple-200 rounded-2xl shadow-xs">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold uppercase tracking-wider text-purple-800 bg-purple-100 px-2.5 py-0.5 rounded-full border border-purple-200">
                Mentor & Evaluator Walkthrough
              </span>
              <span className="text-xs font-semibold text-purple-900">Five-Minute Quick Demo</span>
            </div>
            <p className="text-xs text-gray-700 max-w-2xl leading-relaxed">
              Experience the complete flow in 4 simple clicks:
              <strong> 01 Open sample prescription</strong> → <strong>02 Confirm unclear medicine</strong> → <strong>03 Compare ₹30 with ₹20 (33.33% savings)</strong> → <strong>04 Approve & check stock</strong>.
            </p>
          </div>

          <button
            onClick={handleStartDemo}
            disabled={loadingDemo}
            className="shrink-0 flex items-center gap-2 px-5 py-2.5 bg-purple-700 hover:bg-purple-800 text-white rounded-xl text-sm font-bold shadow-sm transition disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>{loadingDemo ? "Starting..." : "Launch Demo Now"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 6-Step Workflow Navigation Banner (from PPT Slide 03) */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-xs">
        <div className="flex items-center justify-between mb-3 border-b border-gray-100 pb-2">
          <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">
            How the App Works • 6 Steps from Prescription to Order
          </span>
          <span className="text-xs text-gray-400">AI reads text • Staff check it before moving ahead</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          {[
            { num: "01", title: "Add Prescription", desc: "Upload file or type details" },
            { num: "02", title: "Check Details", desc: "Confirm unclear names & strength" },
            { num: "03", title: "Compare Options", desc: "See stock & full-pack prices" },
            { num: "04", title: "Pharmacist Approval", desc: "Review & approve plan" },
            { num: "05", title: "Complete Order", desc: "Save order & update stock" },
            { num: "06", title: "Keep a Record", desc: "Save receipt & stock changes" },
          ].map((st) => (
            <div key={st.num} className="p-2.5 rounded-lg bg-gray-50/70 border border-gray-100 text-xs">
              <div className="font-mono font-bold text-teal-700 text-[11px]">{st.num}</div>
              <div className="font-semibold text-gray-900 mt-0.5 truncate">{st.title}</div>
              <div className="text-[10px] text-gray-500 mt-0.5 line-clamp-1">{st.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-gray-200 rounded-xl" />
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
              className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs hover:border-teal-400 transition"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Pending Prescriptions
                </span>
                <div className="p-2 bg-amber-50 text-amber-700 rounded-lg">
                  <FileText className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-gray-900">
                {stats.pending_prescriptions_count}
              </div>
              <p className="mt-1 text-xs text-gray-500">Drafts awaiting line confirmation</p>
            </Link>

            <Link
              to="/app/approvals"
              className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs hover:border-teal-400 transition"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Pending Approvals
                </span>
                <div className="p-2 bg-teal-50 text-[#0F766E] rounded-lg">
                  <ClipboardCheck className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-gray-900">
                {stats.pending_approvals_count}
              </div>
              <p className="mt-1 text-xs text-gray-500">Pharmacist sign-off required</p>
            </Link>

            <Link
              to="/app/orders"
              className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs hover:border-teal-400 transition"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Dispensed Today
                </span>
                <div className="p-2 bg-emerald-50 text-emerald-700 rounded-lg">
                  <ShoppingBag className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-gray-900">
                {stats.completed_orders_today_count}
              </div>
              <p className="mt-1 text-xs text-gray-500">Completed order transactions</p>
            </Link>

            <Link
              to="/app/inventory"
              className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs hover:border-teal-400 transition"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Stock Expiry Alerts
                </span>
                <div className="p-2 bg-rose-50 text-rose-700 rounded-lg">
                  <AlertTriangle className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-2 text-3xl font-extrabold text-gray-900">
                {stats.low_stock_alerts_count}
              </div>
              <p className="mt-1 text-xs text-gray-500">
                {stats.expiring_soon_alerts_count} batch(es) nearing expiry (FEFO)
              </p>
            </Link>
          </div>

          {/* PPT Reference Guides: How we check a medicine & FEFO Stock */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Guide 1: How we check a medicine (from Slide 04) */}
            <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-3">
              <div className="flex items-center justify-between border-b pb-2">
                <span className="text-xs font-bold text-teal-900 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-teal-700" />
                  <span>How We Check a Medicine (Slide 04 Rules)</span>
                </span>
                <span className="text-[11px] text-gray-500">Must match 100%</span>
              </div>
              <p className="text-xs text-gray-600">
                Details must match before comparing prices:
              </p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 bg-gray-50 rounded border text-gray-700">
                  <strong>• Active ingredient & salt</strong>
                </div>
                <div className="p-2 bg-gray-50 rounded border text-gray-700">
                  <strong>• Strength (e.g. 500 mg)</strong>
                </div>
                <div className="p-2 bg-gray-50 rounded border text-gray-700">
                  <strong>• Form (tablet, liquid)</strong>
                </div>
                <div className="p-2 bg-gray-50 rounded border text-gray-700">
                  <strong>• Release speed (IR vs ER)</strong>
                </div>
              </div>
              <div className="p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-[11px] text-amber-900">
                <strong>Safety pause:</strong> 500mg vs 650mg, Fast vs slow release, or A+B vs A are automatically rejected.
              </div>
            </div>

            {/* Guide 2: Using stock before it expires (from Slide 06) */}
            <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-3">
              <div className="flex items-center justify-between border-b pb-2">
                <span className="text-xs font-bold text-teal-900 flex items-center gap-1.5">
                  <Layers className="w-4 h-4 text-teal-700" />
                  <span>Using Stock Before It Expires (Slide 06 FEFO)</span>
                </span>
                <span className="text-[11px] text-gray-500">First-Expired, First-Out</span>
              </div>
              <p className="text-xs text-gray-600">
                System prioritizes batches by earliest valid expiration date:
              </p>
              <div className="space-y-1.5 text-xs">
                <div className="flex items-center justify-between p-1.5 rounded bg-red-50/70 border border-red-100 text-red-900 text-[11px]">
                  <span>Batch A (Expired)</span>
                  <strong className="text-red-700">BLOCKED: Cannot dispense</strong>
                </div>
                <div className="flex items-center justify-between p-1.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-900 text-[11px]">
                  <span>Batch B (Expires first)</span>
                  <strong className="text-emerald-800">PRIORITIZED: Dispensed first</strong>
                </div>
                <div className="flex items-center justify-between p-1.5 rounded bg-gray-50 border border-gray-200 text-gray-700 text-[11px]">
                  <span>Batch C (Expires later)</span>
                  <span className="text-gray-500">Reserved for subsequent orders</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action Queue & Quick Nav */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-5 shadow-xs">
              <h2 className="text-sm font-bold text-gray-900 mb-3 flex items-center justify-between">
                <span>Immediate Action Queue</span>
                <span className="text-xs font-normal text-gray-400">Live updates</span>
              </h2>

              {stats.action_queue.length === 0 ? (
                <div className="p-8 text-center border-2 border-dashed border-gray-200 rounded-xl">
                  <PackageCheck className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-gray-900">All queues are clear!</p>
                  <p className="text-xs text-gray-500 mt-1">
                    No prescriptions or fulfilment plans currently pending review. Click "Start 5-Minute Demo Flow" above to test.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {stats.action_queue.map((act) => (
                    <div key={act.id} className="py-3 flex items-center justify-between gap-4">
                      <div>
                        <h4 className="text-xs font-bold text-gray-900">{act.title}</h4>
                        <p className="text-xs text-gray-600 mt-0.5">{act.description}</p>
                      </div>
                      <Link
                        to={act.href}
                        className="flex items-center gap-1 text-xs font-bold text-[#0F766E] hover:underline shrink-0 px-2.5 py-1 bg-teal-50 rounded"
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
            <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-xs flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-gray-900 mb-3">Quick Navigation</h3>
                <div className="space-y-2.5">
                  <Link
                    to="/app/prescriptions/new"
                    className="flex items-center justify-between p-3 rounded-lg border border-gray-200 bg-gray-50/50 hover:bg-teal-50 hover:border-teal-300 transition text-xs font-semibold text-gray-800"
                  >
                    <span>Create Prescription Draft</span>
                    <PlusCircle className="w-4 h-4 text-[#0F766E]" />
                  </Link>

                  <Link
                    to="/app/medicines"
                    className="flex items-center justify-between p-3 rounded-lg border border-gray-200 bg-gray-50/50 hover:bg-teal-50 hover:border-teal-300 transition text-xs font-semibold text-gray-800"
                  >
                    <span>Catalogue Search</span>
                    <Search className="w-4 h-4 text-gray-600" />
                  </Link>

                  <Link
                    to="/app/inventory"
                    className="flex items-center justify-between p-3 rounded-lg border border-gray-200 bg-gray-50/50 hover:bg-teal-50 hover:border-teal-300 transition text-xs font-semibold text-gray-800"
                  >
                    <span>Inventory & Batches</span>
                    <ArrowRight className="w-4 h-4 text-gray-600" />
                  </Link>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-gray-100 text-[11px] text-gray-400">
                Logged in as <strong>Pharmacist / Staff</strong> • Scoped strictly to active pharmacy workspace.
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
