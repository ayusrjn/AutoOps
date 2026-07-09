/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0B0F19",
        surface: "#161D2B",
        element: "#212C3F",
        borderDefault: "#2D394E",
        borderFocus: "#3B82F6",
        textPrimary: "#F3F4F6",
        textSecondary: "#9CA3AF",
        textMuted: "#6B7280",
        critical: {
          DEFAULT: "#451A1A",
          text: "#F87171",
          border: "#7F1D1D"
        },
        warning: {
          DEFAULT: "#3C240E",
          text: "#FBBF24",
          border: "#78350F"
        },
        success: {
          DEFAULT: "#064E3B",
          text: "#34D399",
          border: "#065F46"
        },
        info: {
          DEFAULT: "#1E3A8A",
          text: "#60A5FA",
          border: "#1E40AF"
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['SFMono-Regular', 'Consolas', 'Liberation Mono', 'monospace']
      }
    },
  },
  plugins: [],
}
