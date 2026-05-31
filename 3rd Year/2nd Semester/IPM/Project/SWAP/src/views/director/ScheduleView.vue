<template>
  <div class="flex min-h-screen overflow-scroll bg-gray-50">
    <Sidebar :userType="'director'" />
    <div class="flex-1 flex flex-col overflow-hidden ml-[200px]">
      <main class="flex-1 p-6 flex flex-col">
        <PageHeader title="Horários" subtitle="Gestão de horários" />
        <ScheduleToolbar :selectedYear="selectedYear" @update:selectedYear="(val: number) => selectedYear = val"
          @generate="handleGenerate" @publish="handlePublish" />
        <ScheduleTable :horas="horas" :diasSemana="diasSemana" :turnos="turnosFiltrados" @show-all="handleShowAll" />
        <ShiftOverlay v-if="overlayVisible" :dia="overlayDia" :hora="overlayHora" :turnos="overlayTurnos"
          @ver-turno="handleVerTurno" @close="closeOverlay" />
        <ShiftDetailsOverlay v-if="turnoSelecionado" :turno="turnoSelecionado" @close="closeTurnoOverlay" />
        <GenerateConfirmationModal v-if="showGenerateModal" :numAlunos="alunosPorAlocar"
          @close="showGenerateModal = false" @defer="showGenerateModal = false" @resolve="handleResolverAgora" />
        <Notification :show="showNotification" :title="notificationTitle" :message="notificationMessage"
          @close="showNotification = false" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import Sidebar from '@/components/sidebar/Sidebar.vue';
import PageHeader from '@/components/reusables/PageHeader.vue';
import ScheduleToolbar from '@/components/director/schedule/ScheduleToolbar.vue';
import ScheduleTable from '@/components/director/schedule/ScheduleTable.vue';
import ShiftOverlay from '@/components/director/schedule/ShiftOverlay.vue';
import GenerateConfirmationModal from '@/components/director/schedule/GenerateConfirmationModal.vue';
import Notification from '@/components/reusables/Notification.vue';
import ShiftDetailsOverlay from '@/components/director/schedule/ShiftDetailsOverlay.vue';
import { getAllSubjects } from '@/api/subjectAPI';
import { getAllShifts } from '@/api/shiftAPI';
import type { Subject, Shift } from '@/types/types';

// ================================= STATE =================================
const selectedYear = ref(1);
const subjects = ref<Subject[]>([]);
const shifts = ref<Shift[]>([]);
const router = useRouter();
const horas = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];
const diasSemana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta'];
const turnosFiltrados = computed(() => {
  return shifts.value
    .map((shift) => {
      const subject = subjects.value.find(s => s.id === shift.subjectId);
      return {
        id: shift.id,
        dia: diasSemana[shift.day - 1],
        hora: parseInt(shift.start.split(':')[0]),
        disciplina: subject?.shortname || 'Disciplina',
        turma: shift.name,
        year: subject?.year || 1
      };
    })
    .filter(t => t.year === selectedYear.value);
});
const overlayVisible = ref(false);
const overlayDia = ref('');
const overlayHora = ref(0);
const overlayTurnos = ref<typeof turnosFiltrados.value>([]);
const showGenerateModal = ref(false);
const alunosPorAlocar = ref(3);
const showNotification = ref(false);
const notificationTitle = ref('');
const notificationMessage = ref('');
const turnoSelecionado = ref<any | null>(null);

// ================================= DATA =================================
onMounted(async () => {
  subjects.value = await getAllSubjects();
  shifts.value = await getAllShifts();
});

// ================================= FUNCTIONS =================================
function handleShowAll({ dia, hora }: { dia: string, hora: number }) {
  overlayDia.value = dia;
  overlayHora.value = hora;
  overlayVisible.value = true;

  overlayTurnos.value = turnosFiltrados.value.filter(t => t.dia === dia && t.hora === hora);
}

function closeOverlay() {
  overlayVisible.value = false;
}

function handleGenerate() {
  alunosPorAlocar.value = 3;
  showGenerateModal.value = true;
}

function handleResolverAgora() {
  showGenerateModal.value = false;
  router.push('/director/manualAlloc');
}

function handlePublish() {
  console.log("🚀 Publicar horários...");

  notificationTitle.value = 'Horários publicados com sucesso';
  notificationMessage.value = '';
  showNotification.value = true;

  setTimeout(() => showNotification.value = false, 3000);
}

function handleVerTurno(turnoId: number) {
  const turno = shifts.value.find(t => t.id === turnoId);
  if (turno) {
    turnoSelecionado.value = turno;
  }
}

function closeTurnoOverlay() {
  turnoSelecionado.value = null;
}
</script>
