/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1E2422",
        canvas: "#F4F6F4",
        moss: {
          50: "#EEF3EC",
          100: "#DCE7D9",
          300: "#9DB897",
          500: "#4E6B47",
          600: "#3D5638",
          700: "#2E4029",
        },
        slate: {
          400: "#8A9490",
          600: "#4B5550",
        },
        amber: "#C08A2E",
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        body: ["'Inter'", "sans-serif"],
      },
      borderRadius: {
        card: "14px",
      },
    },
  },
  plugins: [],
}
