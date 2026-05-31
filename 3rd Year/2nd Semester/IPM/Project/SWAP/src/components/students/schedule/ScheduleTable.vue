<template>
  <div class="bg-white rounded-lg shadow flex-1 flex flex-col overflow-hidden">
    <div class="flex-1 overflow-hidden">
      <table class="w-full border-collapse h-full">
        <thead class="rounded-t-lg overflow-hidden">
          <tr class="bg-[#D9D9D9]">
            <th class="p-2 border border-[#020B80]/50 w-16"></th>
            <th v-for="dia in diasSemana" :key="dia"
              class="p-2 border border-[#020B80]/50 w-1/5 text-center font-semibold">
              {{ formatDayName(dia) }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-300">
          <tr v-for="hora in horas" :key="hora" class="h-[calc(100%/13)]">
            <td class="border border-[#020B80]/50 text-center text-[#020b80]/60 text-sm">{{ hora }}h</td>
            <td v-for="dia in diasSemana" :key="`${hora}-${dia}`"
              class="p-0 border border-[#020b80]/50 relative h-[60px]">
              <template v-for="turno in getShiftsStartingAt(dia, hora)" :key="turno.id">
                <div
                  class="absolute left-1 right-1 top-1 bg-[#020b80] text-white p-2 rounded text-sm text-left cursor-pointer"
                  :style="{
                    height: `${(turno.duracao || 1) * 57 - 4}px`,
                  }" @click="$emit('turno-click', turno.id)">
                  {{ turno.disciplina }} - {{ turno.turma }}
                </div>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= STATE =================================
const props = defineProps<{
  horas: number[];
  diasSemana: string[];
  turnos: Array<{
    id: number;
    dia: string;
    hora: number;
    disciplina: string;
    turma: string;
  }>;
}>();


// ================================= FUNCTIONS =================================
const getShift = (dia: string, hora: number) => {
  return props.turnos.find(turno => turno.dia === dia && turno.hora === hora);
};

const formatDayName = (dia: string) => {
  const dayMap: Record<string, string> = {
    'segunda': 'Segunda',
    'terca': 'Terça',
    'quarta': 'Quarta',
    'quinta': 'Quinta',
    'sexta': 'Sexta'
  };

  return dayMap[dia] || dia;
};

const getShiftsStartingAt = (dia: string, hora: number) => {
  return props.turnos
    .filter(turno => turno.dia === dia && turno.hora === hora)
    .map(turno => ({
      ...turno,
      duracao: getDuration(turno.id)
    }));
};

const getDuration = (id: number): number => {
  const turno = props.turnos.find(t => t.id === id);
  if (!turno || !('start' in turno) || !('end' in turno)) return 1;

  const start = parseInt((turno as any).start.split(':')[0]);
  const end = parseInt((turno as any).end.split(':')[0]);

  return Math.max(1, end - start);
};
</script>

<style scoped>
table {
  table-layout: fixed;
  height: calc(100% - 1rem);
}
</style>
