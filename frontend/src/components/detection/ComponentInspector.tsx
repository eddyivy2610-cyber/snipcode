"use client";

import React from "react";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { Layers, Box, Move, Palette, Activity } from "lucide-react";

interface ComponentInspectorProps {
  isDarkTheme: boolean;
  selectedBox: any | null;
}

export const ComponentInspector: React.FC<ComponentInspectorProps> = ({
  isDarkTheme,
  selectedBox,
}) => {
  if (!selectedBox) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center text-zinc-500 text-xs p-6 text-center gap-2">
        <Box className="w-8 h-8 opacity-40 text-purple-400" />
        <p className="font-semibold text-zinc-300">No Component Selected</p>
        <p className="text-[11px] text-zinc-500">Click any bounding box or list item to inspect its 4 Pillars</p>
      </div>
    );
  }

  const { type, bbox, confidence, text, label, placeholder, action, input_type } = selectedBox;

  return (
    <div className="flex flex-col h-full overflow-y-auto p-4 space-y-4 no-scrollbar">
      {/* Element Header */}
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800/40">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400">
            Selected Component
          </span>
          <h3 className="text-base font-bold text-zinc-100 flex items-center gap-2">
            {type}
          </h3>
        </div>
        <ConfidenceBadge confidence={confidence} />
      </div>

      {/* Pillar 1: Content */}
      <div className={`p-3 rounded-xl border space-y-2 ${isDarkTheme ? "bg-zinc-900/60 border-zinc-800" : "bg-white border-zinc-200"}`}>
        <h4 className="text-xs font-bold text-purple-400 flex items-center gap-1.5">
          <Box className="w-3.5 h-3.5" /> Content Pillar
        </h4>
        <div className="space-y-1 text-xs font-mono">
          {text && <div><span className="text-zinc-500">text:</span> "{text}"</div>}
          {label && <div><span className="text-zinc-500">label:</span> "{label}"</div>}
          {placeholder && <div><span className="text-zinc-500">placeholder:</span> "{placeholder}"</div>}
          {input_type && <div><span className="text-zinc-500">type:</span> "{input_type}"</div>}
        </div>
      </div>

      {/* Pillar 2: Layout */}
      <div className={`p-3 rounded-xl border space-y-2 ${isDarkTheme ? "bg-zinc-900/60 border-zinc-800" : "bg-white border-zinc-200"}`}>
        <h4 className="text-xs font-bold text-blue-400 flex items-center gap-1.5">
          <Move className="w-3.5 h-3.5" /> Layout Pillar
        </h4>
        <div className="space-y-1 text-xs font-mono text-zinc-300">
          <div><span className="text-zinc-500">bbox:</span> [{bbox.join(", ")}]</div>
          <div><span className="text-zinc-500">width:</span> {bbox[3] - bbox[1]}px</div>
          <div><span className="text-zinc-500">height:</span> {bbox[2] - bbox[0]}px</div>
        </div>
      </div>

      {/* Pillar 3: Style */}
      <div className={`p-3 rounded-xl border space-y-2 ${isDarkTheme ? "bg-zinc-900/60 border-zinc-800" : "bg-white border-zinc-200"}`}>
        <h4 className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
          <Palette className="w-3.5 h-3.5" /> Style Pillar
        </h4>
        <div className="space-y-1 text-xs font-mono text-zinc-300">
          <div><span className="text-zinc-500">variant:</span> standard</div>
          <div><span className="text-zinc-500">radius:</span> medium (8px)</div>
          <div><span className="text-zinc-500">theme:</span> dark</div>
        </div>
      </div>

      {/* Pillar 4: Behavior */}
      <div className={`p-3 rounded-xl border space-y-2 ${isDarkTheme ? "bg-zinc-900/60 border-zinc-800" : "bg-white border-zinc-200"}`}>
        <h4 className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5" /> Behavior Pillar
        </h4>
        <div className="space-y-1 text-xs font-mono text-zinc-300">
          <div><span className="text-zinc-500">action:</span> {action || `submit_${type.toLowerCase()}`}</div>
        </div>
      </div>
    </div>
  );
};
