<script setup>
import { ref, useTemplateRef, onMounted, defineProps, watch } from 'vue'
import { TabulatorFull as Tabulator } from 'tabulator-tables'; // NOTE: Around 420kb
import { useRouter } from 'vue-router'
import UpdateComments from '../components/UpdateComments.vue';
import CRUDLabels from '../components/CRUDLabels.vue';
import SelectDateTime from '../components/SelectDateTime.vue';
import DownloadDB from '../components/DownloadDB.vue';
import NavTabs from '../components/NavTabs.vue';

// Props
const props = defineProps({
    goToPage: {
        default: 1,
        type: Number
    }
})

// HTML References
const search_form = useTemplateRef("searchForm")
const data_table = useTemplateRef("data_table")
let table = null // Tabulator object ref
const comments_ref = useTemplateRef("comments_ref")
const labels_ref = useTemplateRef("labels_ref")
const start_min_date = useTemplateRef("start_min_date")
const end_min_date = useTemplateRef("end_min_date")

const is_ascending_values = [{
    title: 'Ascending',
    value: true
},
{
    title: 'Descending',
    value: false
}]
// TODO: Automate column retrieval
// Columns that are used for db sorting
// MAKE SURE THE VALIDATION MATCHES THESE VALUES
// NOTE: Currently unused columns (date_time_max,)
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
// TODO: Display label names too
// FIXME: Limit/wrap certain columns for ease of comparing multiple rows
const tabulator_columns = [
    { title: "ID", field: "id", sorter: "number", },
    { title: "Time (Min)", field: "date_time_min", sorter: "string", },
    { title: "Time (Max)", field: "date_time_max", sorter: "string", },
    { title: "Event Type", field: "event_type", sorter: "string", },
    { title: "Source File Path", field: "path", sorter: "string", formatter: "textarea", width: 200  },
    { title: "Evidence Entry", field: "evidence", sorter: "string", formatter: "textarea", width: 200 },
    { title: "Plugin", field: "plugin", sorter: "string", formatter: "textarea", width: 200  },
    { title: "Provenence Raw Entry", field: "provenance_raw_entry", sorter: "string", formatter: "textarea", width: 200  },
    { title: "Keys", field: "keys", sorter: "string", },
    { title: "User Comments", field: "user_comments", sorter: "string", formatter: "textarea" , width: 200 },
    {
        title: "Labels", field: "cname", formatter: "array", formatterParams: {
            delimiter: "|", //join values using the "|" delimiter
        }, headerSort: false, width: 200 
    }
]
const date_rules = [
    // Make sure min date is before max date
    () => {
        if (start_min_date.value.datetimeISOString > end_min_date.value.datetimeISOString) return 'Start date must be set before end date!'
        else {
            return true
        }
    }
]
const router = useRouter() // Ref to vue router


// Values to send to API
const include_terms = ref("")
const exclude_terms = ref("")
const is_ascending = ref(true)
const selected_column = ref('id')
// Variables for filter by label components
const label_data = ref([])// HACK: Creates copy from CRUDLabels, retrieve here then pass to CRUDLabels so there's only one copy of labels?
const use_label = ref(false)
const selected_label = ref([]) // List of selected labels
// Variables for filter by min date range components
const use_time_range = ref(false)


// Boolean for data loading state
const is_loading = ref(false)

// Received page data
const page_data = ref()
// Received server error
const is_server_error = ref(false)
const server_error_msg = ref()

// Page information, changed by vuetify pagination component
const current_page = ref(1)
const page_values = ref([1]) //Pagination values
const total_page = ref(10) //Total page length, calculated by db
// Max visible page for pagination, const value
const total_visible = ref(5)
// Selected row's data by tabulator
const selected_row = ref(false)
// HACK: Event to call when page number changes
const page_num_changed = new Event("page_num_changed")

