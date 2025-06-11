<script setup>
// TODO: Show user minutes since last download
import { ref, useTemplateRef } from 'vue'
import ConfirmDownloadIntegrity from './ConfirmDownloadIntegrity.vue';

const integrityRef= useTemplateRef("integrityRef")

function getHash(){
    integrityRef.value.loadHash()
}

async function downloadDB(){
    window.location.assign("/api/v1/download_db")
    // const requestOptions = {
    //     method: "GET",
    // };

    // await fetch(`/api/v1/download_db`, requestOptions)
    //     .then(response => response.json()
    //         .then(data => ({
    //             data: data,
    //             status: response.status
    //         }))
    //         .then(res => {
    //             if (res.status == 200) {

    //             }
    //             else {
    //                 // TODO: Handle server error
    //             }
    //         }));
}
</script>

<template>
    <v-btn>
        <div>Save Database File to Device</div>
        <v-dialog persistent activator="parent" @afterEnter="getHash">
            <template v-slot:default="{ isActive }" >
                <v-card title="Save Database File to Device" class="pa-4">
                    <v-row>
                        <ConfirmDownloadIntegrity ref="integrityRef"></ConfirmDownloadIntegrity>
                    </v-row>
                    <v-row class="mt-3" align="center" justify="center">
                        <v-btn @click="downloadDB" class="mx-2">Save</v-btn>
                        <v-btn @click="isActive.value = false;" class="mx-2">Close</v-btn>
                    </v-row>
                </v-card>
            </template>
        </v-dialog>
    </v-btn>
</template>