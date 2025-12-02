"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const EXPORT_OPTIONS = [
  { label: "Export Profile", endpoint: "/export/profile" },
  { label: "Export Ratings", endpoint: "/export/ratings" },
  { label: "Export Watchlist", endpoint: "/export/watchlist" },
  { label: "Export Recommendations", endpoint: "/export/recommendations" },
  { label: "Export All Data", endpoint: "/export/export_all" },
];

export function ExportButtons() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleExport = async (endpoint: string) => {
    try {
      setLoading(endpoint);
      setError(null);

      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      const token = localStorage.getItem("token");

      if (!token) {
        router.push("/auth/login");
        return;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        router.push("/auth/login");
        throw new Error("Session expired");
      }

      if (!response.ok) {
        throw new Error("Failed to export data");
      }

      const disposition = response.headers.get("Content-Disposition");
      let filename = "export.json";

      if (disposition && disposition.indexOf("filename=") !== -1) {
        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        const matches = filenameRegex.exec(disposition);
        if (matches != null && matches[1]) {
          filename = matches[1].replace(/['"]/g, "");
        }
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();

      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

    } catch (err) {
      console.error("Export failed:", err);
      if (err instanceof Error && err.message !== "Session expired") {
        setError("Failed to download. Please try again.");
      }
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Data Export</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {EXPORT_OPTIONS.map((option) => (
          <button
            key={option.endpoint}
            onClick={() => handleExport(option.endpoint)}
            disabled={loading !== null}
            className={`
              flex items-center justify-center px-4 py-3 rounded-lg border transition-all duration-200
              font-medium text-sm
              ${loading === option.endpoint
                ? "bg-gray-100 text-gray-400 cursor-wait border-gray-200"
                : "bg-white hover:bg-indigo-50 hover:border-indigo-300 border-gray-200 text-gray-700 shadow-sm hover:shadow-md active:scale-95 active:bg-indigo-100 cursor-pointer"}
            `}
          >
            {loading === option.endpoint ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4 text-indigo-600" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Downloading...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 text-gray-500">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
                {option.label}
              </span>
            )}
          </button>
        ))}
      </div>

      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600 mt-2 bg-red-50 p-3 rounded-md border border-red-200 animate-pulse">
           <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
             <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
           </svg>
           {error}
        </div>
      )}
    </div>
  );
}
