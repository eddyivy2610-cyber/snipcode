"use client";

import React, { useState } from "react";
import { DetectionCanvas } from "./DetectionCanvas";
import { DetectionList } from "./DetectionList";
import { OCRViewer } from "./OCRViewer";
import { ComponentInspector } from "./ComponentInspector";
import { Layers, Box, Type, Eye, ChevronRight } from "lucide-react";

interface DetectionViewerProps {
  isDarkTheme: boolean;
  uploadedImage: string;
  detections: any[];
  irTree: any;
}

export const DetectionViewer: React.FC<DetectionViewerProps> = ({
  isDarkTheme,
  uploadedImage,
  detections,
  irTree,
}) => {
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const [showBoxes, setShowBoxes] = useState(true);
  const [activeTab, setActiveTab] = useState<"list" | "ocr" | "inspector">("list");

  const selectedBox = selectedIdx !== null ? detections[selectedIdx] : null;

  return (
    <div className="flex-1 flex h-full overflow-hidden">
      {/* Central Canvas View (DetectionCanvas + BoundingBox) */}
      <div className="flex-1 flex flex-col h-full p-4 border-r border-zinc-800/80 overflow-hidden">
        <DetectionCanvas
          uploadedImage={uploadedImage}
          detections={detections}
          selectedId={selectedIdx}
          onSelectBox={(idx) => setSelectedIdx(idx)}
          showBoxes={showBoxes}
          onToggleShowBoxes={() => setShowBoxes(!showBoxes)}
        />
      </div>

      {/* Right Pipeline Inspection Drawer (DetectionList, OCRViewer, ComponentInspector) */}
      <div className="w-96 flex flex-col h-full bg-zinc-950/60 border-l border-zinc-800/80 overflow-hidden">
        {/* Pipeline Tabs */}
        <div className="flex items-center justify-between p-3 border-b border-zinc-800/80">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setActiveTab("list")}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                activeTab === "list"
                  ? "bg-purple-600 text-white shadow-sm"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              <Box className="w-3.5 h-3.5" /> Bounding Boxes ({detections.length})
            </button>
            <button
              onClick={() => setActiveTab("ocr")}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                activeTab === "ocr"
                  ? "bg-purple-600 text-white shadow-sm"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              <Type className="w-3.5 h-3.5" /> OCR
            </button>
            <button
              onClick={() => setActiveTab("inspector")}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                activeTab === "inspector"
                  ? "bg-purple-600 text-white shadow-sm"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              <Layers className="w-3.5 h-3.5" /> 4-Pillars
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          {activeTab === "list" && (
            <DetectionList
              isDarkTheme={isDarkTheme}
              detections={detections}
              selectedId={selectedIdx}
              onSelectBox={(idx) => {
                setSelectedIdx(idx);
                setActiveTab("inspector");
              }}
            />
          )}

          {activeTab === "ocr" && (
            <OCRViewer isDarkTheme={isDarkTheme} detections={detections} />
          )}

          {activeTab === "inspector" && (
            <ComponentInspector isDarkTheme={isDarkTheme} selectedBox={selectedBox} />
          )}
        </div>
      </div>
    </div>
  );
};
