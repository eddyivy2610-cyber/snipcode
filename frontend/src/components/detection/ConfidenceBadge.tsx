"use client";

import React from "react";

interface ConfidenceBadgeProps {
  confidence: number; // 0 to 1
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence }) => {
  const percent = Math.round(confidence * 100);

  let colorClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
  if (percent < 60) {
    colorClass = "bg-rose-500/10 text-rose-400 border-rose-500/20";
  } else if (percent < 80) {
    colorClass = "bg-amber-500/10 text-amber-400 border-amber-500/20";
  }

  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${colorClass}`}>
      {percent}%
    </span>
  );
};
