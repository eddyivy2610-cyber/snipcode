"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutGrid,
  Code2,
  Eye,
  Layers,
  Sun,
  Moon,
  LogOut,
} from "lucide-react";
import { toast } from "sonner";

interface SidebarProps {
  isDarkTheme: boolean;
  onToggleTheme: () => void;
  onSelectMenu?: (id: string) => void;
  hasCodeOutput?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isDarkTheme,
  onToggleTheme,
  onSelectMenu,
  hasCodeOutput = false,
}) => {
  const [activeItem, setActiveItem] = useState("dashboard");
  const [hoveredItem, setHoveredItem] = useState<{ id: string; label: string; badge?: string; top: number } | null>(null);
  const [activeTop, setActiveTop] = useState<number | null>(null);

  const activeBtnRef = useRef<HTMLButtonElement | null>(null);

  // Active production navigation items only
  const mainMenuItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutGrid },
    { id: "studio", label: "Studio Workspace", icon: Code2, badge: "AI" },
    { id: "preview", label: "Live Preview", icon: Eye, badge: "LIVE" },
    { id: "detection", label: "Detection Pipeline", icon: Layers, badge: "AI" },
  ];

  const handleMouseEnter = (e: React.MouseEvent<HTMLElement>, id: string, label: string, badge?: string) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setHoveredItem({
      id,
      label,
      badge,
      top: rect.top + rect.height / 2,
    });
  };

  useEffect(() => {
    if (activeBtnRef.current) {
      const rect = activeBtnRef.current.getBoundingClientRect();
      setActiveTop(rect.top + rect.height / 2);
    }
  }, [activeItem]);

  return (
    <aside className="relative flex items-center h-full select-none z-50">
      {/* Flush Zero-Gap Sidebar Shell (Fixed 56px Width) */}
      <div
        className={`relative flex flex-col justify-between h-full w-[56px] border-r py-3 px-1.5 transition-all duration-300 overflow-hidden ${
          isDarkTheme
            ? "bg-zinc-900/95 border-zinc-800/90 text-zinc-300"
            : "bg-white/95 border-zinc-200/90 text-zinc-700"
        }`}
      >
        {/* Top Header: Compact Logo */}
        <div
          className="relative flex items-center justify-center mb-1 group cursor-pointer flex-shrink-0"
          onMouseEnter={(e) => handleMouseEnter(e, "brand_logo", "Snipcode AI Studio")}
          onMouseLeave={() => setHoveredItem(null)}
        >
          <div
            className={`w-9 h-9 rounded-xl border flex items-center justify-center flex-shrink-0 shadow-sm transition-transform duration-200 group-hover:scale-105 ${
              isDarkTheme
                ? "bg-zinc-800/90 border-zinc-700/60 text-white"
                : "bg-zinc-100 border-zinc-200 text-zinc-900"
            }`}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M7 17L13 5" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
              <path d="M11 19L17 7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
              <circle cx="6" cy="6" r="1.2" fill="currentColor" />
              <circle cx="18" cy="18" r="1.2" fill="currentColor" />
            </svg>
          </div>
        </div>

        {/* Middle Navigation Menu Items */}
        <div className="flex-1 flex flex-col gap-1.5 my-2 overflow-y-auto overflow-x-hidden no-scrollbar items-center w-full">
          {mainMenuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeItem === item.id;
            const isLocked = item.id === "preview" && !hasCodeOutput;

            return (
              <div
                key={item.id}
                className="relative flex items-center justify-center w-full"
                onMouseEnter={(e) => handleMouseEnter(e, item.id, item.label, item.badge)}
                onMouseLeave={() => setHoveredItem(null)}
              >
                <button
                  ref={isActive ? activeBtnRef : null}
                  onClick={() => {
                    if (isLocked) {
                      toast.error("Live Preview unlocks after generating code output!");
                      return;
                    }
                    setActiveItem(item.id);
                    onSelectMenu?.(item.id);
                  }}
                  className={`relative flex items-center justify-center w-9 h-9 rounded-xl transition-all duration-200 ${
                    isLocked
                      ? "opacity-40 cursor-not-allowed text-zinc-600"
                      : isActive
                      ? isDarkTheme
                        ? "bg-purple-200 text-zinc-950 shadow-sm font-bold"
                        : "bg-purple-600 text-white shadow-sm font-bold"
                      : isDarkTheme
                      ? "text-zinc-400 hover:text-white hover:bg-zinc-800/60"
                      : "text-zinc-500 hover:text-zinc-950 hover:bg-zinc-100"
                  }`}
                >
                  <Icon
                    className={`w-4 h-4 transition-transform duration-200 ${
                      hoveredItem?.id === item.id ? "scale-110" : ""
                    } ${
                      isActive
                        ? isDarkTheme ? "text-zinc-950" : "text-white"
                        : isDarkTheme ? "text-zinc-400" : "text-zinc-500"
                    }`}
                  />
                </button>
              </div>
            );
          })}
        </div>

        {/* Bottom Actions: Theme Toggle & Logout */}
        <div className={`flex flex-col gap-1.5 pt-2 border-t items-center flex-shrink-0 transition-colors w-full ${
          isDarkTheme ? "border-zinc-800/80" : "border-zinc-200"
        }`}>
          {/* Theme Toggle */}
          <div
            className="relative flex items-center justify-center w-full"
            onMouseEnter={(e) => handleMouseEnter(e, "theme_toggle", isDarkTheme ? "Switch to Light Mode" : "Switch to Dark Mode")}
            onMouseLeave={() => setHoveredItem(null)}
          >
            <button
              onClick={onToggleTheme}
              className={`flex items-center justify-center w-9 h-9 rounded-xl transition-all duration-200 ${
                isDarkTheme
                  ? "text-zinc-400 hover:text-white hover:bg-zinc-800/60"
                  : "text-zinc-500 hover:text-zinc-950 hover:bg-zinc-100"
              }`}
            >
              {isDarkTheme ? (
                <Sun className="w-4 h-4 text-amber-400 transition-transform duration-300 hover:rotate-45" />
              ) : (
                <Moon className="w-4 h-4 text-indigo-600 transition-transform duration-300 hover:-rotate-12" />
              )}
            </button>
          </div>

          {/* Logout */}
          <div
            className="relative flex items-center justify-center w-full"
            onMouseEnter={(e) => handleMouseEnter(e, "logout", "Logout")}
            onMouseLeave={() => setHoveredItem(null)}
          >
            <button
              className={`flex items-center justify-center w-9 h-9 rounded-xl transition-all duration-200 group ${
                isDarkTheme
                  ? "text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10"
                  : "text-zinc-500 hover:text-rose-500 hover:bg-rose-500/10"
              }`}
            >
              <LogOut className="w-4 h-4 transition-colors group-hover:text-rose-500" />
            </button>
          </div>
        </div>
      </div>

      {/* Floating Active Indicator Pointer Arrow */}
      {activeTop !== null && (
        <div
          style={{ top: `${activeTop}px` }}
          className={`fixed left-[50px] -translate-y-1/2 w-0 h-0 border-y-[5px] border-y-transparent border-l-[7px] pointer-events-none z-50 transition-all duration-200 ${
            isDarkTheme ? "border-l-zinc-900 drop-shadow-[1px_0_2px_rgba(0,0,0,0.5)]" : "border-l-white drop-shadow-[1px_0_2px_rgba(0,0,0,0.1)]"
          }`}
        />
      )}

      {/* Floating Tooltip Portal */}
      <AnimatePresence>
        {hoveredItem && (
          <motion.div
            key={hoveredItem.id}
            initial={{ opacity: 0, x: -4, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: -4, scale: 0.95 }}
            transition={{ duration: 0.12, ease: "easeOut" }}
            style={{ top: `${hoveredItem.top}px` }}
            className={`fixed left-16 -translate-y-1/2 px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap pointer-events-none z-[100] border shadow-2xl flex items-center gap-2 ${
              isDarkTheme
                ? "bg-zinc-900/95 text-zinc-100 border-zinc-700/80 shadow-black/80"
                : "bg-white/95 text-zinc-900 border-zinc-300/90 shadow-zinc-400/50"
            }`}
          >
            <div
              className={`absolute -left-1 top-1/2 -translate-y-1/2 w-2 h-2 rotate-45 border-l border-b ${
                isDarkTheme ? "bg-zinc-900 border-zinc-700/80" : "bg-white border-zinc-300/90"
              }`}
            />
            <span>{hoveredItem.label}</span>
            {hoveredItem.badge && (
              <span className="px-1.5 py-0.2 text-[9px] font-bold rounded-md bg-purple-500/20 text-purple-400 border border-purple-500/30 uppercase">
                {hoveredItem.badge}
              </span>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </aside>
  );
};
