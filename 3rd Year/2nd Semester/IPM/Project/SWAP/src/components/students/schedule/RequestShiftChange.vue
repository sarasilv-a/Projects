<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
    <div class="bg-white rounded-lg shadow-xl w-[450px] p-6 relative">
      <button @click="close" class="absolute top-2 right-2 text-gray-400 hover:text-gray-600">
        ✕
      </button>
      <h2 class="text-xl font-bold text-blue-900 mb-4">Solicitar troca de turno</h2>
      <p class="mb-4">Selecione o turno para o qual deseja trocar:</p>
      <p v-if="alternativeShifts.length === 0" class="text-orange-500 mb-4">
        Não existem turnos alternativos disponíveis para esta disciplina.
      </p>
      <div v-else class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div class="relative">
            <select v-model="selectedShiftId"
              class="w-full p-2 border border-gray-300 rounded-md appearance-none pr-8 bg-white">
              <option v-for="shift in alternativeShifts" :key="shift.id" :value="shift.id">
                {{ shift.name }}
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
        <div v-if="selectedShift">
          <div>
            <p class="text-gray-500 text-sm">Ocupação</p>
            <p class="font-medium">{{ students.length }}/{{ selectedShift.limit }} alunos</p>
          </div>
          <div class="mt-2">
            <p class="text-gray-500 text-sm">Horário</p>
            <p class="font-medium">{{ formatDay(selectedShift.day) }}, {{ selectedShift.start }}-{{ selectedShift.end }}
            </p>
          </div>
        </div>
      </div>
      <div class="mt-6 flex justify-end space-x-2">
        <button @click="close" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
          Cancelar
        </button>
        <button @click="handleSubmit" :disabled="!selectedShiftId" :class="[
          'px-4 py-2 rounded-md',
          !selectedShiftId
            ? 'bg-gray-400 text-white cursor-not-allowed'
            : 'bg-blue-900 text-white hover:bg-blue-800'
        ]">
          Solicitar troca de turno
        </button>
      </div>
    </div>
  </div>
  <Notification :show="notification.show" :title="notification.title" :message="notification.message"
    @close="closeNotification" />
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, computed, watch } from 'vue';
import type { Shift, Student } from '@/types/types';
import { getStudentsByShift } from '@/api/studentAPI';
import { createNotification } from '@/api/notificationAPI';
import { useSessionStore } from '@/stores/session';
import Notification from '@/components/reusables/Notification.vue';

// ================================= STATE =================================
const props = defineProps<{
  visible: boolean;
  currentShiftId: number;
  shifts: Shift[];
  subjectId: number;
}>();
const emit = defineEmits(['close', 'submit']);
const selectedShiftId = ref<number | null>(null);
const students = ref<Student[]>([]);
const alternativeShifts = computed(() =>
  props.shifts.filter(
    (shift) => shift.subjectId === props.subjectId && shift.id !== props.currentShiftId
  )
);
const selectedShift = computed(() =>
  props.shifts.find((s) => s.id === selectedShiftId.value) || null
);
const formatDay = (day: number): string => {
  const days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'];
  return days[day - 1] || '';
};
const notification = ref({
  show: false,
  title: '',
  message: ''
});
const session = useSessionStore();
const studentId = computed(() => Number(session.id));

// ================================= FUNCTIONS =================================
watch(
  () => props.visible,
  (isOpen) => {
    if (isOpen && alternativeShifts.value.length > 0) {
      selectedShiftId.value = alternativeShifts.value[0].id;
    }
  }
);

watch(selectedShiftId, async (newId) => {
  if (props.visible && newId !== null) {
    try {
      students.value = await getStudentsByShift(newId);
    } catch (error) {
      console.error('Erro ao buscar alunos do turno:', error);
    }
  }
});

function close() {
  emit('close');
}

async function handleSubmit() {
  if (!selectedShiftId.value || !selectedShift.value) return;

  const studentsInShift = await getStudentsByShift(selectedShiftId.value);
  const alreadyInShift = studentsInShift.some(s => s.id === studentId.value);

  if (alreadyInShift) {
    showNotification("Erro", "Já pertence a este turno.");
    return;
  }

  try {
    const now = new Date().toISOString();
    const currentShift = props.currentShiftId;
    const wantedShift = selectedShiftId.value;
    const student = session.id;

    const message = `O aluno ${student} solicitou mudança de turno de ${currentShift} para ${wantedShift}.`;

    await createNotification({
      type: "Change",
      date: now,
      message,
      studentId: Number(student),
      currentShift,
      wantedShift
    } as any);

    showNotification("Solicitação enviada", "O seu pedido foi registado com sucesso.");
    emit('submit', selectedShiftId.value);
  } catch (error) {
    console.error("Erro ao criar notificação:", error);
    showNotification("Erro", "Não foi possível registar o pedido.");
  }
}

function showNotification(title: string, message: string) {
  notification.value = { show: true, title, message };
}

function closeNotification() {
  notification.value.show = false;
}
</script>
