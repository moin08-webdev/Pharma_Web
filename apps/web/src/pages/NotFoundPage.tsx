import React from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, FileQuestion } from "lucide-react";

export function NotFoundPage() {
  return (
    <div className="min-h-screen bg-[#F6F8F9] flex flex-col items-center justify-center p-4 text-center">
      <div className="w-16 h-16 rounded-2xl bg-teal-50 text-[#0F766E] flex items-center justify-center mx-auto mb-4 border border-teal-200">
        <FileQuestion className="w-8 h-8" />
      </div>
      <h1 className="text-2xl font-bold text-gray-900">Page Not Found (404)</h1>
      <p className="text-sm text-gray-500 mt-1 max-w-sm">
        The requested screen does not exist or has been moved.
      </p>
      <div className="mt-6">
        <Link
          to="/app"
          className="inline-flex items-center gap-2 px-4 py-2 bg-[#0F766E] hover:bg-[#0D655E] text-white rounded-md text-sm font-medium shadow-sm transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Workspace</span>
        </Link>
      </div>
    </div>
  );
}
