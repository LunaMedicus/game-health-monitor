import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: "#090909",
        surface: "#111111",
        "surface-raised": "#171717",
        border: "#262626",
        "border-active": "#3a3a3a",
        text: "#f1eee8",
        muted: "#8f8a82",
        "very-muted": "#5a5650",
        healthy: "#70e38b",
        playable: "#e6c84f",
        warning: "#f59e0b",
        danger: "#ef4444",
        cyan: "#22d3ee",
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        display: ["var(--font-display)"],
        mono: ["var(--font-mono)"],
        pixel: ["var(--font-pixel)"],
      },
      animation: {
        "fade-in": "fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
