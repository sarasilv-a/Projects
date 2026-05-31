<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
    <div class="bg-white rounded-lg shadow-xl w-[400px] p-6 relative">
      <button @click="close" class="absolute top-2 right-2 text-gray-400 hover:text-gray-600">
        ✕
      </button>
      <h2 class="text-xl font-bold text-blue-900 mb-4">{{ subject?.name }} ({{ subject?.shortname }})</h2>
      <div class="flex justify-between text-sm text-gray-700 mb-2">
        <div>
          <p class="font-semibold">Turno</p>
          <p>{{ shift?.name }}</p>
        </div>
        <div>
          <p class="font-semibold">Sala</p>
          <p>{{ shift?.room }}</p>
        </div>
      </div>
      <div class="flex justify-between text-sm text-gray-700 mb-2">
        <div>
          <p class="font-semibold">Horário</p>
          <p>{{ diaSemana }}, {{ shift?.start }}h-{{ shift?.end }}h</p>
        </div>
        <div>
          <p class="font-semibold">Ocupação</p>
          <p>{{ students.length }}/{{ shift?.limit }} alunos</p>
        </div>
      </div>
      <div class="flex justify-end mt-4 gap-2">
        <button @click="close"
          class="bg-white border border-blue-900 text-blue-900 px-4 py-2 rounded hover:bg-gray-100">
          Cancelar
        </button>
        <button class="bg-blue-900 text-white px-4 py-2 rounded hover:bg-blue-800" @click="emit('request-change')">
          Solicitar troca de turno
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { onMounted, ref, computed, watch } from 'vue';
import type { Shift, Subject, Student } from '@/types/types';
import { getStudentsByShift } from '@/api/studentAPI';

// ================================= STATE =================================
const props = defineProps<{
  visible: boolean;
  shift: Shift | null;
  subject: Subject | null;
}>();
const emit = defineEmits(['close', 'request-change']);
const students = ref<Student[]>([]);
const diaSemana = computed(() => {
  const dias = ['segunda', 'terça', 'quarta', 'quinta', 'sexta'];
  return dias[(props.shift?.day || 1) - 1] || '';
});

// ================================= FUNCTIONS =================================
function close() {
  emit('close');
}

watch(() => props.shift?.id, async (newId) => {
  if (props.visible && newId !== undefined && newId !== null) {
    students.value = await getStudentsByShift(newId);
  }
});
</script>
