import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle, Sparkles, ShieldCheck, Stethoscope } from "lucide-react";
import { useLogin } from "@/features/auth/hooks";

export function LoginPage() {
  const [email, setEmail] = useState("pharmacist@pharmabridge.demo");
  const [password, setPassword] = useState("DemoPharmacistPass123!");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loginMutation = useLogin();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      await loginMutation.mutateAsync({ email, password });
      navigate("/app");
    } catch (err: any) {
      setErrorMsg(err.message || "Invalid credentials. Please verify your email and password.");
    }
  };

  const handleQuickFill = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setErrorMsg(null);
  };

  return (
    <div className="min-h-screen bg-[#F6F8F9] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="flex justify-center mb-3">
          <img
            src="/logo.png"
            alt="PharmaBridge Logo"
            className="w-20 h-20 object-contain rounded-2xl shadow-md border border-teal-100 bg-white p-1"
          />
        </div>
        <h2 className="text-center text-3xl font-extrabold tracking-tight text-gray-900">
          PharmaBridge
        </h2>
        <p className="mt-1 text-center text-sm font-semibold text-[#0F766E]">
          AI help for everyday pharmacy work
        </p>
        <p className="mt-0.5 text-center text-xs text-gray-500 max-w-sm mx-auto">
          Helps pharmacists check medicines, compare costs, and manage stock.
        </p>
        <div className="flex items-center justify-center gap-2 mt-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-[11px] font-semibold bg-teal-50 text-teal-800 border border-teal-200 shadow-xs">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
            <span>Dispensary Staff Authentication Portal</span>
          </span>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-sm border border-gray-200 sm:rounded-2xl sm:px-10">
          {errorMsg && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-[#0F766E] focus:border-[#0F766E]"
                placeholder="staff@pharmacy.com"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-[#0F766E] focus:border-[#0F766E]"
              />
            </div>

            <button
              type="submit"
              disabled={loginMutation.isPending}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-[#0F766E] hover:bg-[#0D655E] focus:outline-none transition disabled:opacity-50"
            >
              {loginMutation.isPending ? "Signing in..." : "Sign in to Workspace"}
            </button>
          </form>

          {/* Demo Accounts Quick-Fill Section */}
          <div className="mt-6 pt-5 border-t border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-gray-500 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-teal-600" />
                <span>Demo Accounts (Click to Fill)</span>
              </span>
              <span className="text-[10px] text-teal-700 font-semibold bg-teal-50 px-2 py-0.5 rounded">
                Instant Sign-in
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickFill("pharmacist@pharmabridge.demo", "DemoPharmacistPass123!")}
                className="px-2 py-2 text-xs font-bold border border-teal-300 bg-teal-50 hover:bg-teal-100 text-teal-800 rounded-lg transition text-center shadow-xs"
              >
                👨‍⚕️ Pharmacist
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill("assistant@pharmabridge.demo", "DemoAssistantPass123!")}
                className="px-2 py-2 text-xs font-bold border border-amber-300 bg-amber-50 hover:bg-amber-100 text-amber-800 rounded-lg transition text-center shadow-xs"
              >
                📋 Assistant
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill("admin@pharmabridge.demo", "DemoAdminPass123!")}
                className="px-2 py-2 text-xs font-bold border border-purple-300 bg-purple-50 hover:bg-purple-100 text-purple-800 rounded-lg transition text-center shadow-xs"
              >
                ⚙️ Admin
              </button>
            </div>
            <p className="mt-3 text-[11px] text-gray-500 text-center leading-relaxed">
              Only <strong>Pharmacists</strong> have clinical permission to approve substitutions and finalize orders.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
