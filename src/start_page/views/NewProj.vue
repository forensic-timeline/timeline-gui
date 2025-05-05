<!-- TODO: Add icons to buttons for accessibility -->
<script setup>
import { ref, onMounted, watchEffect } from 'vue'
// Dropzone for chunked upload
// Validation for file size and type is handled by Dropzone
import { Dropzone } from "@deltablot/dropzone"
// Import component for getting hash of uploaded file
import ConfirmIntegrity from '../components/ConfirmIntegrity.vue'

const selected_analyzers = ref([])
const analyzer_list = ref([])


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

// Client-side validation using vuetify array of rule functions
const analyzer_list_rule = [
  value => selected_analyzers.value.length > 0 || 'Please select at least 1 analyzers.', //required
]

//Retrieves list of analyzers from server
async function load_analyzer_list() {

  // Retrieve data from api
  const requestOptions = {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  };
  await fetch(`/api/v1/analyzers`, requestOptions)
    .then(response => response.json())
    .then(data => {
      analyzer_list.value = data
    });

}

function on_submit() {
  myForm.value?.validate().then(async ({ valid: isValid }) => {
    if (isValid && myDropzone) {
      // TODO: Prompt message if user haven't selected a file
      myDropzone.processQueue()
      // TODO: Redirect to main
    }
  })
}

onMounted(async () => {
  //TODO: Add loading screen/icon for analyzer data loading
  await load_analyzer_list()
  // Initialize Dropzone
  myDropzone = new Dropzone(dropzoneRef.value, {
    autoProcessQueue: false,
    acceptedFiles: '.csv',
    paramName: 'file',
    chunking: true,// TODO: Implement chunking
    forceChunking: true,
    url: '/api/v1/upload',
    maxFiles: 1,
    maxFilesize: 5 * 1024, // in MiB
    chunkSize: 10 * 1024 * 1024, // in B
    // Custom messages
    dictInvalidFileType: "File must be a plaso timeline with '.csv' output format."
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
    formData.append('analyzers', selected_analyzers.value)
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
  <v-container fluid fill-height>
    <v-col align="center" justify="center">
      <v-btn :to="{ name: 'start' }" variant="tonal">
        Back
      </v-btn>
      <!-- Analyzer Select
          
      TODO: Analyzer search, select/deselect all, grouping, and integrate to actual submitable form.
      -->
      <!-- 'multipart/form-data' Since a file is being uploaded.-->
      <!-- TEST DROPZONE -->
      <v-form ref="myForm" enctype="multipart/form-data" @submit.prevent="on_submit">
        <v-row>
          <v-container fluid>
            <!-- For displaying error value for analyzers -->
            <v-input :rules="analyzer_list_rule">
              <v-virtual-scroll :height="300" :items="analyzer_list">
                <template v-slot:default="{ item }">
                  <!-- Prevent user from changing analyzer list while file is uploaded -->
                  <v-checkbox v-model="selected_analyzers" :label="item['name']" :value="item['name']"
                    :disabled="is_upload ? '' : disabled"></v-checkbox>
                </template>
              </v-virtual-scroll>
            </v-input>

            <p>{{ selected }}</p>
          </v-container>
        </v-row>
        <div ref="dropzoneRef" class="dropzone">
          <v-col>
            <!-- <v-file-input v-model="file_value" label="Upload a plaso timeline (default .csv output)" accept=".csv"
              :rules="file_rule" name=file>

            </v-file-input> -->

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
      </v-form>
      <ConfirmIntegrity @CleanUpFinished="atCleanUp" v-if="is_success" ref="confirmIntegrity">
      </ConfirmIntegrity>
    </v-col>
  </v-container>
</template>
