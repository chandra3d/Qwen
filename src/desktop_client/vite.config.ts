import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
  },
  build: {
    target: ['es2021', 'chrome100', 'safari13'],
    minify: !process.env.VITE_DEV_MODE ? 'terser' : false,
    terserOptions: {
      compress: {
        drop_console: true,
      },
    },
  },
})
