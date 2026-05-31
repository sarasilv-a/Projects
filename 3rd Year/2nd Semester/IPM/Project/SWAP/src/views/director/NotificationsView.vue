<!-- NotificationsView.vue -->
<template>
    <div class="flex min-h-screen bg-gray-50">
        <Sidebar :userType="'director'" />
        <div class="flex-1 flex flex-col overflow-hidden ml-[200px]">
            <PageHeader title="Notificações" subtitle="Gestão de notificações e pedidos de alunos" class="p-4 pb-2" />
            <div class="flex flex-1 gap-4 p-4 pt-0 ">
                <NotificationList :notificacoes="notificacoes" :selected="selectedNotificacao"
                    :getStudentName="getStudentName" :getSubjectName="getSubjectName" :getShiftName="getShiftName"
                    @select="selectedNotificacao = $event" />
                <NotificationDetail :notificacoes="notificacoes" :selectedNotificacao="selectedNotificacao"
                    :turnos="shifts" :getStudentName="getStudentName" :getSubjectName="getSubjectName"
                    @update-turno="selecionarTurnoPretendido" @aprovar="aprovarMudanca" @rejeitar="rejeitarMudanca" />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, onMounted } from 'vue';
import { getAllNotifications } from '@/api/notificationAPI';
import { getAllShifts } from '@/api/shiftAPI';
import { getStudents } from '@/api/studentAPI';
import { getAllSubjects } from '@/api/subjectAPI';
import type { Notification, Student, Subject, Shift } from '@/types/types';
import { updateSchedule } from '@/api/scheduleAPI';
import { deleteNotification } from '@/api/notificationAPI';
import { getScheduleByStudent } from '@/api/scheduleAPI';
import Sidebar from '@/components/sidebar/Sidebar.vue';
import PageHeader from '@/components/reusables/PageHeader.vue';
import NotificationList from '@/components/director/notifications/NotificationList.vue';
import NotificationDetail from '@/components/director/notifications/NotificationDetail.vue';

// ================================= STATE =================================
const notificacoes = ref<Notification[]>([]);
const students = ref<Student[]>([]);
const subjects = ref<Subject[]>([]);
const shifts = ref<Shift[]>([]);
const selectedNotificacao = ref<number | null>(null);

// ================================= DATA =================================
onMounted(async () => {
    notificacoes.value = await getAllNotifications();
    students.value = await getStudents();
    subjects.value = await getAllSubjects();
    shifts.value = await getAllShifts();
});

// ================================= FUNCTIONS =================================
async function aprovarMudanca(studentId: number, wantedShift: number, notificationId: number) {
    const schedules = await getScheduleByStudent(studentId);
    const currentSchedule = schedules.find(s => s.studentId === studentId);

    if (!currentSchedule) {
        console.error("Horário não encontrado para o aluno");
        return;
    }

    const updatedSchedule = {
        ...currentSchedule,
        shiftId: wantedShift,
    };

    await updateSchedule(currentSchedule.id, updatedSchedule);
    await deleteNotification(notificationId);
    notificacoes.value = notificacoes.value.filter(n => n.id !== notificationId);
    selectedNotificacao.value = null;
}

async function rejeitarMudanca(notificationId: number) {
    await deleteNotification(notificationId);
    notificacoes.value = notificacoes.value.filter(n => n.id !== notificationId);
    selectedNotificacao.value = null;
}

function getStudentName(id: number): string {
    return students.value.find((s) => s.id === id)?.name || 'Desconhecido';
}

function getSubjectName(shiftId: number): string {
    const shift = shifts.value.find((s) => s.id === shiftId);
    if (!shift) return 'Desconhecida';
    return subjects.value.find((subj) => subj.id === shift.subjectId)?.name || 'Desconhecida';
}

function getShiftName(id: number): string {
    return shifts.value.find((s) => s.id === id)?.name || 'Desconhecido';
}

function selecionarTurnoPretendido(turnoId: number) {
    if (selectedNotificacao.value === null) return;
    const not = notificacoes.value[selectedNotificacao.value];
    if (not.type === 'Change') {
        not.wantedShift = turnoId;
    }
}
</script>
