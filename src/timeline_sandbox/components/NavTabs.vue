<script setup>
import { ref } from 'vue'
const props = defineProps(['eventType'])
const curTab=props.eventType
</script>
<template>
      <v-card>
    <v-tabs
      v-model="curTab"
      bg-color="primary"
    >
      <v-tab value="low_level" :to="{ name: 'low_level', params: {goToPage: 1} }">Low Level Timeline</v-tab>
      <v-tab value="high_level" :to="{ name: 'high_level' }">High Level Timeline</v-tab>
    </v-tabs>
  </v-card>
</template>