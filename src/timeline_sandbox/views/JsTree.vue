<script setup>
import { jstree } from "jquery"
import "jstree"
import { ref, onMounted, onBeforeMount, onUpdated, useTemplateRef } from 'vue'
import "sortablejs"
import Sortable from "sortablejs"

const timeline_num = ref(0)
const timeline_refs = useTemplateRef("timeline_refs")
// const timeline_refs = ref({})
const timelines_list_ref = useTemplateRef("timelines")

// Stores timeline data after loaded
let data_arr = []

function render_timeline(element_ref, timeline_data) {
  // Render trees
  jstree.create(element_ref, {
    'core': {
      'data': timeline_data
    }
  })
}

async function load_high_data() {

  // Retrieve data from api
  const requestOptions = {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  };
  await fetch(`/api/v1/test-timeline-json`, requestOptions)
    .then(response => response.json())
    .then(data => {
      data_arr = data
    });


  //TODO: Multiple timelines
  // Get references and data for each of the timelines
  timeline_num.value = data_arr.length

}

function render_all_timelines() {
  var timeline_list = []
  for (let x = 0; x < timeline_num.value; x++) {
    timeline_list.push({ "ref": timeline_refs.value[x], "data": data_arr[x] })
  }

  for (let timeline of timeline_list) {
    render_timeline(timeline["ref"], timeline["data"])
  }

  var sortable = Sortable.create(timelines_list_ref.value.$el, { direction: 'horizontal' });
}

onMounted(async () => {
  //TODO: Add loading screen/icon for data loading
  await load_high_data()
  render_all_timelines()
})

// HACK: For some reason, vuetify components with v-for doesn't trigger "onUpdated"
// onUpdated(() => {
//   //TODO: Add loading screen/icon for data loading
//   //TEST
//   console.log("List updated!")
//   render_all_timelines()
// })
</script>

<template>
  <v-row ref="timelines">
    <template v-for="num in timeline_num">
      <v-col>
        <li ref="timeline_refs">
          {{ num }}
        </li>
      </v-col>

    </template>



    <!-- <template v-for="num in timeline_num">
      <li :ref="(el) => (timeline_refs[num] = el)"> {{ num }} </li>
    </template> -->
  </v-row>
</template>

<style>
@import url("../assets/jstree_themes/default/style.min.css");
</style>
