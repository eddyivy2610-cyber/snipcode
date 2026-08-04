"use client";

import React from "react";
import { ResponsiveSwitcher, ViewportMode } from "./ResponsiveSwitcher";
import { RotateCw, RefreshCw, Lock, ExternalLink } from "lucide-react";
import { toast } from "sonner";

interface PreviewToolbarProps {
  isDarkTheme: boolean;
  mode: ViewportMode;
  onSelectMode: (mode: ViewportMode) => void;
  onReload: () => void;
}

export const PreviewToolbar: React.FC<PreviewToolbarProps> = ({
  isDarkTheme,
  mode,
  onSelectMode,
  onReload,
}) => {
  return (
    <div className="h-14 px-5 border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xl flex items-center justify-between gap-4">
      {/* Mock Browser Traffic Lights & Reload Buttons */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-rose-500/80 inline-block" />
          <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
          <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
        </div>

        <div className="flex items-center gap-1 pl-2 border-l border-zinc-800">
          <button
            onClick={() => {
              onReload();
              toast.success("Live preview reloaded!");
            }}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-900 transition-all cursor-pointer"
            title="Reload Preview"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => {
              onReload();
              toast.success("Hard refreshed iframe sandbox!");
            }}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-900 transition-all cursor-pointer"
            title="Hard Refresh Sandbox"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Center Mock URL Bar */}
      <div className="flex-1 max-w-md mx-auto">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-900/90 border border-zinc-800 text-xs font-mono text-zinc-400">
          <Lock className="w-3 h-3 text-emerald-400" />
          <span className="truncate">http://localhost:3000/sandbox/preview.html</span>
        </div>
      </div>

      {/* Right Responsive Switcher */}
      <div className="flex items-center gap-3">
        <ResponsiveSwitcher mode={mode} onSelectMode={onSelectMode} />
      </div>
    </div>
  );
};
