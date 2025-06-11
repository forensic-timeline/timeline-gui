<script setup>
 import SystemBar from './components/SystemBar.vue'
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
