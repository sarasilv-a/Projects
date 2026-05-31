<template>
  <div class="flex gap-[30px] mb-[30px]">
    <div class="flex flex-col w-[200px]">
      <label for="year-select" class="text-[#020B80]/60 mb-[5px]">Ano</label>
      <select id="year-select" :value="selectedYear"
        @change="$emit('update:selectedYear', Number(($event.target as HTMLSelectElement).value))"
        class="p-[10px] rounded-[10px] border border-[#020B80]/50 bg-white text-sm cursor-pointer">
        <option v-for="year in [1, 2, 3]" :key="year" :value="year">{{ year }}º Year</option>
      </select>
    </div>
    <div class="flex flex-col w-[200px]">
      <label for="subject-select" class="text-[#020B80]/60 mb-[5px]">Unidade Curricular</label>
      <select id="subject-select" :value="selectedSubjectId"
        @change="$emit('update:selectedSubjectId', Number(($event.target as HTMLSelectElement).value))"
        class="p-[10px] rounded-[10px] border border-[#020B80]/50 bg-white text-sm cursor-pointer">
        <option v-for="subject in filteredSubjects" :key="subject.id" :value="subject.id">
          {{ subject.shortname }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= STATE =================================
defineProps<{
  selectedYear: number;
  selectedSubjectId: number | null;
  filteredSubjects: Array<{ id: number; shortname: string }>;
}>();

defineEmits(['update:selectedYear', 'update:selectedSubjectId']);
</script>
