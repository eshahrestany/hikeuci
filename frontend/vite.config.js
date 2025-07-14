import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss()
  ],
  build: {
    outDir: 'dist',
    watch: {
      include: 'src/**',
      exclude: 'node_modules/**'
    }
  },
  server: {
    proxy: {
      "/api": "http://localhost:5000"
    }
  }
});