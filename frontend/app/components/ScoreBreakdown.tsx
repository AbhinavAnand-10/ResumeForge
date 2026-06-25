"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ATSScore, FlawItem } from "@/lib/api";
import { AlertOctagon, AlertTriangle, Info } from "lucide-react";

const SUBSCORE_LABELS: { key: keyof ATSScore; label: string }[] = [
  { key: "keyword_match", label: "Keyword Match" },
  { key: "formatting", label: "ATS Formatting" },
  { key: "sections_completeness", label: "Section Completeness" },
  { key: "readability", label: "Readability" },
];

function barColor(value: number): string {
  if (value >= 75) return "#5B8C5A";
  if (value >= 50) return "#D98A3D";
  return "#C0533D";
}

export function ScoreBreakdown({ score }: { score: ATSScore }) {
  return (
    <div className="space-y-3.5 w-full">
      {SUBSCORE_LABELS.map(({ key, label }, i) => {
        const value = score[key] as number;
        return (
          <div key={key}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-ink-700 font-medium">{label}</span>
              <span className="tabular text-ink-600">{value}</span>
            </div>
            <div className="h-1.5 rounded-full bg-ink-600/10 overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ backgroundColor: barColor(value) }}
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                transition={{ duration: 0.8, delay: i * 0.08, ease: "easeOut" }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

const SEVERITY_ICON = { critical: AlertOctagon, moderate: AlertTriangle, minor: Info };
const SEVERITY_COLOR = { critical: "#C0533D", moderate: "#D98A3D", minor: "#8B8F89" };

export function FlawsList({ flaws }: { flaws: FlawItem[] }) {
  if (flaws.length === 0) {
    return <p className="text-sm text-ink-600 italic">No critical flaws detected.</p>;
  }

  const sorted = [...flaws].sort((a, b) => {
    const order = { critical: 0, moderate: 1, minor: 2 };
    return (order[a.severity] ?? 3) - (order[b.severity] ?? 3);
  });

  return (
    <div className="space-y-2.5">
      {sorted.map((flaw, i) => {
        const Icon = SEVERITY_ICON[flaw.severity] || Info;
        const color = SEVERITY_COLOR[flaw.severity] || "#8B8F89";
        return (
          <div
            key={i}
            className="flex gap-3 rounded-lg border border-ink-600/10 p-3 bg-paper-50"
          >
            <Icon className="w-4 h-4 shrink-0 mt-0.5" style={{ color }} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-mono text-ink-600">{flaw.location}</span>
                <span
                  className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded-full font-medium"
                  style={{ backgroundColor: `${color}18`, color }}
                >
                  {flaw.severity}
                </span>
              </div>
              <p className="text-sm text-ink-900 mt-1">{flaw.description}</p>
              <p className="text-xs text-ink-600 mt-0.5">→ {flaw.suggestion}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
