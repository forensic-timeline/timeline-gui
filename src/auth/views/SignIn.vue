<script setup>
import AccountForm from '../components/AccountForm.vue';
import { ref } from 'vue'
const temp_fetch_api = ref(null);
function on_submit(username, password){

    // Client-side validation
    

    // Sends form data to API
    console.log(JSON.stringify({ "username": username, "password": password }))
    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "username": username, "password": password })
    };
    fetch(`/api/v1/sign-in`, requestOptions)
        .then(response => response.json())
        .then(data => temp_fetch_api.value = data);
}
</script>

<template>
    <h1>Sign In</h1>
    <AccountForm @submit_event="on_submit" username='' password=''></AccountForm>
    <v-btn to='sign-up' variant="tonal">
        Create new account
    </v-btn>
</template>