import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { execSync } from 'child_process'

// Get build info
const EXT_BUILD_SHA = process.env.EXT_BUILD_SHA || 'docker-build'
const EXT_BUILD_TIME = process.env.EXT_BUILD_TIME || new Date().toISOString()
const EXT_VERSION = process.env.EXT_VERSION || Date.now().toString()

const BUILD_INFO = {
  commit: EXT_BUILD_SHA,
  buildTime: EXT_BUILD_TIME,
  buildNumber: EXT_VERSION
}

export default defineConfig({
  plugins: [react()],
  base: './',
  define: {
    'BUILD_INFO': JSON.stringify(BUILD_INFO)
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    minify: false, // Disable minification for better Chrome extension compatibility
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'src/popup/index.html'),
        options: resolve(__dirname, 'src/options/index.html'),
        content: resolve(__dirname, 'src/content/index.ts'),
        background: resolve(__dirname, 'src/background/index.ts')
      },
      output: {
        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'content') {
            return 'content/index.js'
          }
          if (chunkInfo.name === 'background') {
            return 'background.js' // Service worker must be in root
          }
          return '[name].js'
        },
        chunkFileNames: 'assets/[name].js',
        assetFileNames: ({ name }) => {
          // CSS files go to content directory
          if (name && name.endsWith('.css')) {
            return 'content/styles.css'
          }
          return 'assets/[name].[ext]'
        }
      }
    }
  },
  publicDir: 'public'
})