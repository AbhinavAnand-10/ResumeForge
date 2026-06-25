/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── ResumeForge AI design tokens ──────────────────────────────────
        // "Forensic lab report" palette: ink black, paper cream, signal amber
        ink: {
          950: "#0B0D0C",
          900: "#121512",
          800: "#1B1F1C",
          700: "#272C28",
          600: "#3A413C",
        },
        paper: {
          50: "#FAF8F3",
          100: "#F2EEE3",
          200: "#E6DFCE",
        },
        signal: {
          DEFAULT: "#E8B23C",   // amber — the diagnostic accent
          dim: "#C99830",
          bright: "#FFD166",
        },
        verdict: {
          good: "#5B8C5A",      // muted forensic green
          warn: "#D98A3D",      // muted amber-orange
          bad: "#C0533D",       // muted brick red
        },
      },
      fontFamily: {
        display: ["'Fraunces'", "Georgia", "serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
        sans: ["'Inter'", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "grain": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E\")",
      },
      animation: {
        "scan": "scan 2.4s ease-in-out infinite",
        "fade-up": "fadeUp 0.5s ease-out forwards",
      },
      keyframes: {
        scan: {
          "0%, 100%": { transform: "translateY(0%)" },
          "50%": { transform: "translateY(100%)" },
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
