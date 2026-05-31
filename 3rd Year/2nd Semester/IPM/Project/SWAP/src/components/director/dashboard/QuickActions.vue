<template>
  <div class="bg-white p-6 rounded-lg shadow border border-[#020B80]/50">
    <div class="mb-4">
      <h2 class="text-lg font-bold text-[#020B80]">Ações Rápidas</h2>
      <p class="text-sm text-[#020B80]/60">Acesso rápido às funcionalidades principais</p>
    </div>
    <div class="space-y-2">
      <button v-for="action in actions" :key="action.label"
        class="w-full flex items-center gap-2 p-3 bg-[#020B80]/50 hover:bg-[#020B80]/20 rounded-md transition-colors"
        @click="$emit('action-click', action.id)">
        <component :is="action.icon" class="w-5 h-5" />
        <span>{{ action.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { h } from 'vue';
import { Calendar, Users, FileText } from 'lucide-vue-next';

// ================================= STATE =================================
const actions = [
  {
    id: 'view-schedule',
    label: 'Consultar Horários',
    icon: h(Calendar)
  },
  {
    id: 'manage-students',
    label: 'Gerir Alocação de Alunos',
    icon: h(Users)
  },
  {
    id: 'publish-schedule',
    label: 'Publicar Horários',
    icon: h(FileText)
  }
];
defineEmits(['action-click']);
</script>
