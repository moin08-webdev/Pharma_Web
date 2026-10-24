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
  Sparkles,
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
          <div className="w-8 h-8 border-4 border-[#0F766E] border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-gray-500 font-medium">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    navigate("/login");
    return null;
  }

  const { user, pharmacy } = session;

  const navItems = [
    { to: "/app", label: "Dashboard", icon: LayoutDashboard, end: true },
    { to: "/app/prescriptions", label: "Prescriptions", icon: FileText },
    { to: "/app/approvals", label: "Review & Approvals", icon: ClipboardCheck },
    { to: "/app/medicines", label: "Medicines Catalogue", icon: Search },
    { to: "/app/inventory", label: "Inventory & Batches", icon: Package },
    { to: "/app/orders", label: "Completed Orders", icon: ShoppingBag },
    { to: "/app/settings", label: "Settings & Staff", icon: Settings },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#F6F8F9]">
      {pharmacy.demo_mode && <DemoDataBanner />}

      {/* Top Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <Link to="/app" className="flex items-center gap-2 hover:opacity-90 transition">
              <AppLogo size="md" showTagline={true} />
            </Link>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/app/prescriptions/new"
              className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-lg shadow-sm transition"
            >
              <PlusCircle className="w-4 h-4" />
              <span>+ New Prescription</span>
            </Link>

            {/* Pharmacy & User Profile */}
            <div className="flex items-center gap-3 pl-3 border-l border-gray-200 text-sm">
              <div className="hidden md:flex flex-col text-right">
                <span className="font-semibold text-gray-900 flex items-center gap-1 justify-end text-xs">
                  <Building2 className="w-3.5 h-3.5 text-gray-500" />
                  {pharmacy.name}
                </span>
                <div className="flex items-center gap-1.5 justify-end mt-0.5">
                  <span className="text-[11px] text-gray-500">{user.email}</span>
                  {user.role === "PHARMACIST" && (
                    <span className="text-[10px] font-bold px-1.5 py-0.2 bg-teal-100 text-teal-800 rounded border border-teal-200">
                      👨‍⚕️ Pharmacist
                    </span>
                  )}
                  {user.role === "ASSISTANT" && (
                    <span className="text-[10px] font-bold px-1.5 py-0.2 bg-amber-100 text-amber-800 rounded border border-amber-200">
                      📋 Assistant
                    </span>
                  )}
                  {user.role === "ADMIN" && (
                    <span className="text-[10px] font-bold px-1.5 py-0.2 bg-purple-100 text-purple-800 rounded border border-purple-200">
                      ⚙️ Admin
                    </span>
                  )}
                </div>
              </div>

              <button
                onClick={() => logout.mutate()}
                title="Logout"
                className="p-2 text-gray-500 hover:text-rose-600 rounded-md hover:bg-gray-100 transition"
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
        <aside className="hidden lg:block w-64 bg-white border-r border-gray-200 p-4 space-y-1 shrink-0">
          <div className="mb-4 px-3 py-2 bg-gray-50 rounded-md border border-gray-100">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Active Pharmacy</div>
            <div className="text-sm font-bold text-gray-800 truncate">{pharmacy.name}</div>
          </div>

          <div className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition ${
                      isActive
                        ? "bg-[#E6F4F2] text-[#0F766E] font-semibold"
                        : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>

          <div className="pt-6 mt-6 border-t border-gray-100 space-y-1">
            <Link
              to="/privacy"
              className="flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-50"
            >
              <Shield className="w-4 h-4" />
              <span>Data & Privacy Notice</span>
            </Link>
          </div>
        </aside>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setMobileMenuOpen(false)}>
            <div
              className="w-64 bg-white h-full p-4 space-y-2 shadow-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between pb-3 border-b border-gray-200 mb-2">
                <span className="font-bold text-gray-800">Menu</span>
                <button onClick={() => setMobileMenuOpen(false)}>
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    onClick={() => setMobileMenuOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition ${
                        isActive
                          ? "bg-[#E6F4F2] text-[#0F766E] font-semibold"
                          : "text-gray-700 hover:bg-gray-100"
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
