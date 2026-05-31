<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
    <div class="bg-white rounded-xl p-6 shadow-lg w-[400px] relative">
      <button @click="$emit('close')"
        class="absolute top-3 right-4 text-gray-400 hover:text-gray-600 text-xl">×</button>
      <h2 class="text-lg font-semibold text-[#020B80] text-center mb-2">Horários gerados com sucesso</h2>
      <div class="flex items-start gap-2 text-sm text-gray-600 mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 mt-0.5 text-[#020B80]" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12" y2="8" />
        </svg>
        <p>Não foi possível alocar <span class="font-semibold text-[#020B80]">{{ numAlunos }}</span> aluno(s) nos turnos
          em falta.</p>
      </div>
      <div class="flex justify-end gap-3">
        <button @click="$emit('defer')"
          class="px-4 py-2 border border-[#020B80] rounded-md text-[#020B80] hover:bg-[#020B80]/10">
          Resolver Depois
        </button>
        <button @click="$emit('resolve')" class="px-4 py-2 rounded-md bg-[#020B80] text-white hover:bg-[#020B80]/90">
          Resolver Agora
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= STATE =================================
defineProps<{
  numAlunos: number;
}>();

defineEmits(['close', 'resolve', 'defer']);
</script>
