import { createApp } from 'vue'
import {createRouter,createWebHashHistory, createMemoryHistory } from 'vue-router'

// SFCs
import App from './App.vue'
import Start from './views/Start.vue'
import New from './views/NewProj.vue'
import Old from './views/OldProj.vue'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { mdi } from 'vuetify/iconsets/mdi'
import { aliases, fa } from 'vuetify/iconsets/fa'
import "@mdi/font/css/materialdesignicons.css"; // Ensure you are using css-loader
import "@fortawesome/fontawesome-free/css/all.css"; // Ensure your project is capable of handling css files
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Dropzone
// HACK: Default css, may not fit with vuetify
import "@deltablot/dropzone/src/dropzone.scss";

const router = createRouter(
  {
    history: createWebHashHistory(),
    routes: [
      {
        path: '/',
        name: 'start',
        component: Start
      },
      {
        path: '/old',
        name: 'old',
        component: Old
      },
      {
        path: '/new',
        name: 'new',
        component: New
      }
    ]
  }
)

const vuetify = createVuetify({
    components,
    directives,
    icons: {
      defaultSet: 'fa',
      aliases,
      sets: {
        mdi, fa
      },
    },
    theme: {
      defaultTheme: 'light',
    },
  })  

const app = createApp(App)
app.use(vuetify)
app.use(router)
app.mount('#app')

