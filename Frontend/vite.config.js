import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
// https://vite.dev/config/
// export default defineConfig({
//   plugins: [react()],
// });
export default defineConfig({
  build: {
      sourcemap: false, // Disable source maps
  },
  server: {
      sourcemap: false, // Disable source maps for dev server
  },
});