<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <div class="bg-white p-4 rounded-lg shadow border border-[#020B80]/50">
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm text-[#020B80]">Total de Alunos</span>
        <span class="text-[#020B80]/50">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="lucide lucide-users">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
        </span>
      </div>
      <div class="text-3xl font-bold text-[#020B80]">{{ totalStudents }}</div>
    </div>
    <div class="bg-white p-4 rounded-lg shadow border border-[#020B80]/50">
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm text-[#020B80]">Alunos Alocados</span>
        <span class="text-[#020B80]/50">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="lucide lucide-check-circle">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <path d="m9 11 3 3L22 4" />
          </svg>
        </span>
      </div>
      <div class="text-3xl font-bold text-[#020B80]">{{ allocatedStudents }}</div>
      <div class="text-sm text-[#020B80]/60">{{ allocatedPercentage }}% dos alunos alocados</div>
    </div>
    <div class="bg-white p-4 rounded-lg shadow border border-[#020B80]/50">
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm text-[#020B80]">Total de Turnos</span>
        <span class="text-[#020B80]/50">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="lucide lucide-clock">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
        </span>
      </div>
      <div class="text-3xl font-bold text-[#020B80]">{{ totalShifts }}</div>
    </div>
    <div class="bg-white p-4 rounded-lg shadow border border-[#020B80]/50">
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm text-[#020B80]">Ocupação Média</span>
        <span class="text-[#020B80]/50">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="lucide lucide-bar-chart-2">
            <line x1="18" x2="18" y1="20" y2="10" />
            <line x1="12" x2="12" y1="20" y2="4" />
            <line x1="6" x2="6" y1="20" y2="14" />
          </svg>
        </span>
      </div>
      <div class="text-3xl font-bold text-[#020B80]">{{ averageOccupancy }}%</div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= STATE =================================
defineProps<{
  totalStudents: number;
  allocatedStudents: number;
  allocatedPercentage: number;
  totalShifts: number;
  averageOccupancy: number;
}>();
</script>
