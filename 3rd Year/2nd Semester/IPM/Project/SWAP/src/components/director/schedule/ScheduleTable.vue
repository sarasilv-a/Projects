<template>
  <div class="bg-white rounded-lg shadow flex-1 flex flex-col overflow-hidden border border-[#020B80]/50">
    <div class="flex-1 overflow-hidden">
      <table class="w-full border-collapse h-full">
        <thead>
          <tr class="bg-[#D9D9D9]">
            <th class="p-2 border border-[#020B80]/50 w-16"> </th>
            <th v-for="dia in diasSemana" :key="dia" class="p-2 border border-[#020B80]/50 text-center font-semibold">
              {{ formatDayName(dia) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="hora in horas" :key="hora">
            <td class="border border-[#020B80]/50 text-center text-[#020b80]/60 text-sm">{{ hora }}h</td>
            <td v-for="dia in diasSemana" :key="`${hora}-${dia}`" class="p-1 border border-[#020B80]/50 relative">
              <div class="flex flex-col gap-1">
                <template v-if="getTurnos(dia, hora).length > 0">
                  <div class="bg-[#020B80] text-white p-1 rounded text-sm cursor-pointer overflow-hidden"
                    @click="$emit('show-all', { dia, hora })">
                    <div v-for="turno in getTurnos(dia, hora).slice(0, 2)" :key="turno.id">
                      {{ turno.disciplina }} – {{ turno.turma }}
                    </div>
                    <div v-if="getTurnos(dia, hora).length > 2" class="italic text-white mt-1">
                      ...
                    </div>
                  </div>
                </template>
              </div>
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
const getTurnos = (dia: string, hora: number) => {
  return props.turnos.filter(turno => turno.dia === dia && turno.hora === hora);
};

const formatDayName = (dia: string) => {
  const map: Record<string, string> = {
    segunda: "Segunda",
    terca: "Terça",
    quarta: "Quarta",
    quinta: "Quinta",
    sexta: "Sexta"
  };
  return map[dia] || dia;
};
</script>

<style scoped>
table {
  table-layout: fixed;
  height: calc(100% - 1rem);
}
</style>
