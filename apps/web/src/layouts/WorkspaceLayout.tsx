import React, { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  Search,
  Package,
  ClipboardCheck,
  ShoppingBag,
  Settings,
  Shield,
  LogOut,
  Menu,
  X,
  PlusCircle,
  Building2,
  Stethoscope,
  Pill,
  ShieldCheck,
  Activity,
  HeartPulse,
} from "lucide-react";
import { useSession, useLogout } from "@/features/auth/hooks";
import { DemoDataBanner } from "@/components/common/DemoDataBanner";
import { AppLogo } from "@/components/common/AppLogo";

export function WorkspaceLayout() {
  const { data: session, isLoading } = useSession();
  const logout = useLogout();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#F6F8F9]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-[#0F766E] border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-teal-800 font-semibold tracking-wide flex items-center gap-2">
            <HeartPulse className="w-4 h-4 text-teal-600 animate-pulse" />
            <span>Initializing clinical dispensary workspace...</span>
          </p>
        </div>
      </div>
    );
  }

  if (!session) {
    navigate("/login");
    return null;
  }

  const { user, pharmacy } = session;

  interface NavItem {
    to: string;
    label: string;
    icon: any;
    end?: boolean;
  }

  const clinicalNav: NavItem[] = [
    { to: "/app", label: "Dashboard", icon: LayoutDashboard, end: true },
    { to: "/app/prescriptions", label: "Prescriptions", icon: FileText },
    { to: "/app/approvals", label: "Review & Approvals", icon: ClipboardCheck },
    { to: "/app/orders", label: "Completed Orders", icon: ShoppingBag },
  ];

  const formularyNav: NavItem[] = [
    { to: "/app/medicines", label: "Medicines Catalogue", icon: Search },
    { to: "/app/inventory", label: "Inventory & Batches", icon: Package },
  ];

  const adminNav: NavItem[] = [
    { to: "/app/settings", label: "Settings & Staff", icon: Settings },
  ];

  const allNav = [...clinicalNav, ...formularyNav, ...adminNav];

  return (
    <div className="min-h-screen flex flex-col bg-[#F6F8F9]">
      {pharmacy.demo_mode && <DemoDataBanner />}

      {/* Top Clinical Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
        <div className="px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-100 focus:outline-none"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <Link to="/app" className="flex items-center gap-2 hover:opacity-95 transition">
              <AppLogo size="md" showTagline={true} />
            </Link>

            {/* Clinical CDS Status Badge (Hidden on mobile) */}
            <div className="hidden xl:flex items-center gap-1.5 pl-3 border-l border-slate-200 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span className="text-[11px] font-semibold text-teal-800 bg-teal-50/80 px-2.5 py-0.5 rounded-full border border-teal-200">
                Clinical Decision Support Active • IP Standards
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/app/prescriptions/new"
              className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-lg shadow-xs transition"
            >
              <PlusCircle className="w-4 h-4" />
              <span>+ New Prescription</span>
            </Link>

            {/* Dispensary & User Profile */}
            <div className="flex items-center gap-3 pl-3 border-l border-slate-200 text-sm">
              <div className="hidden md:flex flex-col text-right">
                <span className="font-bold text-slate-900 flex items-center gap-1.5 justify-end text-xs">
                  <Building2 className="w-3.5 h-3.5 text-teal-600" />
                  <span>{pharmacy.name}</span>
                </span>
                <div className="flex items-center gap-1.5 justify-end mt-0.5">
                  <span className="text-[11px] text-slate-500">{user.email}</span>
                  {user.role === "PHARMACIST" && (
                    <span className="text-[10px] font-extrabold px-2 py-0.5 bg-teal-50 text-teal-800 rounded-md border border-teal-300 flex items-center gap-1">
                      <Stethoscope className="w-3 h-3 text-teal-700" />
                      <span>R.Ph. (Pharmacist)</span>
                    </span>
                  )}
                  {user.role === "ASSISTANT" && (
                    <span className="text-[10px] font-extrabold px-2 py-0.5 bg-amber-50 text-amber-800 rounded-md border border-amber-300 flex items-center gap-1">
                      <FileText className="w-3 h-3 text-amber-700" />
                      <span>Dispensary Assistant</span>
                    </span>
                  )}
                  {user.role === "ADMIN" && (
                    <span className="text-[10px] font-extrabold px-2 py-0.5 bg-purple-50 text-purple-800 rounded-md border border-purple-300 flex items-center gap-1">
                      <Settings className="w-3 h-3 text-purple-700" />
                      <span>Store Admin</span>
                    </span>
                  )}
                </div>
              </div>

              <button
                onClick={() => logout.mutate()}
                title="Logout"
                className="p-2 text-slate-500 hover:text-rose-600 rounded-lg hover:bg-slate-100 transition"
                aria-label="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Desktop Sidebar Navigation */}
        <aside className="hidden lg:block w-64 bg-white border-r border-slate-200 p-4 shrink-0 flex flex-col justify-between">
          <div className="space-y-4">
            {/* Active Pharmacy Card with Medical License Info */}
            <div className="px-3.5 py-3 bg-gradient-to-br from-teal-50/70 to-slate-50 rounded-xl border border-teal-100 shadow-2xs">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-extrabold text-teal-800 uppercase tracking-wider flex items-center gap-1">
                  <Activity className="w-3 h-3 text-teal-600" />
                  <span>Licensed Dispensary</span>
                </span>
                <span className="text-[9px] font-mono font-bold text-slate-500">DL: 20B/21B</span>
              </div>
              <div className="text-sm font-bold text-slate-900 truncate mt-1">{pharmacy.name}</div>
              <div className="text-[10px] text-teal-700/80 mt-0.5 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" />
                <span>Schedule H / H1 Monitored</span>
              </div>
            </div>

            {/* Nav Group 1: Clinical Dispensing */}
            <div className="space-y-1">
              <div className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
                Clinical Dispensing
              </div>
              {clinicalNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) =>
                      `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition ${
                        isActive
                          ? "bg-[#E6F4F2] text-[#0F766E] border-r-2 border-[#0F766E]"
                          : "text-slate-700 hover:bg-slate-50 hover:text-slate-900"
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </div>

            {/* Nav Group 2: Formulary & Inventory */}
            <div className="space-y-1 pt-2 border-t border-slate-100">
              <div className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
                Formulary & Stock
              </div>
              {formularyNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition ${
                        isActive
                          ? "bg-[#E6F4F2] text-[#0F766E] border-r-2 border-[#0F766E]"
                          : "text-slate-700 hover:bg-slate-50 hover:text-slate-900"
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </div>

            {/* Nav Group 3: Governance */}
            <div className="space-y-1 pt-2 border-t border-slate-100">
              <div className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
                Store Governance
              </div>
              {adminNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition ${
                        isActive
                          ? "bg-[#E6F4F2] text-[#0F766E] border-r-2 border-[#0F766E]"
                          : "text-slate-700 hover:bg-slate-50 hover:text-slate-900"
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>

          <div className="pt-4 mt-auto border-t border-slate-100 space-y-2">
            <Link
              to="/privacy"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-[11px] font-medium text-slate-500 hover:text-slate-800 hover:bg-slate-50"
            >
              <Shield className="w-3.5 h-3.5 text-teal-600" />
              <span>DPDP 2023 & Patient Privacy</span>
            </Link>
            <div className="px-3 text-[10px] text-slate-400 leading-tight">
              Pharmacy Act 1948 & CDSCO Compliant
            </div>
          </div>
        </aside>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setMobileMenuOpen(false)}>
            <div
              className="w-64 bg-white h-full p-4 space-y-2 shadow-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-2">
                <div className="flex items-center gap-2">
                  <Stethoscope className="w-4 h-4 text-teal-700" />
                  <span className="font-bold text-slate-900 text-sm">Dispensary Menu</span>
                </div>
                <button onClick={() => setMobileMenuOpen(false)}>
                  <X className="w-5 h-5 text-slate-500" />
                </button>
              </div>

              {allNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    onClick={() => setMobileMenuOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition ${
                        isActive
                          ? "bg-[#E6F4F2] text-[#0F766E]"
                          : "text-slate-700 hover:bg-slate-100"
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto overflow-x-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
