<!--  FIXME: Width and heights using pixels not responsive values like vh -->
<script setup>
import { ref, onBeforeMount, onMounted } from 'vue'
// Event to notify parent to reload data
const emit = defineEmits(['CloseWindow', 'LabelsLoaded'])
const props = defineProps(['eventType'])
// Vars for modifying label to event
const eventType = props.eventType // Low or high
const rowID = ref()
const isMainActive = ref(false)
const mainFormRef = ref()

const labelList = ref() // JSON dict of id:name, retrieved before mount
const userSelectedLabels = ref([]) // New list of initial event label ids, modified by user
let initialLabels = [] // Set of initial event label ids, given from event row
// Vars for modifying label list
const isLabelCRUDActive = ref(false)
const labelCRUDFormRef = ref()
/*
operationType: Int between 1, 2, or 3
1 = Create
2 = Update
3 = Delete
*/
const operationType = ref(0)
const selectedLabel = ref(false) // An id of a label
const newLabel = ref("") // New or existing label value
// General vars
const isProcessing = ref(false) // Prevent user activity while processing
// Server error var
const is_server_error = ref(false)
const server_error_msg = ref("")


// Character limit rules
const name_rules = [v => v ? v.length <= 50 && v.length > 0 : true || 'Max 50 characters']

// TEST Rule if labels aren't changed
const label_rule = [() => {
    const setToDelete = userSelectedLabels.value != null ? initialLabels.filter(x => !userSelectedLabels.value.includes(x)) : false
    const setToAdd = initialLabels != null ? userSelectedLabels.value.filter(x => !initialLabels.includes(x)) : false
    if (setToDelete.length > 0 || setToAdd.length > 0) {
        return true
    }

    else {
        return "This event's label hasn't been changed yet!"
    }
}]

// Toggle for hiding main
function toggle(id, currentLabels) {
    rowID.value = id
    isMainActive.value = true
    // Turns label list into dicts with boolean values for selected labels
    userSelectedLabels.value = currentLabels != null ? currentLabels : []
    initialLabels = currentLabels != null ? currentLabels : []
    retrieveAllLabel()
}

// 

async function retrieveAllLabel() {
    isProcessing.value = true
    const requestOptions = {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    };
    await fetch(
        '/api/v1/timeline/get_labels',
        requestOptions
    )
        .then(response => response.json()
            .then(data => ({
                data: data,
                status: response.status
            }))
            .then(res => {
                if (res.status == 200) {
                    labelList.value = res.data['labels']
                }
                // TODO: Handle server error
            }));
    isProcessing.value = false
    emit("LabelsLoaded", labelList.value)
}

// Creates a set of the old label ids and new label ids
// Calculates the difference for list of id to add and to delete from db
async function updateEventLabel() {

    mainFormRef.value?.validate().then(async ({ valid: isValid }) => {
        if (isValid) {
            const setToDelete = userSelectedLabels.value != null ? initialLabels.filter(x => !userSelectedLabels.value.includes(x)) : []
            const setToAdd = initialLabels != null ? userSelectedLabels.value.filter(x => !initialLabels.includes(x)) : []

            isProcessing.value = true
            // Sends form data to API
            let form = new FormData()
            form.append('rowID', rowID.value)
            // So the server receives the array as an array, not a single string
            form.append('setToDelete', JSON.stringify(setToDelete))
            form.append('setToAdd', JSON.stringify(setToAdd)) // Handle null values
            const requestOptions = {
                method: "POST",
                body: form
            };
            await fetch('/api/v1/timeline/' + eventType + '/u_labels', requestOptions)
                .then(response => response.text()
                    .then(data => ({
                        data: data,
                        status: response.status
                    }))
                    .then(res => {
                        if (res.status == 200) {
                        }
                        else {
                            // TODO: Handle server error
                        }
                        isMainActive.value = false
                        isProcessing.value = false
                        emit("CloseWindow") // Tell parent to change the  isActive value to false
                    }));
        }
    })
}

function onClickLabelOption(operation) {
    /*
    operationType: Int between 1, 2, or 3
    1 = Create
    2 = Update
    3 = Delete
    */
    if (operation == 1) {
        isLabelCRUDActive.value = true
        operationType.value = 1
    }
    else if (operation == 2) {
        isLabelCRUDActive.value = true
        operationType.value = 2
        newLabel.value = labelList.value[selectedLabel.value]
    }
    else if (operation == 3) {
        isLabelCRUDActive.value = true
        operationType.value = 3
    }
    else {
        operationType.value = 0
        return -1
    }
}

