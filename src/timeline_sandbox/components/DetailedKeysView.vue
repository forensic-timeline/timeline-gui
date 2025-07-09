<script setup>
// Component retrieves the keys of an event depending on given id. Displays empty message if not found.
import { ref, onActivated, defineExpose, useTemplateRef } from 'vue'
import { TabulatorFull as Tabulator } from 'tabulator-tables'; // NOTE: Around 420kb
// HTML References
const dataTableRef = ref()
let table = null // Tabulator object ref
// Variables
const rowID = ref() //Assigned eventID prop's value when mounted
const props = defineProps(['id'])
// Received key data
const rowKeyData = ref()


const tabulator_columns = [
    { title: "Key Name", field: "key_name", sorter: "string", },
    { title: "Key Value", field: "key_value", sorter: "string", formatter: "textarea" },
]

function loadRowID(id){
    rowID.value = id
}

function loadTable(){
    // Setup tabulator
    table = new Tabulator(dataTableRef.value, {
        columns: tabulator_columns,
        data: rowKeyData.value,
        minHeight: "10vh",
        maxHeight: "40vh",

    })

}

async function retrieveData() {
    loadTable() // Load table after dialog renders

    const requestOptions = {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    };
    await fetch(
        '/api/v1/timeline/high_level/get_keys?' +
        new URLSearchParams({
            rowID: (Number.isInteger(rowID.value) && rowID.value > 0) ? rowID.value : 0,
        }).toString(),
        requestOptions
    )
        .then(response => response.json()
            .then(data => ({
                data: data,
                status: response.status
            }))
            .then(res => {
                if (res.status == 200) {
                    rowKeyData.value = res.data
                    // TODO: Handle server error

                }
            }));

    // Since values passed from vue's child events is a proxy,
    // must use Reflect functions to access the dict
    if (table instanceof Tabulator) {
        let temp_arr = []
        for (const key of Reflect.ownKeys(rowKeyData.value)) {
            temp_arr.push({
                "key_name": key,
                "key_value": Reflect.get(rowKeyData.value, key)
            })
        }
        rowKeyData.value = temp_arr
        await table.setData(rowKeyData.value)
    }
}




defineExpose({
    loadRowID
});
</script>

<template>
    <v-btn @click="">
        View Keys
        <v-dialog persistent activator="parent" @afterEnter="retrieveData">
            <template v-slot:default="{ isActive }">
                <v-card :title="'Keys for event id: ' + rowID" class="pa-4" max-height="75vh">
                    <v-row>
                        <!-- Table to displays list of keys and values -->
                        <div ref="dataTableRef"></div>
                        <!-- TODO: Show message if empty -->
                    </v-row>
                    <v-row>
                        <v-btn @click="isActive.value = false;">
                            Close
                        </v-btn>
                    </v-row>
                </v-card>
            </template>
        </v-dialog>
    </v-btn>
</template>