<template>
  <div
    class="bg-white mx-auto rounded-[15px] border border-[#020B80]/50 shadow-[0_4px_10px_rgba(0,0,0,0.05)] px-[14px] max-h-[650px]">
    <h2 class="text-[20px] font-bold text-[#020B80] p-4">Lista de Turnos</h2>
    <div class="max-h-[500px] overflow-y-scroll border-[#020B80]/60 px-10">
      <table class="min-w-full divide-y divide-gray-200 divide-[#020B80]/50">
        <thead class="">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">
              ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">
              Capacidade</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">
              Ocupação</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">
              Horário</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">
              Sala</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-[#020B80]/50">
          <tr v-for="shift in shifts" :key="shift.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#000000]">{{ shift.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#000000]">
              <div class="flex flex-col">
                <span class="text-sm font-medium text-[#020B80]">{{ shift.currentCapacity }}/{{ shift.maxCapacity }}
                  alunos</span>
                <div class="h-[8px] w-[90%] bg-[#e7e7e7] rounded mt-[4px] overflow-hidden">
                  <div class="h-full transition-all duration-300" :class="{
                    'bg-red-500': shift.currentCapacity >= shift.maxCapacity,
                    'bg-orange-400': shift.currentCapacity / shift.maxCapacity >= 0.7 && shift.currentCapacity < shift.maxCapacity,
                    'bg-lime-500': shift.currentCapacity / shift.maxCapacity < 0.7,
                    'bg-gray-400': shift.maxCapacity === 0
                  }" :style="{ width: (shift.currentCapacity / shift.maxCapacity * 100) + '%' }"></div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-[#020B80]">{{ shift.occupation }}%</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#020B80]">
              <div>{{ shift.day }}</div>
              <div>{{ shift.time }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#020B80]">
              <div>{{ shift.building }}</div>
              <div>{{ shift.room }}</div>
            </td>
            <td class="px-[14px] py-[14px] text-right">
              <button @click="toggleMenu(shift.id)"
                class="text-[#020B80]/80 hover:text-[#020B80] hover:bg-[rgba(217,217,217,0.6)] p-[10px] rounded-[5px] ml-auto flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" height="16" viewBox="0 0 512 512" fill="currentColor">
                  <path
                    d="M328 256c0 39.8-32.2 72-72 72s-72-32.2-72-72 32.2-72 72-72 72 32.2 72 72zm104-72c-39.8 0-72 32.2-72 72s32.2 72 72 72 72-32.2 72-72-32.2-72-72-72zm-352 0c-39.8 0-72 32.2-72 72s32.2 72 72 72 72-32.2 72-72-32.2-72-72-72z" />
                </svg>
              </button>
              <div
                v-if="openMenuId === shift.id"
                class="absolute right-3 mt-1 w-40 h-32 bg-white border border-[#020B80]/50 rounded-xl shadow z-50">
                <div class="text-sm  text-left text-[#020B80] font-bold px-4 py-2 border-b">Mais Ações</div>
                  <button
                    @click="$emit('open-students', shift.id); closeMenu()"
                    class="block w-full text-left px-4 py-2 text-sm text-[#020B80]/50 hover:bg-gray-100">
                    Ver Alunos
                  </button>
                  <button
                    @click="$emit('change-room', shift.id); closeMenu()"
                    class="block w-full text-left px-4 py-2 text-sm text-[#020B80]/50 hover:bg-gray-100">
                    Trocar Sala
                  </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div
      v-if="openMenuId !== null"
      class="fixed inset-0 z-40"
      @click="closeMenu"
    >
    </div>
  </div>
</template>

<script setup lang="ts">

import { ref } from 'vue';

// ================================= STATE =================================
defineProps<{
  shifts: Array<{
    id: number;
    name: string;
    currentCapacity: number;
    maxCapacity: number;
    occupation: number;
    day: string;
    time: string;
    building: string;
    room: string;
  }>;
}>();

const emit = defineEmits(['open-students', 'change-room']);
const openMenuId = ref<number | null>(null);

function toggleMenu(id: number) {
  openMenuId.value = openMenuId.value === id ? null : id;
}

function closeMenu() {
  openMenuId.value = null;
}
</script>
