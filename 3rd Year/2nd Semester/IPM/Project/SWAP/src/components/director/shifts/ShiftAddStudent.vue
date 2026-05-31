<template>
    <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
        <div class="bg-white rounded-lg shadow-lg w-full max-w-2xl overflow-hidden">

            <div class="p-6">
                <!-- Header -->
                <div class="flex justify-between items-start border-b border-gray-200">
                    <div>
                        <h2 class="text-2xl font-bold text-[#020B80]">Alocar Aluno - {{ shiftName }}</h2>
                        <p class="text-gray-700 mt-2">Pesquise e selecione o aluno a alocar.</p>
                    </div>
                    <button @click="closePopup" class="text-2xl text-[#020B80] -mt-1">×</button>
                </div>
                <div class="relative w-full max-w-xs mt-6 mb-6" >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
                        class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#020B80] fill-current">
                        <path d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/>
                    </svg>
                    <input
                    type="text"
                    v-model="searchQuery"
                    placeholder="Pesquisar alunos..."
                    class="w-full pl-9 pr-3 py-2 border border-[#020B80]/50 rounded-md text-sm placeholder-[#020B80]/60" />
                </div>
                <!-- Tabela -->
                <div class="max-h-[300px] overflow-y-auto border-b border-[#020B80]">
                <table class="min-w-full divide-y divide-[#020B80]/50">
                    <thead>
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Número</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Nome</th>
                        </tr>
                    </thead>
                        <tbody class="bg-white divide-y divide-[#020B80]/50">
                            <tr
                                v-for="student in filteredStudents"
                                :key="student.id"
                                class="hover:bg-gray-50 cursor-pointer"
                                :class="{ 'bg-blue-50': selectedStudent?.id === student.id}"
                                @click="selectStudent(student)"
                            >
                                <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ student.number }}</td>
                                <td class="px-6 py-4 text-sm text-gray-900">{{ student.name }}</td>
                            </tr>
                            <tr v-if="filteredStudents.length === 0">
                                <td colspan="2" class="px-6 py-4 text-center text-sm text-gray-500">Nenhum aluno encontrado</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="text-right mt-4">
                <button
                    @click="addStudent"
                    class="bg-[#020B80] text-white px-5 py-2 rounded"
                >
                    Alocar
                </button>
                </div>
            </div>
        </div>  
    </div>
</template>
  
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';

const props = defineProps<{
    isOpen: boolean;
    shiftId: number;
    shiftName: string;
    students: Array<{ id: number; name: string; number: string}>;
}>();

const emit = defineEmits(['close', 'add-student'])
const searchQuery = ref('')
const selectedStudent = ref<{ id: number; name: string } | null>(null);

const filteredStudents = computed(() => {
    if (!searchQuery.value) return props.students
    const query = searchQuery.value.toLowerCase()
    return props.students.filter(student =>
        String(student.number).includes(query) ||
        student.name.toLowerCase().includes(query)
    )
})

function selectStudent(student: { id: number; name: string }) {
    if (selectedStudent.value?.id === student.id) {
        selectedStudent.value = null;
    } else {
        selectedStudent.value = student;
    }
}

function closePopup() {
    emit('close')
}

function addStudent() {
    if (selectedStudent.value) {
        emit('add-student', {
            shiftId: props.shiftId,
            studentId: selectedStudent.value.id,
        });
    }
    else {
        alert('Por favor selecione um aluno antes de continuar.');
        return;
    } 
}

// reset
watch(() => props.isOpen, (open) => {
    if (!open) {
        searchQuery.value = '';
        selectedStudent.value = null;
    }
});

</script>
  