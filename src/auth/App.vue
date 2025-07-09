<script setup>
  import { RouterView } from 'vue-router'
  import SystemBar from './components/SystemBar.vue'

</script>

<template>
  <v-layout>
    <SystemBar></SystemBar>
  </v-layout>
  <main>
    
    <RouterView />
  </main>
</template>

<style scoped>

</style>
