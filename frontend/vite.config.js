import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy: las llamadas a /api se redirigen al backend durante desarrollo.
    // Así evitamos CORS en dev y no hardcodeamos la URL del backend en el frontend.
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
