/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f4ff',
          100: '#bae3ff',
          200: '#7cc4ff',
          300: '#47a3ff',
          400: '#218aff',
          500: '#0958d9',
          600: '#003eb0',
          700: '#002c8c',
          800: '#001d66',
          900: '#001233',
        },
        goose: {
          yellow: '#FFE55C',
          orange: '#FF9F43',
          blue: '#54A0FF',
          green: '#5FD068',
          purple: '#9B59B6',
        },
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
}