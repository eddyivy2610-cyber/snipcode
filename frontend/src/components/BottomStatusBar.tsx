"use client";

import React from "react";
import { Activity, ShieldCheck, Sparkles, CheckCircle2 } from "lucide-react";

interface BottomStatusBarProps {
  isDarkTheme: boolean;
  detectionCount: number;
}

export const BottomStatusBar: React.FC<BottomStatusBarProps> = ({
  isDarkTheme,
  detectionCount,
}) => {
  return (
    <footer
      className={`h-7 px-5 border-t flex items-center justify-between text-[11px] font-mono transition-colors duration-300 ${
        isDarkTheme
          ? "bg-zinc-950 border-zinc-800/80 text-zinc-400"
          : "bg-zinc-100 border-zinc-200 text-zinc-600"
      }`}
    >
      <div className="flex items-center gap-4">
        <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Backend API: Online ({process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"})
        </span>
        <span className="text-zinc-600">|</span>
        <span>YOLO + EasyOCR Pipeline</span>
      </div>

      <div className="flex items-center gap-4">
        {detectionCount > 0 && (
          <span className="text-purple-400 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> {detectionCount} Boxes Detected
          </span>
        )}
        <span className="text-zinc-600">|</span>
        <span className="text-zinc-400">IR v4.0 AST Schema</span>
      </div>
    </footer>
  );
};
