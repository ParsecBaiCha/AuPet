<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ courseTitle: string }>()
const source = computed(() => '/online-programming/index.html?course=' + encodeURIComponent(props.courseTitle))
</script>
<template><iframe class="programming-frame" :src="source" :title="courseTitle + '在线编程练习'" /></template>
<style scoped>
.programming-frame {
  width: 100%; height: 100%; flex: 1; min-height: 0;
  border: 0; display: block; background: white;
}
</style>
