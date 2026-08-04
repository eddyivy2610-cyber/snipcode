"use client";

import React, { useState, useRef } from "react";
import {
  Upload,
  ArrowUp,
  Home as HomeIcon,
  Compass,
  Folder,
  ChevronDown,
  Loader2,
  PanelLeftClose,
  PanelLeftOpen,
  Image as ImageIcon,
  RefreshCw,
  Sparkles,
  Trash2,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useProjectHistory } from "@/hooks/useProjectHistory";

export default function Home() {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedModel, setSelectedModel] = useState("Qwen 2.5 Coder 32B");

  const { projects, saveProject, clearProjects } = useProjectHistory();
  const [activeNav, setActiveNav] = useState<"home" | "resources" | "projects">("home");
  const [activeRecentId, setActiveRecentId] = useState<string | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleRunCompiler = async () => {
    if (!selectedFile && !prompt) return;
    const projId = `proj_${Date.now()}`;

    // Convert image to base64 and persist in sessionStorage for the project page
    let imageDataUrl: string | null = null;
    if (selectedFile) {
      imageDataUrl = await new Promise<string>(resolve => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target?.result as string);
        reader.readAsDataURL(selectedFile);
      });
    }

    sessionStorage.setItem(`snipcode_input_${projId}`, JSON.stringify({
      prompt,
      model: selectedModel,
      imageDataUrl,
      imageName: selectedFile?.name ?? null,
      imageType: selectedFile?.type ?? null,
    }));

    saveProject(projId, prompt || selectedFile?.name || "", selectedModel);
    setActiveRecentId(projId);
    router.push(`/project/${projId}`);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="min-h-screen hero-image-bg text-gray-100 flex selection:bg-purple-500/30 overflow-hidden">
      
      {/* Left Sidebar */}
      <aside className={`sticky top-0 h-screen glass-nav-header border-r border-white/10 flex flex-col justify-between transition-all duration-300 z-40 ${
        isSidebarCollapsed ? "w-12" : "w-52"
      }`}>
        
        {/* Sidebar Top: Window Toggle Button */}
        <div className="px-3 py-3 border-b border-white/5 flex items-center">
          <button 
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="p-1.5 rounded-lg glass-chip text-gray-300 hover:text-white"
            title="Toggle Sidebar"
          >
            {isSidebarCollapsed ? <PanelLeftOpen className="w-3.5 h-3.5" /> : <PanelLeftClose className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Sidebar Middle Navigation & Recents */}
        <div className="flex-1 overflow-y-auto p-3 space-y-6">
          
          <nav className="space-y-0.5">
            <button
              onClick={() => setActiveNav("home")}
              className={`w-full flex items-center space-x-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all ${
                activeNav === "home"
                  ? isSidebarCollapsed
                    ? "border-l-2 border-purple-400 text-white bg-transparent pl-[9px]"
                    : "bg-white/15 text-white font-semibold shadow-sm"
                  : "text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent"
              }`}
            >
              <HomeIcon className={`w-3.5 h-3.5 shrink-0 ${
                activeNav === "home" ? "text-purple-400" : "text-purple-300"
              }`} />
              {!isSidebarCollapsed && <span>Home</span>}
            </button>

            <button
              onClick={() => setActiveNav("resources")}
              className={`w-full flex items-center space-x-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all ${
                activeNav === "resources"
                  ? isSidebarCollapsed
                    ? "border-l-2 border-emerald-400 text-white bg-transparent pl-[9px]"
                    : "bg-white/15 text-white font-semibold shadow-sm"
                  : "text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent"
              }`}
            >
              <Compass className={`w-3.5 h-3.5 shrink-0 ${
                activeNav === "resources" ? "text-emerald-400" : "text-emerald-300"
              }`} />
              {!isSidebarCollapsed && <span>Resources</span>}
            </button>

            <button
              onClick={() => setActiveNav("projects")}
              className={`w-full flex items-center space-x-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all ${
                activeNav === "projects"
                  ? isSidebarCollapsed
                    ? "border-l-2 border-amber-400 text-white bg-transparent pl-[9px]"
                    : "bg-white/15 text-white font-semibold shadow-sm"
                  : "text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent"
              }`}
            >
              <Folder className={`w-3.5 h-3.5 shrink-0 ${
                activeNav === "projects" ? "text-amber-400" : "text-amber-300"
              }`} />
              {!isSidebarCollapsed && <span>My Projects</span>}
            </button>
          </nav>

          {/* RECENTS SECTION */}
          {!isSidebarCollapsed && (
            <div className="space-y-1.5 pt-2 border-t border-white/5">
              <div className="flex items-center justify-between px-2.5">
                <span className="text-[10px] font-semibold tracking-wider text-gray-500 uppercase">
                  Recents
                </span>
                {projects.length > 0 && (
                  <button
                    onClick={clearProjects}
                    className="text-gray-600 hover:text-red-400 transition-all"
                    title="Clear history"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                )}
              </div>

              <div className="space-y-0.5">
                {projects.length === 0 ? (
                  <p className="px-2.5 text-[11px] text-gray-600 italic">No projects yet</p>
                ) : (
                  projects.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        setActiveRecentId(item.id);
                        router.push(`/project/${item.id}`);
                      }}
                      className={`w-full text-left px-2.5 py-1.5 rounded-lg text-[11px] font-medium truncate transition-all ${
                        activeRecentId === item.id
                          ? "bg-purple-600/25 border border-purple-500/40 text-purple-200"
                          : "text-gray-400 hover:text-gray-200 hover:bg-white/5"
                      }`}
                    >
                      {item.title}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}


        </div>

        {/* Sidebar Footer: App name only */}
        {!isSidebarCollapsed && (
          <div className="px-3 py-3 border-t border-white/5">
            <span className="text-[10px] font-semibold text-gray-500 tracking-widest uppercase">Snipcode</span>
          </div>
        )}
      </aside>

      {/* Main Canvas Workspace */}
      <main className="flex-1 flex flex-col justify-between overflow-y-auto h-screen relative">

        {activeNav === "home" && (
          <div className="max-w-3xl mx-auto w-full my-auto flex flex-col items-center justify-center text-center py-8 px-8">
            
            {/* Image-First Headline & Subtitle */}
            <div className="mb-6 space-y-2">
              <h1 className="text-3xl md:text-5xl font-poppins font-semibold text-white">
                Turn sketches & screenshots into code.
              </h1>
              <p className="text-sm md:text-base text-gray-400 max-w-xl mx-auto font-normal">
                Upload any UI wireframe, design sketch, or screenshot to compile production-ready AST components.
              </p>
            </div>

            {/* Central Dark Glass Vision-First Compiler Card */}
            <div className="w-full max-w-2xl glass-card-dark rounded-2xl p-5 md:p-6 text-left relative transition-all duration-300 border border-white/10 shadow-2xl">
              
              {/* Working / Inferring Status Banner ABOVE Area */}
              {isProcessing && (
                <div className="mb-4 px-4 py-2 rounded-xl bg-purple-950/70 border border-purple-500/40 flex items-center space-x-3 text-xs text-purple-300 animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                  <span className="font-semibold tracking-wide uppercase">
                    Running Sensor Fusion & Compiling Code...
                  </span>
                </div>
              )}

              {/* PRIMARY VISUAL FEATURE: Large Drag & Drop Screenshot Dropzone */}
              <div 
                onClick={() => fileInputRef.current?.click()}
                className={`relative rounded-xl border-2 border-dashed transition-all duration-300 p-6 text-center cursor-pointer flex flex-col items-center justify-center min-h-[160px] mb-4 ${
                  imagePreview 
                    ? "border-purple-500/60 bg-purple-950/20" 
                    : "border-white/15 hover:border-purple-500/40 bg-white/5 hover:bg-white/[0.07]"
                }`}
              >
                <input 
                  type="file" 
                  ref={fileInputRef}
                  onChange={handleFileChange} 
                  accept="image/*" 
                  className="hidden" 
                />

                {imagePreview ? (
                  <div className="flex items-center space-x-4">
                    <img 
                      src={imagePreview} 
                      alt="Uploaded Sketch" 
                      className="w-20 h-20 object-cover rounded-lg border border-purple-500/40 shadow-md"
                    />
                    <div className="text-left space-y-1">
                      <p className="text-xs font-semibold text-purple-200">{selectedFile?.name}</p>
                      <p className="text-[11px] text-gray-400">Click or drop another image to replace</p>
                      <span className="inline-block px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono border border-emerald-500/30">
                        Screenshot Loaded
                      </span>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="w-12 h-12 rounded-2xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center mb-3">
                      <ImageIcon className="w-6 h-6 text-purple-300" />
                    </div>
                    <p className="text-sm font-semibold text-gray-200">Drop a sketch or UI screenshot here</p>
                    <p className="text-xs text-gray-400 mt-1">Supports PNG, JPG, WebP wireframes & mockups</p>
                  </>
                )}
              </div>

              {/* SECONDARY FEATURE: Compact Design Notes Input */}
              <div className="mb-4">
                <label className="block text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
                  Design Tweaks & Specs (Optional)
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Add specific notes for this screenshot (e.g. 'Use dark mode palette, make buttons rounded')..."
                  rows={2}
                  disabled={isProcessing}
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-xs md:text-sm text-gray-100 placeholder-gray-500 resize-none focus:outline-none focus:border-purple-500/40 disabled:opacity-60"
                />
              </div>

              {/* Card Controls Bar */}
              <div className="flex items-center justify-between pt-3 border-t border-white/10">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isProcessing}
                  className="glass-chip px-3 py-1.5 rounded-lg text-xs font-medium text-gray-300 flex items-center space-x-1.5 disabled:opacity-50"
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>{selectedFile ? "Change Image" : "Attach Image"}</span>
                </button>

                <div className="flex items-center space-x-3 ml-auto">
                  <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="glass-chip text-xs font-medium text-gray-300 px-3 py-2 rounded-lg bg-transparent focus:outline-none cursor-pointer"
                  >
                    <option value="Qwen 2.5 Coder 32B" className="bg-gray-900 text-white">Qwen 2.5 Coder 32B</option>
                    <option value="Llama 3.3 70B" className="bg-gray-900 text-white">Llama 3.3 70B</option>
                    <option value="Rule-Based AST Engine" className="bg-gray-900 text-white">Rule-Based AST Engine</option>
                  </select>

                  <button
                    onClick={handleRunCompiler}
                    disabled={isProcessing}
                    className="px-4 py-2 rounded-xl glow-purple-btn flex items-center space-x-2 text-white text-xs font-semibold disabled:opacity-50"
                  >
                    {isProcessing ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <span>Compile Code</span>
                        <ArrowUp className="w-3.5 h-3.5" />
                      </>
                    )}
                  </button>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* Resources View */}
        {activeNav === "resources" && (
          <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col gap-4 px-8 py-6">
            <h2 className="text-xl font-bold text-white font-poppins">Resources & Component Library</h2>
            <div className="glass-card-dark rounded-2xl p-6 text-gray-300 text-sm">
              <p>Explore IR v5.0 documentation, AST node specs, and UI templates.</p>
            </div>
          </div>
        )}

        {/* My Projects View */}
        {activeNav === "projects" && (
          <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col gap-4 px-8 py-6">
            <h2 className="text-xl font-bold text-white font-poppins">My Projects</h2>
            <div className="glass-card-dark rounded-2xl p-6 text-gray-300 text-sm">
              <p>Manage compiled React JSX components and HTML5 projects.</p>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="py-4 border-t border-white/5 text-center mt-auto">
          <p className="text-xs text-gray-500 font-poppins">
            Snipcode Vision-to-Code Compiler Engine
          </p>
        </footer>
      </main>

    </div>
  );
}
