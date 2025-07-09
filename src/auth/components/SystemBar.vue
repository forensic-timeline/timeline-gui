<script setup>
import { ref, onMounted } from 'vue'
import { useTheme } from 'vuetify'
// Toggle if used in pages for not logged in user
const props = defineProps(['isLoggedIn'])

const theme = useTheme()
const themeIcon = ref()
const currentUser = ref("Not logged in")
const isLoggedIn = ref(props.isLoggedIn)
function toggleTheme() {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
  themeIcon.value = theme.global.current.value.dark ? 'fa-solid fa-moon' : 'fa-solid fa-sun'
}

async function logOut() {
  if (isLoggedIn.value == 1) {
    // Sends form data to API
    const requestOptions = {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    };
    await fetch(`/api/v1/sign-out`, requestOptions)
      .then(response => response.text())
      
      window.location.reload()
  }
  
}
async function getCurUser() {
  if (isLoggedIn.value == 1) {
    const requestOptions = {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    };
    await fetch(`/api/v1/get-user`, requestOptions)
      .then(response => response.text())
      .then(data => currentUser.value = data);
  }
}
onMounted(async () => {
  //TODO: Add loading screen/icon for data loading
  if (isLoggedIn.value == 1) {
    await getCurUser()
  }
  themeIcon.value = theme.global.current.value.dark ? 'fa-solid fa-moon' : 'fa-solid fa-sun'
})
</script>

<template>
  <v-toolbar density="compact" :title="currentUser">
    <v-btn :prepend-icon="themeIcon" @click="toggleTheme">Toggle Theme</v-btn>
    <v-btn v-if="isLoggedIn == 1" prepend-icon="fa-solid fa-right-from-bracket" @click="logOut">Logout</v-btn>
  </v-toolbar>
</template>