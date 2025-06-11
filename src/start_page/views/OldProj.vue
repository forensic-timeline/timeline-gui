<!-- TODO: Add icons to buttons for accessibility -->
<script setup>
import { ref, onMounted, watchEffect } from 'vue'
// Dropzone for chunked upload
// Validation for file size and type is handled by Dropzone
import { Dropzone } from "@deltablot/dropzone"
// Import component for getting hash of uploaded file
import ConfirmUploadIntegrity from '../components/ConfirmUploadIntegrity.vue'

// Dropzone
const dropzoneRef = ref() // Ref to component where dropzone is initialized
var myDropzone = false // Dropzone can only be initialized AFTER mounted

// Ref to vuetify form
const myForm = ref();
const is_upload = ref(false)
const is_success = ref(false)
const upload_progress = ref()

// Ref to ConfirmIntegrity component
const confirmIntegrity = ref()

function on_submit() {
  if (myDropzone) {
    // TODO: Prompt message if user haven't selected a file
    myDropzone.processQueue()
    // TODO: Redirect to main
  }
}


onMounted(async () => {
  // Initialize Dropzone
  myDropzone = new Dropzone(dropzoneRef.value, {
    autoProcessQueue: false,
    acceptedFiles: '.sqlite',
    paramName: 'file',
    chunking: true,// TODO: Implement chunking
    forceChunking: true,
    url: '/api/v1/upload',
    maxFiles: 1,
    maxFilesize: 2 * 1024, // in MiB
    chunkSize: 10 * 1024 * 1024, // in B
    // Custom messages
    dictInvalidFileType: "File must be an sqlite db with '.sqlite' extension."
  })

  // Clear selected file if another file is dropped
  myDropzone.on("addedfile", function (file) {
    // If a new file is selected, remove the previous one
    // Returns an array, so access the first item
    if (myDropzone.getAcceptedFiles()[0]) {
      myDropzone.removeFile(myDropzone.getAcceptedFiles()[0])
    }
  })

  // Display upload progress
  myDropzone.on("uploadprogress", function (file, progress, bytesSent) {
    upload_progress.value = progress.toFixed(2)
  })

  // Append selected analysers value before sending to server
  myDropzone.on("sending", function (file, xhr, formData) {
    is_upload.value = true
  })
  // Show ConfirmIntegrity component
  myDropzone.on("success", function () {
    is_success.value = true
  })
  // TODO: On upload failure, check if file validation failed or not
  // Reset if failed
  myDropzone.on("error", function (file, response) {
    is_upload.value = false
  })

  // TODO: Add option to cancel upload

})


function atCleanUp() {
  if (myDropzone) {
    myDropzone.removeFile(myDropzone.getAcceptedFiles()[0])
    is_upload.value = false
    is_success.value = false
  }
}

// Watch for state changes
watchEffect(() => {
  if (is_success.value && confirmIntegrity.value) {
    confirmIntegrity.value.loadHash()
  }
})
</script>

<template>
  <v-row fluid class="justify-center align-center">
    <v-sheet height="80vh" width="80vw">
      <v-col align="center" justify="center">
        <v-btn :to="{ name: 'start' }" variant="tonal">
          Back
        </v-btn>
        <!-- 'multipart/form-data' Since a file is being uploaded.-->
        <v-form ref="myForm" enctype="multipart/form-data" @submit.prevent="on_submit">
          <v-progress-linear v-if="is_upload" v-model="upload_progress" color="purple" height="25">
            <template v-slot:default="{ value }">
              <strong>{{ Math.ceil(value) }}%</strong>
            </template>
          </v-progress-linear>
          <v-btn type="submit">
            Upload
          </v-btn>
          <div ref="dropzoneRef" class="dropzone">
          </div>
        </v-form>
        <ConfirmUploadIntegrity @CleanUpFinished="atCleanUp" v-if="is_success" ref="confirmIntegrity">
        </ConfirmUploadIntegrity>
      </v-col>
    </v-sheet>
  </v-row>

</template>
