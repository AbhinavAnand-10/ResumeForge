"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Loader2,
  Sparkles,
  CheckCircle2,
  XCircle,
  Download,
  ArrowLeft,
  FileText,
  Smile,
  AlertTriangle,
  KeySquare,
  Map,
} from "lucide-react";

import { ScoreGauge } from "@/components/ScoreGauge";
import { ScoreBreakdown, FlawsList } from "@/components/ScoreBreakdown";
import {
  DiagnosticPanel,
  GoodPointsList,
  FluffyPhrasesList,
  MissingKeywordsList,
} from "@/components/DiagnosticPanel";
import { DiffViewer } from "@/components/DiffViewer";
import { SkillGapRoadmap } from "@/components/SkillGapRoadmap";
import {
  diagnoseResume,
  optimizeResume,
  exportResume,
  type DiagnoseResponse,
  type OptimizeResponse,
} from "@/lib/api";

type Stage = "loading" | "diagnosed" | "optimizing" | "revealed" | "error";

interface UploadPayload {
  session_id: string;
  raw_text: string;
  target_role: string;
  job_description?: string;
  filename: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stage, setStage] = useState<Stage>("loading");
  const [upload, setUpload] = useState<UploadPayload | null>(null);
  const [diagnosis, setDiagnosis] = useState<DiagnoseResponse | null>(null);
  const [optimization, setOptimization] = useState<OptimizeResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [exporting, setExporting] = useState<"pdf" | "docx" | null>(null);

  // ── Load upload payload + run diagnosis on mount ────────────────────────
  useEffect(() => {
    const raw = sessionStorage.getItem("resumeforge_upload");
    if (!raw) {
      router.push("/");
      return;
    }
    const parsed: UploadPayload = JSON.parse(raw);
    setUpload(parsed);

    diagnoseResume({
      session_id: parsed.session_id,
      raw_text: parsed.raw_text,
      target_role: parsed.target_role,
      job_description: parsed.job_description,
    })
      .then((res) => {
        setDiagnosis(res);
        setStage("diagnosed");
      })
      .catch((err) => {
        setErrorMsg(err?.detail || "Diagnosis failed. Please try again.");
        setStage("error");
      });
  }, [router]);

  const handleOptimize = useCallback(async () => {
    if (!upload || !diagnosis) return;
    setStage("optimizing");
    try {
      const result = await optimizeResume({
        session_id: upload.session_id,
        raw_text: upload.raw_text,
        target_role: upload.target_role,
        job_description: upload.job_description,
        diagnosis,
      });
      setOptimization(result);
      setStage("revealed");
    } catch (err: any) {
      setErrorMsg(err?.detail || "Optimization failed. Please try again.");
      setStage("error");
    }
  }, [upload, diagnosis]);

  const handleExport = useCallback(
    async (format: "pdf" | "docx") => {
      if (!upload || !optimization) return;
      setExporting(format);
      try {
        const blob = await exportResume({
          session_id: upload.session_id,
          optimized_text: optimization.optimized_text,
          target_role: upload.target_role,
          format,
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `ResumeForge_${upload.target_role.replace(/\s+/g, "_")}.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      } catch {
        setErrorMsg("Export failed. Please try again.");
      } finally {
        setExporting(null);
      }
    },
    [upload, optimization]
  );

  // ── Loading state ─────────────────────────────────────────────────────────
  if (stage === "loading") {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-8 h-8 text-signal animate-spin" />
        <p className="text-ink-700 font-medium">Running diagnostic on your resume…</p>
        <p className="text-sm text-ink-600">Checking ATS compatibility, content quality, and keyword gaps</p>
      </main>
    );
  }

  // ── Error state ───────────────────────────────────────────────────────────
  if (stage === "error") {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center gap-4 px-6 text-center">
        <XCircle className="w-10 h-10 text-verdict-bad" />
        <p className="text-ink-900 font-medium max-w-md">{errorMsg}</p>
        <button
          onClick={() => router.push("/")}
          className="inline-flex items-center gap-2 rounded-lg bg-ink-950 text-paper-50 px-5 py-2.5 text-sm font-medium hover:bg-ink-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Start over
        </button>
      </main>
    );
  }

  if (!diagnosis || !upload) return null;

  return (
    <main className="min-h-screen pb-24">
      {/* Top bar */}
      <div className="border-b border-ink-600/10 bg-white/70 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => router.push("/")}
            className="flex items-center gap-2 text-sm text-ink-600 hover:text-ink-950 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> New resume
          </button>
          <div className="flex items-center gap-2 text-sm text-ink-700">
            <FileText className="w-4 h-4" />
            <span className="font-medium">{upload.filename}</span>
            <span className="text-ink-600">·</span>
            <span>{upload.target_role}</span>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 pt-10">
        {/* ── PHASE 1: DIAGNOSTIC RESULTS ─────────────────────────────────── */}
        <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-2 mb-1">
            <div className="h-px w-8 bg-signal-dim/40" />
            <span className="text-xs uppercase tracking-[0.2em] text-signal-dim font-medium">
              Phase 1 · Diagnosis
            </span>
          </div>
          <h1 className="font-display text-3xl text-ink-950 font-medium mb-6">The Honest Assessment</h1>

          <div className="grid md:grid-cols-[220px_1fr] gap-8 items-start">
            <div className="flex flex-col items-center gap-6 md:sticky md:top-24">
              <ScoreGauge score={diagnosis.ats_score.overall} />
              {diagnosis.jd_alignment_percent !== null && (
                <div className="text-center">
                  <p className="text-xs uppercase tracking-wide text-ink-600">JD Alignment</p>
                  <p className="tabular text-2xl font-semibold text-ink-950">
                    {diagnosis.jd_alignment_percent}%
                  </p>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div className="rounded-xl border border-ink-600/15 bg-paper-50 p-5">
                <p className="text-sm text-ink-800 leading-relaxed">{diagnosis.summary}</p>
              </div>

              <div className="rounded-xl border border-ink-600/15 bg-white p-5">
                <p className="text-xs uppercase tracking-wide text-ink-600 font-medium mb-3">
                  Score Breakdown
                </p>
                <ScoreBreakdown score={diagnosis.ats_score} />
              </div>

              {diagnosis.flaws.length > 0 && (
                <div>
                  <p className="text-xs uppercase tracking-wide text-ink-600 font-medium mb-3">
                    Critical Flaws
                  </p>
                  <FlawsList flaws={diagnosis.flaws} />
                </div>
              )}
            </div>
          </div>

          {/* Collapsible panels */}
          <div className="grid md:grid-cols-3 gap-3 mt-6">
            <DiagnosticPanel
              title="The Good"
              icon={Smile}
              accentColor="#5B8C5A"
              count={diagnosis.content_analysis.strong_points.length}
              defaultOpen
            >
              <GoodPointsList items={diagnosis.content_analysis.strong_points} />
            </DiagnosticPanel>

            <DiagnosticPanel
              title="The Fluffy"
              icon={AlertTriangle}
              accentColor="#D98A3D"
              count={
                diagnosis.content_analysis.weak_points.length +
                diagnosis.content_analysis.fluffy_phrases.length
              }
            >
              <FluffyPhrasesList
                weakPoints={diagnosis.content_analysis.weak_points}
                fluffyPhrases={diagnosis.content_analysis.fluffy_phrases}
              />
            </DiagnosticPanel>

            <DiagnosticPanel
              title="Missing Keywords"
              icon={KeySquare}
              accentColor="#E8B23C"
              count={diagnosis.must_haves.length}
            >
              <MissingKeywordsList mustHaves={diagnosis.must_haves} />
            </DiagnosticPanel>
          </div>
        </motion.section>

        {/* ── THE AI PIVOT ─────────────────────────────────────────────────── */}
        {stage !== "revealed" && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-10 rounded-2xl border border-signal/30 bg-signal/[0.06] p-6 md:p-8 text-center"
          >
            <Sparkles className="w-7 h-7 text-signal-dim mx-auto mb-3" />
            <h2 className="font-display text-2xl text-ink-950 font-medium mb-2">
              Optimize using real-world successful patterns?
            </h2>
            <p className="text-sm text-ink-700 max-w-lg mx-auto mb-5 leading-relaxed">
              ResumeForge AI will research how strong resumes for{" "}
              <span className="font-medium text-ink-950">{upload.target_role}</span> are
              typically structured, then rewrite yours to match — without inventing a single
              fact you haven&apos;t already told it.
            </p>
            <button
              onClick={handleOptimize}
              disabled={stage === "optimizing"}
              className="inline-flex items-center gap-2 rounded-lg bg-ink-950 text-paper-50 px-6 py-3
                         text-sm font-medium hover:bg-ink-900 transition-colors disabled:opacity-60"
            >
              {stage === "optimizing" ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Researching & rewriting…
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" /> Yes, optimize my resume
                </>
              )}
            </button>
            {stage === "optimizing" && (
              <p className="text-xs text-ink-600 mt-3">
                Searching the web for accepted resume patterns, then applying the guardrailed rewrite agent…
              </p>
            )}
          </motion.div>
        )}

        {/* ── PHASE 2: THE REVEAL ──────────────────────────────────────────── */}
        <AnimatePresence>
          {stage === "revealed" && optimization && (
            <motion.section
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-12"
            >
              <div className="flex items-center gap-2 mb-1">
                <div className="h-px w-8 bg-signal-dim/40" />
                <span className="text-xs uppercase tracking-[0.2em] text-signal-dim font-medium">
                  Phase 2 · The Reveal
                </span>
              </div>
              <h2 className="font-display text-3xl text-ink-950 font-medium mb-6">
                Old vs. New, Side by Side
              </h2>

              {/* Score comparison strip */}
              <div className="flex items-center justify-center gap-10 mb-8 rounded-2xl border border-ink-600/15 bg-white p-6">
                <ScoreGauge score={diagnosis.ats_score.overall} label="BEFORE" size={140} />
                <CheckCircle2 className="w-6 h-6 text-verdict-good shrink-0" />
                <ScoreGauge
                  score={optimization.projected_ats_score.overall}
                  label="PROJECTED"
                  size={140}
                  delta={optimization.score_delta}
                />
              </div>

              <div className="rounded-xl border border-ink-600/15 bg-paper-50 p-5 mb-6">
                <p className="text-sm text-ink-800 leading-relaxed">{optimization.changes_summary}</p>
                {optimization.web_sources_used.length > 0 && (
                  <p className="text-xs text-ink-600 mt-2">
                    Informed by {optimization.web_sources_used.length} publicly available reference{" "}
                    {optimization.web_sources_used.length === 1 ? "source" : "sources"} for this role.
                  </p>
                )}
              </div>

              <DiffViewer diffLines={optimization.diff_lines} />

              {/* Export actions */}
              <div className="flex flex-wrap gap-3 mt-6 justify-center">
                <button
                  onClick={() => handleExport("pdf")}
                  disabled={exporting !== null}
                  className="inline-flex items-center gap-2 rounded-lg bg-ink-950 text-paper-50 px-5 py-2.5
                             text-sm font-medium hover:bg-ink-900 transition-colors disabled:opacity-60"
                >
                  {exporting === "pdf" ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4" />
                  )}
                  Download as PDF
                </button>
                <button
                  onClick={() => handleExport("docx")}
                  disabled={exporting !== null}
                  className="inline-flex items-center gap-2 rounded-lg border border-ink-600/30 text-ink-900 px-5 py-2.5
                             text-sm font-medium hover:bg-ink-950/5 transition-colors disabled:opacity-60"
                >
                  {exporting === "docx" ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4" />
                  )}
                  Download as DOCX
                </button>
              </div>

              {/* ── PHASE 3: SKILL GAP ROADMAP ─────────────────────────────── */}
              <div className="mt-14">
                <div className="flex items-center gap-2 mb-1">
                  <div className="h-px w-8 bg-signal-dim/40" />
                  <span className="text-xs uppercase tracking-[0.2em] text-signal-dim font-medium">
                    Phase 3 · The Roadmap
                  </span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <Map className="w-5 h-5 text-ink-950" />
                  <h2 className="font-display text-3xl text-ink-950 font-medium">
                    Skill Gap Closure Plan
                  </h2>
                </div>
                <p className="text-sm text-ink-700 mb-6 max-w-2xl">
                  These keywords mattered for the role but had no basis in your resume — so we
                  didn&apos;t add them. Here&apos;s how to legitimately close each gap.
                </p>
                <SkillGapRoadmap items={optimization.skill_gap_plan} />
              </div>
            </motion.section>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
