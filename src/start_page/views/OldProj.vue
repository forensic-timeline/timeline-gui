<!-- TODO: Add icons to buttons for accessibility -->
<script setup>
import { ref } from 'vue'

// The 'File' object will be automatically stored in an array.
// To access a single file upload directly, use the first member ([0])
// https://stackoverflow.com/questions/857618/javascript-how-to-extract-filename-from-a-file-input-control
const file_value = ref()

// Ref to vuetify form
const myForm = ref();
const is_upload = ref(false)
const upload_progress = ref()
// Client-side validation using vuetify array of rule functions
// CONST: SERVER SIDE MAX FILE SIZE
const file_rule = [
  value => {
    if (!value || !value.length) {
      return 'Field is required'
    }
    else {
      if (!((value[0].name.indexOf('.') > -1) &&
        value[0].name.split('.')[value[0].name.split('.').length - 1].toLowerCase() == "sqlite")) {
        // If filename contains '.' and extension is ".csv"
        return 'File extension must be .csv'
      }
      else if (value[0].size > (5 * 1073741824)) {
        return 'File size must be less than 5 GB' //Max size
      }
      else {
        return true
      }
    }

  }
]

function on_submit() {
  console.log("waiting...")

  myForm.value?.validate().then(async ({ valid: isValid }) => {
    if (isValid) {
      // Construct and send form data to API
      const formData = new FormData()
      formData.append('file', file_value.value)
      // TEST: XHR Request for upload
      const xhr = new XMLHttpRequest()
      xhr.open("POST", "/api/v1/upload")
      // Calculates and logs upload progress
      is_upload.value = true
      xhr.upload.addEventListener("progress", (e) => {
        const percent = e.lengthComputable ? (e.loaded / e.total) * 100 : 0
        console.log(percent.toFixed(2))
        upload_progress.value = percent.toFixed(2)
      })

      xhr.send(formData)
      xhr.onreadystatechange = function () {
        if (xhr.readyState == XMLHttpRequest.DONE) {
          // TEST: Assume redirect if success
          alert(xhr.responseText);
          is_upload.value = false
          upload_progress.value = 0

        }
      }

      //TODO: Redirect to main
    }
  })
}

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
            <v-col>
              <v-file-input v-model="file_value" label="Upload an existing DFTPL timeline (.sqlite database)"
                accept=".sqlite" :rules="file_rule" name=file>

              </v-file-input>
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
          </v-row>
        </v-col>
      </v-form>

    </v-row>
  </v-container>
</template>
