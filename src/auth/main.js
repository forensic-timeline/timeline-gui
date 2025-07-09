import { createApp } from 'vue'
import {createRouter, createWebHashHistory, createMemoryHistory } from 'vue-router'

// SFCs
import App from './App.vue'
import SignIn from './views/SignIn.vue'
import SignUp from './views/SignUp.vue'
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
        path: '/sign-in',
        name: 'sign-in',
        component: SignIn
      },
      {
        path: '/',
        redirect: '/sign-in'
      },
      {
        path: '/sign-up',
        name: 'sign-up',
        component: SignUp
      },
      {
        // To catch 404 errors using history mode.
        path: '/:pathMatch(.*)',
        redirect: '/sign-in' // FIXME: Show proper 404 page
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

