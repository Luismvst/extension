import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'src/popup/index.html'),
        options: resolve(__dirname, 'src/options/index.html'),
        content: resolve(__dirname, 'src/content/index.ts'),
        background: resolve(__dirname, 'src/background/index.ts'),
        'content/styles': resolve(__dirname, 'src/content/styles.css')
      },
      output: {
        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'content') {
            return 'content/index.js'
          }
          if (chunkInfo.name === 'background') {
            return 'background/index.js'
          }
          if (chunkInfo.name === 'content/styles') {
            return 'content/styles.css'
          }
          return '[name].js'
        }
      }
    }
  },
  publicDir: 'public'
})