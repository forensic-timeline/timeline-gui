<script setup>
import { ref } from 'vue'

// Event to notify parent to clean up upload view
const emit = defineEmits(['CleanUpFinished'])

const file_hash = ref("")

// Gets called by parent to get the hash of recently uploaded file
async function loadHash() {
    // Sends form data to API

    const requestOptions = {
        method: "GET",
    };

    await fetch(`/api/v1/confirm-hash/download`, requestOptions)
        .then(response => response.text()
            .then(data => ({
                data: data,
                status: response.status
            }))
            .then(res => {
                if (res.status == 200) {
                    file_hash.value = res.data

                }
                else {
                    // TODO: Handle server error
                    file_hash.value = res.status
                }
            }));
}

defineExpose({
    loadHash
});
</script>

<template>
    <v-card class="mx-auto">
        <template v-slot:title>
            <span class="font-weight-black">Please confirm SHA256 file hash below with the downloaded file</span>
        </template>

        <v-card-text class="bg-surface-light pt-4">
            {{ file_hash }}
        </v-card-text>
    </v-card>

</template>