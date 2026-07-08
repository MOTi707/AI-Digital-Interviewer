import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Noto Sans SC', 'sans-serif'],
        mono: ['Space Mono', 'monospace'],
      },
      colors: {
        memphis: {
          coral: '#ff006e',
          yellow: '#ffbe0b',
          teal: '#00f5d4',
          blue: '#3a86ff',
          purple: '#8338ec',
          orange: '#fb5607',
          cream: '#fef9ef',
          black: '#000000',
          white: '#ffffff',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
