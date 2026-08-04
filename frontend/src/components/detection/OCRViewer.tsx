"use client";

import React from "react";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { Type, Sparkles } from "lucide-react";

interface OCRViewerProps {
  isDarkTheme: boolean;
  detections: any[];
}

export const OCRViewer: React.FC<OCRViewerProps> = ({ isDarkTheme, detections }) => {
  const ocrItems = detections.filter((d) => d.text && d.text.trim().length > 0);

  return (
    <div className="flex flex-col h-full overflow-hidden p-3 space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800/40">
        <h3 className="text-xs font-semibold flex items-center gap-1.5 text-purple-400">
          <Type className="w-3.5 h-3.5" /> EasyOCR Extracted Text Snippets ({ocrItems.length})
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 no-scrollbar">
        {ocrItems.length > 0 ? (
          ocrItems.map((item, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-xl border flex items-center justify-between ${
                isDarkTheme ? "bg-zinc-900/60 border-zinc-800/80" : "bg-white border-zinc-200"
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span className="w-6 h-6 rounded-md bg-purple-500/10 text-purple-400 font-mono text-[10px] font-bold flex items-center justify-center">
                  #{idx + 1}
                </span>
                <div>
                  <p className="text-xs font-semibold text-zinc-100">"{item.text}"</p>
                  <p className="text-[10px] text-zinc-500 font-mono">
                    Parent: {item.type}
                  </p>
                </div>
              </div>

              <ConfidenceBadge confidence={item.text_confidence || item.confidence} />
            </div>
          ))
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-zinc-500 text-xs gap-2">
            <Type className="w-6 h-6 opacity-40" />
            <span>No OCR text recognized yet</span>
          </div>
        )}
      </div>
    </div>
  );
};
