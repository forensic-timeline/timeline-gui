<!-- TODO: Add icons to buttons for accessibility -->
<script setup>
</script>

<template>
  <v-container height="50vh" >
      <v-col align="center" justify="center" class="fill-height" >
        <a href="https://vuejs.org/" target="_blank">
          <img src="../assets/vue.svg" class="logo vue" alt="Vue logo" />
        </a>
        <div class="text-h3 pa-2"> Placeholder Description </div>
        <v-row justify="center">
          <v-btn to='new' variant="tonal" class="my-3">
            Upload New Timeline
            (Plaso default dynamic .csv format)
          </v-btn>
        </v-row>

        <v-row justify="center">
          <v-btn to='old' variant="tonal" class="my-3">
            Load Existing DFTPL Timeline
          </v-btn> 
        </v-row>

      </v-col>
  </v-container>
</template>
