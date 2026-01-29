import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#c2410c",
          light: "#ea580c",
          dark: "#9a3412",
        },
        surface: {
          DEFAULT: "#fafafa",
          muted: "#f5f5f5",
          border: "#e5e5e5",
        },
        ink: {
          DEFAULT: "#171717",
          muted: "#525252",
          subtle: "#a3a3a3",
        },
      },
      fontFamily: {
        sans: ["var(--font-outfit)", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
