<script setup>
import { ref } from 'vue'

// Event to notify parent to reload data
const emit = defineEmits(['CloseWindow'])
const props = defineProps(['EventType'])
const EventType = props.EventType
const RowId = ref()
const IsActive = ref(false)
const CommentValue = ref("")

// Character limit rules
const rules = [v => v ? v.length <= 200 : true || 'Max 200 characters']

function toggle(Id, Comment){
    RowId.value = Id
    IsActive.value = true
    CommentValue.value = Comment ? Comment : ""
}

// Call to load 
async function updateComments() {
    // Sends form data to API
    let form = new FormData()
    form.append('row_id', RowId.value)
    form.append('comment', CommentValue.value ? CommentValue.value : "") // Handle null values
    const requestOptions = {
        method: "POST",
        body: form
    };
    await fetch('/api/v1/timeline/' + EventType + '/u_comments', requestOptions)
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
                IsActive.value = false
                emit("CloseWindow") // Tell parent to change the  IsActive value to false
            }));
}

defineExpose({
    toggle
});

</script>

<template>
    <v-overlay v-model="IsActive">
        <v-form @submit.prevent="updateComments">
            <h3> Editing event id:{{ RowId }} </h3>
            <v-textarea v-model="CommentValue" label="Edit Comments" clear-icon="mdi-close-circle" clearable
                :rules="rules" counter no-resize>
            </v-textarea>
            <v-btn type="submit" class="mb-8" color="blue" size="large" variant="tonal" block>
                Update comments
            </v-btn>
            <v-btn @click="IsActive = false" class="mb-8" color="yellow" size="large" variant="tonal" block>
                Cancel
            </v-btn>
        </v-form>
    </v-overlay>

</template>