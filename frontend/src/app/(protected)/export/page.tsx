import { ExportButtons } from "@/../components/export/ExportButtons";
import Link from "next/link";

export const metadata = {
  title: "Export Data | Movie App",
  description: "Download your profile, ratings, and recommendations.",
};

export default function ExportPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <Link 
            href="/profile" 
            className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1 mb-4 transition-colors"
          >
            ← Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
            Your Data
          </h1>
          <p className="mt-2 text-gray-600">
            Download a copy of your personal data. All files are provided in JSON format, suitable for backups or importing into other tools.
          </p>
        </div>

        <div className="bg-white shadow-sm ring-1 ring-gray-900/5 sm:rounded-xl md:col-span-2">
          <div className="px-4 py-6 sm:p-8">
            <ExportButtons />
          </div>
          
          <div className="bg-gray-50 px-4 py-4 sm:px-8 sm:rounded-b-xl border-t border-gray-100">
            <p className="text-xs text-gray-500">
              {'Note: Large exports (like "Export All Data") may take a few moments to generate depending on your account history.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
