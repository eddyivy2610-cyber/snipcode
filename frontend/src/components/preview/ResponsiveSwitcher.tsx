"use client";

import React from "react";
import { Monitor, Tablet, Smartphone } from "lucide-react";

export type ViewportMode = "desktop" | "tablet" | "mobile";

interface ResponsiveSwitcherProps {
  mode: ViewportMode;
  onSelectMode: (mode: ViewportMode) => void;
}

export const ResponsiveSwitcher: React.FC<ResponsiveSwitcherProps> = ({
  mode,
  onSelectMode,
}) => {
  return (
    <div className="p-1 rounded-xl bg-zinc-900/90 border border-zinc-800 flex items-center gap-1 shadow-inner">
      <button
        onClick={() => onSelectMode("desktop")}
        className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
          mode === "desktop"
            ? "bg-purple-600 text-white shadow-md shadow-purple-600/20"
            : "text-zinc-400 hover:text-zinc-200"
        }`}
      >
        <Monitor className="w-3.5 h-3.5" /> Desktop <span className="text-[10px] opacity-70 font-mono">1440px</span>
      </button>
      <button
        onClick={() => onSelectMode("tablet")}
        className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
          mode === "tablet"
            ? "bg-purple-600 text-white shadow-md shadow-purple-600/20"
            : "text-zinc-400 hover:text-zinc-200"
        }`}
      >
        <Tablet className="w-3.5 h-3.5" /> Tablet <span className="text-[10px] opacity-70 font-mono">768px</span>
      </button>
      <button
        onClick={() => onSelectMode("mobile")}
        className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
          mode === "mobile"
            ? "bg-purple-600 text-white shadow-md shadow-purple-600/20"
            : "text-zinc-400 hover:text-zinc-200"
        }`}
      >
        <Smartphone className="w-3.5 h-3.5" /> Mobile <span className="text-[10px] opacity-70 font-mono">375px</span>
      </button>
    </div>
  );
};
