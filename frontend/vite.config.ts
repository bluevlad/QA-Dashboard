import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 4095,
    proxy: {
      '/api': {
        target: 'http://localhost:9095',
        changeOrigin: true,
      },
    },
  },
});
