"use client";

import { useState, useEffect } from "react";

export interface Project {
  id: string;
  title: string;
  timestamp: string;
  model?: string;
  prompt?: string;
}

const STORAGE_KEY = "snipcode_projects";
const MAX_PROJECTS = 20;

/** Extract a 2–3 word theme from a prompt string */
function generateTitle(prompt: string): string {
  if (!prompt.trim()) return "UI Sketch";

  const stopWords = new Set([
    "a","an","the","make","create","build","with","and","for","to","of","in",
    "on","at","by","from","that","this","into","use","add","some","give","show",
    "me","please","can","could","would","like","want","need","help","its","my",
    "is","are","was","were","be","been","have","has","do","does","did","will",
  ]);

  const words = prompt
    .toLowerCase()
    .replace(/[^a-z\s]/g, "")
    .split(/\s+/)
    .filter(w => w.length > 2 && !stopWords.has(w));

  if (words.length === 0) return "UI Sketch";

  return words
    .slice(0, 3)
    .map(w => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}

/** Human-readable relative time */
export function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "Yesterday";
  return `${days}d ago`;
}

export function useProjectHistory() {
  const [projects, setProjects] = useState<Project[]>([]);

  // Hydrate from localStorage on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setProjects(JSON.parse(raw));
    } catch {
      // corrupted storage — start fresh
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  /** Save a new project (or update existing by id) and return it */
  const saveProject = (id: string, prompt: string, model?: string): Project => {
    const title = generateTitle(prompt);
    const entry: Project = {
      id,
      title,
      timestamp: new Date().toISOString(),
      model,
      prompt,
    };

    setProjects(prev => {
      const deduped = prev.filter(p => p.id !== id);
      const updated = [entry, ...deduped].slice(0, MAX_PROJECTS);
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch {}
      return updated;
    });

    return entry;
  };

  /** Remove a single project */
  const removeProject = (id: string) => {
    setProjects(prev => {
      const updated = prev.filter(p => p.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  /** Wipe all history */
  const clearProjects = () => {
    setProjects([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  // Attach live relative timestamps
  const projectsWithLabel = projects.map(p => ({
    ...p,
    timestampLabel: relativeTime(p.timestamp),
  }));

  return { projects: projectsWithLabel, saveProject, removeProject, clearProjects };
}
