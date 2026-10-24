/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: {
          light: "#F6F8F9",
          dark: "#0F171C",
        },
        surface: {
          light: "#FFFFFF",
          dark: "#18232A",
        },
        text: {
          light: "#14232B",
          dark: "#EDF2F4",
          muted: {
            light: "#52616B",
            dark: "#8D9DA8",
          },
        },
        primary: {
          DEFAULT: "#0F766E",
          hover: "#0D655E",
          light: "#E6F4F2",
          dark: "#14B8A6",
        },
        border: {
          light: "#DCE4E8",
          dark: "#2A3842",
        },
        danger: {
          DEFAULT: "#DC2626",
          light: "#FEF2F2",
        },
        warning: {
          DEFAULT: "#D97706",
          light: "#FFFBEB",
        },
        success: {
          DEFAULT: "#16A34A",
          light: "#F0FDF4",
        },
      },
    },
  },
  plugins: [],
};
