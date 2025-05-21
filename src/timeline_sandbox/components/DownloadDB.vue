<script setup>
// TODO: Show user minutes since last download
import { ref, useTemplateRef } from 'vue'
import ConfirmIntegrity from './ConfirmIntegrity.vue';

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
                        <ConfirmIntegrity ref="integrityRef"></ConfirmIntegrity>
                    </v-row>
                    <v-row>
                        <v-btn @click="downloadDB">Save</v-btn>
                        <v-btn @click="isActive.value = false;">Close</v-btn>
                    </v-row>
                </v-card>
            </template>
        </v-dialog>
    </v-btn>
</template>