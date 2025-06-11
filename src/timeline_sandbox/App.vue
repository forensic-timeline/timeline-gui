<script setup>
import { RouterView } from 'vue-router'
import { ref } from 'vue'
import SystemBar from './components/SystemBar.vue'
import "tabulator-tables/dist/css/tabulator.css"; //import Tabulator stylesheet

</script>

<template>
  <v-layout>
    <SystemBar isLoggedIn=1></SystemBar>
  </v-layout>

  <main>
    
    <RouterView />
  </main>
</template>

<style scoped></style>
