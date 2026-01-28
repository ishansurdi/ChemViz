/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-base': '#F7F8FA',
        'surface': '#FFFFFF',
        'border': '#D1D5DB',
        'charcoal': '#1F2933',
        'slate': '#4B5563',
        'ash': '#6B7280',
        'industrial-blue': '#365F8B',
        'industrial-blue-hover': '#2F5278',
        'pale-steel': '#E6EEF7',
      },
      fontFamily: {
        'heading': ['IBM Plex Sans', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
