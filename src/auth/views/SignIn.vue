<script setup>
import AccountForm from '../components/AccountForm.vue';
import { ref } from 'vue'

// Stores API reply like error codes
const temp_fetch_api = ref(null);
async function on_submit(username, password) {
    // Sends form data to API
    // FIXME: Change to formdata
    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "username": username, "password": password })
    };

    await fetch(`/api/v1/sign-in`, requestOptions)
        .then(response => response.json())
        .then(data => temp_fetch_api.value = data);
    if (temp_fetch_api.value["message"] == "redirect") {
        window.location.replace("start")
    }
}
</script>

<template>
    <h1>Sign In</h1>
    <!-- TODO: Implement hints for server-side validation errors -->
    <AccountForm @submit_event="on_submit" is_sign_up="false" username='' password=''></AccountForm>
    <v-btn to='sign-up' variant="tonal">
        Create new account
    </v-btn>
    {{ temp_fetch_api }}
</template>