<script setup>
import { ref } from 'vue'

// Event to notify parent to reload data
const emit = defineEmits(['CloseWindow'])
const props = defineProps(['eventType'])

// Ref to vuetify form
const myForm = ref();

const eventType = props.eventType
const rowID = ref()
const isActive = ref(false)
const commentValue = ref("")
const isProcessing = ref(false) // Prevent user activity while processing

// Character limit rules
const rules = [v => v ? v.length <= 200 : true || 'Max 200 characters']

function toggle(id, comment) {
    rowID.value = id
    isActive.value = true
    commentValue.value = comment ? comment : ""
}

// Call to load 
async function updateComments() {
    myForm.value?.validate().then(async ({ valid: isValid }) => {
        if (isValid) {
            isProcessing.value = true
            // Sends form data to API
            let form = new FormData()
            form.append('row_id', rowID.value)
            form.append('comment', commentValue.value ? commentValue.value : "") // Handle null values
            const requestOptions = {
                method: "POST",
                body: form
            };
            await fetch('/api/v1/timeline/' + eventType + '/u_comments', requestOptions)
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
                        isActive.value = false
                        isProcessing.value = false
                        emit("CloseWindow") // Tell parent to change the  isActive value to false
                    }));
        }
    })
}

defineExpose({
    toggle
});

</script>

<template>
    <v-dialog v-model="isActive" width="auto">
        <v-card max-width="500" :title="'Editing comment for event id: ' + rowID">
            <v-form @submit.prevent="updateComments" ref="myForm">
                <v-textarea :disabled="isProcessing == 1" v-model="commentValue" label="Edit Comments"
                    clear-icon="mdi-close-circle" clearable :rules="rules" counter no-resize>
                </v-textarea>
                <v-btn :disabled="isProcessing == 1" type="submit" class="mb-8" color="blue" size="large"
                    variant="tonal" block>
                    Update comments
                </v-btn>
                <v-btn :disabled="isProcessing == 1" @click="isActive = false" class="mb-8" color="yellow" size="large"
                    variant="tonal" block>
                    Cancel
                </v-btn>
            </v-form>
        </v-card>
    </v-dialog>

</template>