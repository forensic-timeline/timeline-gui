<!-- TODO: Add icons to buttons for accessibility -->
<script setup>
</script>

<template>
  <v-container fill-height>
    <v-row align="center" justify="center">
      <v-btn to='start' variant="tonal">
            Back
      </v-btn>
      <v-col>
        <v-row>
        <v-col>
          <v-file-input label="Upload an existing DFTPL timeline (.sqlite database)">

          </v-file-input>
        </v-col>
        <v-col>
          <v-btn>
            Upload
          </v-btn>
        </v-col>
      </v-row>
      </v-col>
    </v-row>
  </v-container>  
</template>
