<script setup>
/**
 * TODO:
 * V. Define JSON Structure and load from API
 * V. Test multiple timelines (category)
 * V. Event listener, on click load a different JSON data and rebuild graph
 * 4. Differenciate on click function for first level (time) and second level (event)
 * V. Make function get JSON structure by accessing db
 */
/**
 * TODO: 
 * Find out if vuetify's scrollers can be used alongside 
 * separating each timeline into individual milestone objects
 * and watchers to have multiple timelines and only
 * retrieve data for interacted timeline so less data downloaded
 */
import { ref, useTemplateRef, onMounted, watchEffect } from 'vue'
import OverviewDetailedView from '../components/OverviewDetailedView.vue'
import SelectDateTime from '../components/SelectDateTime.vue';
import NavTabs from '../components/NavTabs.vue';
import milestones from 'd3-milestones'

const d3MilestoneRef = useTemplateRef("d3_milestone") // d3-milestone DOM Ref
const detailedView = useTemplateRef("detailedView")
let milestonesObj = false // d3-milestone object reference
const start_min_date = useTemplateRef("start_min_date")
const end_min_date = useTemplateRef("end_min_date")

const timelineJSON = ref([]) // timeline data
const isLoading = ref(false) // flag for waiting for API response

// Variables for error message
const isServerError = ref(false)
const serverErrorMessage = ref("")

// Variables for timeline interaction
let openNodes = new Map()
const TIME_RANGE = ["month", "day", "hour", "minute"]
const aggregatePeriod = ref("month")
const loadInvalidDate = ref(false)
const mergeTimelines = ref(false)
// Variables for filter by min date range components
const useTimeRange = ref(false)

// Helper function
function mapToJson(map) {
    const obj = {};
    for (const [key, value] of map) {
        obj[key] = value instanceof Map ? mapToJson(value) : value;
    }
    return JSON.stringify(obj);
}

// TEST: aggregateBy
// FIXME: Warn user if amount of event in node is >1000
/**
 * Retrieves all timeline data.
 * @param openNodes Dicts of dicts {analyser: {entry_id: [[start_id, amount]]}} to expand. Empty array if none is selected.
 * @param aggregateBy Time interval for period ("month","day", "hour", or "minute"), unused if reqType = "event"
 * @param loadInvalid Flag, enable to load events before epoch time and current time which doesn't have valid timestamps
 * @param doMergeTimelines Flag, enable to merge all categories into one timeline
 * @param minDateRangeArr Custom range where only events within the range is loaded. Takes precedence over loadInvalid.
 */
async function retrieveData(openNodes, aggregateBy, loadInvalid, doMergeTimelines) {
    // Set flag
    let isSuccess = false
    isLoading.value = true

    // Create form contents
    let form = new FormData()
    form.append("openNodes", mapToJson(openNodes))
    form.append("aggregateBy", aggregateBy)
    form.append("loadInvalid", JSON.stringify(loadInvalid))
    form.append("doMergeTimelines", JSON.stringify(doMergeTimelines))
    form.append("minDateRangeArr", (useTimeRange.value) ? JSON.stringify([start_min_date.value.datetimeISOString, end_min_date.value.datetimeISOString]) : "\"\"")
    const requestOptions = {
        method: "POST", // Using POST since assuming a lot of period nodes and analysers
        // Using GET search params could exceed max URL length
        body: form
    };
    await fetch(
        '/api/v1/timeline/high_level/overview',
        requestOptions)
        .then(response => response.text() //Assumes error
            .then(data => ({
                data: response.status == 200 ? JSON.parse(data) : data, //If not error, parse data json
                status: response.status
            }))
            .then(res => {
                if (res.status == 200) {
                    timelineJSON.value = res.data
                    isSuccess = true
                }
                else {
                    isServerError.value = true
                    serverErrorMessage.value = res.data
                }
            }));


    // TODO: Redraw graph


    isLoading.value = false //Always stop loading after error or data loaded
    return isSuccess

}

// Need to recreate object when changing aggregate else 
// the timelone won't update the nodes
// also done by official examples
async function reloadTimeline() {
    if (await retrieveData(openNodes, aggregatePeriod.value, loadInvalidDate.value, mergeTimelines.value)) {
        milestonesObj = milestones(d3MilestoneRef.value)
            .optimize(true)
            .orientation("horizontal")
            .aggregateBy(aggregatePeriod.value)
            .parseTime('%Y-%m-%dT%H:%M:%S.%f%Z')
            .mapping({
                category: 'category',
                entries: 'nodes',
                id: undefined, // Unused html id
                timestamp: 'timestamp',
                text: 'text',
            })
        if (milestonesObj) {
            milestonesObj.onEventClick((d) => onClick(d))
            // Trick milestones to using on hover classes that can be edited
            milestonesObj.onEventMouseOver((d) => {
            })
            milestonesObj.onEventMouseLeave((d) => {
            })
        }

        milestonesObj.render(timelineJSON.value)
    }
}

