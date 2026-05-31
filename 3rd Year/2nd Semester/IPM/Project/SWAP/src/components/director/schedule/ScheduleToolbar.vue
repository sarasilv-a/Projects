<template>
  <div class="flex justify-between items-center mb-6">
    <div class="flex flex-col ">
      <label class="font-medium text-[#020B80]/60">Ano</label>
      <select v-model="localYear" class="border rounded px-2 py-1">
        <option v-for="year in [1, 2, 3]" :key="year" :value="year">
          {{ year }}º Year
        </option>
      </select>
    </div>
    <div class="flex gap-3">
      <button
        class="flex items-center gap-1 px-4 py-2 border rounded text-[#020B80] border-[#020B80] hover:bg-[#020B80]/10"
        @click="$emit('generate')">
        📅 Gerar Horários
      </button>
      <button class="flex items-center gap-1 px-4 py-2 bg-[#020B80] text-white rounded hover:bg-[#020B80]/90"
        @click="$emit('publish')">
        🚀 Publicar Horários
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, watch } from 'vue';

// ================================= STATE =================================
const props = defineProps<{
  selectedYear: number
}>();
const emit = defineEmits(['update:selectedYear', 'generate', 'publish']);
const localYear = ref(props.selectedYear);

// ================================= FUNCTIONS =================================
watch(localYear, (newYear) => {
  emit('update:selectedYear', newYear);
});

watch(() => props.selectedYear, (newVal) => {
  if (localYear.value !== newVal) {
    localYear.value = newVal;
  }
});
</script>
