<script setup>
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <!-- TODO: Add icons to buttons for accessibility -->
  <v-app>
    <v-container fill-height>
      <v-row align="center" justify="center">
        <v-col>
          <a href="https://vuejs.org/" target="_blank">
            <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
          </a>
          <div class="text-h3 pa-2"> Placeholder Description </div>
          <v-row>
            <v-btn variant="tonal">
              Upload New Timeline
              (Plaso default dynamic .csv format)
            </v-btn>
          </v-row>
          <v-row align="center" justify="center">
            <v-btn variant="tonal">
              Load Existing DFTPL Timeline
            </v-btn>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
    
  </v-app>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
