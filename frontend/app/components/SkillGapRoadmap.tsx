"use client";

import { motion } from "framer-motion";
import { Clock, ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { SkillGapItem } from "@/lib/api";

const PRIORITY_STYLE: Record<string, string> = {
  high: "bg-verdict-bad/10 text-verdict-bad border-verdict-bad/20",
  medium: "bg-verdict-warn/10 text-verdict-warn border-verdict-warn/20",
  low: "bg-ink-600/10 text-ink-600 border-ink-600/20",
};

export function SkillGapRoadmap({ items }: { items: SkillGapItem[] }) {
  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-verdict-good/20 bg-verdict-good/5 p-6 text-center">
        <p className="text-sm text-ink-800">
          No legitimate skill gaps to flag — every relevant keyword had a basis in your existing
          experience.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06 }}
          className="rounded-xl border border-ink-600/15 bg-paper-50 p-4"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="font-mono font-medium text-ink-950 text-sm">{item.skill}</span>
                <span
                  className={cn(
                    "text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded-full border font-medium",
                    PRIORITY_STYLE[item.priority] || PRIORITY_STYLE.low
                  )}
                >
                  {item.priority}
                </span>
              </div>
              <p className="text-sm text-ink-800 leading-relaxed">{item.suggested_action}</p>

              {item.resources.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2.5">
                  {item.resources.map((res, j) => (
                    <span
                      key={j}
                      className="text-xs px-2 py-0.5 rounded-md bg-ink-950/[0.04] text-ink-700 flex items-center gap-1"
                    >
                      {res} <ArrowUpRight className="w-2.5 h-2.5" />
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="flex items-center gap-1 text-xs text-ink-600 whitespace-nowrap shrink-0">
              <Clock className="w-3 h-3" />
              {item.estimated_time}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
