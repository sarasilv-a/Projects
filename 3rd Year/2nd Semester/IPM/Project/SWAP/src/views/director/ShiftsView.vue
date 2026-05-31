<template>
    <div class="flex min-h-screen bg-[#f5f5f5]">
        <Sidebar :userType="userType" class="w-[200px] fixed left-0 top-0 bottom-0 z-10" />
        <div class="flex-1 ml-[200px] p-6">
            <PageHeader title="Turnos" subtitle="Gestão de turnos e respectivas alocações" class="mb-8" />
            <ShiftFilters :selectedYear="selectedYear" :selectedSubjectId="selectedSubjectId"
                :filteredSubjects="filteredSubjects" @update:selectedYear="selectedYear = $event"
                @update:selectedSubjectId="selectedSubjectId = $event" />
            <ShiftTable :shifts="filteredShifts" @open-students="openStudentPopup" @change-room="openChangeRoomPopup"/>
            <ShiftStudents :isOpen="showStudentPopup" 
            :shift="selectedShiftInfo ?? undefined" :students="popupStudents" 
            @add="openAddStudentPopup" @close="showStudentPopup = false" 
            @request-delete="onDeleteRequest" @request-delete-all="onDeleteAllRequest"/>
            <ShiftChangeRoom :isOpen="showRoomPopup" :shift="selectedRoomShift" @close="showRoomPopup = false" @change-room="handleRoomChange"/>
            <SuccessRoomModal v-if="showSuccessRoomPopup" @close="showSuccessRoomPopup = false"/>
            <ShiftAddStudent :isOpen = "showStudentAddPopup" :shiftId="selectedAddShiftId!" :shiftName="selectedAddShiftName!" :students="shiftAddCandidates" @close="showStudentAddPopup = false" @add-student="handleStudentAdd"/>
            <SuccessStudentModal v-if="showSuccessStudentPopup" @close="showSuccessStudentPopup = false" />
            <ConfirmDeleteModal v-if="showConfirmDeleteModal" @confirm="confirmDeleteStudent" @cancel="showConfirmDeleteModal = false" />
            <ConfirmDeleteAllModal v-if="showConfirmDeleteAll" @confirm="confirmDeleteAll" @cancel="showConfirmDeleteAll = false" />
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, computed, onMounted, watch } from 'vue';
import Sidebar from '@/components/sidebar/Sidebar.vue';
import ShiftStudents from '@/components/director/shifts/ShiftStudents.vue';
import PageHeader from '@/components/reusables/PageHeader.vue';
import ShiftFilters from '@/components/director/shifts/ShiftFilters.vue'
import ShiftTable from '@/components/director/shifts/ShiftTable.vue'
import ShiftChangeRoom from '@/components/director/shifts/ShiftChangeRoom.vue'
import ShiftAddStudent from '@/components/director/shifts/ShiftAddStudent.vue'
import { getAllShifts, getShiftById, updateShift} from '@/api/shiftAPI';
import { getAllSubjects } from '@/api/subjectAPI';
import { getAllSchedules , getSchedulesByShift, deleteSchedule, createSchedule} from '@/api/scheduleAPI';
import { getStudentsByShift, getStudentsWithEnrollments } from '@/api/studentAPI';
import type { Shift, Subject, Schedule, Student } from '@/types/types';
import SuccessRoomModal from '@/components/director/shifts/SuccessRoomModal.vue';
import SuccessStudentModal from '@/components/director/shifts/SuccessStudentModal.vue';
import ConfirmDeleteModal from '@/components/director/shifts/ConfirmDeleteModal.vue'
import ConfirmDeleteAllModal from '@/components/director/shifts/ConfirmDeleteAllModal.vue'
// ================================= STATE =================================

interface ShiftInfo {
    id: number;
    name: string;
    building: string;
    room: string;
    limit: number;
}

const userType = ref('director');
const selectedYear = ref(1);
const selectedSubjectId = ref<number | null>(null);
const showStudentPopup = ref(false);
const popupStudents = ref<Student[]>([]);
const shifts = ref<Shift[]>([]);
const subjects = ref<Subject[]>([]);
const schedules = ref<Schedule[]>([]);
const shiftOccupancy = computed(() => {
    const counts: Record<number, number> = {};
    schedules.value.forEach(s => {
        counts[s.shiftId] = (counts[s.shiftId] || 0) + 1;
    });
    return counts;
});
const filteredSubjects = computed(() =>
    subjects.value.filter(s => s.year === selectedYear.value)
);
const filteredShifts = computed(() =>
    shifts.value
        .filter(shift => shift.subjectId === selectedSubjectId.value)
        .map(shift => {
            const current = shiftOccupancy.value[shift.id] || 0;
            const occupation = Math.round((current / shift.limit) * 100);
            return {
                id: shift.id,
                name: shift.name,
                currentCapacity: current,
                maxCapacity: shift.limit,
                occupation,
                day: getDayName(shift.day),
                time: `${shift.start}–${shift.end}`,
                building: shift.building,
                room: shift.room
            };
        })
);

const selectedShiftInfo = ref<{ id: number, name: string, subjectName: string } | null>(null);

const showRoomPopup = ref(false);
const selectedRoomShift = ref<ShiftInfo | null>(null)
const showSuccessRoomPopup = ref(false);

const showStudentAddPopup = ref(false)
const selectedAddShiftId = ref<number | null>(null);
const selectedAddShiftName = ref<string | null>(null);
const shiftAddCandidates = ref<Student[]>([]);

const showSuccessStudentPopup = ref(false);

const showConfirmDeleteModal = ref(false);
const pendingDeleteStudent = ref<{ studentId: number; shiftId: number } | null>(null);

