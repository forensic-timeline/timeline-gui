<script setup>
import { ref } from 'vue'

// Event to notify parent to clean up upload view
const emit = defineEmits(['CleanUpFinished'])

const server_response = ref(null);
const file_hash = ref("")

// Sends request for server to clean up uploaded file and data
async function cleanUp() {
    // Sends form data to API

    const requestOptions = {
        method: "GET",
    };

    await fetch(`/api/v1/upload/undo-upload`, requestOptions)
        .then(response => response.status)
        .then(data => server_response.value  = data)
    // TEST
        if (server_response.value == 200){
            emit("CleanUpFinished")
        }
    
}

// Gets called by parent to get the hash of recently uploaded file
async function loadHash() {
    // Sends form data to API

    const requestOptions = {
        method: "GET",
    };

    await fetch(`/api/v1/confirm-hash/upload`, requestOptions)
        .then(response => response.text())
        .then(data => file_hash.value  = data)
}

// TEST
// Sends request for server to call dftpl
// FIXME: Show message if no high level timeline
// TODO: Add loading screen with progress messages
async function callDftpl() {
    // Sends form data to API

    const requestOptions = {
        method: "GET",
    };

    await fetch(`/api/v1/run-dftpl`, requestOptions)
        .then(response => response)
        .then(data => server_response.value  = data)
    // TEST
        if (server_response.value.status == 200){
            alert("DB SUCCESS")
        }
        else{
            alert(server_response.value.text())
        }
    
}
defineExpose({
    loadHash
});
</script>

<template>
    <v-card class="mx-auto">
        <template v-slot:title>
            <span class="font-weight-black">Please confirm SHA256 file hash below with your local file</span>
        </template>

        <v-card-text class="bg-surface-light pt-4">
            {{ file_hash }}
        </v-card-text>
    </v-card>
    <!-- TODO: Redirect to main page -->
     <!-- TEST -->
    <v-btn @click="callDftpl" variant="tonal" color="green">
        Process timeline
    </v-btn>
    <v-btn @click="cleanUp" variant="flat" color="red-lighten-3">
        Delete file and reupload
    </v-btn>

</template>