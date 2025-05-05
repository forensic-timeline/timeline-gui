<!-- TODO: Add icons to buttons for accessibility -->
<script setup>
import { ref, onMounted } from 'vue'
// Dropzone for chunked upload
// Validation for file size and type is handled by Dropzone
import { Dropzone } from "@deltablot/dropzone"

// The 'File' object will be automatically stored in an array.
// To access a single file upload directly, use the first member ([0])
// https://stackoverflow.com/questions/857618/javascript-how-to-extract-filename-from-a-file-input-control
const file_value = ref()

// Dropzone
const dropzoneRef = ref() // Ref to component where dropzone is initialized
var myDropzone = false // Dropzone can only be initialized AFTER mounted

// Ref to vuetify form
const myForm = ref();
const is_upload = ref(false)
const upload_progress = ref()
// Client-side validation using vuetify array of rule functions
function on_submit() {
  console.log("waiting...")

  myForm.value?.validate().then(async ({ valid: isValid }) => {
    if (isValid && myDropzone) {
      // TODO: Prompt message if user haven't selected a file
      console.log("GO!")
      myDropzone.processQueue()
      // TODO: Redirect to main
    }
  })
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
    maxFilesize: 5 * 1024, // in MiB
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

  // Append selected analyzers value before sending to server
  myDropzone.on("sending", function (file, xhr, formData) {
    is_upload.value = true
  })
  // TODO: On upload failure, check if file validation failed or not
  // Reset if failed
  myDropzone.on("error", function (file, response) {
    is_upload.value = false
  })

  // TODO: Add option to cancel upload

})
</script>

<template>
  <v-container fill-height>
    <v-row align="center" justify="center">
      <v-btn :to="{ name: 'start' }" variant="tonal">
        Back
      </v-btn>
      <!-- 'multipart/form-data' Since a file is being uploaded.-->
      <v-form ref="myForm" enctype="multipart/form-data" @submit.prevent="on_submit">
        <v-col>
          <v-row>
            <div ref="dropzoneRef" class="dropzone">
              <v-col>
                <v-progress-linear v-if="is_upload" v-model="upload_progress" color="purple" height="25">
                  <template v-slot:default="{ value }">
                    <strong>{{ Math.ceil(value) }}%</strong>
                  </template>
                </v-progress-linear>
              </v-col>
              <v-col>
                <v-btn type="submit">
                  Upload
                </v-btn>
              </v-col>
            </div>
          </v-row>
        </v-col>
      </v-form>

    </v-row>
  </v-container>
</template>
