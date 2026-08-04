"use client";

import React from "react";
import { StepStatus, StatusType } from "./StepStatus";
import { LucideIcon } from "lucide-react";

interface PipelineStepProps {
  isDarkTheme: boolean;
  name: string;
  description: string;
  icon: LucideIcon;
  status: StatusType;
  durationMs?: number;
  outputSummary?: string;
  isLast?: boolean;
}

export const PipelineStep: React.FC<PipelineStepProps> = ({
  isDarkTheme,
  name,
  description,
  icon: Icon,
  status,
  durationMs,
  outputSummary,
  isLast = false,
}) => {
  return (
    <div className="relative flex flex-col items-center">
      {/* Step Card */}
      <div
        className={`w-full p-3.5 rounded-2xl border transition-all duration-300 shadow-md ${
          status === "running"
            ? "border-purple-500 bg-purple-500/10 shadow-purple-500/20 ring-1 ring-purple-500/40"
            : status === "completed"
            ? isDarkTheme
              ? "bg-zinc-900/80 border-zinc-800 hover:border-zinc-700"
              : "bg-white border-zinc-200"
            : isDarkTheme
            ? "bg-zinc-950/40 border-zinc-800/40 opacity-50"
            : "bg-zinc-100/50 border-zinc-200/50 opacity-50"
        }`}
      >
        <div className="flex items-center justify-between gap-3 mb-1.5">
          <div className="flex items-center gap-2.5">
            <div
              className={`w-8 h-8 rounded-xl border flex items-center justify-center flex-shrink-0 ${
                status === "completed"
                  ? "bg-purple-500/10 border-purple-500/30 text-purple-400"
                  : status === "running"
                  ? "bg-purple-600 text-white border-purple-500 animate-pulse"
                  : "bg-zinc-800 border-zinc-700 text-zinc-500"
              }`}
            >
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-zinc-100">{name}</h4>
              <p className="text-[10px] text-zinc-500">{description}</p>
            </div>
          </div>

          <StepStatus status={status} />
        </div>

        {/* Step Execution Info */}
        {(durationMs !== undefined || outputSummary) && (
          <div className="mt-2 pt-2 border-t border-zinc-800/40 flex items-center justify-between text-[10px] font-mono text-zinc-400">
            {outputSummary && <span className="truncate max-w-[200px] text-purple-300">{outputSummary}</span>}
            {durationMs !== undefined && <span className="text-zinc-500">{durationMs}ms</span>}
          </div>
        )}
      </div>

      {/* Vertical Connecting Flowchart Line */}
      {!isLast && (
        <div className="my-1.5 flex flex-col items-center">
          <div className={`w-0.5 h-4 transition-colors ${status === "completed" ? "bg-purple-500" : "bg-zinc-800"}`} />
          <div className={`w-1.5 h-1.5 rotate-45 border-r border-b ${status === "completed" ? "border-purple-500" : "border-zinc-800"}`} />
        </div>
      )}
    </div>
  );
};
