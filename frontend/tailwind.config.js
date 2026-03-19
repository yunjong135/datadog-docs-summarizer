/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        dd: {
          purple: '#632CA6',
          'purple-dark': '#4a1f7e',
          'purple-light': '#7b3bbf',
          'purple-bg': '#f5f0fb',
        },
      },
    },
  },
  plugins: [],
}
