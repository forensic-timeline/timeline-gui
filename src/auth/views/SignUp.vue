<script setup>
import AccountForm from '../components/AccountForm.vue';
import { ref } from 'vue'
const temp_fetch_api = ref(null);
function on_submit(username, password, confirm){
    console.log(JSON.stringify({ "username": username, "password": password, "confirm": confirm }))
    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "username": username, "password": password, "confirm": confirm })
    };
    fetch(`/api/v1/sign-up`, requestOptions)
        .then(response => response.json())
        .then(data => temp_fetch_api.value = data);
}

</script>

<template>
    <h1>Create a new account</h1>
    <AccountForm @submit_event="on_submit" is_sign_up="true" username='' password='' confirm=''></AccountForm>
    <v-btn  to='sign-in' variant="tonal">
        Sign in to existing account
    </v-btn>
    <p>{{temp_fetch_api}}</p>
</template>