const showConfirmDeleteAll = ref(false)
const pendingDeleteAllShiftId = ref<number | null>(null);

// ================================= DATA =================================
onMounted(async () => {
    subjects.value = await getAllSubjects();
    shifts.value = await getAllShifts();
    schedules.value = await getAllSchedules();

    const defaultSubject = subjects.value.find(s => s.year === selectedYear.value);
    if (defaultSubject) selectedSubjectId.value = defaultSubject.id;
});

// ================================= FUNCTIONS =================================
function getDayName(day: number): string {
    const map = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'];
    return map[day - 1] || '';
}

function getCapacityClass(current: number, max: number): string {
    if (!current || !max || isNaN(current) || isNaN(max)) return 'unknown';
    if (current === max) return 'full';
    if (current / max >= 0.7) return 'almost-full';
    return 'available';
}

watch(selectedYear, (newYear) => {
    const currentSubjects = filteredSubjects.value;

    if (newYear === 2) {
        const algc = currentSubjects.find((s) => s.shortname.toLowerCase().includes('algc'));
        selectedSubjectId.value = algc ? algc.id : currentSubjects[0]?.id ?? null;
    } else if (newYear === 3) {
        const cp = currentSubjects.find((s) => s.shortname.toLowerCase().includes('cp'));
        selectedSubjectId.value = cp ? cp.id : currentSubjects[0]?.id ?? null;
    } else {
        selectedSubjectId.value = currentSubjects[0]?.id ?? null;
    }
});

async function openStudentPopup(shiftId: number) {
    const shift = shifts.value.find(s => s.id === shiftId);
    if (!shift) return;

    const subject = subjects.value.find(sub => sub.id === shift.subjectId);
    showStudentPopup.value = true;
    popupStudents.value = await getStudentsByShift(shiftId);
    selectedShiftInfo.value = {
        id: shift.id,
        name: shift.name,
        subjectName: subject?.name ?? 'Disciplina'
    };
}

function openChangeRoomPopup(shiftId: number) {
    const shift = shifts.value.find(s => s.id === shiftId);
    if (!shift) return;

    selectedRoomShift.value = {
        id: shift.id,
        name: shift.name,
        building: shift.building,
        room: shift.room,
        limit: shift.limit
    }
    showRoomPopup.value = true;
}

async function openAddStudentPopup({ shiftId }: { shiftId: number }) {
    const shift = shifts.value.find(s => s.id === shiftId);
    if (!shift) return;

    const allStudents = await getStudentsWithEnrollments(shift.subjectId);
    const currentStudents = await getStudentsByShift(shiftId);

    const currentIds = new Set(currentStudents.map(s => s.id));
    const availableStudents = allStudents.filter(s => !currentIds.has(s.id));

    shiftAddCandidates.value = availableStudents;
    selectedAddShiftId.value = shift.id;
    selectedAddShiftName.value = shift.name;
    showStudentAddPopup.value = true;
}

function onDeleteRequest(payload: { studentId: number; shiftId: number }) {
  pendingDeleteStudent.value = payload;
  showConfirmDeleteModal.value = true;
}

async function confirmDeleteStudent() {
  if (!pendingDeleteStudent.value) return;

  await handleDeleteStudent(pendingDeleteStudent.value);

  showConfirmDeleteModal.value = false;
  pendingDeleteStudent.value = null;
}

async function handleDeleteStudent({ studentId, shiftId }: { studentId: number, shiftId: number }) {
    const shiftSchedules = await getSchedulesByShift(shiftId);
    const match = shiftSchedules.find(s => s.studentId === studentId);

    if (match) {
        await deleteSchedule(match.id);
        schedules.value = await getAllSchedules();
        if (selectedShiftInfo.value?.id === shiftId) {
            const updated = await getStudentsByShift(shiftId);
            popupStudents.value = updated;
        }
    }
}

function onDeleteAllRequest(shiftId: number) {
  pendingDeleteAllShiftId.value = shiftId;
  showConfirmDeleteAll.value = true;
}

async function confirmDeleteAll() {
  const shiftId = pendingDeleteAllShiftId.value;
  if (shiftId === null) return;

  const shiftSchedules = await getSchedulesByShift(shiftId);
  const deletions = shiftSchedules.map(s => deleteSchedule(s.id));
  await Promise.all(deletions);

  schedules.value = await getAllSchedules();

  if (selectedShiftInfo.value?.id === shiftId) {
    popupStudents.value = await getStudentsByShift(shiftId);
  }

  showConfirmDeleteAll.value = false;
  pendingDeleteAllShiftId.value = null;
}

async function handleRoomChange({ shiftId, newBuilding, newRoom , newLimit}: { shiftId: number, newBuilding: string, newRoom: string, newLimit : number }) {
    const originalShift = shifts.value.find(s => s.id === shiftId);
    if (!originalShift) return;

    const updated = await updateShift(shiftId, {
        ...originalShift,
        building: newBuilding,
        room: newRoom,
        limit: newLimit
    });

    const index = shifts.value.findIndex(s => s.id === shiftId);
    if (index !== -1) {
        shifts.value[index] = updated;
    }

    showRoomPopup.value = false;
    showSuccessRoomPopup.value = true;
}

async function handleStudentAdd({ shiftId, studentId }: { shiftId: number, studentId: number }) {
    const allSchedules = await getAllSchedules();
    await createSchedule({
        studentId,
        shiftId
    });

    schedules.value = await getAllSchedules();
    showStudentAddPopup.value = false;
    showSuccessStudentPopup.value = true;

    if (selectedShiftInfo.value?.id === shiftId) {
        popupStudents.value = await getStudentsByShift(shiftId);
    }
}

</script>
