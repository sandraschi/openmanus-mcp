import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const devPort = Number(env.VITE_DEV_PORT ?? "10769");
  const apiTarget = env.VITE_API_TARGET ?? "http://127.0.0.1:10768";

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
          allowedHosts: ['goliath'],
      port: Number.isFinite(devPort) ? devPort : 10769,
      host: "127.0.0.1",
      strictPort: true,
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
