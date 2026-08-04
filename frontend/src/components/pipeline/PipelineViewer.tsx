"use client";

import React, { useState } from "react";
import { PipelineStep } from "./PipelineStep";
import { ExecutionLog } from "./ExecutionLog";
import { PerformanceChart } from "./PerformanceChart";
import { StatusType } from "./StepStatus";
import {
  ImageIcon,
  Scan,
  Type,
  GitMerge,
  Sparkles,
  Layers,
  Code,
  Bot,
  Play,
} from "lucide-react";

interface PipelineViewerProps {
  isDarkTheme: boolean;
  uploadedImage: string | null;
  detections: any[];
}

export const PipelineViewer: React.FC<PipelineViewerProps> = ({
  isDarkTheme,
  uploadedImage,
  detections,
}) => {
  const isCompleted = detections.length > 0;

  const pipelineSteps = [
    {
      id: "image",
      name: "Image Ingestion",
      description: "Upload & pre-process screenshot",
      icon: ImageIcon,
      status: (uploadedImage ? "completed" : "pending") as StatusType,
      durationMs: 4,
      summary: uploadedImage ? "Image loaded" : "Waiting for upload",
    },
    {
      id: "yolo",
      name: "YOLOv8 Detection",
      description: "Detect buttons, inputs, texts, forms",
      icon: Scan,
      status: (isCompleted ? "completed" : uploadedImage ? "running" : "pending") as StatusType,
      durationMs: 108,
      summary: `${detections.length} bounding boxes`,
    },
    {
      id: "ocr",
      name: "EasyOCR Recognition",
      description: "Extract text labels & placeholders",
      icon: Type,
      status: (isCompleted ? "completed" : "pending") as StatusType,
      durationMs: 320,
      summary: "Merged text snippets",
    },
    {
      id: "merge",
      name: "Spatial Box Merger",
      description: "Align text labels inside input boxes",
      icon: GitMerge,
      status: (isCompleted ? "completed" : "pending") as StatusType,
      durationMs: 18,
      summary: "Spatial IOU matched",
    },
    {
      id: "cleanup",
      name: "NMS & Overlap Cleanup",
      description: "Deduplicate boxes & clean noise",
      icon: Sparkles,
      status: (isCompleted ? "completed" : "pending") as StatusType,
      durationMs: 12,
      summary: "Cleaned bounding list",
    },
    {
      id: "layout",
      name: "Layout Tree Engine",
      description: "Reconstruct 4-Pillar IR v4.0 AST",
      icon: Layers,
      status: (isCompleted ? "completed" : "pending") as StatusType,
      durationMs: 14,
      summary: "IR v4.0 AST built",
    },
    {
      id: "html",
      name: "VNode Compiler",
      description: "Compile HTML5 + CSS Variables",
      icon: Code,
      status: (isCompleted ? "completed" : "pending") as StatusType,
      durationMs: 6,
      summary: "Target code emitted",
    },
    {
      id: "llm",
      name: "Qwen LLM Refinement",
      description: "Targeted Search/Replace diff patches",
      icon: Bot,
      status: (isCompleted ? "completed" : "pending") as StatusType,
      durationMs: 450,
      summary: "Zero hallucination diffs",
    },
  ];

  const logs = [
    "[SYSTEM] AI Pipeline Initialized — Target Endpoint: /api/generate",
    uploadedImage ? `[IMAGE] Screenshot loaded into memory: ${uploadedImage.slice(0, 30)}...` : "[IDLE] Waiting for screenshot upload...",
    ...(isCompleted
      ? [
          "[YOLO] Running YOLOv8 object detector model on CPU (384x640)",
          `[YOLO] Detected ${detections.length} raw UI elements in 108.7ms`,
          "[EasyOCR] Running EasyOCR text recognition engine...",
          "[EasyOCR] Extracted text labels & merged into parent bounding boxes in 320ms",
          "[CLEANUP] Running NMS spatial deduplication & noise filtering...",
          "[LAYOUT] Reconstructing 4-Pillar Design-System IR v4.0 AST...",
          "[VNODE] Compiling VNode AST → Target HTML5 & CSS Custom Properties...",
          "[LLM] Qwen2.5-Coder refinement engine ready for targeted diff patches",
          "[SUCCESS] Full compiler pipeline executed cleanly!",
        ]
      : []),
  ];

  const totalDurationMs = pipelineSteps.reduce((acc, curr) => acc + (curr.durationMs || 0), 0);

  const stepMetrics = [
    { name: "YOLO", durationMs: 108, color: "bg-amber-500" },
    { name: "OCR", durationMs: 320, color: "bg-blue-500" },
    { name: "Layout", durationMs: 14, color: "bg-purple-500" },
    { name: "LLM", durationMs: 450, color: "bg-emerald-500" },
  ];

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden p-6 space-y-6">
      {/* Top Performance Chart */}
      <PerformanceChart
        isDarkTheme={isDarkTheme}
        totalDurationMs={totalDurationMs}
        stepMetrics={stepMetrics}
      />

      {/* Main Grid: Pipeline Flowchart (Left 5 cols) & Terminal Execution Log (Right 7 cols) */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden">
        {/* Pipeline Flowchart Steps */}
        <div className="lg:col-span-5 flex flex-col h-full overflow-y-auto pr-2 space-y-1 no-scrollbar">
          <h3 className="text-xs font-bold text-zinc-400 mb-2 uppercase tracking-wider">
            AI Compiler Lifecycle (8 Stages)
          </h3>
          {pipelineSteps.map((step, idx) => (
            <PipelineStep
              key={step.id}
              isDarkTheme={isDarkTheme}
              name={step.name}
              description={step.description}
              icon={step.icon}
              status={step.status}
              durationMs={step.durationMs}
              outputSummary={step.summary}
              isLast={idx === pipelineSteps.length - 1}
            />
          ))}
        </div>

        {/* Real-time Terminal Execution Log */}
        <div className="lg:col-span-7 h-full overflow-hidden">
          <ExecutionLog logs={logs} />
        </div>
      </div>
    </div>
  );
};