// retrieveData: Retrieve paginated data asynchronously
// Uses GET, example like sciencedirect.com
async function retrieveData(curPage) {
    search_form.value?.validate().then(async ({ valid: isValid }) => {
        if (isValid) {
            is_loading.value = true
            selected_row.value = false // Clear selected column
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
                    curPage: (curPage > 0) ? curPage : 1, // Server already checks for out of bounds current page
                    filterLabel: (use_label.value && selected_label.value.length) ? JSON.stringify(selected_label.value) : "\"\"",
                    // Just send the ISO String since regex can validate if it's a valid string
                    // No need to validate if it's valid range (e.g 32nd day) since it's string comparison
                    minDateRangeArr: (use_time_range.value) ? JSON.stringify([start_min_date.value.datetimeISOString, end_min_date.value.datetimeISOString]) : "\"\""
                }).toString(),
                requestOptions
            )
                .then(response => response.text() //Assumes error
                    .then(data => ({
                        data: response.status == 200 ? JSON.parse(data) : data, //If not error, parse data json
                        status: response.status
                    }))
                    .then(res => {
                        if (res.status == 200) {
                            page_data.value = res.data["page_rows"]
                            total_page.value = res.data["max_page"]

                            // Update "go to page" values
                            page_values.value = [1] // Must at least have 1 page
                            for (let i = 2; i <= total_page.value; i++) {
                                page_values.value.push(i)
                            }

                        }
                        else {
                            is_server_error.value = true
                            server_error_msg.value = res.data
                        }
                    }));

            if (table instanceof Tabulator) {

                await table.setData(page_data.value)
                is_loading.value = false
            }
        }
    })
}
function toggleComments() {
    if (table instanceof Tabulator) {
        comments_ref.value.toggle(selected_row.value['id'], selected_row.value['user_comments'])
    }
}

function toggleLabels() {
    if (table instanceof Tabulator) {
        // cid: List of label id's
        labels_ref.value.toggle(selected_row.value['id'], selected_row.value['cid'])
    }
}

// Since values passed from vue's child events is a proxy,
// must use Reflect functions to access the dict
function loadLabels(label_dict) {
    label_data.value = []
    for (const key of Reflect.ownKeys(label_dict)) {
        label_data.value.push({
            "title": Reflect.get(label_dict, key),
            "value": parseInt(key)
        })
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
        selectableRows: 1,
    })
    // To select a row
    table.on("rowSelected", function (row) {
        selected_row.value = row.getData()
    });
    // When no row is selected, so the buttons are disabled
    table.on("rowDeselected", function (row) {
        //row - row component for the deselected row
        if (selected_row.value == row.getData()) {
            selected_row.value = false
        }
    });

    // If user wants to go to a specific page, send here
    current_page.value = (typeof +props.goToPage === "number" && !isNaN(+props.goToPage)) ? +props.goToPage : current_page.value
    await retrieveData(current_page.value)

    // Reload when page number is changed
    addEventListener("page_num_changed", async () => {
        // If user wants to go to a specific page, send here
        await retrieveData(current_page.value)
    })

})

// If props changed, assigns new page value and call event for retrieveData
// since if retrieveData is watched, any changes to search form values
// will trigger it


watch ( props, async () => {
    current_page.value = (typeof +props.goToPage === "number" && !isNaN(+props.goToPage)) ? +props.goToPage : current_page.value
    dispatchEvent(page_num_changed)
})

// TEST: Testing pagination events
// When pagination state changes, call API to load said page
function onPageChange(event) {
    router.push({
        name: "low_level",
        params: {
            goToPage: current_page.value
        }
    })
}

// Wait for button's submit event to resolve
async function on_submit() {
    await retrieveData(current_page.value)
}


</script>

