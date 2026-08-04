"use client";

import React from "react";
import { ConfidenceBadge } from "./ConfidenceBadge";

interface BoundingBoxProps {
  id: string;
  type: string;
  bbox: [number, number, number, number]; // [ymin, xmin, ymax, xmax]
  confidence: number;
  text?: string;
  isSelected?: boolean;
  onSelect?: () => void;
}

export const BoundingBox: React.FC<BoundingBoxProps> = ({
  type,
  bbox,
  confidence,
  text,
  isSelected,
  onSelect,
}) => {
  const [ymin, xmin, ymax, xmax] = bbox;
  const width = xmax - xmin;
  const height = ymax - ymin;

  return (
    <div
      onClick={onSelect}
      style={{
        top: `${ymin}px`,
        left: `${xmin}px`,
        width: `${width}px`,
        height: `${height}px`,
      }}
      className={`absolute cursor-pointer border rounded-lg transition-all duration-200 pointer-events-auto flex flex-col justify-between p-1 group ${
        isSelected
          ? "border-purple-400 bg-purple-500/20 ring-2 ring-purple-500/50 z-30 scale-[1.01]"
          : "border-purple-500/60 bg-purple-500/10 hover:border-purple-400 hover:bg-purple-500/20 z-10"
      }`}
    >
      {/* Label Badge */}
      <div className="flex items-center justify-between gap-1 overflow-hidden pointer-events-none">
        <span className="px-1.5 py-0.5 rounded bg-zinc-950/90 text-purple-300 font-mono text-[9px] font-bold border border-purple-500/30 truncate">
          {type} {text ? `"${text}"` : ""}
        </span>
        <ConfidenceBadge confidence={confidence} />
      </div>
    </div>
  );
};
