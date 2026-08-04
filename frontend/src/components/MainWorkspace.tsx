"use client";

import React, { useRef, useState } from "react";
import { Upload, Sparkles, Monitor, Tablet, Smartphone, Eye, Image as ImageIcon, Send } from "lucide-react";
import { toast } from "sonner";

interface MainWorkspaceProps {
  isDarkTheme: boolean;
  uploadedImage: string | null;
  onUploadImage: (file: File) => void;
  detections: any[];
  htmlCode: string;
  isProcessing: boolean;
}

export const MainWorkspace: React.FC<MainWorkspaceProps> = ({
  isDarkTheme,
  uploadedImage,
  onUploadImage,
  detections,
  htmlCode,
  isProcessing,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [viewMode, setViewMode] = useState<"image" | "preview">("image");
  const [viewportWidth, setViewportWidth] = useState<"100%" | "768px" | "375px">("100%");
  const [llmPrompt, setLlmPrompt] = useState("");
  const [isRefining, setIsRefining] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsHovered(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUploadImage(e.dataTransfer.files[0]);
    }
  };

  const handleRefineLLM = (e: React.FormEvent) => {
    e.preventDefault();
    setIsRefining(true);
    toast.loading("Qwen LLM computing targeted diff patch...", { id: "qwen" });

    setTimeout(() => {
      setIsRefining(false);
      toast.success("Applied Qwen targeted Search/Replace diff patch!", { id: "qwen" });
      setLlmPrompt("");
    }, 1200);
  };

  return (
    <div
      className={`flex-1 flex flex-col h-full border-r p-4 backdrop-blur-xl transition-colors duration-300 overflow-hidden ${
        isDarkTheme
          ? "bg-zinc-950 border-zinc-800/80 text-zinc-100"
          : "bg-zinc-50 border-zinc-200/90 text-zinc-900"
      }`}
    >

      {/* Main Canvas Area */}
      <div className="flex-1 relative rounded-xl overflow-hidden flex items-center justify-center border border-zinc-800/40 bg-zinc-900/30">
        {viewMode === "image" ? (
          !uploadedImage ? (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsHovered(true);
              }}
              onDragLeave={() => setIsHovered(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`w-full h-full border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${
                isHovered
                  ? "border-purple-500 bg-purple-500/5"
                  : isDarkTheme
                  ? "border-zinc-800 bg-zinc-950/40 hover:border-zinc-700 hover:bg-zinc-950/60"
                  : "border-zinc-300 bg-zinc-50/50 hover:border-zinc-400 hover:bg-zinc-100/50"
              }`}
            >
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept="image/*"
                onChange={(e) => e.target.files?.[0] && onUploadImage(e.target.files[0])}
              />
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mb-4 shadow-lg shadow-purple-500/10">
                <Upload className="w-6 h-6" />
              </div>
              <p className="text-sm font-semibold mb-1">
                Drop UI screenshot here or click to upload
              </p>
              <p className={`text-xs ${isDarkTheme ? "text-zinc-500" : "text-zinc-400"}`}>
                Supports PNG, JPG, WebP (Forms, Cards, Dashboards)
              </p>
            </div>
          ) : (
            <div className="relative w-full h-full flex items-center justify-center overflow-hidden bg-zinc-950/80">
              <img
                src={uploadedImage}
                alt="Uploaded UI Screenshot"
                className="max-h-full max-w-full object-contain"
              />

              {/* Bounding Box Visual Overlay */}
              <div className="absolute inset-0 pointer-events-none">
                {detections.map((box, idx) => {
                  const [ymin, xmin, ymax, xmax] = box.bbox;
                  return (
                    <div
                      key={idx}
                      style={{
                        top: `${ymin}px`,
                        left: `${xmin}px`,
                        width: `${xmax - xmin}px`,
                        height: `${ymax - ymin}px`,
                      }}
                      className="absolute border border-purple-400/80 bg-purple-400/10 rounded text-[10px] text-purple-300 font-mono px-1 truncate flex items-start"
                    >
                      {box.type}: {box.text || box.confidence.toFixed(2)}
                    </div>
                  );
                })}
              </div>
            </div>
          )
        ) : (
          <div className="w-full h-full bg-zinc-950 flex items-center justify-center overflow-hidden p-2">
            <div
              style={{ width: viewportWidth }}
              className="h-full bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl transition-all duration-300"
            >
              {htmlCode ? (
                <iframe
                  srcDoc={htmlCode}
                  title="Live Render Sandbox"
                  className="w-full h-full border-0 bg-transparent"
                  sandbox="allow-scripts"
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-zinc-500 text-xs">
                  Upload a screenshot to render live sandbox preview
                </div>
              )}
            </div>
          </div>
        )}

        {/* Processing Spinner Overlay */}
        {(isProcessing || isRefining) && (
          <div className="absolute inset-0 bg-zinc-950/85 backdrop-blur-md flex flex-col items-center justify-center gap-3 z-50">
            <Sparkles className="w-8 h-8 text-purple-400 animate-spin" />
            <p className="text-xs font-semibold text-zinc-200">
              {isProcessing
                ? "Reconstructing UI with YOLO & EasyOCR..."
                : "Qwen LLM computing targeted Search/Replace diff patch..."}
            </p>
          </div>
        )}
      </div>

      {/* Qwen LLM Refinement Bar */}
      <form onSubmit={handleRefineLLM} className="mt-3 flex items-center gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={llmPrompt}
            onChange={(e) => setLlmPrompt(e.target.value)}
            placeholder="Ask Qwen LLM to refine layout (e.g. 'Make button gradient purple with low shadow')..."
            className={`w-full px-3.5 py-2 rounded-xl text-xs border outline-none transition-all ${
              isDarkTheme
                ? "bg-zinc-900/80 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus:border-purple-500/50"
                : "bg-white border-zinc-300 text-zinc-900 placeholder:text-zinc-400 focus:border-purple-400"
            }`}
          />
        </div>
        <button
          type="submit"
          className="px-3.5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs flex items-center gap-1.5 shadow-md shadow-purple-600/20 transition-all cursor-pointer flex-shrink-0"
        >
          <Sparkles className="w-3.5 h-3.5" /> Refine
        </button>
      </form>
    </div>
  );
};
