<template>
  <div class="flex min-h-screen bg-gray-100 font-sans">
    <Sidebar :userType="'director'" />
    <div class="flex-1 p-6 ml-[200px]">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-[#020B80]">Alocação manual</h1>
        <p class="text-[#020B80]/60">Distribuição manual dos alunos aos turnos disponíveis</p>
      </div>
      <div class="flex flex-col gap-6">
        <div class="flex gap-6">
          <div class="flex flex-col bg-white rounded-lg shadow p-4 flex-1 border border-[#020b80]/50">
            <h2 class="text-lg font-bold text-[#020b80] mb-4">Lista de Alunos Pendentes</h2>
            <div class="flex gap-2 mb-4">
              <div class="flex items-center bg-gray-100 rounded px-3 flex-1 border border-[#020b80]/50">
                <span class="mr-2 text-gray-500">🔍</span>
                <input type="text" v-model="searchQuery" placeholder="Pesquisar aluno..."
                  class="w-full bg-transparent border-0 outline-none py-2 text-sm" />
              </div>
              <button class="border border-gray-300 rounded px-4 py-2 text-sm">Filter By</button>
            </div>
            <div class="overflow-y-auto max-h-[300px]">
              <div v-for="student in filteredStudents" :key="student.id" @click="selectStudent(student)"
                class="p-3 rounded cursor-pointer transition hover:bg-gray-200"
                :class="{ 'bg-blue-100': selectedStudent && selectedStudent.id === student.id }">
                <div class="font-medium text-gray-800">{{ student.name }}</div>
                <div class="text-xs text-gray-500">{{ student.id }}</div>
              </div>
            </div>
          </div>
          <div v-if="selectedStudent" class="flex flex-col bg-white rounded-lg shadow p-4 flex-1">
            <h2 class="text-lg font-bold text-[#1a237e] mb-4">Detalhes do aluno</h2>
            <div class="py-2">
              <h3 class="text-xl font-semibold text-gray-800">{{ selectedStudent.name }}</h3>
              <p class="text-sm text-gray-500">{{ selectedStudent.id }}</p>
              <div class="mt-4">
                <div class="flex mb-2">
                  <p class="w-20 font-medium text-gray-600">Ano:</p>
                  <p class="text-gray-700">{{ selectedStudent.year }}</p>
                </div>
                <div class="flex mb-2">
                  <p class="w-20 font-medium text-gray-600">Estatuto:</p>
                  <p class="text-gray-700">{{ selectedStudent.status }}</p>
                </div>
              </div>
              <p class="font-medium text-gray-700 mt-4 mb-2">Disciplinas:</p>
              <div class="flex flex-col gap-2">
                <div v-for="(course, index) in selectedStudent.courses" :key="index"
                  class="py-2 border-b last:border-0">
                  <div class="text-sm font-medium text-gray-800">{{ course.name }}</div>
                  <div v-if="course.allocated" class="text-xs text-blue-600">Alocado: {{ course.allocatedTo }}</div>
                  <div v-else-if="course.conflict" class="text-xs text-red-500">
                    Conflito Detectado
                    <div class="mt-1 p-2 bg-red-100 rounded text-xs">{{ course.conflictDetails }}</div>
                  </div>
                </div>
              </div>
              <button v-if="showCompleteButton" @click="completeAllocation"
                class="mt-6 float-right bg-[#1a237e] text-white py-2 px-4 rounded hover:bg-[#0d1450] transition">
                Concluir
              </button>
            </div>
          </div>
        </div>
        <div class="flex gap-6">
          <div class="flex flex-col bg-white rounded-lg shadow p-4 flex-1 border border-[#020b80]/50">
            <h2 class="text-lg font-bold text-[#1a237e] mb-4">Turnos disponíveis</h2>
            <div class="flex flex-col gap-4 max-h-[300px] overflow-y-auto pr-2">
              <div v-for="(shift, index) in shifts" :key="index" class="p-4 bg-gray-100 rounded">
                <div class="flex justify-between items-center mb-2">
                  <div>
                    <div class="font-bold text-[#020b80]">{{ shift.name }} - {{ shift.code }}</div>
                    <div class="text-xs text-[#020b80]">{{ shift.day }}, {{ shift.time }}</div>
                  </div>
                  <div class="font-bold text-[#020b80]">{{ shift.capacity }}%</div>
                </div>
                <div class="w-full h-2 bg-gray-300 rounded overflow-hidden mb-3">
                  <div class="h-2 rounded"
                    :style="{ width: `${shift.capacity}%`, backgroundColor: getProgressColor(shift.capacity) }"></div>
                </div>
                <div class="flex justify-end">
                  <button v-if="shift.allocated"
                    class="bg-gray-300 text-gray-600 text-xs px-4 py-2 rounded cursor-not-allowed"
                    disabled>Alocado</button>
                  <button v-else :disabled="!canAllocate(shift)" @click="allocateStudent(shift)"
                    class="bg-indigo-400 hover:bg-indigo-600 text-white text-xs px-4 py-2 rounded transition disabled:bg-gray-300 disabled:text-gray-500">
                    Alocar Aluno
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="flex flex-col bg-white rounded-lg shadow p-4 flex-1 border border-[#020b80]/50">
            <h2 class="text-lg font-bold text-[#020b80] mb-4">Avisos</h2>
            <div class="flex flex-col gap-4 overflow-y-auto max-h-[300px] pr-2">
              <div v-for="(notice, index) in notices" :key="index"
                class="flex items-center gap-4 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition cursor-pointer">
                <div
                  class="flex items-center justify-center w-12 h-12 bg-[#e8eaf6] rounded-full text-[#3f51b5] text-xl">
                  📅
                </div>
                <div class="flex flex-col">
                  <div class="font-medium text-[#020b80]">{{ notice.title }}</div>
                  <div class="text-xs text-[#020b80]">{{ notice.date }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, computed } from 'vue';
import Sidebar from '@/components/sidebar/Sidebar.vue';

// ================================= STATE =================================
const searchQuery = ref('');
const selectedStudent = ref<any>(null);
const showCompleteButton = ref(false);
const students = ref([
  {
    id: 'A104567',
    name: 'Ana Maria Santos',
    year: '1º ano',
    status: 'Sem Estatuto',
    courses: [
      {
        name: 'Programação Funcional (PF)',
        allocated: false,
        allocatedTo: null
      },
      {
        name: 'Tópicos de Matemática Discreta (TMD)',
        allocated: true,
        allocatedTo: 'T2'
      },
      {
        name: 'Métodos Numéricos e Otimização Não Linear (MNum)',
        allocated: false,
        allocatedTo: null,
        conflict: true,
        conflictDetails: 'Existe um conflito de horário entre Programação Funcional (T1) e Métodos Numéricos e Otimização Não Linear (T1) no Segunda-feira.'
      }
    ]
  },
  {
    id: 'A123456',
    name: 'Carlos Silva Pires',
    year: '1º ano',
    status: 'Sem Estatuto',
    courses: [
      {
        name: 'Programação Funcional (PF)',
        allocated: false,
        allocatedTo: null
      },
      {
        name: 'Tópicos de Matemática Discreta (TMD)',
        allocated: false,
        allocatedTo: null
      },
      {
        name: 'Métodos Numéricos e Otimização Não Linear (MNum)',
        allocated: false,
        allocatedTo: null
      }
    ]
  }
]);
const shifts = ref([
  {
    name: 'Programação Funcional',
    code: 'T1',
    day: 'Segunda',
    time: '10h-12h',
    capacity: 85,
    allocated: false,
    course: 'Programação Funcional (PF)'
  },
  {
    name: 'Programação Funcional',
    code: 'T2',
    day: 'Terça',
    time: '10h-12h',
    capacity: 70,
    allocated: false,
    course: 'Programação Funcional (PF)'
  },
  {
    name: 'Métodos Numéricos e Otimização Não Linear',
    code: 'T1',
    day: 'Segunda',
    time: '10h-12h',
    capacity: 100,
    allocated: false,
    course: 'Métodos Numéricos e Otimização Não Linear (MNum)'
  },
  {
    name: 'Métodos Numéricos e Otimização Não Linear',
    code: 'T2',
    day: 'Terça',
    time: '10h-12h',
    capacity: 60,
    allocated: false,
    course: 'Métodos Numéricos e Otimização Não Linear (MNum)'
  },
  {
    name: 'Tópicos de Matemática Discreta',
    code: 'T1',
    day: 'Segunda',
    time: '14h-16h',
    capacity: 100,
    allocated: false,
    course: 'Tópicos de Matemática Discreta (TMD)'
  },
  {
    name: 'Tópicos de Matemática Discreta',
    code: 'T2',
    day: 'Terça',
    time: '14h-16h',
    capacity: 60,
    allocated: true,
    course: 'Tópicos de Matemática Discreta (TMD)'
  }
]);
const notices = ref([
  {
    title: 'Mudança de horário do T1 de PF',
    date: '2025-02-03'
  },
  {
    title: 'Eliminação do turno TP3 de IPM',
    date: '2025-02-20'
  },
  {
    title: 'Mudança de docente do TP2 de CG',
    date: '2025-01-20'
  }
]);
const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value;

  const query = searchQuery.value.toLowerCase();
  return students.value.filter(student =>
    student.name.toLowerCase().includes(query) ||
    student.id.toLowerCase().includes(query)
  );
});

