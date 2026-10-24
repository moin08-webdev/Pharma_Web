import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Settings, Users, Shield, PlusCircle, CheckCircle2, AlertCircle } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { useSession } from "@/features/auth/hooks";

export function SettingsPage() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [expiryBuffer, setExpiryBuffer] = useState(30);
  const [msg, setMsg] = useState<string | null>(null);

  // New staff form state
  const [newEmail, setNewEmail] = useState("");
  const [newPass, setNewPass] = useState("");
  const [newRole, setNewRole] = useState("ASSISTANT");
  const [staffMsg, setStaffMsg] = useState<string | null>(null);

  const { data: settings, isLoading } = useQuery({
    queryKey: ["pharmacy-settings"],
    queryFn: async () => {
      const data = await apiFetch<any>("/api/v1/settings");
      setName(data.name);
      setExpiryBuffer(data.expiry_buffer_days);
      return data;
    },
  });

  const { data: staff } = useQuery({
    queryKey: ["staff-list"],
    queryFn: () => apiFetch<any[]>("/api/v1/settings/staff"),
    enabled: session?.user.role === "ADMIN",
  });

  const updateSettingsMutation = useMutation({
    mutationFn: async () => {
      if (!settings) return;
      return apiFetch("/api/v1/settings", {
        method: "PATCH",
        body: JSON.stringify({
          name,
          expiry_buffer_days: expiryBuffer,
          expected_version: settings.settings_version,
        }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pharmacy-settings"] });
      queryClient.invalidateQueries({ queryKey: ["session"] });
      setMsg("Settings updated successfully.");
    },
    onError: (err: any) => {
      setMsg(`Error: ${err.message}`);
    },
  });

  const createStaffMutation = useMutation({
    mutationFn: async () => {
      return apiFetch("/api/v1/settings/staff", {
        method: "POST",
        body: JSON.stringify({
          email: newEmail,
          password: newPass,
          role: newRole,
        }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff-list"] });
      setNewEmail("");
      setNewPass("");
      setStaffMsg("Staff account created.");
    },
    onError: (err: any) => {
      setStaffMsg(`Error: ${err.message}`);
    },
  });

  const isAdmin = session?.user.role === "ADMIN";

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <PageHeader
        title="Pharmacy Settings & Administration"
        description="Workspace configuration, expiry policies, and staff user access control"
      />

      {/* Pharmacy Settings Form */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-4">
        <h3 className="font-bold text-gray-900 text-base border-b pb-3 flex items-center gap-2">
          <Settings className="w-4 h-4 text-[#0F766E]" />
          <span>General Pharmacy Settings</span>
        </h3>

        {msg && (
          <div className="p-3 bg-teal-50 border border-teal-200 text-teal-800 text-xs rounded-lg">
            {msg}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block font-medium text-gray-700 mb-1">Pharmacy Workspace Name</label>
            <input
              type="text"
              disabled={!isAdmin}
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none disabled:bg-gray-50"
            />
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Expiry Safety Buffer (Days)</label>
            <input
              type="number"
              min="0"
              max="365"
              disabled={!isAdmin}
              value={expiryBuffer}
              onChange={(e) => setExpiryBuffer(parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none disabled:bg-gray-50 font-mono"
            />
            <p className="text-[11px] text-gray-400 mt-1">
              Batches expiring within this number of days are excluded from FEFO allocation.
            </p>
          </div>
        </div>

        {isAdmin && (
          <div className="pt-3 border-t flex justify-end">
            <button
              onClick={() => updateSettingsMutation.mutate()}
              disabled={updateSettingsMutation.isPending}
              className="px-4 py-2 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded text-xs font-semibold shadow-sm transition"
            >
              {updateSettingsMutation.isPending ? "Saving..." : "Save Settings"}
            </button>
          </div>
        )}
      </div>

      {/* Staff Management (Admin only) */}
      {isAdmin && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b pb-3">
            <h3 className="font-bold text-gray-900 text-base flex items-center gap-2">
              <Users className="w-4 h-4 text-[#0F766E]" />
              <span>Staff Accounts & Role Enforcement</span>
            </h3>
          </div>

          {staffMsg && (
            <div className="p-3 bg-teal-50 border border-teal-200 text-teal-800 text-xs rounded-lg">
              {staffMsg}
            </div>
          )}

          {/* Add Staff Member Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createStaffMutation.mutate();
            }}
            className="p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-3 text-xs"
          >
            <div className="font-semibold text-gray-800">Add New Staff Member</div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-gray-600 mb-1">Email</label>
                <input
                  type="email"
                  required
                  placeholder="assistant2@pharmabridge.demo"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 mb-1">Temporary Password</label>
                <input
                  type="password"
                  required
                  placeholder="Min 8 characters"
                  value={newPass}
                  onChange={(e) => setNewPass(e.target.value)}
                  className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-gray-600 mb-1">Role</label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  className="w-full px-2.5 py-1.5 border border-gray-300 rounded text-xs bg-white focus:outline-none"
                >
                  <option value="ASSISTANT">Assistant (Intake & Drafts)</option>
                  <option value="PHARMACIST">Pharmacist (Clinical Approval)</option>
                  <option value="ADMIN">Administrator (Staff & Settings)</option>
                </select>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                disabled={createStaffMutation.isPending}
                className="px-3 py-1.5 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded text-xs font-semibold shadow-sm"
              >
                Create Staff Account
              </button>
            </div>
          </form>

          {/* Staff Accounts Table */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-xs text-left">
              <thead className="bg-gray-50 text-gray-600 font-semibold border-b">
                <tr>
                  <th className="py-2.5 px-4">Staff Email</th>
                  <th className="py-2.5 px-4">Role</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4">Created Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {staff?.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="py-2.5 px-4 font-semibold text-gray-900">{u.email}</td>
                    <td className="py-2.5 px-4">
                      <span className="font-semibold text-teal-800">{u.role}</span>
                    </td>
                    <td className="py-2.5 px-4">
                      <span className="text-emerald-700 font-medium">Active</span>
                    </td>
                    <td className="py-2.5 px-4 text-gray-500">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
