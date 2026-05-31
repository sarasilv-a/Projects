<template>
  <div class="flex gap-6 mb-6">
    <div class="flex flex-col w-40">
      <label class="text-[#020B80]/60 text-sm mb-1">Ano</label>
      <select class="border border-[#020B80]/50 rounded-md px-3 py-2 text-sm bg-white" :value="selectedYear"
        @change="(e: Event) => $emit('update:selectedYear', Number((e.target as HTMLSelectElement).value))">
        <option v-for="year in [1, 2, 3]" :key="year" :value="year">
          {{ year }}º Year
        </option>
      </select>
    </div>
    <div class="flex flex-col w-72">
      <label class="text-[#020B80]/60 text-sm mb-1">Unidade Curricular</label>
      <select class="border border-[#020B80]/50 rounded-md px-3 py-2 text-sm bg-white" :value="selectedSubjectId"
        @change="(e: Event) => $emit('update:selectedSubjectId', Number((e.target as HTMLSelectElement).value))">
        <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
          {{ subject.name }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import type { Subject } from '@/types/types'

// ================================= STATE =================================
defineProps<{
  selectedYear: number
  selectedSubjectId: number
  subjects: Subject[]
}>()
defineEmits(['update:selectedYear', 'update:selectedSubjectId'])
</script>
