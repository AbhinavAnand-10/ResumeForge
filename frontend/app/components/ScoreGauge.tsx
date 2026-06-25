"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface ScoreGaugeProps {
  score: number;
  label?: string;
  size?: number;
  delta?: number | null;
}

function scoreColor(score: number): string {
  if (score >= 75) return "#5B8C5A"; // verdict-good
  if (score >= 50) return "#D98A3D"; // verdict-warn
  return "#C0533D"; // verdict-bad
}

function scoreVerdict(score: number): string {
  if (score >= 85) return "Strong";
  if (score >= 70) return "Competitive";
  if (score >= 50) return "Needs Work";
  return "At Risk";
}

export function ScoreGauge({ score, label = "ATS SCORE", size = 180, delta = null }: ScoreGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const radius = size / 2 - 14;
  const circumference = 2 * Math.PI * radius;
  const color = scoreColor(score);

  useEffect(() => {
    const timeout = setTimeout(() => setAnimatedScore(score), 100);
    return () => clearTimeout(timeout);
  }, [score]);

  const offset = circumference - (animatedScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#E6DFCE"
            strokeWidth={10}
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={10}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="tabular text-4xl font-semibold text-ink-950"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {Math.round(animatedScore)}
          </motion.span>
          <span className="text-[10px] tracking-[0.18em] text-ink-600 font-medium uppercase mt-0.5">
            / 100
          </span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-xs tracking-[0.14em] text-ink-600 uppercase font-medium">{label}</p>
        <p className="text-sm font-semibold mt-0.5" style={{ color }}>
          {scoreVerdict(score)}
        </p>
        {delta !== null && (
          <p
            className={`text-xs tabular mt-1 font-medium ${
              delta > 0 ? "text-verdict-good" : delta < 0 ? "text-verdict-bad" : "text-ink-600"
            }`}
          >
            {delta > 0 ? "+" : ""}
            {delta} pts
          </p>
        )}
      </div>
    </div>
  );
}
