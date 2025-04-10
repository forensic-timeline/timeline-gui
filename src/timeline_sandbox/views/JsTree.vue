<script setup>
import { jstree } from "jquery"
import "jstree"
import { ref, onMounted, useTemplateRef } from 'vue'
const timelines = [useTemplateRef('timeline1')]

onMounted(() => {
    jstree.create(pElementRef.value, { 'core' : {
    'data' : [
       'Simple root node',
       {
         'text' : 'Root node 2',  
         'state' : {
           'opened' : true,
           'selected' : true,
         },
         'children' : [
           { 'text' : 'Child 1', 'desc' : "312312313" },
           'Child 2'
         ]
      }
    ]
} })
})
</script>

<template>
    <div ref="timeline1">Hello</div>
</template>

<style>
@import url("../assets/jstree_themes/default/style.min.css");
</style>
