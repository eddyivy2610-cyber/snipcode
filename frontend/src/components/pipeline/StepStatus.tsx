"use client";

import React from "react";
import { CheckCircle2, Clock, Loader2, AlertCircle } from "lucide-react";

export type StatusType = "pending" | "running" | "completed" | "failed";

interface StepStatusProps {
  status: StatusType;
}

export const StepStatus: React.FC<StepStatusProps> = ({ status }) => {
  switch (status) {
    case "completed":
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
          <CheckCircle2 className="w-3 h-3" /> Done
        </span>
      );
    case "running":
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center gap-1 animate-pulse">
          <Loader2 className="w-3 h-3 animate-spin" /> Running
        </span>
      );
    case "failed":
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center gap-1">
          <AlertCircle className="w-3 h-3" /> Error
        </span>
      );
    case "pending":
    default:
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-zinc-800 text-zinc-500 border border-zinc-700/50 flex items-center gap-1">
          <Clock className="w-3 h-3" /> Waiting
        </span>
      );
  }
};
