<script setup>
import { ref } from 'vue'

// Event to notify parent to clean up upload view
const emit = defineEmits(['CleanUpFinished'])

const server_response = ref(null);
const file_hash = ref("")
const is_loading = ref(false)
const dftpl_status = ref("")

// Sends request for server to clean up uploaded file and data
async function cleanUp() {
    // Sends form data to API

    const requestOptions = {
        method: "GET",
    };

    await fetch(`/api/v1/upload/undo-upload`, requestOptions)
        .then(response => response.status)
        .then(data => server_response.value = data)
    // TEST
    if (server_response.value == 200) {
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
        .then(data => file_hash.value = data)
}

// Sends request for server to call dftpl
// FIXME: Show message if no high level timeline
// TODO: Add loading screen with progress messages
async function callDftpl() {
    // Sends form data to API
    is_loading.value = true
    const requestOptions = {
        method: "GET",
    };

    await fetch(`/api/v1/run-dftpl`, requestOptions)
        .then(response => response)
        .then(data => server_response.value = data)
    if (server_response.value.status == 200) {
        // TODO: Replace with better alert
        is_loading.value = false
        alert("DFTPL Finished Processing") //TEST
        window.location.href = "timeline"
    }
    else {
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

    <!-- Shows loading message for when dftpl is called -->
    <v-row v-if="is_loading"
        align-content="center"
        class="fill-height"
        justify="center"
      >
        <v-col
          class="text-subtitle-1 text-center"
          cols="12"
        >
        <p>Loading timeline, please wait...</p>
        </v-col>
        <v-col cols="6">
          <v-progress-linear
            color="deep-purple-accent-4"
            height="6"
            indeterminate
            rounded
          ></v-progress-linear>
        </v-col>
      </v-row>
    <!-- TODO: Redirect to main page -->
    <!-- TEST -->
    <v-row class="mt-3" align="center" justify="center"> 
        <v-btn :disabled="is_loading == 1" @click="callDftpl" variant="tonal" color="green" class="mx-2">
            Process timeline
        </v-btn>
        <v-btn :disabled="is_loading == 1" @click="cleanUp" variant="flat" color="red-lighten-3" class="mx-2">
            Delete file and reupload
        </v-btn></v-row>


</template>