"use client";

import React from "react";
import { User, Sparkles } from "lucide-react";

interface TopbarProps {
  isDarkTheme: boolean;
  pageName?: string;
}

export const Topbar: React.FC<TopbarProps> = ({
  isDarkTheme,
  pageName = "Dashboard",
}) => {
  return (
    <header
      className={`h-14 px-6 border-b flex items-center justify-between backdrop-blur-xl transition-colors duration-300 ${
        isDarkTheme
          ? "bg-zinc-950/80 border-zinc-800/80 text-zinc-100"
          : "bg-white/80 border-zinc-200/90 text-zinc-900"
      }`}
    >
      {/* Left Section: Page Name */}
      <div className="flex items-center gap-3">
        <h1 className="text-base font-bold tracking-tight text-zinc-100 flex items-center gap-2">
          {pageName}
        </h1>
      </div>

      {/* Far Right Section: Account User Icon */}
      <div className="flex items-center gap-3">
        <button
          className={`w-9 h-9 rounded-full border flex items-center justify-center transition-all cursor-pointer group shadow-sm ${
            isDarkTheme
              ? "bg-zinc-900 border-zinc-800 text-zinc-300 hover:text-white hover:border-zinc-700"
              : "bg-zinc-100 border-zinc-200 text-zinc-700 hover:text-zinc-950 hover:border-zinc-300"
          }`}
          title="Account Profile"
        >
          <User className="w-4.5 h-4.5 transition-transform duration-200 group-hover:scale-105" />
        </button>
      </div>
    </header>
  );
};
