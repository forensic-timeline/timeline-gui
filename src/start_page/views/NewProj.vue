<!-- TODO: Add icons to buttons for accessibility -->
<script setup>
import { ref, onMounted } from 'vue'
// TEST
import { Dropzone } from "@deltablot/dropzone"

const selected_analyzers = ref([])
const analyzer_list = ref([])


// TEST
const dropzoneRef = ref()
var myDropzone = false
const file_value = ref() // TODO: Store on file added

// Ref to vuetify form
const myForm = ref();
const is_upload = ref(false)
const upload_progress = ref()
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
      // TEST
      console.log("GO!")
      myDropzone.processQueue()
      // TODO: Redirect to main
    }
  })
}

onMounted(async () => {
  //TODO: Add loading screen/icon for analyzer data loading
  await load_analyzer_list()
  //TEST
  myDropzone = new Dropzone(dropzoneRef.value, {
    autoProcessQueue: false,
    acceptedFiles: '.csv',
    paramName: 'file',
    chunking: false, // TEST
    forceChunking: true,
    url: '/api/v1/upload',
    maxFiles: 1,
    maxFilesize: 5 * 1024, // in MiB
    chunkSize: 10 * 1024 * 1024, // in B
    // Custom messages
    dictInvalidFileType: "File must be a plaso timeline with '.csv' output format."
  })

  // Clear selected file if another file is dropped
  myDropzone.on("addedfile", function(file){
    // If a new file is selected, remove the previous one
    console.log(myDropzone.getAcceptedFiles())
    if(myDropzone.getAcceptedFiles()[0]){
      myDropzone.removeFile(myDropzone.getAcceptedFiles()[0])
    }
  })

  // Display upload progress
  myDropzone.on("uploadprogress", function(file, progress, bytesSent) {
    upload_progress.value = progress.toFixed(2)
  })

  // Append selected analyzers value before sending to server
  myDropzone.on("sending", function(file, xhr, formData){
    formData.append('analyzers', selected_analyzers.value)
    is_upload.value = true
  })

  myDropzone.on("success", function(file, response){
    // TODO: On upload success, check if file validation failed or not
    // TEST
    alert("success" + JSON.stringify(response))
  })

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
                  <v-checkbox v-model="selected_analyzers" :label="item['name']" :value="item['name']"></v-checkbox>
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
    </v-col>
  </v-container>
</template>