<template>
    <NavTabs eventType="low_level"></NavTabs>
    <v-alert v-model="is_server_error" border="start" close-label="Close Alert" color="error" title="Error"
        variant="tonal" closable>{{ server_error_msg }}</v-alert>
    <v-row fluid class="mt-3" align="center" justify="center">
        <v-sheet width="80vw" class="position-relative">
            <v-overlay v-model="is_loading" class="align-center justify-center" contained> <v-progress-circular
                    v-if="is_loading" color="primary" indeterminate size="100"></v-progress-circular>
            </v-overlay>
            <v-col align="center" justify="center">
                <!-- Filter and sort submition -->
                <!-- FIXME: Validate terms amount or display error from server and reenable -->

                <v-card variant="outlined" class="pa-1">
                    <v-form @submit.prevent="on_submit" ref="searchForm">
                        <h3> Search time, event type, source file path, evidence entry, plugin, raw entry, or keys. </h3>
                        <h2> NOTE: Use whole words for searching </h2>
                        <v-text-field v-model="include_terms" label="Include terms (whole words separated by space)"
                            :disabled="is_loading == 1"></v-text-field>
                        <v-text-field v-model="exclude_terms" label="Exclude terms (whole words separated by space)"
                            :disabled="is_loading == 1"></v-text-field>
                        <v-select v-model="is_ascending" label="Sort direction" :items="is_ascending_values"
                            :disabled="is_loading == 1"></v-select>
                        <v-select v-model="selected_column" label="Sort by column" :items="low_level_columns"
                            :disabled="is_loading == 1"></v-select>
                        <v-row>
                            <v-col><v-switch v-model="use_label" :disabled="is_loading == 1"
                                    :label="`Filter by a label?: ${(use_label) ? `Yes` : `No`}`"></v-switch></v-col>

                            <v-col><v-select v-model="selected_label" :disabled="is_loading == 1 || !use_label"
                                    label="Select label" :items="label_data" multiple chips></v-select></v-col>
                        </v-row>
                        <v-row align="center" justify="center">
                            <v-card>
                                <v-col>
                                    <v-col><v-switch v-model="use_time_range" :disabled="is_loading == 1"
                                            :label="`Filter by minimum date range?: ${(use_time_range) ? `Yes` : `No`}`"></v-switch></v-col>
                                </v-col>
                                <v-col>
                                    <v-input :rules="date_rules">
                                        <v-card subtitle="Start date">
                                            <SelectDateTime :disabled="is_loading == 1 || !use_time_range"
                                                ref="start_min_date">
                                            </SelectDateTime>
                                        </v-card>
                                        <v-card subtitle="End date">
                                            <SelectDateTime :disabled="is_loading == 1 || !use_time_range"
                                                ref="end_min_date">
                                            </SelectDateTime>

                                        </v-card>
                                    </v-input>

                                </v-col>
                            </v-card>
                        </v-row>
                        <v-row align="center" justify="center">
                            <v-btn type="submit" class="ma-8 " color="blue" size="large" variant="tonal" block
                                :disabled="is_loading == 1">
                                Search
                            </v-btn>

                        </v-row>

                    </v-form>
                </v-card>
                <DownloadDB class="ma-2"></DownloadDB>
                <!-- NOTE: Button icons must use mdi icons manually, empty by default -->
                <!-- Page navigation -->
                <v-select class="ma-2" v-model="current_page" label="Go to page:" :items="page_values"
                    :disabled="is_loading == 1" @update:modelValue="onPageChange"></v-select>

                <v-row class="ma-2" align="center" justify="center">
                    <!-- Elements for comment editing -->
                    <v-btn @click="toggleComments" :disabled="selected_row == 0 || is_loading == 1"> Edit Comment
                    </v-btn>
                    <UpdateComments @CloseWindow="on_submit" eventType="low_level" ref="comments_ref"></UpdateComments>
                    <!-- Elements for label editing -->
                    <v-spacer></v-spacer>
                    <v-btn @click="toggleLabels" :disabled="selected_row == 0 || is_loading == 1"> Edit Labels </v-btn>
                    <CRUDLabels @CloseWindow="on_submit" @LabelsLoaded="loadLabels" eventType="low_level"
                        ref="labels_ref">
                    </CRUDLabels>

                </v-row>

                <v-pagination v-model="current_page" :length="total_page" :total-visible="total_visible"
                    show-first-last-page=true variant="outlined" @update:modelValue="onPageChange"
                    :disabled="is_loading == 1"></v-pagination>
                <div>
                    <div class="mx-3" ref="data_table">

                    </div>
                </div>

            </v-col>
        </v-sheet>
    </v-row>

</template>