async function createNewLabel() {
    labelCRUDFormRef.value?.validate().then(async ({ valid: isValid }) => {
        if (isValid) {
            isProcessing.value = true
            // Sends form data to API
            let form = new FormData()
            form.append('newLabel', newLabel.value)
            const requestOptions = {
                method: "POST",
                body: form
            };
            await fetch('/api/v1/timeline/add_label', requestOptions)
                .then(response => response.text()
                    .then(data => ({
                        data: data,
                        status: response.status
                    }))
                    .then(res => {
                        if (res.status == 200) {
                            isMainActive.value = false
                            isLabelCRUDActive.value = false
                            emit("CloseWindow") // Tell parent to change the  isActive value to false
                        }
                        else {
                            is_server_error.value = true
                            
                            server_error_msg.value = res.data
                            // TODO: Handle server error
                        }
                        isProcessing.value = false
                    }));
        }
    })
}

async function updateExistingLabel() {
    labelCRUDFormRef.value?.validate().then(async ({ valid: isValid }) => {
        if (isValid) {
            isProcessing.value = true
            // Sends form data to API
            let form = new FormData()
            form.append('selectedLabel', parseInt(selectedLabel.value))
            form.append('newLabel', newLabel.value)
            const requestOptions = {
                method: "POST",
                body: form
            };
            await fetch('/api/v1/timeline/update_label', requestOptions)
                .then(response => response.text()
                    .then(data => ({
                        data: data,
                        status: response.status
                    }))
                    .then(res => {
                        if (res.status == 200) {
                            isMainActive.value = false
                            isLabelCRUDActive.value = false
                            emit("CloseWindow") // Tell parent to change the  isActive value to false
                        }
                        else {
                            is_server_error.value = true
                            
                            server_error_msg.value = res.data
                            // TODO: Handle server error
                        }
                        isProcessing.value = false
                    }));
        }
    })
}

async function deleteExistingLabel() {

    isProcessing.value = true
    // Sends form data to API
    let form = new FormData()
    form.append('selectedLabel', parseInt(selectedLabel.value))
    const requestOptions = {
        method: "POST",
        body: form
    };
    await fetch('/api/v1/timeline/delete_label', requestOptions)
        .then(response => response.text()
            .then(data => ({
                data: data,
                status: response.status
            }))
            .then(res => {
                if (res.status == 200) {
                }
                else {
                    
                    // TODO: Handle server error
                }
                isMainActive.value = false
                isLabelCRUDActive.value = false
                isProcessing.value = false
                emit("CloseWindow") // Tell parent to change the  isActive value to false
            }));

}

onMounted(async () => {
    await retrieveAllLabel()
})

// Expose list of labels and function to activate component
defineExpose({
    labelList,
    toggle
});
</script>

