import { createApp } from 'vue'
import {createRouter, createWebHashHistory} from 'vue-router'

// SFCs
import App from './App.vue'
import DetailedHighLevel from './views/DetailedHighLevel.vue'
import DetailedLowLevel from './views/DetailedLowLevel.vue'
// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { mdi } from 'vuetify/iconsets/mdi'
import { aliases, fa } from 'vuetify/iconsets/fa'
import "@mdi/font/css/materialdesignicons.css"; // Ensure you are using css-loader
import "@fortawesome/fontawesome-free/css/all.css"; // Ensure your project is capable of handling css files
import "d3-milestones/build/d3-milestones.css" //Test d3-milestones css
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import OverviewLowLevel from './views/OverviewLowLevel.vue'
import OverviewHighLevel from './views/OverviewHighLevel.vue'


const router = createRouter(
  // TEST: Finalize routes later
  {
    history: createWebHashHistory(),
    routes: [
      // {
      //   path: '/observable',
      //   name: 'observable',
      //   component: Observable
      // },
      {
        path: '/',
        redirect: '/low-level/1'
      },
      {
        path: '/low-level',
        redirect: '/low-level/1'
      },
      {
        path: '/low-level/:goToPage',
        name: 'low_level',
        component: DetailedLowLevel,
        props: true
      }
      ,
      {
        path: '/high-level',
        name: 'high_level',
        component: DetailedHighLevel
      }
      ,
      {
        path: '/overview-low',
        name: 'overview_low',
        component: OverviewLowLevel
      }
      ,
      {
        path: '/overview-high',
        name: 'overview_high',
        component: OverviewHighLevel
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

