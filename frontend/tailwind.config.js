/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,jsx}', './components/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#05060f',
          900: '#0a0b1a',
          800: '#10112a',
          700: '#1a1d3a',
          600: '#262a4f',
        },
        neon: {
          purple: '#b36cff',
          blue: '#4ea8ff',
          pink: '#ff6ab8',
          cyan: '#7ee8fa',
          lime: '#c8ff6b',
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          'Noto Sans SC',
          'PingFang SC',
          'Microsoft YaHei',
          'sans-serif',
        ],
      },
      boxShadow: {
        glow: '0 0 40px -10px rgba(179, 108, 255, 0.55)',
        'glow-blue': '0 0 40px -10px rgba(78, 168, 255, 0.45)',
      },
      keyframes: {
        blink: {
          '0%,50%': { opacity: 1 },
          '51%,100%': { opacity: 0 },
        },
        'float-slow': {
          '0%,100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      animation: {
        blink: 'blink 1s steps(1) infinite',
        'float-slow': 'float-slow 6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
