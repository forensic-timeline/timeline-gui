<script setup>
import AccountForm from '../components/AccountForm.vue';
import { ref } from 'vue'

// Stores API reply like error codes
const temp_fetch_api = ref(null);

// Vars for server error
const is_server_error = ref(false)
const server_error_msg = ref("")

async function on_submit(username, password) {
    // Sends form data to API
    // FIXME: Change to formdata
    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "username": username, "password": password })
    };

    await fetch(`/api/v1/sign-in`, requestOptions)
    .then(response => response.text() //Assumes error
                    .then(data => ({
                        data: data, //If not error, parse data json
                        status: response.status
                    }))
                    .then(res => {
                        if (res.status == 200) {
                            window.location.href = "start"
                        }
                        else {
                            is_server_error.value = true
                            server_error_msg.value = res.data
                        }
                    }));
}
</script>

<template>
    <v-row fluid align="center" justify="center">
        <v-sheet height="80vh" width="80vw">
            <v-col align="center" justify="center">
                <v-alert v-model="is_server_error" border="start" close-label="Close Alert" color="error" title="Error"
                variant="tonal" closable>{{ server_error_msg }}</v-alert>
                <h1>Sign In</h1>
                <!-- TODO: Implement card for server-side confirmation and validation errors -->
                <AccountForm @submit_event="on_submit" is_sign_up="false" username='' password=''></AccountForm>
                <v-btn to='sign-up' variant="tonal">
                    Create new account
                </v-btn>
            </v-col>

        </v-sheet>
    </v-row>


</template>