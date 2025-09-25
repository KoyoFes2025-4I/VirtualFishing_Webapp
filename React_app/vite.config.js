import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// React Routerはクライアントサイドルーティング
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    fs: { strict: false }, // 任意のURLアクセスを可能にする
    middlewareMode: false, // 通常のサーバーモード
  },
  // build時にindex.htmlをSPA として扱う
  build: {
    rollupOptions: {
      input: 'index.html',
    },
  },
})