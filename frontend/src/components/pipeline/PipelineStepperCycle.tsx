"use client";

import React, { useState, useEffect } from "react";
import {
  ImageIcon,
  Scan,
  Type,
  GitMerge,
  Sparkles,
  Layers,
  Code,
  Bot,
  CheckCircle2,
  Loader2,
} from "lucide-react";

interface PipelineStepperCycleProps {
  isDarkTheme: boolean;
}

export const PipelineStepperCycle: React.FC<PipelineStepperCycleProps> = ({
  isDarkTheme,
}) => {
  const steps = [
    { name: "Image Ingestion", icon: ImageIcon, desc: "Reading pixel buffer" },
    { name: "YOLOv8 Detection", icon: Scan, desc: "Detecting buttons, inputs & forms" },
    { name: "EasyOCR Recognition", icon: Type, desc: "Extracting text labels" },
    { name: "Spatial Merger", icon: GitMerge, desc: "Bounding box spatial alignment" },
    { name: "NMS Cleanup", icon: Sparkles, desc: "Filtering box overlaps" },
    { name: "4-Pillar Layout Engine", icon: Layers, desc: "Reconstructing IR v4.0 AST" },
    { name: "VNode AST Compiler", icon: Code, desc: "Emitting HTML5 & CSS Variables" },
    { name: "Qwen LLM Refinement", icon: Bot, desc: "Computing targeted diff patch" },
  ];

  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 450);

    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-6 bg-zinc-950/90 text-zinc-100 font-sans">
      <div className="w-full max-w-sm flex flex-col items-center space-y-4">
        {/* Animated Cycle Header */}
        <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/30 text-purple-400 flex items-center justify-center shadow-lg shadow-purple-500/10">
          <Loader2 className="w-6 h-6 animate-spin" />
        </div>

        <div className="text-center space-y-1">
          <h3 className="text-sm font-bold text-zinc-100 tracking-tight">
            Compiling 4-Pillar IR v4.0 AST...
          </h3>
          <p className="text-[11px] text-zinc-500 font-mono">
            Executing real-time 8-stage compiler cycle
          </p>
        </div>

        {/* Stepper Cycle List */}
        <div className="w-full space-y-2 mt-2">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            const isDone = idx < currentStep;
            const isCurrent = idx === currentStep;

            return (
              <div
                key={idx}
                className={`p-2.5 rounded-xl border transition-all duration-300 flex items-center justify-between ${
                  isCurrent
                    ? "bg-purple-500/15 border-purple-500/50 shadow-md ring-1 ring-purple-500/30"
                    : isDone
                    ? "bg-zinc-900/60 border-zinc-800/80 text-zinc-300"
                    : "bg-zinc-950/40 border-zinc-900 opacity-40"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <div
                    className={`w-6 h-6 rounded-lg border flex items-center justify-center text-[10px] ${
                      isDone
                        ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                        : isCurrent
                        ? "bg-purple-600 border-purple-500 text-white animate-pulse"
                        : "bg-zinc-800 border-zinc-700 text-zinc-500"
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    ) : (
                      <Icon className="w-3 h-3" />
                    )}
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold">{step.name}</h4>
                    <p className="text-[10px] text-zinc-500 font-mono">{step.desc}</p>
                  </div>
                </div>

                {isCurrent && (
                  <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 animate-pulse">
                    Running
                  </span>
                )}
                {isDone && (
                  <span className="text-[10px] font-mono text-emerald-400 font-semibold">
                    Done
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
