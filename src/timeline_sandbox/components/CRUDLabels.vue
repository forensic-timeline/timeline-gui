<script setup>
import { ref, onBeforeMount, onMounted } from 'vue'
// Event to notify parent to reload data
const emit = defineEmits(['CloseWindow'])
const props = defineProps(['eventType'])
// Vars for modifying label to event
const eventType = props.eventType // Low or high
const rowID = ref()
const isMainActive = ref(false)
const mainFormRef = ref()

const labelList = ref() // JSON dict of id:name, retrieved before mount
const labelsForEvent = ref([]) // List of id, given from event row

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

// Character limit rules
const rules = [v => v ? v.length <= 50 : true || 'Max 50 characters']


// Toggle for hiding main
function toggle(id, currentLabels) {
    rowID.value = id
    isMainActive.value = true
    labelsForEvent.value = [] // TEST: Input must be an array of label ids
    retrieveAllLabel()
}

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
}

async function updateEventLabel() { }

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

async function createNewLabel() { }

async function updateExistingLabel() { }

async function deleteExistingLabel() { }

onMounted(async () => {
    await retrieveAllLabel()
})

defineExpose({
    toggle
});
</script>

<template>
    <v-dialog v-model="isMainActive" width="auto">
        <v-card max-width="500" :title="'Editing labels for event id: ' + rowID">
            <v-form @submit.prevent="" ref="mainFormRef">
                <v-row>
                    <!-- TEST -->
                    <p>Selected label for edit:{{ selectedLabel }}</p>
                    <p>Selected label for checkbox: {{ labelsForEvent }}</p>
                    <v-col>
                        <v-slide-group v-model="selectedLabel" selected-class="bg-success" show-arrows
                            direction="vertical" max="1">
                            <v-slide-group-item v-for="(name, id) in labelList" :key="id" :value="id"
                                v-slot="{ isSelected, toggle, selectedClass }">
                                <v-card :disabled="isProcessing == 1" :class="['ma-4', selectedClass]"
                                    color="grey-lighten-1" rounded @click="toggle" width="200">
                                    <v-card-actions>
                                        <v-checkbox :disabled="isProcessing == 1" v-model="labelsForEvent" :label="name"
                                            :value="id" false-icon="mdi-checkbox-blank-outline" true-icon="mdi-checkbox-outline"></v-checkbox>
                                    </v-card-actions>

                                </v-card>
                            </v-slide-group-item>
                        </v-slide-group>
                    </v-col>

                    <v-col>
                        <!-- Buttons for label creation, updating, and deleting -->
                        <!-- Disabled if no label is selected (slide group) -->
                        <v-btn @click="onClickLabelOption(1)" :disabled="isProcessing == 1 && selectedLabel == 0">
                            New Label
                        </v-btn>
                        <v-btn @click="onClickLabelOption(2)" :disabled="isProcessing == 1 && selectedLabel == 0">
                            Edit Selected Label
                        </v-btn>
                        <v-btn @click="onClickLabelOption(3)" :disabled="isProcessing == 1 && selectedLabel == 0">
                            Delete Selected Label
                        </v-btn>

                    </v-col>
                </v-row>
            </v-form>
            <!-- Update selected event's label based on selected labels (checkbox) -->
            <v-btn :disabled="isProcessing == 1" @click="updateEventLabel" type="submit" class="mb-8" color="blue"
                size="large" variant="tonal" block>
                Update event label
            </v-btn>
            <v-btn :disabled="isProcessing == 1" @click="isMainActive = false" class="mb-8" color="yellow" size="large"
                variant="tonal" block>
                Cancel
            </v-btn>

            <!-- Overlay for label create or selected label's update and delete -->
            <v-dialog v-model="isLabelCRUDActive" width="auto">
                <!-- Dialogue content and behavior depends on which operation -->
                <!-- Done instead of modifying form content for readability -->
                <!-- CREATE -->
                <v-card v-if="operationType == 1" max-width="500" :title="'Editing label: ' + labelList[selectedLabel]">
                    <v-form @submit.prevent="createNewLabel" ref="labelCRUDFormRef">
                        <v-text-field :disabled="isProcessing == 1 && selectedLabel == 0" v-model="newLabel"
                            label="Label Name" clear-icon="mdi-close-circle" clearable :rules="rules" counter
                            no-resize></v-text-field>
                        <!-- Label create -->
                        <v-btn :disabled="isProcessing == 1 && selectedLabel == 0" type="submit" class="mb-8"
                            color="blue" size="large" variant="tonal" block>
                            Create new label
                        </v-btn>
                        <!-- Cancel button -->
                        <v-btn :disabled="isProcessing == 1" @click="isLabelCRUDActive = false" class="mb-8"
                            color="yellow" size="large" variant="tonal" block>
                            Cancel
                        </v-btn>
                    </v-form>
                </v-card>

                <!-- UPDATE -->
                <v-card v-else-if="operationType == 2" max-width="500"
                    :title="'Editing label: ' + labelList[selectedLabel]">

                    <v-form @submit.prevent="updateExistingLabel" ref="labelCRUDFormRef">
                        <v-text-field :disabled="isProcessing == 1 && selectedLabel == 0" v-model="newLabel"
                            label="Label Name" clear-icon="mdi-close-circle" clearable :rules="rules" counter
                            no-resize></v-text-field>
                        <!-- Label update -->
                        <p> Editing label: {{ }}</p>
                        <v-btn :disabled="isProcessing == 1 && selectedLabel == 0" type="submit" class="mb-8"
                            color="blue" size="large" variant="tonal" block>
                            Update label text
                        </v-btn>
                        <!-- Cancel button -->
                        <v-btn :disabled="isProcessing == 1" @click="isLabelCRUDActive = false" class="mb-8"
                            color="yellow" size="large" variant="tonal" block>
                            Cancel
                        </v-btn>
                    </v-form>
                </v-card>

                <!-- DELETE -->
                <v-card v-else-if="operationType == 3" max-width="500"
                    :title="'Editing label: ' + labelList[selectedLabel]">
                    <v-form @submit.prevent="deleteExistingLabel">
                        <v-btn :disabled="isProcessing == 1 && selectedLabel == 0" type="submit" class="mb-8"
                            color="blue" size="large" variant="tonal" block>
                            Delete label {{ }}
                            <v-dialog>
                                <!-- TODO: Dialog box for confirmation -->
                            </v-dialog>
                        </v-btn>
                        <!-- Cancel button -->
                        <v-btn :disabled="isProcessing == 1" @click="isLabelCRUDActive = false" class="mb-8"
                            color="yellow" size="large" variant="tonal" block>
                            Cancel
                        </v-btn>
                    </v-form>
                </v-card>

                <!-- ERROR HANDLING -->
                <v-card v-else>
                    Invalid label operation, please refresh page!
                </v-card>
            </v-dialog>

        </v-card>
    </v-dialog>

</template>