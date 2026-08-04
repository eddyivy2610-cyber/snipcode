"use client";

import React from "react";
import { Activity, Zap } from "lucide-react";

interface PerformanceChartProps {
  isDarkTheme: boolean;
  totalDurationMs: number;
  stepMetrics: { name: string; durationMs: number; color: string }[];
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({
  isDarkTheme,
  totalDurationMs,
  stepMetrics,
}) => {
  return (
    <div
      className={`p-4 rounded-2xl border backdrop-blur-xl transition-all shadow-md ${
        isDarkTheme ? "bg-zinc-900/60 border-zinc-800" : "bg-white border-zinc-200"
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold flex items-center gap-1.5 text-purple-400">
          <Activity className="w-3.5 h-3.5" /> Pipeline Performance & Latency Breakdown
        </h3>
        <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1">
          <Zap className="w-3 h-3" /> Total: {totalDurationMs}ms
        </span>
      </div>

      {/* Segmented Progress Bar */}
      <div className="w-full h-3 rounded-full bg-zinc-950 overflow-hidden flex p-0.5 border border-zinc-800">
        {stepMetrics.map((m, idx) => {
          const percentage = totalDurationMs > 0 ? (m.durationMs / totalDurationMs) * 100 : 0;
          return (
            <div
              key={idx}
              style={{ width: `${Math.max(percentage, 2)}%` }}
              className={`h-full transition-all duration-300 ${m.color}`}
              title={`${m.name}: ${m.durationMs}ms (${Math.round(percentage)}%)`}
            />
          );
        })}
      </div>

      {/* Legend Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3 text-[10px] font-mono">
        {stepMetrics.map((m, idx) => (
          <div key={idx} className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${m.color}`} />
            <span className="text-zinc-400">{m.name}:</span>
            <span className="font-semibold text-zinc-200">{m.durationMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
};