// ================================= FUNCTIONS =================================
function selectStudent(student: any) {
  selectedStudent.value = student;
  showCompleteButton.value = false;

  shifts.value.forEach(shift => {
    const matchingCourse = student.courses.find((course: any) => course.name.includes(shift.name));
    if (matchingCourse && matchingCourse.allocated && matchingCourse.allocatedTo === shift.code) {
      shift.allocated = true;
    } else {
      shift.allocated = false;
    }
  });
}

function getProgressColor(capacity: number) {
  if (capacity >= 90) return '#ff4d4d';
  if (capacity >= 70) return '#ff9933';
  return '#66cc66';
}

function canAllocate(shift: any) {
  if (!selectedStudent.value) return false;

  const course = selectedStudent.value.courses.find((c: any) => c.name.includes(shift.name));
  return course && !course.allocated;
}

function allocateStudent(shift: any) {
  if (!selectedStudent.value) return;

  const courseIndex = selectedStudent.value.courses.findIndex((c: any) => c.name.includes(shift.name));

  if (courseIndex !== -1) {
    selectedStudent.value.courses[courseIndex].allocated = true;
    selectedStudent.value.courses[courseIndex].allocatedTo = shift.code;

    if (selectedStudent.value.courses[courseIndex].conflict) {
      selectedStudent.value.courses[courseIndex].conflict = false;
      selectedStudent.value.courses[courseIndex].conflictDetails = null;
    }

    shift.allocated = true;
    showCompleteButton.value = true;
  }
}

function completeAllocation() {
  const index = students.value.findIndex(s => s.id === selectedStudent.value.id);
  if (index !== -1) {
    students.value.splice(index, 1);
  }

  selectedStudent.value = students.value.length > 0 ? students.value[0] : null;
  showCompleteButton.value = false;

  if (selectedStudent.value) {
    shifts.value.forEach(shift => {
      const matchingCourse = selectedStudent.value.courses.find((course: any) => course.name.includes(shift.name));
      if (matchingCourse && matchingCourse.allocated && matchingCourse.allocatedTo === shift.code) {
        shift.allocated = true;
      } else {
        shift.allocated = false;
      }
    });
  }
}
</script>
