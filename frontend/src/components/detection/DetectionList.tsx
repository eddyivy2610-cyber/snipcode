"use client";

import React, { useState } from "react";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { Search, Filter, Layers, Type, FormInput, Box } from "lucide-react";

interface DetectionListProps {
  isDarkTheme: boolean;
  detections: any[];
  selectedId: number | null;
  onSelectBox: (idx: number) => void;
}

export const DetectionList: React.FC<DetectionListProps> = ({
  isDarkTheme,
  detections,
  selectedId,
  onSelectBox,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");

  const filteredDetections = detections.filter((item) => {
    const matchesSearch =
      item.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.text && item.text.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesFilter = filterType === "all" || item.type.toLowerCase() === filterType.toLowerCase();
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Search & Filter Header */}
      <div className="p-3 border-b border-zinc-800/40 space-y-2">
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search detected elements..."
            className={`w-full pl-8 pr-3 py-1.5 rounded-xl text-xs border outline-none ${
              isDarkTheme
                ? "bg-zinc-900/80 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus:border-purple-500/50"
                : "bg-white border-zinc-200 text-zinc-900 placeholder:text-zinc-400"
            }`}
          />
        </div>

        <div className="flex items-center gap-1 overflow-x-auto no-scrollbar">
          {["all", "button", "input", "text", "form"].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-semibold capitalize transition-all ${
                filterType === type
                  ? "bg-purple-600 text-white"
                  : "bg-zinc-800/60 text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Detections List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 no-scrollbar">
        {filteredDetections.map((item, idx) => {
          const isSelected = selectedId === idx;

          return (
            <div
              key={idx}
              onClick={() => onSelectBox(idx)}
              className={`p-2.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                isSelected
                  ? "bg-purple-500/15 border-purple-500/50 shadow-sm"
                  : isDarkTheme
                  ? "bg-zinc-900/60 border-zinc-800/80 hover:border-zinc-700"
                  : "bg-white border-zinc-200 hover:border-zinc-300"
              }`}
            >
              <div className="flex items-center gap-2.5 overflow-hidden">
                <div className="w-7 h-7 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center flex-shrink-0">
                  <Box className="w-3.5 h-3.5" />
                </div>
                <div className="truncate">
                  <h4 className="text-xs font-bold text-zinc-200 flex items-center gap-1.5">
                    {item.type}
                  </h4>
                  {item.text && (
                    <p className="text-[11px] text-zinc-400 truncate">"{item.text}"</p>
                  )}
                </div>
              </div>

              <ConfidenceBadge confidence={item.confidence} />
            </div>
          );
        })}
      </div>
    </div>
  );
};
