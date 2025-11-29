"use client";

import { useState } from "react";
import { useFetch } from "@/../hooks/useFetch";
import { useAuth } from "@/../hooks/auth/useAuth";
import { useRouter } from "next/navigation";

interface Penalty {
  id: number;
  user_id: number;
  reason: string;
  description?: string;
  active: boolean;
  created_at: string;
}

interface User {
  id: number;
  email: string;
  full_name?: string;
  username?: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface AdminStats {
  total_users: number;
  active_penalties: number;
  total_movies: number;
  total_ratings: number;
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<"stats" | "users" | "penalties">("stats");
  const { isAuthenticated, authFetch, loading: authLoading } = useAuth();
  const router = useRouter();

  const [penalizeUser, setPenalizeUser] = useState<User | null>(null);
  const [penaltyReason, setPenaltyReason] = useState("");
  const [penaltyDescription, setPenaltyDescription] = useState("");

  const { data: stats, reload: reloadStats } = useFetch<AdminStats>("/admin/stats"); // eslint-disable-line
  const { data: users, reload: reloadUsers } = useFetch<User[]>("/admin/users"); // eslint-disable-line
  
  const { data: penalties, reload: reloadPenalties } = useFetch<Penalty[]>("/admin/penalties");

  if (!authLoading && !isAuthenticated) {
    router.push("/login");
  }


  const handleResolvePenalty = async (penaltyId: number) => {
    if (!confirm("Are you sure you want to resolve this penalty?")) return;
    try {
      const res = await authFetch(`/admin/penalties/${penaltyId}/resolve`, { method: "PUT" });
      if (res.ok) reloadPenalties();
    } catch (err) {
      console.error(err);
      alert("Failed to resolve penalty");
    }
  };

  const handleDeletePenalty = async (penaltyId: number) => {
    if (!confirm("Delete this penalty record permanently?")) return;
    try {
      const res = await authFetch(`/admin/penalties/${penaltyId}`, { method: "DELETE" });
      if (res.ok) reloadPenalties();
    } catch (err) {
      console.error(err);
      alert("Failed to delete penalty");
    }
  };

  const submitPenalty = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!penalizeUser) return;

    try {
      const res = await authFetch("/admin/penalties", {
        method: "POST",
        body: JSON.stringify({
          user_id: penalizeUser.id,
          reason: penaltyReason,
          description: penaltyDescription || null
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to apply penalty");
      }

      alert(`Penalty applied to ${penalizeUser.username}`);
      setPenalizeUser(null);
      setPenaltyReason("");
      setPenaltyDescription(""); 
      reloadPenalties();
    } catch (err) {
      console.error(err);
      alert("Error applying penalty");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <div className="flex space-x-2 bg-white p-1 rounded-lg border border-gray-200 mt-4 md:mt-0">
            {(["stats", "users", "penalties"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors capitalize ${
                  activeTab === tab
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "text-gray-500 hover:text-gray-900 hover:bg-gray-100"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {activeTab === "stats" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard title="Total Users" value={stats?.total_users ?? 0} color="bg-blue-500" />
            <StatCard title="Active Penalties" value={stats?.active_penalties ?? 0} color="bg-red-500" />
            <StatCard title="Total Movies" value={stats?.total_movies ?? 0} color="bg-green-500" />
            <StatCard title="Total Ratings" value={stats?.total_ratings ?? 0} color="bg-purple-500" />
          </div>
        )}

        {activeTab === "users" && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users?.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{user.full_name || user.username}</div>
                        <div className="text-xs text-gray-500">ID: {user.id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button 
                          onClick={() => setPenalizeUser(user)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Penalize
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === "penalties" && (
          <div className="space-y-6">
             {(!penalties || penalties.length === 0) ? (
                 <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
                   No active penalties found system-wide.
                 </div>
              ) : (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                   <ul className="divide-y divide-gray-200">
                    {penalties.map((penalty) => (
                      <li key={penalty.id} className="p-6 flex flex-col md:flex-row justify-between gap-4">
                        <div>
                          <div className="flex items-center gap-2">
                             <span className="font-bold text-gray-900">User #{penalty.user_id}</span>
                             <span className={`px-2 py-0.5 rounded text-xs font-medium ${penalty.active ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                               {penalty.active ? "Active" : "Resolved"}
                             </span>
                          </div>
                          <p className="text-sm text-gray-900 font-medium mt-1">{penalty.reason}</p>
                          {penalty.description && (
                            <p className="text-sm text-gray-600 mt-1">{penalty.description}</p>
                          )}
                          <p className="text-xs text-gray-400 mt-1">Created: {new Date(penalty.created_at).toLocaleDateString()}</p>
                        </div>
                        
                        <div className="flex items-center gap-3">
                          {penalty.active && (
                            <button 
                              onClick={() => handleResolvePenalty(penalty.id)}
                              className="text-sm text-indigo-600 hover:text-indigo-900 font-medium"
                            >
                              Resolve
                            </button>
                          )}
                          <button 
                            onClick={() => handleDeletePenalty(penalty.id)}
                            className="text-sm text-red-600 hover:text-red-900 font-medium"
                          >
                            Delete
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
          </div>
        )}

      </div>

      {penalizeUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-xl font-bold mb-4 text-red-600">Apply Penalty</h2>
            <p className="text-gray-600 mb-4">
              You are applying a penalty to <strong>{penalizeUser.username || penalizeUser.email}</strong>.
            </p>
            <form onSubmit={submitPenalty} className="space-y-4">
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reason <span className="text-red-500">*</span></label>
                <input 
                  type="text"
                  required
                  maxLength={500}
                  className="w-full border border-gray-300 rounded-md p-2"
                  placeholder="e.g. Terms Violation"
                  value={penaltyReason}
                  onChange={(e) => setPenaltyReason(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
                <textarea 
                  className="w-full border border-gray-300 rounded-md p-2 h-24"
                  placeholder="Additional details about the violation..."
                  value={penaltyDescription}
                  onChange={(e) => setPenaltyDescription(e.target.value)}
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button 
                  type="button" 
                  onClick={() => {
                    setPenalizeUser(null);
                    setPenaltyReason("");
                    setPenaltyDescription("");
                  }}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Apply Penalty
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}

function StatCard({ title, value, color }: { title: string, value: number | string, color: string }) {
  return (
    <div className="bg-white overflow-hidden rounded-xl shadow-sm border border-gray-200 p-6">
      <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
      <dd className="mt-1 text-3xl font-semibold text-gray-900 flex items-center gap-2">
        <div className={`w-2 h-8 rounded-full ${color}`} />
        {value}
      </dd>
    </div>
  );
}