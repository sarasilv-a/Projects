<template>
  <div class="bg-white p-6 rounded-lg shadow border border-[#020B80]/50">
    <div class="flex justify-between items-center mb-4">
      <div>
        <h2 class="text-lg font-bold text-[#020B80]">Ocupação dos Turnos</h2>
        <p class="text-sm text-[#020B80]/60">Percentagem de ocupação de cada turno</p>
      </div>
      <button class="text-[#020B80]" @click="showNotes = true">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          class="lucide lucide-edit">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
        </svg>
      </button>
    </div>
    <div v-if="showNotes" class="fixed inset-0 flex items-center justify-center bg-black/30 z-50">
      <div class="bg-[#fefbfb] p-6 rounded-xl w-[320px] shadow-lg border border-[#020B80]/30 relative">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold text-[#020B80]">Apontamentos</h2>
          <button class="text-[#020B80]" @click="showNotes = false">✕</button>
        </div>
        <textarea v-model="notes"
          class="w-full h-48 p-2 rounded-lg border text-sm text-[#020B80] border-[#020B80]/20 focus:outline-none resize-none"></textarea>
      </div>
    </div>
    <div class="flex flex-wrap gap-4 mb-4">
      <div class="relative w-40">
        <select v-model="selectedYear"
          class="w-full p-2 border border-[#020B80]/50 rounded-md appearance-none pr-8 bg-white">
          <option value="1">1st Year</option>
          <option value="2">2nd Year</option>
          <option value="3">3rd Year</option>
        </select>
        <div class="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none text-[#020B80]">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="lucide lucide-chevron-down">
            <path d="m6 9 6 6 6-6" />
          </svg>
        </div>
      </div>
      <div class="relative w-40">
        <select v-model="selectedSubject"
          class="w-full p-2 border border-[#020B80]/50 rounded-md appearance-none pr-8 bg-white">
          <option value="">Todas as disciplinas</option>
          <option v-for="subject in filteredSubjects" :key="subject.id" :value="subject.id">
            {{ subject.shortname }}
          </option>
        </select>
        <div class="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none text-blue-900">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="lucide lucide-chevron-down">
            <path d="m6 9 6 6 6-6" />
          </svg>
        </div>
      </div>
    </div>
    <div class="space-y-4 max-h-[400px] overflow-y-auto pr-2">
      <div v-for="shift in filteredShifts" :key="shift.id" class="mb-4">
        <div class="flex justify-between mb-1">
          <span class="font-bold text-[#020B80]">{{ shift.name }}</span>
          <span class="text-[#020B80] font-bold">{{ getOccupancyPercentage(shift) }}%</span>
        </div>
        <div class="flex items-center">
          <div class="text-sm text-[#020B80]/60 w-24">{{ getShiftStudentCount(shift) }}/{{ shift.limit }} alunos</div>
          <div class="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
            <div class="h-full rounded-full" :class="getBarColorClass(getOccupancyPercentage(shift))"
              :style="{ width: `${getOccupancyPercentage(shift)}%` }"></div>
          </div>
        </div>
      </div>
      <div v-if="filteredShifts.length === 0" class="text-center py-8 text-gray-500">
        Nenhum turno encontrado para os filtros selecionados
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, computed } from 'vue';
import type { Subject, Shift } from '@/types/types';

// ================================= STATE =================================
const showNotes = ref(false)
const notes = ref('Estes são os meus apontamentos.')
const props = defineProps<{
  subjects: Subject[];
  shifts: Shift[];
  schedules: any[];
}>();
const selectedYear = ref('1');
const selectedSubject = ref('');
const filteredSubjects = computed(() => {
  return props.subjects.filter(subject => subject.year === parseInt(selectedYear.value));
});
const filteredShifts = computed(() => {
  let filtered = props.shifts;

  filtered = filtered.filter(shift => {
    const subject = props.subjects.find(s => s.id === shift.subjectId);
    return subject && subject.year === parseInt(selectedYear.value);
  });

  if (selectedSubject.value) {
    filtered = filtered.filter(shift => shift.subjectId === parseInt(selectedSubject.value));
  }

  return filtered;
});

// ================================= FUNCTIONS =================================
const getShiftStudentCount = (shift: Shift) => {
  return props.schedules.filter(schedule => schedule.shiftId === shift.id).length;
};

const getOccupancyPercentage = (shift: Shift) => {
  const count = getShiftStudentCount(shift);
  return Math.round((count / shift.limit) * 100);
};

const getBarColorClass = (percentage: number) => {
  if (percentage >= 90) return 'bg-red-500';
  if (percentage >= 70) return 'bg-orange-500';
  return 'bg-green-500';
};
</script>
