/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink:     { DEFAULT: '#0a0a0f', 2: '#111118', 3: '#17171f', 4: '#1f1f2a', 5: '#2a2a38' },
        amber:   { DEFAULT: '#d97706', light: '#f59e0b', glow: '#fbbf24' },
        jade:    { DEFAULT: '#059669', light: '#10b981', glow: '#34d399' },
        rose:    { DEFAULT: '#e11d48', light: '#f43f5e' },
        sky:     { DEFAULT: '#0284c7', light: '#38bdf8' },
        violet:  { DEFAULT: '#7c3aed', light: '#a78bfa' },
      },
      fontFamily: {
        sans:  ['Inter', 'system-ui', 'sans-serif'],
        mono:  ['JetBrains Mono', 'Fira Code', 'monospace'],
        serif: ['Playfair Display', 'Georgia', 'serif'],
      },
      animation: {
        'fade-up':  'fadeUp 0.4s ease both',
        'fade-in':  'fadeIn 0.3s ease both',
        'pulse-dot':'pulseDot 2s infinite',
      },
      keyframes: {
        fadeUp:   { from: { opacity: 0, transform: 'translateY(16px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        fadeIn:   { from: { opacity: 0 }, to: { opacity: 1 } },
        pulseDot: { '0%,100%': { opacity: 1 }, '50%': { opacity: 0.3 } },
      }
    },
  },
  plugins: [],
}
