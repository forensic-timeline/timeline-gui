<script setup>
import { RouterView } from 'vue-router'
import { ref, onMounted } from 'vue'
// TEST: Current user display
var cur_user = ref("Placeholder1")
var message = ref("Placeholder2")

async function get_user() {
  const requestOptions = {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  };
  await fetch(`/api/v1/get-user`, requestOptions)
    .then(response => response.json())
    .then(data => cur_user.value = data);
}
// TEST: Logout button
async function log_out() {
  // Sends form data to API
  const requestOptions = {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  };
  await fetch(`/api/v1/sign-out`, requestOptions)
    .then(response => response.json())
    .then(data => message.value = data["message"]);
}

onMounted(async () => {
  //TODO: Add loading screen/icon for data loading
  await get_user()
})
</script>

<template>

  <main>
    <RouterView />
    <h1>{{ cur_user }}</h1>
    <v-btn @click="log_out" class="mb-8" color="blue" size="large" variant="tonal" block>
      Sign Out
    </v-btn>
    <h1>{{ message }}</h1>
  </main>
</template>

<style scoped></style>
