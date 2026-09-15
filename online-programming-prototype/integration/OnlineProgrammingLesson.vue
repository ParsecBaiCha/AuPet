<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ courseTitle: string }>()
const source = computed(() => '/online-programming/index.html?course=' + encodeURIComponent(props.courseTitle))
</script>
<template><iframe class="programming-frame" :src="source" :title="courseTitle + '在线编程练习'" /></template>
<style scoped>.programming-frame{width:100%;height:calc(100vh - 230px);min-height:720px;border:0;display:block;background:white} @media(max-width:760px){.programming-frame{min-height:1100px}}</style>
