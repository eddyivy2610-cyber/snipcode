import { create } from "zustand";

export type ThemeType = "dark" | "light" | "cyber_blue";
export type FrameworkType = "html" | "react" | "flutter";
export type CodeLanguageType = "html" | "css" | "ir_json" | "react" | "flutter";

export interface DetectionBox {
  type: string;
  bbox: [number, number, number, number];
  confidence: number;
  text?: string;
}

export interface AppState {
  uploadedImage: string | null;
  detections: DetectionBox[];
  irTree: any | null;
  vnodeTree: any | null;
  htmlCode: string;
  cssCode: string;
  reactCode: string;
  flutterCode: string;

  activeTab: "editor" | "preview" | "ir_tree";
  activeCodeLanguage: CodeLanguageType;
  selectedFramework: FrameworkType;
  theme: ThemeType;
  isProcessing: boolean;
  viewportWidth: "100%" | "768px" | "375px";

  // Actions
  setUploadedImage: (image: string | null) => void;
  setDetections: (detections: DetectionBox[]) => void;
  setIrTree: (tree: any) => void;
  setVnodeTree: (tree: any) => void;
  setGeneratedCode: (html: string, css: string, react?: string, flutter?: string) => void;
  setActiveTab: (tab: "editor" | "preview" | "ir_tree") => void;
  setActiveCodeLanguage: (lang: CodeLanguageType) => void;
  setSelectedFramework: (fw: FrameworkType) => void;
  setTheme: (theme: ThemeType) => void;
  setIsProcessing: (processing: boolean) => void;
  setViewportWidth: (width: "100%" | "768px" | "375px") => void;
  resetAll: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  uploadedImage: null,
  detections: [],
  irTree: null,
  vnodeTree: null,
  htmlCode: "",
  cssCode: "",
  reactCode: "",
  flutterCode: "",

  activeTab: "editor",
  activeCodeLanguage: "html",
  selectedFramework: "html",
  theme: "dark",
  isProcessing: false,
  viewportWidth: "100%",

  setUploadedImage: (image) => set({ uploadedImage: image }),
  setDetections: (detections) => set({ detections }),
  setIrTree: (tree) => set({ irTree: tree }),
  setVnodeTree: (tree) => set({ vnodeTree: tree }),
  setGeneratedCode: (html, css, react = "", flutter = "") =>
    set({
      htmlCode: html,
      cssCode: css,
      reactCode: react,
      flutterCode: flutter,
    }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setActiveCodeLanguage: (lang) => set({ activeCodeLanguage: lang }),
  setSelectedFramework: (fw) => set({ selectedFramework: fw }),
  setTheme: (theme) => set({ theme }),
  setIsProcessing: (processing) => set({ isProcessing: processing }),
  setViewportWidth: (width) => set({ viewportWidth: width }),
  resetAll: () =>
    set({
      uploadedImage: null,
      detections: [],
      irTree: null,
      vnodeTree: null,
      htmlCode: "",
      cssCode: "",
      reactCode: "",
      flutterCode: "",
      isProcessing: false,
    }),
}));
