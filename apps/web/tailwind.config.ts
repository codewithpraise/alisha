import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        void: "var(--theme-bg, #0A0908)",
        deep: "var(--theme-deep, #111210)",
        surface: "var(--theme-surface-solid, #181917)",
        raised: "var(--theme-raised, #21221F)",
        hairline: "var(--theme-border, #2C2B29)",
        ivory: "#F2EFE8",
        muted: "#8A8880",
        tertiary: "#5C5A55",
        amber: {
          DEFAULT: "var(--theme-accent, #D4A853)",
          dark: "var(--theme-accent-dark, #A07A30)",
          dim: "rgba(var(--theme-accent-rgb, 212, 168, 83), 0.15)",
          glow: "rgba(var(--theme-accent-rgb, 212, 168, 83), 0.35)",
        },
        rose: {
          DEFAULT: "#C47067",
          dim: "rgba(196, 112, 103, 0.15)",
        },
        sage: {
          DEFAULT: "#5E7A68",
          dim: "rgba(94, 122, 104, 0.15)",
        },
        bubble: {
          alisha: "#1E1F1D",
          user: "#2C2822",
        },
      },
      fontFamily: {
        serif: ['"Instrument Serif"', '"Playfair Display"', "Georgia", "serif"],
        arabic: ['"Amiri"', '"Noto Naskh Arabic"', "serif"],
        sans: [
          'var(--font-custom, "Geist")',
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "Roboto",
          "sans-serif",
        ],
        mono: ["ui-monospace", "SFMono-Regular", "Consolas", "monospace"],
      },
      keyframes: {
        "pulse-amber": {
          "0%, 100%": { opacity: "0.4", transform: "scale(0.9)" },
          "50%": { opacity: "1", transform: "scale(1.2)" },
        },
        "breath-ring": {
          "0%, 100%": { transform: "scale(0.92)", opacity: "0.35" },
          "50%": { transform: "scale(1.08)", opacity: "0.8" },
        },
        "typing-bounce": {
          "0%, 80%, 100%": { transform: "scale(0.6)", opacity: "0.4" },
          "40%": { transform: "scale(1.1)", opacity: "1" },
        },
        "ripple-wave": {
          "0%": { transform: "translate(-50%, -50%) scale(0.2)", opacity: "1" },
          "100%": { transform: "translate(-50%, -50%) scale(1.6)", opacity: "0" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "pulse-amber": "pulse-amber 2.8s infinite",
        "breath-ring": "breath-ring 3.5s ease-in-out infinite",
        "typing-bounce": "typing-bounce 1.4s infinite ease-in-out both",
        "ripple-wave": "ripple-wave 0.95s cubic-bezier(0.1, 0.8, 0.3, 1) forwards",
        "fade-in": "fade-in 0.25s ease-out forwards",
        "spin-slow": "spin 12s linear infinite",
      },
      borderRadius: {
        sm: "8px",
        md: "14px",
        lg: "20px",
        full: "9999px",
      },
    },
  },
  plugins: [],
};

export default config;
