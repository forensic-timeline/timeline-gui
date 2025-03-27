import { createApp } from 'vue'
import {createRouter, createWebHashHistory} from 'vue-router'

// SFCs
import App from './App.vue'
import Observable from './views/Observable.vue'
import JsTree from './views/JsTree.vue'
// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { mdi } from 'vuetify/iconsets/mdi'
import { aliases, fa } from 'vuetify/iconsets/fa'
import "@mdi/font/css/materialdesignicons.css"; // Ensure you are using css-loader
import "@fortawesome/fontawesome-free/css/all.css"; // Ensure your project is capable of handling css files
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const router = createRouter(
  {
    history: createWebHashHistory(),
    routes: [
      {
        path: '/observable',
        name: 'observable',
        component: Observable
      },
      {
        path: '/',
        name: 'jstree',
        component: JsTree
      }
    ]
  }
)

const vuetify = createVuetify({
    components,
    directives,
    icons: {
      defaultSet: 'mdi',
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

