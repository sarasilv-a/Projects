<template>
  <div class="flex h-screen bg-gray-50">
    <Sidebar :userType="'student'" class="sidebar" />
    <div class="flex-1 flex flex-col ml-[200px]">
      <main class="flex-1 p-6 flex flex-col">
        <PageHeader title="Horário" subtitle="Visualização do horário semanal" />

        <ScheduleTable :horas="horas" :diasSemana="diasSemana" :turnos="turnos" @turno-click="handleShiftClick" />

        <ShiftDetailsModal :visible="showDetailsModal" :shift="selectedShift" :subject="selectedSubject"
          @close="closeDetailsModal" @request-change="openChangeModal" />

        <RequestShiftChangeModal :visible="showChangeModal" :currentShiftId="selectedShiftId ?? 0"
          :subjectId="selectedSubject?.id || 0" :shifts="shifts" @close="closeChangeModal"
          @submit="handleShiftChange" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, onMounted, computed } from 'vue';
import Sidebar from '@/components/sidebar/Sidebar.vue';
import PageHeader from '@/components/reusables/PageHeader.vue';
import ScheduleTable from '@/components/students/schedule/ScheduleTable.vue';
import ShiftDetailsModal from '@/components/students/schedule/ShiftDetailsModal.vue';
import RequestShiftChangeModal from '@/components/students/schedule/RequestShiftChange.vue';
import { useSessionStore } from '@/stores/session';
import { getAllSchedules } from '@/api/scheduleAPI';
import { getAllShifts } from '@/api/shiftAPI';
import { getAllSubjects } from '@/api/subjectAPI';
import { createNotification } from '@/api/notificationAPI';
import type { Schedule, Shift, Subject } from '@/types/types';

// ================================= STATE =================================
const session = useSessionStore();
const schedules = ref<Schedule[]>([]);
const shifts = ref<Shift[]>([]);
const subjects = ref<Subject[]>([]);
const horas = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];
const diasSemana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta'];
const turnos = computed(() => {
  return schedules.value.map(s => {
    const shift = shifts.value.find(t => t.id === s.shiftId);
    const subject = subjects.value.find(d => d.id === shift?.subjectId);

    return {
      id: shift?.id || 0,
      dia: getWeekDay(shift?.day || 1),
      hora: parseInt((shift?.start || '0:00').split(':')[0]),
      disciplina: subject?.shortname || 'Disciplina',
      turma: shift?.name || 'TP1',
      start: shift?.start || '00:00',
      end: shift?.end || '00:00'
    };
  });
});
const selectedShiftId = ref<number | null>(null);
const showDetailsModal = ref(false);
const selectedShift = computed(() =>
  shifts.value.find(s => s.id === selectedShiftId.value) || null
);
const selectedSubject = computed(() => {
  const shift = selectedShift.value;
  return subjects.value.find(sub => sub.id === shift?.subjectId) || null;
});
const showChangeModal = ref(false);

// ================================= DATA =================================
onMounted(async () => {
  try {
    const studentId = Number(session.id);

    const allSchedules = await getAllSchedules();
    schedules.value = allSchedules.filter(s => s.studentId === studentId);

    shifts.value = await getAllShifts();
    subjects.value = await getAllSubjects();
  } catch (error) {
    console.error('Error loading schedule data:', error);
  }
});

// ================================= FUNCTIONS =================================
function getWeekDay(dia: number): string {
  return ['segunda', 'terca', 'quarta', 'quinta', 'sexta'][dia - 1];
}

function handleShiftClick(id: number) {
  selectedShiftId.value = id;
  showDetailsModal.value = true;
}

function closeDetailsModal() {
  selectedShiftId.value = null;
  showDetailsModal.value = false;
}

function openChangeModal() {
  showChangeModal.value = true;
}

function closeChangeModal() {
  showChangeModal.value = false;
}

function handleShiftChange(newShiftId: number) {
  if (!selectedShift.value) {
    console.error('No shift selected.');
    return;
  }

  const notification = {
    type: 'Change' as const,
    date: new Date().toISOString().split('T')[0],
    message: 'Gostava de trocar de turno.',
    studentId: Number(session.id),
    currentShift: selectedShift.value.id,
    wantedShift: newShiftId,
  };

  createNotification(notification)
    .then(() => {
      console.log('Success creating notification!');
    })
    .catch((error) => {
      console.error('Error creating notification:', error);
    });

  showChangeModal.value = false;
}
</script>
