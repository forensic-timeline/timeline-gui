<script setup>
import { ref, useTemplateRef, onMounted } from 'vue'
import { TabulatorFull as Tabulator } from 'tabulator-tables'; // NOTE: Around 420kb
import UpdateComments from '../components/UpdateComments.vue';
import "tabulator-tables/dist/css/tabulator.css"; //import Tabulator stylesheet

// HTML References
const data_table = useTemplateRef("data_table")
let table = null // Tabulator object ref
const comments_ref = useTemplateRef("comments_ref")

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
const page_values = ref([1])
// HACK: Total page is retrieved by getting max 'id' from db each page change
const total_page = ref(10) //Total page length
// Max visible page for pagination, const value
const total_visible = ref(5)
// Selected row's data by tabulator
const selected_row = ref(false)


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

                    // Update "go to page" values
                    page_values.value = [1] // Must at least have 1 page
                    for (let i = 2; i <= total_page.value; i++){
                        page_values.value.push(i)
                    }
                    

                    // TODO: Handle server error

                }
            }));

    // TODO: Handle server error
    if (table instanceof Tabulator) {
        
        await table.setData(page_data.value)
        is_loading.value = false
    }
    
}

function toggleComments(){
    if (table instanceof Tabulator){
        comments_ref.value.toggle(selected_row.value['id'], selected_row.value['user_comments'] )
    }
}

// onBeforeMount: Call retrieveData to get first page and max amount of page for pagination
onMounted(async () => {
    // Setup tabulator
    table = new Tabulator(data_table.value, {
        columns: tabulator_columns,
        data: page_data.value,
        minHeight: "10vh",
        maxHeight: "50vh",
        selectableRows:1,
    })
    // To select a row
    table.on("rowSelected", function(row){
        selected_row.value = row.getData()
    });
    
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
    <!-- Filter and sort submition -->
    <!-- FIXME: Validate terms amount or display error from server and reenable -->
    <v-form @submit.prevent="on_submit">
        <h3> Search time, event type, source file path, evidence entry, or plugin. </h3>
        <v-text-field v-model="include_terms" label="Include terms (separated by space)" :disabled="is_loading == 1"></v-text-field>
        <v-text-field v-model="exclude_terms" label="Exclude terms (separated by space)" :disabled="is_loading == 1"></v-text-field>
        <v-select v-model="is_ascending" label="Sort direction" :items="is_ascending_values" :disabled="is_loading == 1"></v-select>
        <v-select v-model="selected_column" label="Sort by column" :items="low_level_columns" :disabled="is_loading == 1"></v-select>
        <v-btn type="submit" class="mb-8" color="blue" size="large" variant="tonal" block :disabled="is_loading == 1">
            Search
        </v-btn>
    </v-form>
    <!-- NOTE: Button icons must use mdi icons manually, empty by default -->
     <!-- Page navigation -->
    <v-select v-model="current_page" label="Go to page:" :items="page_values" :disabled="is_loading == 1" @update:modelValue="onPageChange"></v-select>
    <!-- Elements for comment editing -->
    <v-btn @click="toggleComments" :disabled="selected_row == 0"> Edit Comment </v-btn>
    <UpdateComments @CloseWindow="on_submit" EventType="low_level" ref="comments_ref"></UpdateComments>

    <v-pagination v-model="current_page" :length="total_page" :total-visible="total_visible" show-first-last-page=true
        variant="outlined" next-icon="mdi-page-next" prev-icon="mdi-page-previous"
        @update:modelValue="on_submit" :disabled="is_loading == 1"></v-pagination>
    <!-- TODO: Loading bar for data -->
    <div>
        <v-progress-circular v-if="is_loading" color="primary" indeterminate></v-progress-circular>
        <div ref="data_table">

        </div>
    </div>

</template>