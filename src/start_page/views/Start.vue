<!-- TODO: Add icons to buttons for accessibility -->
<script setup>
import { ref, watch } from 'vue'
    const overlay = ref(false)
    watch ( 
      overlay, (val) => {
        val && setTimeout(() => {
          overlay.value = false
        }, 3000)
      }
    )
</script>

<template>
  <v-container fill-height>
    <v-row align="center" justify="center">
      <v-col>
        <a href="https://vuejs.org/" target="_blank">
          <img src="../assets/vue.svg" class="logo vue" alt="Vue logo" />
        </a>
        <div class="text-h3 pa-2"> Placeholder Description </div>
        <v-row>
          <v-btn to='new' variant="tonal">
            Upload New Timeline
            (Plaso default dynamic .csv format)
          </v-btn>
        </v-row>
        <v-row align="center" justify="center">
          <v-btn to='old' variant="tonal">
            Load Existing DFTPL Timeline
          </v-btn>
        </v-row>
        <div class="text-center">
          <v-btn color="error" @click="overlay = !overlay">
            Show Overlay
          </v-btn>

          <v-overlay v-model="overlay" disabled=true persistent=true>
            <v-btn color="error" @click.once="overlay = !overlay">
              Close Overlay
            </v-btn>
          </v-overlay>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>
