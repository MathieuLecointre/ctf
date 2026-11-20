/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'ctf-navy': '#0a1a2f',
        'ctf-card': '#162545',
        'ctf-border': '#333f59',
        'ctf-blue': '#004e7a',
        'ctf-cyan': '#7ec8ff',
        'ctf-red': '#ff3e3e',
        'ctf-gold': '#ffcc00',
        'ctf-gray': '#7b7b7b',
      },
      fontFamily: {
        rajdhani: ['Rajdhani', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
