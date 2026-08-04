"use client";

import React, { useRef, useEffect } from "react";
import { Terminal, Check, Copy } from "lucide-react";
import { toast } from "sonner";

interface ExecutionLogProps {
  logs: string[];
}

export const ExecutionLog: React.FC<ExecutionLogProps> = ({ logs }) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = React.useState(false);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const handleCopyLogs = () => {
    navigator.clipboard.writeText(logs.join("\n"));
    setCopied(true);
    toast.success("Pipeline logs copied!");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full rounded-2xl border border-zinc-800 bg-zinc-950 font-mono overflow-hidden shadow-xl">
      {/* Terminal Bar */}
      <div className="h-10 px-4 bg-zinc-900 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold text-zinc-300">
          <Terminal className="w-3.5 h-3.5 text-purple-400" /> Pipeline Execution Terminal
        </div>
        <button
          onClick={handleCopyLogs}
          className="p-1 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-all cursor-pointer text-xs flex items-center gap-1"
        >
          {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>

      {/* Terminal Logs Output */}
      <div
        ref={terminalRef}
        className="flex-1 p-4 text-[11px] leading-relaxed text-zinc-300 overflow-y-auto space-y-1.5 no-scrollbar"
      >
        {logs.length > 0 ? (
          logs.map((log, idx) => {
            let color = "text-zinc-300";
            if (log.includes("[YOLO]")) color = "text-amber-300";
            if (log.includes("[EasyOCR]")) color = "text-blue-300";
            if (log.includes("[Layout]")) color = "text-purple-300";
            if (log.includes("[SUCCESS]")) color = "text-emerald-400 font-bold";
            if (log.includes("[ERROR]")) color = "text-rose-400 font-bold";

            return (
              <div key={idx} className={`font-mono flex items-start gap-2 ${color}`}>
                <span className="text-zinc-600 select-none">{idx + 1}.</span>
                <span className="flex-1 whitespace-pre-wrap">{log}</span>
              </div>
            );
          })
        ) : (
          <div className="text-zinc-600 text-xs italic">Waiting for pipeline execution...</div>
        )}
      </div>
    </div>
  );
};
