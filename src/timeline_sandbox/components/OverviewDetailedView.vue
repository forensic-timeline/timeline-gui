<script setup>
// Component retrieves the keys of an event depending on given id. Displays empty message if not found.
import { ref, onActivated, defineExpose, useTemplateRef } from 'vue'
import { TabulatorFull as Tabulator } from 'tabulator-tables'; // NOTE: Around 420kb
// HTML References
const keyDataTableRef = ref()
const rowDataTableRef = ref()
let keyTable = null // Tabulator object ref
let rowTable = null
// Variables
const rowID = ref() //Assigned eventID prop's value when mounted
let isHighLevel = false
// Received key data
const rowKeyData = ref()
const rowData = ref()
// Flag
const isActive = ref(false)

const key_tabulator_columns = [
    { title: "Key Name", field: "key_name", sorter: "string", },
    { title: "Key Value", field: "key_value", sorter: "string", formatter: "textarea" },
]

const row_tabulator_columns = [
    { title: "Value Name", field: "key_name", sorter: "string", },
    { title: "Value", field: "key_value", sorter: "string", formatter: "textarea" },
]

/**
 * 
 * @param id : Row id to get data from
 * @param isHighLevel : true for high level events
 */
function loadRowID(id, type) {
    rowID.value = id
    isHighLevel = type
    isActive.value = true
}

function loadTable() {
    // Setup tabulator
    if (isHighLevel) {
        keyTable = new Tabulator(keyDataTableRef.value, {
            columns: key_tabulator_columns,
            data: rowKeyData.value,
            minHeight: "10vh",
            maxHeight: "40vh",

        })
    }

    rowTable = new Tabulator(
        rowDataTableRef.value,
        {
            columns: row_tabulator_columns,
            data: rowData.value,
            minHeight: "10vh",
            maxHeight: "40vh",
        }
    )

}

async function retrieveData() {
    loadTable() // Load table after dialog renders
    if(isHighLevel){
        const requestOptions1 = {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    };
    await fetch(
        '/api/v1/timeline/high_level/get_keys?' +
        new URLSearchParams({
            rowID: (Number.isInteger(rowID.value) && rowID.value > 0) ? rowID.value : 1,
        }).toString(),
        requestOptions1
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
    if (keyTable instanceof Tabulator) {
        let temp_arr = []
        for (const key of Reflect.ownKeys(rowKeyData.value)) {
            temp_arr.push({
                "key_name": key,
                "key_value": Reflect.get(rowKeyData.value, key)
            })
        }
        rowKeyData.value = temp_arr
        await keyTable.setData(rowKeyData.value)
    }
    }

    let eventString = isHighLevel ? "high_level" : "low_level"
    const requestOptions2 = {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    };
    await fetch(
        '/api/v1/timeline/'+ eventString + '/overview_detail?' +
        new URLSearchParams({
            rowID: (Number.isInteger(rowID.value) && rowID.value > 0) ? rowID.value : 0,
        }).toString(),
        requestOptions2
    )
        .then(response => response.json()
            .then(data => ({
                data: data,
                status: response.status
            }))
            .then(res => {
                if (res.status == 200) {
                    rowData.value = res.data
                    // TODO: Handle server error

                }
            }));

    // Since values passed from vue's child events is a proxy,
    // must use Reflect functions to access the dict
    if (rowTable instanceof Tabulator) {
        let temp_arr = []
        for (const key of Reflect.ownKeys(rowData.value)) {
            temp_arr.push({
                "key_name": key,
                "key_value": Reflect.get(rowData.value, key)
            })
        }
        rowData.value = temp_arr
        await rowTable.setData(rowData.value)
    }

}




defineExpose({
    loadRowID
});
</script>

<template>
    <v-dialog persistent v-model="isActive" @afterEnter="retrieveData">
        <v-card :title="'Values for event id: ' + rowID" class="pa-4" max-height="75vh">
            <v-row>
                <!-- Table to displays list of keys and values -->
                <div ref="rowDataTableRef"></div>
                <!-- TODO: Show message if empty -->
            </v-row>
            <v-row>
                <!-- Table to displays list of keys and values -->
                <div ref="keyDataTableRef"></div>
                <!-- TODO: Show message if empty -->
            </v-row>
            <v-row>
                <v-btn @click="isActive = false;">
                    Close
                </v-btn>
            </v-row>
        </v-card>
    </v-dialog>
</template>