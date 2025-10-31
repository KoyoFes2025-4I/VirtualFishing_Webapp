import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// React Routerはクライアントサイドルーティング
export default defineConfig({
  plugins: [react()],
  base: '/',
  
  // build時にindex.htmlをSPA として扱う
  build: {
    rollupOptions: {
      input: 'index.html',
    },
  },
})