<template>
  <div class="flex h-screen overflow-hidden bg-gray-50">
    <Sidebar :userType="'director'" />
    <div class="flex-1 flex flex-col overflow-hidden ml-[200px]">
      <main class="flex-1 overflow-y-auto p-6">
        <PageHeader title="Dashboard" subtitle="Visão geral da alocação de turnos para o semestre atual" />
        <StatsCards :totalStudents="totalStudents" :allocatedStudents="allocatedStudents"
          :allocatedPercentage="allocatedPercentage" :totalShifts="totalShifts" :averageOccupancy="averageOccupancy" />
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 space-y-6">
            <ShiftOccupancy :subjects="subjects" :shifts="shifts" :schedules="schedules" />
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <QuickActions @action-click="handleActionClick" />
              <Notification :show="showNotification" title="Sucesso" message="Horários publicados com sucesso"
                @close="showNotification = false" />
              <UpcomingEvents :events="upcomingEvents" />
            </div>
          </div>
          <div>
            <RecentNotifications :notifications="adaptedNotifications" @view-all="viewAllNotifications" />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, onMounted, computed } from 'vue';
import Sidebar from '@/components/sidebar/Sidebar.vue';
import PageHeader from '@/components/reusables/PageHeader.vue';
import StatsCards from '@/components/director/dashboard/StatsCards.vue';
import ShiftOccupancy from '@/components/director/dashboard/ShiftOccupancy.vue';
import UpcomingEvents from '@/components/director/dashboard/UpcomingEvents.vue';
import RecentNotifications from '@/components/director/dashboard/RecentNotifications.vue';
import QuickActions from '@/components/director/dashboard/QuickActions.vue';
import Notification from '@/components/reusables/Notification.vue';
import { getStudents } from '@/api/studentAPI';
import { getAllEnrollments } from '@/api/enrollmentAPI';
import { getAllSubjects } from '@/api/subjectAPI';
import { getAllShifts } from '@/api/shiftAPI';
import { getAllNotifications } from '@/api/notificationAPI';
import { getAllSchedules } from '@/api/scheduleAPI';
import type { Student, Subject, Enrollment, Shift, Notification as Notif, Schedule } from '@/types/types';
import { useRouter } from 'vue-router'

// ================================= STATE =================================
const students = ref<Student[]>([]);
const subjects = ref<Subject[]>([]);
const shifts = ref<Shift[]>([]);
const enrollments = ref<Enrollment[]>([]);
const notifications = ref<Notif[]>([]);
const schedules = ref<Schedule[]>([]);
const upcomingEvents = ref([
  {
    id: 1,
    title: 'Apresentação de Projetos Finais',
    date: '2025-04-28',
    location: 'Auditório B1'
  },
  {
    id: 2,
    title: 'Reunião de Diretores de Curso',
    date: '2025-05-05',
    location: 'Sala 201'
  }
]);
const totalStudents = computed(() => students.value.length);
const totalSubjects = computed(() => subjects.value.length);
const totalShifts = computed(() => shifts.value.length);
const totalEnrollments = computed(() => enrollments.value.length);
const recentNotifications = computed(() =>
  notifications.value
    .filter((n: any) => n.type === 'Change' || n.type === 'Deadline')
    .sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 4)
);
const allocatedStudents = computed(() => {
  const uniqueStudentIds = new Set(schedules.value.map(s => s.studentId));
  return uniqueStudentIds.size;
});
const allocatedPercentage = computed(() => {
  return totalStudents.value > 0
    ? Math.round((allocatedStudents.value / totalStudents.value) * 100)
    : 0;
});
const averageOccupancy = computed(() => {
  if (shifts.value.length === 0) return 0;

  const shiftCounts = shifts.value.map(shift =>
    schedules.value.filter(s => s.shiftId === shift.id).length
  );

  const total = shiftCounts.reduce((sum, count) => sum + count, 0);
  return Math.round(total / shifts.value.length);
});
const router = useRouter()
const showNotification = ref(false)

// ================================= DATA =================================
onMounted(async () => {
  try {
    students.value = await getStudents();
    subjects.value = await getAllSubjects();
    shifts.value = await getAllShifts();
    enrollments.value = await getAllEnrollments();
    notifications.value = await getAllNotifications();
    schedules.value = await getAllSchedules();
  } catch (err) {
    console.error('Erro ao carregar dados do dashboard:', err);
  }
});

// ================================= FUNCTIONS =================================
const handleActionClick = (actionId: string) => {
  if (actionId === 'view-schedule') {
    router.push('/director/schedule')
  } else if (actionId === 'manage-students') {
    router.push('/director/manualAlloc')
  } else if (actionId === 'publish-schedule') {
    showNotification.value = true
    setTimeout(() => {
      showNotification.value = false
    }, 3000)
  }
}

const viewAllNotifications = () => {
  console.log('Ver todas as notificações');
};

const adaptedNotifications = computed(() =>
  notifications.value.map(n => {
    if (n.type === "Change") {
      const student = students.value.find(s => s.id === n.studentId);
      return {
        id: n.id,
        tipo: "mudanca",
        data: n.date,
        aluno: student?.name ?? "Desconhecido",
        turnoAtual: `#${n.currentShift}`,
        turnoDesejado: `#${n.wantedShift}`,
      };
    } else {
      return {
        id: n.id,
        tipo: "deadline",
        data: n.date,
        titulo: "Prazo importante",
        descricao: n.message,
      };
    }
  })
);
</script>
