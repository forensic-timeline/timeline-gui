<script setup>
import AccountForm from '../components/AccountForm.vue';
import { ref } from 'vue'

// Stores API reply like error codes
const temp_fetch_api = ref(null);

async function on_submit(username, password, confirm){
    // Sends form data to API
    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "username": username, "password": password, "confirm": confirm })
    };
    await fetch(`/api/v1/sign-up`, requestOptions)
        .then(response => response.json())
        .then(data => temp_fetch_api.value = data);
    if (temp_fetch_api.value["message"] == "redirect") {
        window.location.replace("start")
    }
}

</script>

<template>
    <h1>Create a new account</h1>
    <!-- TODO: Implement hints for server-side validation errors -->
    <AccountForm @submit_event="on_submit" is_sign_up="true" username='' password='' confirm=''></AccountForm>
    <v-btn  to='sign-in' variant="tonal">
        Sign in to existing account
    </v-btn>
    {{ temp_fetch_api }}
</template>