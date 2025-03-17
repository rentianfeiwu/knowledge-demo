import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0',
    https: {
      key: fs.readFileSync('.cert/key.pem'),
      cert: fs.readFileSync('.cert/cert.pem'),
    },
    proxy: {
      '/api': {
        target: 'https://localhost:8000',
        secure: false,
        changeOrigin: true
      }
    }
  },
})