"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, CheckCircle2, AlertTriangle, KeySquare, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface DiagnosticPanelProps {
  title: string;
  icon: LucideIcon;
  accentColor: string;
  count: number;
  defaultOpen?: boolean;
  children: React.ReactNode;
}

export function DiagnosticPanel({
  title,
  icon: Icon,
  accentColor,
  count,
  defaultOpen = false,
  children,
}: DiagnosticPanelProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="rounded-xl border border-ink-600/15 bg-paper-50 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-ink-950/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div
            className="rounded-lg p-1.5"
            style={{ backgroundColor: `${accentColor}14`, color: accentColor }}
          >
            <Icon className="w-4 h-4" />
          </div>
          <span className="font-medium text-ink-900">{title}</span>
          <span className="text-xs tabular text-ink-600 bg-ink-600/10 rounded-full px-2 py-0.5">
            {count}
          </span>
        </div>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown className="w-4 h-4 text-ink-600" />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-1">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Pre-built content renderers for each panel type ─────────────────────────

export function GoodPointsList({ items }: { items: string[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-ink-600 italic">No standout strengths identified yet.</p>;
  }
  return (
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex gap-2 text-sm text-ink-800">
          <CheckCircle2 className="w-4 h-4 text-verdict-good shrink-0 mt-0.5" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function FluffyPhrasesList({
  weakPoints,
  fluffyPhrases,
}: {
  weakPoints: string[];
  fluffyPhrases: string[];
}) {
  if (weakPoints.length === 0 && fluffyPhrases.length === 0) {
    return <p className="text-sm text-ink-600 italic">No fluff detected — refreshingly direct.</p>;
  }
  return (
    <div className="space-y-3">
      {fluffyPhrases.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-wide text-ink-600 font-medium mb-1.5">
            Generic phrases to cut
          </p>
          <div className="flex flex-wrap gap-1.5">
            {fluffyPhrases.map((phrase, i) => (
              <span
                key={i}
                className="text-xs px-2.5 py-1 rounded-md bg-verdict-warn/10 text-verdict-warn font-medium line-through"
              >
                {phrase}
              </span>
            ))}
          </div>
        </div>
      )}
      {weakPoints.length > 0 && (
        <ul className="space-y-2 pt-1">
          {weakPoints.map((item, i) => (
            <li key={i} className="flex gap-2 text-sm text-ink-800">
              <AlertTriangle className="w-4 h-4 text-verdict-warn shrink-0 mt-0.5" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function MissingKeywordsList({
  mustHaves,
}: {
  mustHaves: { keyword: string; reason: string; example_usage: string }[];
}) {
  if (mustHaves.length === 0) {
    return <p className="text-sm text-ink-600 italic">No critical keyword gaps found.</p>;
  }
  return (
    <div className="space-y-3">
      {mustHaves.map((item, i) => (
        <div key={i} className="rounded-lg border border-ink-600/10 p-3 bg-ink-950/[0.015]">
          <div className="flex items-center gap-2 mb-1">
            <KeySquare className="w-3.5 h-3.5 text-signal" />
            <span className="font-mono text-sm font-medium text-ink-950">{item.keyword}</span>
          </div>
          <p className="text-xs text-ink-700 leading-relaxed">{item.reason}</p>
        </div>
      ))}
    </div>
  );
}
