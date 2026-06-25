"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck, Search, FileSearch } from "lucide-react";
import { UploadZone, type UploadState } from "@/components/UploadZone";
import { uploadResume } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [fileName, setFileName] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [targetRole, setTargetRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [pendingFile, setPendingFile] = useState<File | null>(null);

  const handleFileSelected = useCallback((file: File) => {
    setPendingFile(file);
    setFileName(file.name);
    setUploadState("idle");
    setErrorMessage(null);
  }, []);

  const handleClear = useCallback(() => {
    setPendingFile(null);
    setFileName(null);
    setUploadState("idle");
    setErrorMessage(null);
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!pendingFile || !targetRole.trim()) return;

    try {
      setUploadState("uploading");
      await new Promise((r) => setTimeout(r, 350)); // perceptible state transition
      setUploadState("processing");

      const result = await uploadResume(pendingFile, targetRole, jobDescription);

      setUploadState("analyzing");

      // Stash the upload payload for the dashboard to pick up and run diagnosis
      sessionStorage.setItem(
        "resumeforge_upload",
        JSON.stringify({
          session_id: result.session_id,
          raw_text: result.raw_text,
          target_role: targetRole,
          job_description: jobDescription || undefined,
          filename: result.filename,
        })
      );

      setUploadState("done");
      router.push("/dashboard");
    } catch (err: any) {
      setUploadState("error");
      setErrorMessage(err?.detail || "Upload failed. Please try again.");
    }
  }, [pendingFile, targetRole, jobDescription, router]);

  const canSubmit = pendingFile && targetRole.trim().length > 1 && uploadState === "idle";

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Ambient backdrop accent */}
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-signal/[0.04] rounded-full blur-3xl -translate-y-1/3 translate-x-1/3" />

      <div className="relative max-w-3xl mx-auto px-6 py-16 md:py-24">
        {/* Eyebrow */}
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 text-signal-dim mb-6"
        >
          <div className="h-px w-8 bg-signal-dim/40" />
          <span className="text-xs uppercase tracking-[0.2em] font-medium">Resume Diagnostic Lab</span>
        </motion.div>

        {/* Hero headline */}
        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="font-display text-5xl md:text-6xl text-ink-950 leading-[1.05] font-medium"
        >
          ResumeForge AI
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-ink-700 text-lg mt-4 max-w-xl leading-relaxed"
        >
          An honest ATS diagnosis first. A guardrailed AI rewrite second — one that{" "}
          <span className="text-ink-950 font-medium">never invents</span> a skill, title, or metric
          you don&apos;t already have.
        </motion.p>

        {/* Three-step process strip */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
          className="flex flex-wrap gap-x-6 gap-y-2 mt-8 text-sm text-ink-600"
        >
          <span className="flex items-center gap-1.5">
            <FileSearch className="w-3.5 h-3.5" /> Diagnose honestly
          </span>
          <span className="flex items-center gap-1.5">
            <Search className="w-3.5 h-3.5" /> Learn from real patterns
          </span>
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" /> Rewrite without fabricating
          </span>
        </motion.div>

        {/* Upload form card */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-10 rounded-2xl border border-ink-600/10 bg-white/60 backdrop-blur-sm p-6 md:p-8 shadow-[0_1px_3px_rgba(0,0,0,0.03)]"
        >
          <UploadZone
            state={uploadState}
            fileName={fileName}
            errorMessage={errorMessage}
            onFileSelected={handleFileSelected}
            onClear={handleClear}
          />

          <div className="mt-6 space-y-5">
            <div>
              <label className="block text-sm font-medium text-ink-900 mb-1.5">
                Target job title <span className="text-verdict-bad">*</span>
              </label>
              <input
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g. Senior Product Manager"
                disabled={uploadState !== "idle"}
                className="w-full rounded-lg border border-ink-600/20 bg-paper-50 px-4 py-2.5 text-sm
                           text-ink-950 placeholder:text-ink-600/50 focus:border-signal focus:ring-1
                           focus:ring-signal/30 outline-none transition-colors disabled:opacity-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-ink-900 mb-1.5">
                Job description <span className="text-ink-600 font-normal">(optional, but recommended)</span>
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job posting here for tighter keyword alignment…"
                rows={4}
                disabled={uploadState !== "idle"}
                className="w-full rounded-lg border border-ink-600/20 bg-paper-50 px-4 py-2.5 text-sm
                           text-ink-950 placeholder:text-ink-600/50 focus:border-signal focus:ring-1
                           focus:ring-signal/30 outline-none transition-colors resize-none disabled:opacity-50"
              />
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="mt-7 w-full md:w-auto inline-flex items-center justify-center gap-2 rounded-lg
                       bg-ink-950 text-paper-50 px-6 py-3 text-sm font-medium transition-all
                       hover:bg-ink-900 disabled:opacity-30 disabled:cursor-not-allowed
                       active:scale-[0.98]"
          >
            Run Diagnostic <ArrowRight className="w-4 h-4" />
          </button>
        </motion.div>

        <p className="text-xs text-ink-600/70 mt-6 text-center">
          Your resume is processed for this session only and never used to train models.
        </p>
      </div>
    </main>
  );
}
