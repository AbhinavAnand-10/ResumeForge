"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { DiffLine } from "@/lib/api";
import { Plus, Minus, Pencil } from "lucide-react";

interface DiffViewerProps {
  diffLines: DiffLine[];
}

const CHANGE_STYLES: Record<string, { bgOld: string; bgNew: string; icon: typeof Plus | null }> = {
  unchanged: { bgOld: "", bgNew: "", icon: null },
  modified: { bgOld: "bg-verdict-bad/[0.07]", bgNew: "bg-verdict-good/[0.08]", icon: Pencil },
  added: { bgOld: "", bgNew: "bg-verdict-good/[0.08]", icon: Plus },
  removed: { bgOld: "bg-verdict-bad/[0.07]", bgNew: "", icon: Minus },
};

export function DiffViewer({ diffLines }: DiffViewerProps) {
  return (
    <div className="rounded-xl border border-ink-600/15 overflow-hidden bg-white">
      {/* Header row */}
      <div className="grid grid-cols-2 border-b border-ink-600/15 bg-ink-950 text-paper-50">
        <div className="px-4 py-2.5 text-xs font-mono uppercase tracking-wider border-r border-paper-50/10">
          Original
        </div>
        <div className="px-4 py-2.5 text-xs font-mono uppercase tracking-wider">
          AI-Optimized
        </div>
      </div>

      {/* Diff body */}
      <div className="diff-scroll max-h-[560px] overflow-y-auto font-mono text-[13px] leading-relaxed">
        {diffLines.map((line, idx) => {
          const style = CHANGE_STYLES[line.change_type] || CHANGE_STYLES.unchanged;
          const Icon = style.icon;

          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: Math.min(idx * 0.008, 0.4) }}
              className="grid grid-cols-2 border-b border-ink-600/[0.06] group"
            >
              {/* Original side */}
              <div
                className={cn(
                  "px-4 py-1.5 border-r border-ink-600/10 whitespace-pre-wrap break-words text-ink-800",
                  style.bgOld
                )}
              >
                <span className="text-ink-600/40 select-none mr-3 tabular text-xs">
                  {line.line_no + 1}
                </span>
                {line.change_type === "removed" && (
                  <Minus className="inline w-3 h-3 text-verdict-bad mr-1 -mt-0.5" />
                )}
                {line.original || (
                  <span className="text-ink-600/30 italic">—</span>
                )}
              </div>

              {/* Optimized side */}
              <div
                className={cn(
                  "px-4 py-1.5 whitespace-pre-wrap break-words text-ink-900",
                  style.bgNew
                )}
              >
                <span className="text-ink-600/40 select-none mr-3 tabular text-xs">
                  {line.line_no + 1}
                </span>
                {line.change_type === "added" && (
                  <Plus className="inline w-3 h-3 text-verdict-good mr-1 -mt-0.5" />
                )}
                {line.change_type === "modified" && (
                  <Pencil className="inline w-3 h-3 text-signal mr-1 -mt-0.5" />
                )}
                {line.optimized || (
                  <span className="text-ink-600/30 italic">—</span>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
