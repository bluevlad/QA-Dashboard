import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/qa/',
  plugins: [react()],
  server: {
    port: 4095,
    proxy: {
      '/qa/api': {
        target: 'http://localhost:9095',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/qa/, ''),
      },
    },
  },
});
