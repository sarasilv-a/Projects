<template>
    <div class="flex min-h-screen bg-[D9D9D9]">
        <Sidebar :userType="'director'" />>
        <div class="flex-1 ml-[200px] p-6">
            <PageHeader title="Alunos" subtitle="Gestão de alunos e inscrições em disciplinas" />
            <ButtonZone searchPlaceholder="Pesquisar alunos..." @search="handleSearch" @add="showAddModal = true"
                @import="fileInput?.click()" @export="exportStudents" @delete-all="showDeleteAllModal = true" />
            <input ref="fileInput" type="file" accept="application/json" @change="handleFileUpload" class="hidden" />
            <StudentsTable :students="filteredStudents" :subjects="subjects" :enrollments="enrollments"
                @edit="editStudent" @delete="deleteStudent" />
        </div>
        <StudentModal v-if="showAddModal" :student="editingStudent" :subjects="subjects" :enrollments="enrollments"
            :errors="errors" @close="closeModal" @save="saveStudent" />
        <DeleteConfirmation v-if="showDeleteModal" @cancel="showDeleteModal = false" @confirm="confirmDelete" />
        <DeleteAllConfirmation v-if="showDeleteAllModal" @cancel="showDeleteAllModal = false"
            @confirm="confirmDeleteAll" />
        <Notification :show="notification.show" :title="notification.title" :message="notification.message"
            @close="closeNotification" />
    </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, computed, onMounted } from 'vue';
import Sidebar from '@/components/sidebar/Sidebar.vue';
import PageHeader from '@/components/reusables/PageHeader.vue';
import ButtonZone from '@/components/director/students/ButtonZone.vue';
import StudentsTable from '@/components/director/students/StudentsTable.vue';
import StudentModal from '@/components/director/students/StudentModal.vue';
import DeleteConfirmation from '@/components/director/students/DeleteConfirmation.vue';
import DeleteAllConfirmation from '@/components/director/students/DeleteAllConfirmation.vue';
import Notification from '@/components/reusables/Notification.vue';
import type { Student, Subject, Enrollment } from '@/types/types';
import * as studentAPI from '@/api/studentAPI';
import * as subjectAPI from '@/api/subjectAPI';
import * as enrollmentAPI from '@/api/enrollmentAPI';
import * as scheduleAPI from '@/api/scheduleAPI';

// ================================= STATE =================================
const students = ref<Student[]>([]);
const subjects = ref<Subject[]>([]);
const enrollments = ref<Enrollment[]>([]);
const searchQuery = ref('');
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showDeleteAllModal = ref(false);
const editingStudent = ref<Student | undefined>(undefined);
const studentToDelete = ref<Student | undefined>(undefined);
const fileInput = ref<HTMLInputElement | null>(null);
const errors = ref<Record<string, string>>({});
const notification = ref({ show: false, title: '', message: '' });
const filteredStudents = computed(() => {
    if (!searchQuery.value) return students.value;
    const query = searchQuery.value.toLowerCase();
    return students.value.filter(student =>
        student.number.toLowerCase().includes(query) ||
        student.name.toLowerCase().includes(query) ||
        student.email.toLowerCase().includes(query)
    );
});

// ================================= DATA =================================
onMounted(async () => loadData());

// ================================= FUNCTIONS =================================
const loadData = async () => {
    try {
        students.value = await studentAPI.getStudents();
        subjects.value = await subjectAPI.getAllSubjects();
        enrollments.value = await enrollmentAPI.getAllEnrollments();
    } catch (error) {
        showNotification('Erro ao carregar dados', 'Não foi possível carregar os dados dos alunos.');
        console.error(error);
    }
};

const handleSearch = (query: string) => {
    searchQuery.value = query;
};

const editStudent = (student: Student) => {
    editingStudent.value = { ...student };
    showAddModal.value = true;
};

const deleteStudent = (student: Student) => {
    studentToDelete.value = student;
    showDeleteModal.value = true;
};

