"use client";

import { useFetch } from "@/../hooks/useFetch";
import { useAuth } from "@/../hooks/auth/useAuth";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { UserInsightsCard } from "@/../components/insights/UserInsightsCard";
import { useState, useEffect } from "react";

interface DashboardData {
  user: {
    id: number;
    email: string;
    username: string;
    full_name?: string;
    created_at?: string;
  };

  stats?: {
    ratings_count: number;
    watchlist_count: number;
    reviews_count?: number;
  };
}

interface ProfileUpdatePayload {
  username?: string;
  email?: string;
  password?: string;
}

export default function DashboardPage() {
  const { isAuthenticated, loading: authLoading, login, authFetch } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [editStatus, setEditStatus] = useState<{ type: 'success' | 'error' | null, message: string }>({ type: null, message: "" });
  const [isSaving, setIsSaving] = useState(false);

  const {
    data: dashboardData,
    loading: dashLoading,
    error: dashError,
    reload
  } = useFetch<DashboardData>("/users/me/dashboard");

  const { data: ratingsList } = useFetch<unknown[]>("/ratings/me");
  const { data: watchlistList } = useFetch<unknown[]>("/watchlist");

  const handleEditClick = () => {
    if (dashboardData?.user) {
      setFormData({
        username: dashboardData.user.username,
        email: dashboardData.user.email,
        password: ""
      });
      setIsEditing(true);
      setEditStatus({ type: null, message: "" });
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditStatus({ type: null, message: "" });
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setEditStatus({ type: null, message: "" });

    try {
      const payload: ProfileUpdatePayload = {};
      const currentUsername = dashboardData?.user.username;

      if (formData.username !== currentUsername) payload.username = formData.username;
      if (formData.email !== dashboardData?.user.email) payload.email = formData.email;
      if (formData.password) payload.password = formData.password;

      if (Object.keys(payload).length === 0) {
        setIsEditing(false);
        setIsSaving(false);
        return;
      }

      const response = await authFetch("/users/me", {
        method: "PUT",
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        let errorMsg = data.detail || data.message || "Failed to update profile.";
        if (Array.isArray(errorMsg)) {
          errorMsg = errorMsg
            .map((err: { msg?: string }) => err.msg || JSON.stringify(err))
            .join(", ");
        }
        throw new Error(errorMsg);
      }

      setEditStatus({ type: 'success', message: "Profile updated successfully!" });

      if (data.access_token) {
        login(data.access_token);
      }

      setTimeout(() => {
        setIsEditing(false);
        reload();
      }, 1000);

    } catch (err: unknown) {
      let errorMsg = "Failed to update profile.";
      if (err instanceof Error) {
        errorMsg = err.message;
      }
      setEditStatus({ type: 'error', message: errorMsg });
    } finally {
      setIsSaving(false);
    }
  };

  if (authLoading || dashLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  if (dashError || !dashboardData) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 text-center p-4">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Failed to load dashboard</h2>
        <p className="text-gray-500 mb-6">{dashError || "Unknown error occurred"}</p>
        <button onClick={() => window.location.reload()} className="text-indigo-600 hover:underline">
          Try Again
        </button>
      </div>
    );
  }

  const { user, stats } = dashboardData;

  const ratingsCount = stats?.ratings_count ?? ratingsList?.length ?? 0;
  const watchlistCount = stats?.watchlist_count ?? watchlistList?.length ?? 0;

  const joinDate = user.created_at
    ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    : 'Unknown';

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="h-32 bg-gradient-to-r from-indigo-500 to-purple-600"></div>
          <div className="px-8 pb-8">
            <div className="relative flex justify-between items-end -mt-12 mb-6">
              <div className="flex items-end">
                <div className="h-24 w-24 rounded-2xl bg-white p-1 shadow-lg">
                  <div className="h-full w-full bg-indigo-100 rounded-xl flex items-center justify-center text-3xl font-bold text-indigo-600">
                    {user.username?.[0]?.toUpperCase() || "U"}
                  </div>
                </div>
                <div className="ml-4 mb-1 pt-15">
                  <h1 className="text-2xl font-bold text-gray-900">{user.username}</h1>
                  <p className="text-sm text-gray-500">{user.email}</p>
                </div>
              </div>
              <div className="hidden sm:block text-sm text-gray-500 mb-2">
                Member since {joinDate}
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-6 border-t border-gray-100">
              <div className="text-center sm:text-left">
                <Link href="/ratings" className="group block">
                  <div className="text-2xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
                    {ratingsCount}
                  </div>
                  <div className="text-xs font-medium text-gray-500 uppercase tracking-wide group-hover:text-indigo-500 transition-colors">
                    Ratings
                  </div>
                </Link>
              </div>
              <div className="text-center sm:text-left">
                <Link href="/watchlist" className="group block">
                  <div className="text-2xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
                    {watchlistCount}
                  </div>
                  <div className="text-xs font-medium text-gray-500 uppercase tracking-wide group-hover:text-indigo-500 transition-colors">
                    Watchlist
                  </div>
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center text-green-600 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-gray-900">Download Your Data</h3>
              <p className="text-gray-500 text-sm mt-2">
                Get a copy of your ratings, watchlist, and profile information.
              </p>
            </div>
            <Link
              href="/export"
              className="mt-6 block w-full text-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Go to Export Page
            </Link>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between transition-all">
             <div>
              <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.174 1.059c.212.007.427.027.64.058l1.018-.46a1.127 1.127 0 011.23.14l.773.774c.345.344.437.86.241 1.288l-.458 1.019c.14.213.266.442.373.68l1.06.175c.53.088.92.545.92 1.082v1.093c0 .537-.39.994-.92 1.082l-1.06.174a8.106 8.106 0 01-.373.68l.458 1.02c.196.427.104.943-.242 1.287l-.773.774a1.125 1.125 0 01-1.23.14l-1.018-.459a8.106 8.106 0 01-.64.059l-.174 1.06a1.128 1.128 0 01-1.11.94h-1.093a1.128 1.128 0 01-1.11-.94l-.174-1.059a8.106 8.106 0 01-.64-.059l-1.018.459a1.125 1.125 0 01-1.23-.14l-.773-.774a1.125 1.125 0 01-.242-1.288l.458-1.019a8.106 8.106 0 01-.373-.68l-1.06-.175a1.128 1.128 0 01-.92-1.082V9.75c0-.537.39-.994.92-1.082l1.06-.174a8.106 8.106 0 01.373-.68l-.458-1.02a1.125 1.125 0 01.242-1.287l.773-.774a1.125 1.125 0 011.23-.14l1.018.46a8.106 8.106 0 01.64-.059l.174-1.06z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-gray-900">Edit Profile</h3>

              {!isEditing ? (
                <>
                  <p className="text-gray-500 text-sm mt-2">
                    Update your username, email, or change your password.
                  </p>
                  <button
                    onClick={handleEditClick}
                    className="mt-6 block w-full text-center py-2 px-4 border border-indigo-600 rounded-lg shadow-sm text-sm font-medium text-indigo-600 bg-white hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
                  >
                    Edit Details
                  </button>
                </>
              ) : (
                <form onSubmit={handleSave} className="mt-4 space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700">Username</label>
                    <input
                      type="text"
                      value={formData.username}
                      onChange={(e) => setFormData({...formData, username: e.target.value})}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700">Email</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700">New Password (Optional)</label>
                    <input
                      type="password"
                      placeholder="Leave blank to keep current"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                    />
                  </div>

                  {editStatus.message && (
                    <div className={`text-sm ${editStatus.type === 'error' ? 'text-red-600' : 'text-green-600'}`}>
                      {editStatus.message}
                    </div>
                  )}

                  <div className="flex space-x-3 pt-2">
                    <button
                      type="submit"
                      disabled={isSaving}
                      className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 cursor-pointer"
                    >
                      {isSaving ? "Saving..." : "Save"}
                    </button>
                    <button
                      type="button"
                      onClick={handleCancelEdit}
                      disabled={isSaving}
                      className="flex-1 bg-white border border-gray-300 text-gray-700 py-2 px-4 rounded-md text-sm font-medium hover:bg-gray-50 cursor-pointer"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>

        <UserInsightsCard />

      </div>
    </div>
  );
}
