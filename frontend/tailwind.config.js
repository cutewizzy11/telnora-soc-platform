/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        telnora: {
          dark: "#0b1120",
          panel: "#111827",
          accent: "#22d3ee",
          accent2: "#38bdf8",
        },
      },
    },
  },
  plugins: [],
};