// When a timeline entry is clicked
function onClick(d) {
    // Accessing the dict of the node
    // HACK: Convert proxy to {} object
    let nodeType = JSON.parse(JSON.stringify(d.target.__data__.attributes))
    if (nodeType["type"] == "period") {
        // Checkbox logic
        // If analyser category key doesn't exists, create new
        if (!openNodes.has(nodeType["category"])) {
            openNodes.set(nodeType["category"], new Map([[nodeType["entry_id"], [nodeType["start_id"], nodeType["evt_count"]]]]))
        }
        else {
            // If node clicked already added, remove
            if (openNodes.get(nodeType["category"]).has(nodeType["entry_id"])) {
                openNodes.get(nodeType["category"]).delete(nodeType["entry_id"])
            }
            else {
                openNodes.get(nodeType["category"]).set(nodeType["entry_id"], [nodeType["start_id"], nodeType["evt_count"]])
            }
        }
        reloadTimeline()
    }
    else if (nodeType["type"] == "event") {
        detailedView.value.loadRowID(parseInt(nodeType["event_id"]), true)
    }

}

// Cleans selected node when changing period since 
// entry_id will be refreshed
function changePeriod() {
    openNodes = new Map()
    reloadTimeline()
}

onMounted(() => {
    reloadTimeline()
})



</script>

<template>
    <NavTabs eventType="overview_high"></NavTabs>
    <OverviewDetailedView :disabled="isLoading == 1" ref="detailedView"></OverviewDetailedView>
    <!-- Loading indicator -->
    <v-overlay v-model="isLoading" class="align-center justify-center"> <v-progress-circular v-if="isLoading"
            color="primary" indeterminate size="100"></v-progress-circular>
    </v-overlay>
    <!-- Inside card to give size of timeline -->
    <v-col class="align-center justify-center">
        <v-row>
            <h3>NOTE: Time shown is based on current timezone</h3>
        </v-row>
        <v-row>
            <v-col> <v-select :disabled="isLoading == 1" label="Select time range from grouping events"
                    v-model="aggregatePeriod" :items="TIME_RANGE"></v-select></v-col>
            <v-col>
                <v-btn @click="changePeriod" :disabled="isLoading == 1"> Reload timeline </v-btn>
                <v-switch v-model="loadInvalidDate" :disabled="isLoading == 1"
                    :label="`Load all events including possibly invalid timestamps?: ${(loadInvalidDate) ? `Yes` : `No`}`"></v-switch>
                <v-switch v-model="mergeTimelines" :disabled="isLoading == 1"
                    :label="`Merge all category into one timeline?: ${(mergeTimelines) ? `Yes` : `No`}`"></v-switch>
            </v-col>

        </v-row>
        <!-- If user doesn't load all events, can select partial events -->
        <v-row align="center" justify="center">
            <v-card>
                <v-col>
                    <v-col><v-switch v-model="useTimeRange" :disabled="isLoading == 1 || loadInvalidDate == 1"
                            :label="`Set custom time range of events?: ${(useTimeRange) ? `Yes` : `No`}`"></v-switch></v-col>
                </v-col>
                <v-col>
                    <v-input :rules="date_rules">
                        <v-card subtitle="Start date (Not included)">
                            <SelectDateTime :disabled="isLoading == 1 || !useTimeRange  || loadInvalidDate == 1" ref="start_min_date">
                            </SelectDateTime>
                        </v-card>
                        <v-card subtitle="End date (Not included)">
                            <SelectDateTime :disabled="isLoading == 1 || !useTimeRange  || loadInvalidDate == 1" ref="end_min_date">
                            </SelectDateTime>

                        </v-card>
                    </v-input>

                </v-col>
            </v-card>
        </v-row>
        <v-row class="justify-center d-flex overflow-auto">
            <v-card class="d-flex overflow-auto" color="grey-lighten-3" height="90vh" width="90vw">
                <div class="d3Milestones">
                    <div class="timeline" ref="d3_milestone"></div>
                </div>
            </v-card>
        </v-row>
    </v-col>

</template>

<!-- 
CSS Comments:
.milestones__group__label__text__event--hover = Class used when onEventMouseOver is setup
.timeline = CSS used by official examples, help to keep the graph from being
    too close to or even exceeding the edge of the parent elemnt
.milestones__group__label-horizontal = Keep it from blocking the clickable text since it could be in front
.wrapper = Keep the clickable text working since it's the child of .milestones__group__label-horizontal
-->
<style>
.milestones__group__label__text__event--hover {
    background: cyan;
}

.d3Milestones {
    font-family: sans-serif;
}


.timeline {
    width: 200vw;
    height: 100vh;
    margin: -20px -20px -20px -20px;
    padding: 20px 20px 20px 20px;
}

.milestones__group__label-horizontal {
    pointer-events: none;
}

.wrapper {
    pointer-events: auto;
}
</style>