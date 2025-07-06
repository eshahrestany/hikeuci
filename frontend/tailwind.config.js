import { defineConfig } from 'tailwindcss'

export default defineConfig({
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  plugins: [],
  theme: {
    extend: {
      colors: {
        /* UCI palette — all use CSS variables so opacity variants work */
        'uci-blue':   'rgb(var(--uci-blue) / <alpha-value>)',
        'uci-gold':   'rgb(var(--uci-gold) / <alpha-value>)',
        forest:       'rgb(var(--forest) / <alpha-value>)',
        sky:          'rgb(var(--sky) / <alpha-value>)',
        earth:        'rgb(var(--earth) / <alpha-value>)',
        stone:        'rgb(var(--stone) / <alpha-value>)',
        midnight:     'rgb(var(--midnight) / <alpha-value>)',
      },
    },
  },
})