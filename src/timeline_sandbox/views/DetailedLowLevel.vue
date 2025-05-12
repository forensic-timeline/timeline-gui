<script setup>
import { ref, useTemplateRef, onMounted } from 'vue'
import { TabulatorFull as Tabulator } from 'tabulator-tables'; // NOTE: Around 420kb
import "tabulator-tables/dist/css/tabulator.css"; //import Tabulator stylesheet

// HTML References
const data_table = useTemplateRef("data_table")
let table = null // Tabulator object ref

const is_ascending_values = [{
    title: 'Ascending',
    value: true
},
{
    title: 'Descending',
    value: false
}]
// TODO: Automate column retrieval
// Not done because some columns contains null, might as well set this manually to avoid that
// MAKE SURE THE VALIDATION MATCHES THESE VALUES
const low_level_columns = [
    {
        title: 'ID',
        value: 'id'
    },
    {
        title: 'Time (Min)',
        value: 'date_time_min'
    },
    {
        title: 'Event Type',
        value: 'event_type'
    },
    {
        title: 'Source File Path',
        value: 'path'
    },
    {
        title: 'Evidence Entry',
        value: 'evidence'
    },
    {
        title: 'Plugin',
        value: 'plugin'
    },
]
// MAKE SURE DB SCHEMA MATCHES THE COLUMNS
const tabulator_columns = [
    { title: "ID", field: "id", sorter: "number", },
    { title: "Time (Min)", field: "date_time_min", sorter: "string", },
    { title: "Time (Max)", field: "date_time_max", sorter: "string", },
    { title: "Event Type", field: "event_type", sorter: "string", },
    { title: "Source File Path", field: "path", sorter: "string", },
    { title: "Evidence Entry", field: "evidence", sorter: "string", },
    { title: "Plugin", field: "plugin", sorter: "string", },
    { title: "Provenence Raw Entry", field: "provenence_raw_entry", sorter: "string", },
    { title: "Keys", field: "keys", sorter: "string", },
    { title: "User Comments", field: "user_comments", sorter: "string", },
]

// Values to send to API
const include_terms = ref("")
const exclude_terms = ref("")
const is_ascending = ref(true)
const selected_column = ref('id')

// Boolean for data loading state
const is_loading = ref(false)

// Received page data
const page_data = ref()

// Page information, changed by vuetify pagination component
const current_page = ref(1)
// HACK: Total page is retrieved by getting max 'id' from db each page change
const total_page = ref(10) //Total page length
// Max visible page for pagination, const value
const total_visible = ref(5)
// retrieveData: Retrieve paginated data asynchronously
// Uses GET, example like sciencedirect.com
async function retrieveData(curPage) {
    is_loading.value = true
    const requestOptions = {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    };
    await fetch(
        '/api/v1/timeline/low_level?' +
        new URLSearchParams({
            include: include_terms.value,
            exclude: exclude_terms.value,
            asc: is_ascending.value,
            byCol: selected_column.value,
            curPage: (curPage > 0) ? curPage : 1,
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
                    page_data.value = res.data["page_rows"]
                    total_page.value = res.data["max_page"]
                }
            }));

    if (table != null) {
        
        await table.setData(page_data.value)
        is_loading.value = false
    }
    // TODO: Handle error

}

// onBeforeMount: Call retrieveData to get first page and max amount of page for pagination
onMounted(async () => {
    // Setup tabulator
    table = new Tabulator(data_table.value, {
        columns: tabulator_columns,
        data: page_data.value,
        minHeight: "10vh",
        maxHeight: "50vh"
    })
    await retrieveData(1)

})

// TEST: Testing pagination events
// When pagination state changes, call API to load said page
async function onPageChange(event) {

    await retrieveData(current_page.value)

}

// Wait for button's submit event to resolve
async function on_submit() {

    await retrieveData(current_page.value)

}
</script>

<template>
    <h2> Current page: {{ current_page }}</h2>
    <v-icon icon="mdi-abacus" /> <!-- TEST -->
    <v-form @submit.prevent="on_submit">
        <h3> Search time, event type, source file path, evidence entry, or plugin. </h3>
        <v-text-field v-model="include_terms" label="Include terms (separated by space)" :disabled="is_loading == 1"></v-text-field>
        <v-text-field v-model="exclude_terms_terms" label="Exclude terms (separated by space)" :disabled="is_loading == 1"></v-text-field>
        <v-select v-model="is_ascending" label="Sort direction" :items="is_ascending_values" :disabled="is_loading == 1"></v-select>
        <v-select v-model="selected_column" label="Sort by column" :items="low_level_columns" :disabled="is_loading == 1"></v-select>
        <v-btn type="submit" class="mb-8" color="blue" size="large" variant="tonal" block :disabled="is_loading == 1">
            Search
        </v-btn>
    </v-form>
    <!-- NOTE: Button icons must use mdi icons manually, empty by default -->
    <v-pagination v-model="current_page" :length="total_page" :total-visible="total_visible" show-first-last-page=true
        variant="outlined" next-icon="mdi-page-next" prev-icon="mdi-page-previous"
        @update:modelValue="onPageChange" :disabled="is_loading == 1"></v-pagination>
    <!-- TODO: Loading bar for data -->
    <div>
        <v-progress-circular v-if="is_loading" color="primary" indeterminate></v-progress-circular>
        <div ref="data_table">

        </div>
    </div>

</template>