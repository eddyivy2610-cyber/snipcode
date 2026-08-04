"use client";

import React from "react";
import { ViewportMode } from "./ResponsiveSwitcher";

interface DeviceFrameProps {
  mode: ViewportMode;
  children: React.ReactNode;
}

export const DeviceFrame: React.FC<DeviceFrameProps> = ({ mode, children }) => {
  const getWidth = () => {
    switch (mode) {
      case "desktop":
        return "w-full max-w-[1440px]";
      case "tablet":
        return "w-[768px]";
      case "mobile":
        return "w-[375px]";
      default:
        return "w-full";
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center p-6 overflow-auto bg-zinc-950/60 no-scrollbar">
      <div
        className={`h-full max-h-full transition-all duration-300 flex flex-col ${getWidth()}`}
      >
        <div className="relative flex-1 w-full h-full rounded-2xl border border-zinc-800/90 bg-zinc-900 overflow-hidden shadow-2xl shadow-black/80 flex flex-col">
          {/* Mobile/Tablet Notch indicator */}
          {mode === "mobile" && (
            <div className="h-5 bg-zinc-950 flex items-center justify-center flex-shrink-0 border-b border-zinc-800">
              <div className="w-16 h-3 bg-zinc-900 rounded-full border border-zinc-800" />
            </div>
          )}
          {children}
        </div>
      </div>
    </div>
  );
};
