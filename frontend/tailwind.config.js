/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: ["class", '[data-mode="dark"]'],
  theme: {
    extend: {
      colors: {
        "always-white": "hsl(var(--always-white) / <alpha-value>)",
        "always-black": "hsl(var(--always-black) / <alpha-value>)",
        "accent-brand": "hsl(var(--accent-brand) / <alpha-value>)",
        "accent-main-000": "hsl(var(--accent-main-000) / <alpha-value>)",
        "accent-main-100": "hsl(var(--accent-main-100) / <alpha-value>)",
        "accent-main-200": "hsl(var(--accent-main-200) / <alpha-value>)",
        "accent-main-900": "hsl(var(--accent-main-900) / <alpha-value>)",
        "accent-pro-000": "hsl(var(--accent-pro-000) / <alpha-value>)",
        "accent-pro-100": "hsl(var(--accent-pro-100) / <alpha-value>)",
        "accent-pro-200": "hsl(var(--accent-pro-200) / <alpha-value>)",
        "accent-pro-900": "hsl(var(--accent-pro-900) / <alpha-value>)",
        "accent-secondary-000": "hsl(var(--accent-secondary-000) / <alpha-value>)",
        "accent-secondary-100": "hsl(var(--accent-secondary-100) / <alpha-value>)",
        "accent-secondary-200": "hsl(var(--accent-secondary-200) / <alpha-value>)",
        "accent-secondary-900": "hsl(var(--accent-secondary-900) / <alpha-value>)",
        "bg-000": "hsl(var(--bg-000) / <alpha-value>)",
        "bg-100": "hsl(var(--bg-100) / <alpha-value>)",
        "bg-200": "hsl(var(--bg-200) / <alpha-value>)",
        "bg-300": "hsl(var(--bg-300) / <alpha-value>)",
        "bg-400": "hsl(var(--bg-400) / <alpha-value>)",
        "bg-500": "hsl(var(--bg-500) / <alpha-value>)",
        "border-100": "hsl(var(--border-100) / <alpha-value>)",
        "border-200": "hsl(var(--border-200) / <alpha-value>)",
        "border-300": "hsl(var(--border-300) / <alpha-value>)",
        "border-400": "hsl(var(--border-400) / <alpha-value>)",
        "danger-000": "hsl(var(--danger-000) / <alpha-value>)",
        "danger-100": "hsl(var(--danger-100) / <alpha-value>)",
        "danger-200": "hsl(var(--danger-200) / <alpha-value>)",
        "danger-900": "hsl(var(--danger-900) / <alpha-value>)",
        "oncolor-100": "hsl(var(--oncolor-100) / <alpha-value>)",
        "oncolor-200": "hsl(var(--oncolor-200) / <alpha-value>)",
        "oncolor-300": "hsl(var(--oncolor-300) / <alpha-value>)",
        "pictogram-100": "hsl(var(--pictogram-100) / <alpha-value>)",
        "pictogram-200": "hsl(var(--pictogram-200) / <alpha-value>)",
        "pictogram-300": "hsl(var(--pictogram-300) / <alpha-value>)",
        "pictogram-400": "hsl(var(--pictogram-400) / <alpha-value>)",
        "success-000": "hsl(var(--success-000) / <alpha-value>)",
        "success-100": "hsl(var(--success-100) / <alpha-value>)",
        "success-200": "hsl(var(--success-200) / <alpha-value>)",
        "success-900": "hsl(var(--success-900) / <alpha-value>)",
        "text-000": "hsl(var(--text-000) / <alpha-value>)",
        "text-100": "hsl(var(--text-100) / <alpha-value>)",
        "text-200": "hsl(var(--text-200) / <alpha-value>)",
        "text-300": "hsl(var(--text-300) / <alpha-value>)",
        "text-400": "hsl(var(--text-400) / <alpha-value>)",
        "text-500": "hsl(var(--text-500) / <alpha-value>)",
        "warning-000": "hsl(var(--warning-000) / <alpha-value>)",
        "warning-100": "hsl(var(--warning-100) / <alpha-value>)",
        "warning-200": "hsl(var(--warning-200) / <alpha-value>)",
        "warning-900": "hsl(var(--warning-900) / <alpha-value>)"
      },
      fontFamily: {
        ui: ["var(--font-ui)"],
        "ui-serif": ["var(--font-ui-serif)"],
        "claude-response": ["var(--font-claude-response)"],
        mono: ["var(--font-mono)"]
      },
      boxShadow: {
        card: "0 0.25rem 1.25rem hsl(var(--always-black) / 3.5%)",
        "card-strong": "0 0.25rem 1.25rem hsl(var(--always-black) / 7.5%)"
      }
    }
  },
  plugins: []
};
