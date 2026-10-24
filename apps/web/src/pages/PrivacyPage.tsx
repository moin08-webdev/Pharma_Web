import React from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, ArrowLeft, Clock, Lock, Database } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";

export function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link
        to="/app"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Return to Workspace</span>
      </Link>

      <PageHeader
        title="Privacy & Data Retention Notice"
        description="Transparent disclosure of local storage, processing policies, and data handling"
      />

      <div className="bg-white rounded-xl border border-gray-200 p-6 sm:p-8 shadow-sm space-y-6 text-sm text-gray-700 leading-relaxed">
        <div className="flex items-center gap-3 p-4 bg-teal-50 border border-teal-200 rounded-lg text-teal-900">
          <ShieldCheck className="w-6 h-6 text-[#0F766E] shrink-0" />
          <div className="text-xs">
            <strong>Local Processing Commitment:</strong> Uploaded prescriptions are retained on private isolated server storage and are never indexed publicly or shared with unapproved third parties.
          </div>
        </div>

        <section className="space-y-2">
          <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#0F766E]" />
            <span>Prescription Document Retention Policy</span>
          </h3>
          <p className="text-xs text-gray-600">
            Original prescription upload documents are automatically scheduled for permanent deletion after 24 hours in demo mode, or 7 days in production mode. Once deleted, only structured operational audit metadata and the finalized dispensing records remain.
          </p>
        </section>

        <section className="space-y-2">
          <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
            <Lock className="w-4 h-4 text-[#0F766E]" />
            <span>OCR & Vision Model Processing</span>
          </h3>
          <p className="text-xs text-gray-600">
            Machine-printed text is processed locally using embedded OCR capabilities. When an external vision adapter (such as Google GenAI) is enabled by the pharmacy administrator, document text is sent over encrypted TLS connections solely for transcription and is never used for general model training.
          </p>
        </section>

        <section className="space-y-2">
          <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
            <Database className="w-4 h-4 text-[#0F766E]" />
            <span>Patient Privacy & Minimal Identifiers</span>
          </h3>
          <p className="text-xs text-gray-600">
            PharmaBridge employs minimal patient identifiers. Patient references are optional local records scoped strictly to the authenticated pharmacy workspace.
          </p>
        </section>
      </div>
    </div>
  );
}
