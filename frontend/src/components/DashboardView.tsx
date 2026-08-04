"use client";

import React from "react";
import {
  Sparkles,
  Upload,
  FolderPlus,
  Component,
  Code2,
  Clock,
  FileCode,
  ArrowRight,
  Layers,
  Layout,
  Plus,
} from "lucide-react";

interface DashboardViewProps {
  isDarkTheme: boolean;
  onUploadClick: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  isDarkTheme,
  onUploadClick,
}) => {
  const quickActions = [
    {
      title: "Upload Screenshot",
      description: "Convert UI image to HTML/CSS/JSX using YOLO & OCR",
      icon: Upload,
      color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
      action: onUploadClick,
    },
    {
      title: "New Empty Design",
      description: "Start a fresh VNode AST UI canvas",
      icon: FolderPlus,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
      action: () => {},
    },
    {
      title: "Import from Figma",
      description: "Sync layout frames directly into IR v4.0",
      icon: Component,
      color: "text-rose-400 bg-rose-500/10 border-rose-500/20",
      action: () => {},
    },
    {
      title: "Refine with Qwen LLM",
      description: "Targeted Search/Replace diff refinements",
      icon: Sparkles,
      color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
      action: () => {},
    },
  ];

  const templates = [
    { name: "Sign Up Form", category: "Auth", tags: ["Form", "Inputs", "OAuth"] },
    { name: "Analytics Dashboard", category: "Dashboard", tags: ["Sidebar", "Cards", "Charts"] },
    { name: "Pricing Table", category: "Marketing", tags: ["Cards", "Pills", "CTA"] },
    { name: "E-Commerce Product Card", category: "Shop", tags: ["Image", "Badge", "Button"] },
  ];

  const recentProjects = [
    {
      name: "Login Modal Form",
      time: "2 hours ago",
      framework: "HTML5",
      boxes: 11,
    },
    {
      name: "SaaS Dashboard Wireframe",
      time: "Yesterday",
      framework: "React JSX",
      boxes: 24,
    },
    {
      name: "Mobile Checkout Screen",
      time: "3 days ago",
      framework: "Flutter",
      boxes: 18,
    },
  ];

  const recentFiles = [
    { name: "screenshot19_output.html", size: "12 KB", type: "HTML5", date: "Today" },
    { name: "theme_dark_tokens.css", size: "4 KB", type: "CSS", date: "Yesterday" },
    { name: "vnode_tree_ast.json", size: "8 KB", type: "JSON", date: "2 days ago" },
  ];

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto p-6 space-y-6 no-scrollbar">

      {/* 2. Quick Actions */}
      <div>
        <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Plus className="w-4 h-4 text-purple-400" /> Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, idx) => {
            const Icon = action.icon;
            return (
              <div
                key={idx}
                onClick={action.action}
                className={`p-4 rounded-2xl border cursor-pointer transition-all duration-200 hover:-translate-y-0.5 shadow-md ${
                  isDarkTheme
                    ? "bg-zinc-900/60 border-zinc-800/80 hover:border-purple-500/40 hover:bg-zinc-900"
                    : "bg-white border-zinc-200 hover:border-purple-300 hover:bg-purple-50/30"
                }`}
              >
                <div className={`w-10 h-10 rounded-xl border flex items-center justify-center mb-3 ${action.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-sm font-semibold mb-1">{action.title}</h3>
                <p className={`text-xs ${isDarkTheme ? "text-zinc-400" : "text-zinc-500"}`}>
                  {action.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. Grid Row: Recent Projects & Templates */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Projects (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold flex items-center gap-2">
              <Clock className="w-4 h-4 text-purple-400" /> Recent Projects
            </h2>
            <button className="text-xs font-semibold text-purple-400 hover:text-purple-300 flex items-center gap-1">
              View All <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-2.5">
            {recentProjects.map((project, idx) => (
              <div
                key={idx}
                className={`p-3.5 rounded-2xl border flex items-center justify-between transition-all ${
                  isDarkTheme
                    ? "bg-zinc-900/60 border-zinc-800/80 hover:border-zinc-700"
                    : "bg-white border-zinc-200 hover:border-zinc-300"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
                    <Layout className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold">{project.name}</h4>
                    <p className={`text-[11px] ${isDarkTheme ? "text-zinc-500" : "text-zinc-400"}`}>
                      {project.boxes} detected elements • {project.time}
                    </p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-lg bg-zinc-800 text-[10px] font-mono text-purple-300 border border-zinc-700">
                  {project.framework}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Templates (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" /> Starter Templates
            </h2>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {templates.map((tpl, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-2xl border cursor-pointer transition-all hover:border-purple-500/40 ${
                  isDarkTheme ? "bg-zinc-900/60 border-zinc-800/80" : "bg-white border-zinc-200"
                }`}
              >
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 uppercase">
                  {tpl.category}
                </span>
                <h4 className="text-xs font-semibold mt-2 mb-2 truncate">{tpl.name}</h4>
                <div className="flex flex-wrap gap-1">
                  {tpl.tags.map((t, tid) => (
                    <span key={tid} className="text-[9px] text-zinc-500 bg-zinc-800/40 px-1.5 py-0.5 rounded">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 4. Recent Files */}
      <div>
        <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <FileCode className="w-4 h-4 text-purple-400" /> Recent Exported Files
        </h2>
        <div className={`rounded-2xl border overflow-hidden ${
          isDarkTheme ? "bg-zinc-900/60 border-zinc-800/80" : "bg-white border-zinc-200"
        }`}>
          <div className="divide-y divide-zinc-800/50">
            {recentFiles.map((file, idx) => (
              <div key={idx} className="p-3 px-4 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2.5 font-mono">
                  <FileCode className="w-4 h-4 text-purple-400" />
                  <span className="font-semibold">{file.name}</span>
                </div>
                <div className="flex items-center gap-4 text-zinc-500 text-[11px]">
                  <span>{file.size}</span>
                  <span className="px-2 py-0.5 rounded bg-zinc-800 text-purple-300 font-mono text-[10px]">
                    {file.type}
                  </span>
                  <span>{file.date}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
