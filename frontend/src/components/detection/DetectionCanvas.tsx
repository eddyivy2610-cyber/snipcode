"use client";

import React from "react";
import { BoundingBox } from "./BoundingBox";
import { Eye, EyeOff } from "lucide-react";

interface DetectionCanvasProps {
  uploadedImage: string;
  detections: any[];
  selectedId: number | null;
  onSelectBox: (idx: number) => void;
  showBoxes: boolean;
  onToggleShowBoxes: () => void;
}

export const DetectionCanvas: React.FC<DetectionCanvasProps> = ({
  uploadedImage,
  detections,
  selectedId,
  onSelectBox,
  showBoxes,
  onToggleShowBoxes,
}) => {
  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center overflow-hidden bg-zinc-950/80 rounded-xl border border-zinc-800/40 p-2">
      {/* Controls Overlay Bar */}
      <div className="absolute top-3 right-3 z-40 flex items-center gap-2 bg-zinc-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-zinc-800 shadow-xl">
        <button
          onClick={onToggleShowBoxes}
          className="text-xs font-semibold text-zinc-300 hover:text-white flex items-center gap-1.5 cursor-pointer"
        >
          {showBoxes ? <Eye className="w-3.5 h-3.5 text-purple-400" /> : <EyeOff className="w-3.5 h-3.5 text-zinc-500" />}
          {showBoxes ? "Hide Bounding Boxes" : "Show Bounding Boxes"}
        </button>
      </div>

      {/* Image & Bounding Box Layers */}
      <div className="relative max-h-full max-w-full flex items-center justify-center">
        <img
          src={uploadedImage}
          alt="Detection Canvas Image"
          className="max-h-full max-w-full object-contain rounded-lg"
        />

        {showBoxes && (
          <div className="absolute inset-0 pointer-events-none">
            {detections.map((box, idx) => (
              <BoundingBox
                key={idx}
                id={`box-${idx}`}
                type={box.type}
                bbox={box.bbox}
                confidence={box.confidence}
                text={box.text}
                isSelected={selectedId === idx}
                onSelect={() => onSelectBox(idx)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
