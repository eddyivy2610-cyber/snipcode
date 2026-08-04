"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Code2,
  Copy,
  RefreshCw,
  Eye,
  HomeIcon,
  Compass,
  Folder,
  ChevronDown,
  PanelLeftClose,
  PanelLeftOpen,
  Image as ImageIcon,
  Send,
  Play,
  Download,
  Maximize2,
  Plus,
  Loader2,
  Sparkles,
  Trash2,
} from "lucide-react";
import { useProjectHistory } from "@/hooks/useProjectHistory";

export default function VisionCodeProject() {
  const params = useParams();
  const router = useRouter();
  const projectId = (params?.id as string) || "project_demo";

  // ─── Sidebar state (mirrored from home page) ───
  const [activeNav, setActiveNav] = useState<"home" | "resources" | "projects">("projects");
  const [activeRecentId, setActiveRecentId] = useState<string>(projectId);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const { projects, clearProjects } = useProjectHistory();

  // ─── Workspace state ───
  const [activeTab, setActiveTab] = useState<"code" | "preview">("code");
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const threadEndRef = useRef<HTMLDivElement>(null);

  // ─── Generated output ───
  const [generatedCode, setGeneratedCode] = useState("");

  // ─── Thread messages ───
  interface ThreadMessage {
    id: string;
    role: "user" | "agent";
    text?: string;
    imageUrl?: string;
    isLoading?: boolean;
    isError?: boolean;
    timestamp: Date;
  }
  const [messages, setMessages] = useState<ThreadMessage[]>([]);

  // ─── Stored input from home page ───
  interface PendingInput {
    prompt: string;
    model: string;
    imageDataUrl: string | null;
    imageName: string | null;
    imageType: string | null;
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  // ─── Core generation function ───
  const runGeneration = useCallback(async (
    userPrompt: string,
    imageDataUrl: string | null,
    imageName: string | null,
    imageType: string | null,
    userImagePreview: string | null,
  ) => {
    setIsGenerating(true);

    // Add user message
    const userMsgId = `u_${Date.now()}`;
    setMessages(prev => [...prev, {
      id: userMsgId,
      role: "user",
      text: userPrompt || undefined,
      imageUrl: userImagePreview || undefined,
      timestamp: new Date(),
    }]);

    // Add agent loading message
    const agentMsgId = `a_${Date.now()}`;
    setMessages(prev => [...prev, {
      id: agentMsgId,
      role: "agent",
      isLoading: true,
      timestamp: new Date(),
    }]);

    setTimeout(() => threadEndRef.current?.scrollIntoView({ behavior: "smooth" }), 50);

    try {
      const formData = new FormData();

      if (imageDataUrl) {
        const res = await fetch(imageDataUrl);
        const blob = await res.blob();
        formData.append("file", new File([blob], imageName || "image.png", { type: imageType || "image/png" }));
      } else {
        // Blank canvas fallback for text-only
        const canvas = document.createElement("canvas");
        canvas.width = 800; canvas.height = 600;
        const blob = await new Promise<Blob>(resolve => canvas.toBlob(b => resolve(b!)));
        formData.append("file", new File([blob], "blank.png", { type: "image/png" }));
      }
      if (userPrompt) formData.append("prompt", userPrompt);

      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`Server error ${response.status}`);

      const data = await response.json();
      const html: string = data.html || data.code || "";

      setGeneratedCode(html);
      setMessages(prev => prev.map(m =>
        m.id === agentMsgId
          ? { ...m, isLoading: false, text: "Code generated successfully from your input." }
          : m
      ));
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Generation failed";
      setMessages(prev => prev.map(m =>
        m.id === agentMsgId
          ? { ...m, isLoading: false, isError: true, text: `Error: ${msg}` }
          : m
      ));
    } finally {
      setIsGenerating(false);
      setTimeout(() => threadEndRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  }, []);

  // ─── Auto-generate on mount from sessionStorage ───
  useEffect(() => {
    const raw = sessionStorage.getItem(`snipcode_input_${projectId}`);
    if (!raw) return;
    try {
      const input: PendingInput = JSON.parse(raw);
      sessionStorage.removeItem(`snipcode_input_${projectId}`);
      if (input.imageDataUrl) setImagePreview(input.imageDataUrl);
      runGeneration(input.prompt, input.imageDataUrl, input.imageName, input.imageType, input.imageDataUrl);
    } catch {}
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  // ─── Handle refine submit ───
  const handleRefineSubmit = async () => {
    if (!prompt.trim() && !selectedFile) return;

    let dataUrl: string | null = null;
    let name: string | null = null;
    let type: string | null = null;
    let preview: string | null = imagePreview;

    if (selectedFile) {
      dataUrl = await new Promise<string>(resolve => {
        const r = new FileReader();
        r.onload = e => resolve(e.target?.result as string);
        r.readAsDataURL(selectedFile);
      });
      name = selectedFile.name;
      type = selectedFile.type;
    }

    const currentPrompt = prompt;
    setPrompt("");
    setSelectedFile(null);
    setImagePreview(null);

    await runGeneration(currentPrompt, dataUrl, name, type, preview);
  };

  return (
    <div className="min-h-screen hero-image-bg text-gray-100 flex selection:bg-purple-500/30 overflow-hidden">

      {/* ═══════════════════════════════════════════════
          LEFT SIDEBAR — identical to home page
      ═══════════════════════════════════════════════ */}
      <aside
        className={`sticky top-0 h-screen glass-nav-header border-r border-white/10 flex flex-col justify-between transition-all duration-300 z-40 ${
          isSidebarCollapsed ? "w-12" : "w-52"
        }`}
      >
        <div className="px-3 py-3 border-b border-white/5 flex items-center">
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="p-1.5 rounded-lg glass-chip text-gray-300 hover:text-white"
            title="Toggle Sidebar"
          >
            {isSidebarCollapsed ? (
              <PanelLeftOpen className="w-3.5 h-3.5" />
            ) : (
              <PanelLeftClose className="w-3.5 h-3.5" />
            )}
          </button>
        </div>

        {/* Nav Items + Recents */}
        <div className="flex-1 overflow-y-auto p-3 space-y-6">
          <nav className="space-y-0.5">
            <button
              onClick={() => { setActiveNav("home"); router.push("/"); }}
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

          {/* Recents */}
          {!isSidebarCollapsed && (
            <div className="space-y-1.5 pt-2 border-t border-white/5">
              <div className="flex items-center justify-between px-2.5">
                <span className="text-[10px] font-semibold tracking-wider text-gray-500 uppercase">
                  Recents
                </span>
                <div className="flex items-center space-x-2">
                  {projects.length > 0 && (
                    <button
                      onClick={clearProjects}
                      className="text-gray-600 hover:text-red-400 transition-all"
                      title="Clear history"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  )}
                  <button
                    onClick={() => router.push("/")}
                    className="text-gray-500 hover:text-purple-300 transition-all"
                    title="New Project"
                  >
                    <Plus className="w-3 h-3" />
                  </button>
                </div>
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

      {/* ═══════════════════════════════════════════════
          MAIN CONTENT — full height, scrollable internally
      ═══════════════════════════════════════════════ */}
      <main className="flex-1 flex flex-col overflow-hidden h-screen">

        {/* ── Two-column workspace body ── */}
        <div className="flex-1 flex overflow-hidden">

          {/* ── LEFT: Chat & Vision Thread ── */}
          <div className="flex flex-col border-r border-white/10 overflow-hidden"
            style={{ width: "420px", minWidth: "320px" }}
          >
            {/* Thread header */}
            <div className="px-5 py-3 border-b border-white/10 flex items-center justify-between bg-[#07050e]/60 shrink-0">
              <div className="flex items-center space-x-2 text-sm font-semibold text-white font-poppins">
                <Eye className="w-4 h-4 text-purple-400" />
                <span>Vision Thread</span>
              </div>
              <button
                onClick={() => { setMessages([]); setGeneratedCode(""); }}
                className="px-3 py-1 rounded-lg glass-chip text-xs font-medium text-gray-300 flex items-center space-x-1.5 transition-all hover:text-white"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Clear</span>
              </button>
            </div>

            {/* Scrollable thread area */}
            <div className="flex-1 overflow-y-auto p-5 space-y-5">

              {/* Empty state */}
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full text-center space-y-3 opacity-40">
                  <Eye className="w-8 h-8 text-purple-400" />
                  <p className="text-xs text-gray-400">Submit an image or prompt to begin</p>
                </div>
              )}

              {/* Dynamic messages */}
              {messages.map((msg) => (
                <div key={msg.id}>
                  {msg.role === "user" ? (
                    /* User message */
                    <div className="glass-card-dark p-4 rounded-2xl border border-white/10 space-y-3">
                      {msg.imageUrl && (
                        <div className="rounded-xl overflow-hidden border border-white/10 bg-black/60 max-h-52 flex items-center justify-center">
                          <img src={msg.imageUrl} alt="User upload" className="w-full h-full object-cover" />
                        </div>
                      )}
                      {msg.text && (
                        <p className="text-xs text-gray-200 font-medium leading-relaxed">{msg.text}</p>
                      )}
                      {!msg.text && !msg.imageUrl && (
                        <p className="text-xs text-gray-500 italic">Image submitted</p>
                      )}
                    </div>
                  ) : (
                    /* Agent message */
                    <div className="space-y-2.5">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-6 h-6 rounded-lg bg-purple-600/30 border border-purple-400/40 flex items-center justify-center shrink-0">
                          <Sparkles className="w-3.5 h-3.5 text-purple-300" />
                        </div>
                        <span className="text-xs font-semibold text-purple-300">Vision Agent</span>
                        <span className="text-[11px] text-gray-500">
                          {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </span>
                      </div>

                      <div className={`glass-card-dark p-4 rounded-2xl border text-xs leading-relaxed ${
                        msg.isError
                          ? "border-red-500/30 text-red-300"
                          : "border-white/10 text-gray-300"
                      }`}>
                        {msg.isLoading ? (
                          <div className="flex items-center space-x-2 text-purple-300">
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            <span>Analysing input and generating code...</span>
                          </div>
                        ) : (
                          <p>{msg.text}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              <div ref={threadEndRef} />
            </div>

            {/* ── Refine Input Bar ── */}
            <div className="p-4 border-t border-white/10 bg-[#07050e]/60 shrink-0">
              <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" className="hidden" />

              {imagePreview && (
                <div className="mb-2 flex items-center space-x-2 px-2">
                  <img src={imagePreview} alt="Attached" className="w-10 h-10 rounded-lg object-cover border border-purple-500/40" />
                  <p className="text-[11px] text-purple-300 truncate">{selectedFile?.name}</p>
                </div>
              )}

              <div className="relative glass-card-dark rounded-2xl p-2 flex items-center space-x-2 border border-white/10">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-gray-400 hover:text-purple-300 transition-all"
                  title="Attach image"
                >
                  <ImageIcon className="w-4 h-4" />
                </button>

                <input
                  type="text"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && !isGenerating) handleRefineSubmit(); }}
                  placeholder="Refine output or attach another screenshot..."
                  disabled={isGenerating}
                  className="flex-1 bg-transparent text-xs text-gray-100 placeholder-gray-500 focus:outline-none disabled:opacity-60"
                />

                <button
                  onClick={handleRefineSubmit}
                  disabled={isGenerating || (!prompt.trim() && !selectedFile)}
                  className="w-8 h-8 rounded-xl glow-purple-btn text-white flex items-center justify-center transition-all shadow-md disabled:opacity-40"
                >
                  {isGenerating ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Send className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* ── RIGHT: Code / Preview Panel ── */}
          <div className="flex-1 flex flex-col overflow-hidden bg-[#06040f]/50">

            {/* Panel header */}
            <div className="px-5 py-3 border-b border-white/10 flex items-center justify-between bg-[#07050e]/60 shrink-0">
              {/* Code / Preview toggle */}
              <div className="flex items-center space-x-1 bg-black/60 p-1 rounded-xl border border-white/10">
                <button
                  onClick={() => setActiveTab("code")}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    activeTab === "code"
                      ? "bg-purple-600 text-white shadow"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <Code2 className="w-3.5 h-3.5" />
                  <span>Code</span>
                </button>

                <button
                  onClick={() => setActiveTab("preview")}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    activeTab === "preview"
                      ? "bg-purple-600 text-white shadow"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>Preview</span>
                </button>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 text-gray-400">
                <button
                  onClick={() => copyToClipboard(generatedCode || "")}
                  className="p-1.5 hover:text-white glass-chip rounded-lg transition-all"
                  title="Copy Code"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button className="p-1.5 hover:text-white glass-chip rounded-lg transition-all" title="Download">
                  <Download className="w-4 h-4" />
                </button>
                <button className="p-1.5 hover:text-white glass-chip rounded-lg transition-all" title="Fullscreen">
                  <Maximize2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Code View */}
            {activeTab === "code" ? (
              <div className="flex-1 flex flex-col overflow-hidden p-4 space-y-3">
                {/* Tech Badges */}
                <div className="flex items-center space-x-2 text-[11px] shrink-0">
                  <span className="px-2.5 py-0.5 rounded bg-orange-950 text-orange-300 border border-orange-800/40 font-mono">HTML5</span>
                  <span className="px-2.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800/40 font-mono">CSS3</span>
                </div>

                {/* Code Area */}
                {generatedCode ? (
                  <div className="flex-1 bg-[#04020a] rounded-2xl p-4 border border-white/10 font-mono text-xs overflow-auto text-purple-200 leading-relaxed shadow-inner">
                    <pre className="whitespace-pre-wrap">{generatedCode}</pre>
                  </div>
                ) : (
                  <div className="flex-1 flex items-center justify-center">
                    {isGenerating ? (
                      <div className="flex items-center space-x-2 text-purple-300 text-xs">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Generating code...</span>
                      </div>
                    ) : (
                      <p className="text-xs text-gray-600 italic">No code generated yet</p>
                    )}
                  </div>
                )}
              </div>
            ) : (
              /* Live Preview */
              <div className="flex-1 p-4 overflow-hidden">
                <div className="w-full h-full rounded-2xl bg-black border border-white/10 overflow-hidden shadow-2xl">
                  {generatedCode ? (
                    <iframe
                      srcDoc={generatedCode}
                      title="Live Output Preview"
                      className="w-full h-full border-0"
                      sandbox="allow-scripts"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs text-gray-600 italic">
                      {isGenerating ? "Generating preview..." : "No preview yet"}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}
