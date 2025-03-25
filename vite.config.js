import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
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
        start_page: resolve(__dirname, 'src/start_page/index.html'),
        auth: resolve(__dirname, 'src/auth/index.html'),
        plot_sandbox: resolve(__dirname, 'src/plot_sandbox/index.html')
      }
    },
  },
})
