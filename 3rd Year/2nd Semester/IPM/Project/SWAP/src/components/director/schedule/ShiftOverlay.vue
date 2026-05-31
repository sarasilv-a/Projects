<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
    <div class="bg-white rounded-xl p-6 shadow-lg border-2 border-[#020B80] w-[400px] relative">
      <button @click="$emit('close')"
        class="absolute top-2 right-3 text-gray-400 hover:text-gray-600 text-xl">×</button>
      <h2 class="text-lg font-bold text-[#020B80] mb-2">
        {{ formatDay(dia) }} {{ hora }}h
      </h2>
      <hr class="mb-3 border-[#020B80]" />
      <ul class="space-y-2">
        <li v-for="turno in turnos" :key="turno.id" class="text-[#020B80] hover:underline cursor-pointer"
          @click="$emit('ver-turno', turno.id)">
          {{ turno.disciplina }} – {{ turno.turma }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= STATE =================================
defineProps<{
  dia: string;
  hora: number;
  turnos: Array<{
    id: number;
    disciplina: string;
    turma: string;
  }>;
}>();
defineEmits(['close', 'ver-turno']);

// ================================= FUNCTIONS =================================
const formatDay = (dia: string): string => {
  const map: Record<string, string> = {
    segunda: 'Segunda',
    terca: 'Terça',
    quarta: 'Quarta',
    quinta: 'Quinta',
    sexta: 'Sexta'
  };
  return map[dia] || dia;
};
</script>
