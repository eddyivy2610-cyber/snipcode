"use client";

import React, { useState } from "react";
import Editor from "@monaco-editor/react";
import { Code, FileCode, Layers, Copy, Check, Play, ExternalLink } from "lucide-react";
import { PipelineStepperCycle } from "@/components/pipeline/PipelineStepperCycle";
import { toast } from "sonner";

interface RightPanelProps {
  isDarkTheme: boolean;
  htmlCode: string;
  cssCode: string;
  irTree: any;
  onChangeCode: (code: string) => void;
  isProcessing?: boolean;
  onSendToLivePreview?: () => void;
}

export const RightPanel: React.FC<RightPanelProps> = ({
  isDarkTheme,
  htmlCode,
  cssCode,
  irTree,
  onChangeCode,
  isProcessing = false,
  onSendToLivePreview,
}) => {
  const [activeTab, setActiveTab] = useState<"html" | "css" | "ir">("html");
  const [copied, setCopied] = useState(false);

  const getActiveCode = () => {
    switch (activeTab) {
      case "html":
        return htmlCode;
      case "css":
        return cssCode;
      case "ir":
        return irTree ? JSON.stringify(irTree, null, 2) : "{}";
      default:
        return htmlCode;
    }
  };

  const handleCopy = () => {
    const code = getActiveCode();
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    toast.success("Code copied to clipboard!");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`w-96 flex flex-col h-full p-4 backdrop-blur-xl transition-colors duration-300 overflow-hidden ${
        isDarkTheme
          ? "bg-zinc-950 text-zinc-100"
          : "bg-zinc-50 text-zinc-900"
      }`}
    >
      {/* Header & Tabs */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-zinc-800/40">
        <div className="flex items-center gap-1">
          <button
            onClick={() => setActiveTab("html")}
            className={`px-2.5 py-1 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
              activeTab === "html"
                ? "bg-purple-600 text-white shadow-sm"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            <Code className="w-3.5 h-3.5" /> HTML
          </button>
          <button
            onClick={() => setActiveTab("css")}
            className={`px-2.5 py-1 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
              activeTab === "css"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            <FileCode className="w-3.5 h-3.5" /> CSS
          </button>
          <button
            onClick={() => setActiveTab("ir")}
            className={`px-2.5 py-1 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
              activeTab === "ir"
                ? "bg-amber-600 text-white shadow-sm"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            <Layers className="w-3.5 h-3.5" /> IR AST
          </button>
        </div>

        {/* Action Buttons: Send to Live Preview & Copy */}
        <div className="flex items-center gap-1.5">
          {onSendToLivePreview && (
            <button
              onClick={() => {
                if (!htmlCode) {
                  toast.error("Generate code output before sending to Live Preview!");
                  return;
                }
                onSendToLivePreview();
                toast.success("Sent code output to Live Preview sandbox!");
              }}
              disabled={!htmlCode}
              className="px-2.5 py-1 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white font-semibold text-xs flex items-center gap-1 shadow-sm shadow-purple-600/20 transition-all cursor-pointer"
              title="Send to Live Preview"
            >
              <Play className="w-3 h-3 fill-current" /> Live
            </button>
          )}

          <button
            onClick={handleCopy}
            disabled={!htmlCode}
            className="p-1.5 rounded-xl bg-zinc-800/80 hover:bg-zinc-700 disabled:opacity-40 text-zinc-300 hover:text-white text-xs font-semibold transition-all cursor-pointer"
            title="Copy Code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Monaco Code Editor OR Stepper Cycle in Workspace Output */}
      <div className="flex-1 rounded-xl overflow-hidden border border-zinc-800/40 bg-zinc-900/40 relative">
        {isProcessing ? (
          <PipelineStepperCycle isDarkTheme={isDarkTheme} />
        ) : (
          <Editor
            height="100%"
            language={activeTab === "ir" ? "json" : activeTab === "css" ? "css" : "html"}
            theme={isDarkTheme ? "vs-dark" : "light"}
            value={getActiveCode()}
            onChange={(val) => val && activeTab === "html" && onChangeCode(val)}
            options={{
              fontSize: 12,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              smoothScrolling: true,
              lineNumbers: "on",
              padding: { top: 10, bottom: 10 },
            }}
          />
        )}
      </div>
    </div>
  );
};