const confirmDelete = async () => {
    if (!studentToDelete.value) return;
    try {
        const studentId = studentToDelete.value.id;
        const schedules = (await scheduleAPI.getAllSchedules()).filter(s => s.studentId === studentId);
        await Promise.all(schedules.map(s => scheduleAPI.deleteSchedule(s.id)));

        const studentEnrollments = enrollments.value.filter(e => e.studentId === studentId);
        await Promise.all(studentEnrollments.map(e => enrollmentAPI.deleteEnrollment(e.id)));

        await studentAPI.deleteStudent(studentId);
        await loadData();

        showNotification('Aluno removido', 'O aluno foi removido com sucesso.');
    } catch (err) {
        console.error(err);
        showNotification('Erro', 'Ocorreu um erro ao remover o aluno.');
    }
    showDeleteModal.value = false;
    studentToDelete.value = undefined;
};

const confirmDeleteAll = async () => {
    try {
        await Promise.all(enrollments.value.map(e => enrollmentAPI.deleteEnrollment(e.id)));
        await Promise.all(students.value.map(s => studentAPI.deleteStudent(s.id)));
        await loadData();
        showNotification('Alunos removidos', 'Todos os alunos foram removidos com sucesso.');
    } catch (err) {
        console.error(err);
        showNotification('Erro', 'Erro ao apagar todos os alunos.');
    }
    showDeleteAllModal.value = false;
};

const closeModal = () => {
    showAddModal.value = false;
    editingStudent.value = undefined;
    errors.value = {};
};

const saveStudent = async (data: { student: Partial<Student>, enrollments: number[] }) => {
    errors.value = {};

    if (!data?.student?.number) errors.value.number = 'O número do aluno é obrigatório';
    if (!data?.student?.name) errors.value.name = 'O nome do aluno é obrigatório';
    if (!data?.student?.email) errors.value.email = 'O email do aluno é obrigatório';
    if (Object.keys(errors.value).length > 0) return;

    try {
        let studentId: number;
        if (editingStudent.value) {
            const updated = await studentAPI.updateStudent(editingStudent.value.id!, data.student);
            studentId = updated.id;
            const oldEnrollments = enrollments.value.filter(e => e.studentId === studentId);
            await Promise.all(oldEnrollments.map(e => enrollmentAPI.deleteEnrollment(e.id)));
        } else {
            const created = await studentAPI.createStudent({
                ...data.student,
                password: 'password123',
                status: 'Ativo'
            } as Omit<Student, 'id'>);
            studentId = created.id;
        }

        await Promise.all(data.enrollments.map(subjectId => enrollmentAPI.createEnrollment({ studentId, subjectId })));
        await loadData();
        showNotification(
            editingStudent.value ? 'Aluno atualizado' : 'Aluno adicionado',
            editingStudent.value ? 'Dados atualizados com sucesso.' : 'Aluno criado com sucesso.'
        );
        closeModal();
    } catch (err) {
        console.error(err);
        showNotification('Erro', 'Ocorreu um erro ao guardar os dados.');
    }
};

const handleFileUpload = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
        try {
            const data = JSON.parse(e.target?.result as string);
            if (data.students) students.value = data.students;
            if (data.enrollments) enrollments.value = data.enrollments;
            showNotification('Importação concluída', 'Os dados foram importados com sucesso.');
        } catch {
            showNotification('Erro na importação', 'O arquivo não está no formato correto.');
        }
    };
    reader.readAsText(file);
    if (fileInput.value) fileInput.value.value = '';
};

const exportStudents = () => {
    const data = {
        students: students.value,
        enrollments: enrollments.value
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'alunos.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showNotification('Exportação concluída', 'Os dados foram exportados com sucesso.');
};

const showNotification = (title: string, message: string = '') => {
    notification.value = { show: true, title, message };
    setTimeout(() => closeNotification(), 3000);
};

const closeNotification = () => {
    notification.value.show = false;
};
</script>