<template>
    <v-dialog persistent v-model="isMainActive" width="50vw">
        <v-card :title="'Editing labels for event id: ' + rowID">
            <v-col align="center" justify="center"> <v-form @submit.prevent="" ref="mainFormRef">
                    <v-col>
                        <!-- To display no labels changed error -->
                        <v-input :rules="label_rule"></v-input>
                        <v-sheet max-height="50vh" class="border border-b-lg rounded-lg">
                            <v-slide-group v-model="selectedLabel" selected-class="bg-success" show-arrows="always"
                                direction="vertical" max="1" prev-icon="fa-solid fa-arrow-up"
                                next-icon="fa-solid fa-arrow-down">
                                <!-- NOTE: Javascript dict keys must be obj or string, so cast id to number before searching on db -->
                                <v-slide-group-item v-for="name, id in labelList" :key="id" :value="id"
                                    v-slot="{ isSelected, toggle, selectedClass }">
                                    <v-card :disabled="isProcessing == 1" :class="['my-4', selectedClass]"
                                        color="grey-lighten-1" rounded @click="toggle" width="200" height="50">
                                        <v-card-actions>
                                            <v-checkbox :disabled="isProcessing == 1" v-model="userSelectedLabels"
                                                :label="name" :value="id"></v-checkbox>
                                        </v-card-actions>

                                    </v-card>
                                </v-slide-group-item>
                            </v-slide-group>
                        </v-sheet>
                    </v-col>

                    <v-col>
                        <v-row align="center" justify="center">
                            <!-- Buttons for label creation, updating, and deleting -->
                            <!-- Disabled if no label is selected (slide group) -->
                            <v-btn @click="onClickLabelOption(1)" :disabled="isProcessing == 1">
                                New Label
                            </v-btn>
                            <v-btn @click="onClickLabelOption(2)" :disabled="isProcessing == 1 || !selectedLabel">
                                Edit Selected Label
                            </v-btn>
                            <v-btn @click="onClickLabelOption(3)" :disabled="isProcessing == 1 || !selectedLabel">
                                Delete Selected Label
                            </v-btn>
                        </v-row>


                    </v-col>
                </v-form>
                <!-- Update selected event's label based on selected labels (checkbox) -->
                <v-btn :disabled="isProcessing == 1" @click="updateEventLabel" type="submit" class="my-4"
                    color="primary" size="large" variant="tonal" block>
                    Update event label
                </v-btn>
                <v-btn :disabled="isProcessing == 1" @click="isMainActive = false" class="my-4" csize="large"
                    variant="tonal" block>
                    Cancel
                </v-btn></v-col>


            <!-- Overlay for label create or selected label's update and delete -->
            <!-- NOTE: Javascript dict keys must be obj or string, so cast id to number before searching on db -->
            <v-dialog persistent v-model="isLabelCRUDActive" width="auto">
                <!-- Dialogue content and behavior depends on which operation -->
                <!-- Done instead of modifying form content for readability -->
                <!-- CREATE -->
                <v-card v-if="operationType == 1" max-width="500" title="Create new label (max 50 characters)">
                    <v-alert v-model="is_server_error" border="start" close-label="Close Alert" color="error"
                        title="Error" variant="tonal" closable>{{ server_error_msg }}</v-alert>
                    <v-form @submit.prevent="createNewLabel" ref="labelCRUDFormRef">
                        <v-text-field :disabled="isProcessing == 1" v-model="newLabel" label="Label Name"
                            clear-icon="fa-solid fa-circle-xmark" clearable :rules="name_rules" counter
                            no-resize></v-text-field>
                        <!-- Label create -->
                        <v-btn :disabled="isProcessing == 1" type="submit" class="my-4" color="primary" size="large"
                            variant="tonal" block>
                            Create new label
                        </v-btn>
                        <!-- Cancel button -->
                        <v-btn :disabled="isProcessing == 1" @click="isLabelCRUDActive = false" class="my-4"
                            size="large" variant="tonal" block>
                            Cancel
                        </v-btn>
                    </v-form>
                </v-card>

                <!-- UPDATE -->
                <v-card v-else-if="operationType == 2" max-width="500"
                    :title="'Editing label: ' + labelList[selectedLabel]">
                    <v-alert v-model="is_server_error" border="start" close-label="Close Alert" color="error"
                        title="Error" variant="tonal" closable>{{ server_error_msg }}</v-alert>
                    <v-form @submit.prevent="updateExistingLabel" ref="labelCRUDFormRef">
                        <v-text-field :disabled="isProcessing == 1 || !selectedLabel" v-model="newLabel"
                            label="Label Name" clear-icon="fa-solid fa-circle-xmark" clearable :rules="name_rules"
                            counter no-resize></v-text-field>
                        <!-- Label update -->
                        <v-btn :disabled="isProcessing == 1 || !selectedLabel" type="submit" class="my-4"
                            color="primary" size="large" variant="tonal" block>
                            Update label text
                        </v-btn>
                        <!-- Cancel button -->
                        <v-btn :disabled="isProcessing == 1" @click="isLabelCRUDActive = false" class="my-4"
                            size="large" variant="tonal" block>
                            Cancel
                        </v-btn>
                    </v-form>
                </v-card>

                <!-- DELETE -->
                <v-card v-else-if="operationType == 3" max-width="500" title="Delete label">

                    <v-btn :disabled="isProcessing == 1 || !selectedLabel" class="my-4" color="warning" size="large"
                        variant="tonal" block>
                        Delete label {{ labelList[selectedLabel] }}
                        <v-dialog persistent activator="parent">
                            <template v-slot:default="{ isActive }">
                                <v-card max-width="400"
                                    text="Are you sure to delete the label? This process is irreversable!"
                                    :title="'Confirm Deletion for ' + labelList[selectedLabel]">
                                    <template v-slot:actions>
                                        <v-btn @click="deleteExistingLabel" class="ml-auto" color="warning"
                                            text="Delete"></v-btn>
                                        <v-btn class="ml-auto" text="Cancel" @click="isActive.value = false"></v-btn>
                                    </template>
                                </v-card>
                            </template>
                            <!-- TODO: Dialog box for confirmation -->
                        </v-dialog>
                    </v-btn>
                    <!-- Cancel button -->
                    <v-btn :disabled="isProcessing == 1" @click="isLabelCRUDActive = false" class="my-4" size="large"
                        variant="tonal" block>
                        Cancel
                    </v-btn>
                </v-card>

                <!-- ERROR HANDLING -->
                <v-card v-else>
                    Invalid label operation, please refresh page!
                </v-card>
            </v-dialog>

        </v-card>
    </v-dialog>

</template>