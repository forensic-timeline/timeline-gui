import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from "path"
//import vueJsx from '@vitejs/plugin-vue-jsx'

const __dirname = dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()
  ],
  build: {
    assetsDir: "static",
    rollupOptions: {
      input: {
        // TODO: Only build pages needed
        //start_page: resolve(__dirname, 'src/start_page/index.html'),
        auth: resolve(__dirname, 'src/auth/index.html'),
        start_page: resolve(__dirname, 'src/start_page/index.html'),
        timeline_sandbox: resolve(__dirname, 'src/timeline_sandbox/index.html')
      }
    },
  },
})
