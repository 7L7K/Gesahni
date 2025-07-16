import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      // Proxy API calls starting with /auth to your FastAPI backend (change 8000 if needed)
      '/auth': 'http://localhost:5000'
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './setupTests.ts'
  }
})
