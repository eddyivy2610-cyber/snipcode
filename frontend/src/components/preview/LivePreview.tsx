"use client";

import React, { useState, useRef } from "react";
import { PreviewToolbar } from "./PreviewToolbar";
import { DeviceFrame } from "./DeviceFrame";
import { ViewportMode } from "./ResponsiveSwitcher";
import { Eye, Code2 } from "lucide-react";

interface LivePreviewProps {
  isDarkTheme: boolean;
  htmlCode: string;
}

export const LivePreview: React.FC<LivePreviewProps> = ({ isDarkTheme, htmlCode }) => {
  const [viewportMode, setViewportMode] = useState<ViewportMode>("desktop");
  const [reloadKey, setReloadKey] = useState(0);

  const handleReload = () => {
    setReloadKey((prev) => prev + 1);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-zinc-950">
      {/* Top Preview Toolbar */}
      <PreviewToolbar
        isDarkTheme={isDarkTheme}
        mode={viewportMode}
        onSelectMode={setViewportMode}
        onReload={handleReload}
      />

      {/* Main Responsive Sandbox Area */}
      <DeviceFrame mode={viewportMode}>
        {htmlCode ? (
          <iframe
            key={reloadKey}
            srcDoc={htmlCode}
            title="Live Interactive Sandbox"
            className="w-full h-full border-0 bg-transparent"
            sandbox="allow-scripts"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center gap-3 text-zinc-500">
            <Eye className="w-10 h-10 text-purple-400 opacity-40 animate-pulse" />
            <p className="text-sm font-semibold text-zinc-300">No Live Code Loaded</p>
            <p className="text-xs text-zinc-500">Upload a UI screenshot in Studio or Dashboard to render live preview</p>
          </div>
        )}
      </DeviceFrame>
    </div>
  );
};
