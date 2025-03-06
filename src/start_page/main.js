import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import {createRouter} from 'vue-router'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const router = createRouter(
  {
    routes: [
      {
        path: '/',
        component: App
      }
    ]
  }
)

const vuetify = createVuetify({
    components,
    directives,
    theme: {
      defaultTheme: 'dark',
    },
  })  

const app = createApp(App)
app.use(vuetify)
app.mount('#app')

