<!-- TODO: Add icons to buttons for accessibility -->
<script setup>
// Select list of analyzers to use
import { ref } from 'vue'

const selected = ref([])

</script>

<template>
  <v-container fluid fill-height>
    <v-col align="center" justify="center">
      <v-btn to='start' variant="tonal">
            Back
      </v-btn>
      <!-- Analyzer Select
          
      TODO: Analyzer search, select/deselect all, grouping, and integrate to actual submitable form.
      -->
      <v-row>
        <v-container fluid>
          <v-virtual-scroll :height="300"
            :items="['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']">
            <template v-slot:default="{ item }">
              <v-checkbox v-model="selected" :label=item :value=item></v-checkbox>
            </template>
          </v-virtual-scroll>
          <p>{{ selected }}</p>
        </v-container>
      </v-row>
      <v-row>
        <v-col>
          <v-file-input label="Upload a plaso timeline (default .csv output)">

          </v-file-input>
        </v-col>
        <v-col>
          <v-btn>
            Upload
          </v-btn>
        </v-col>
      </v-row>
    </v-col>
  </v-container>
</template>
