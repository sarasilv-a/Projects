<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="w-[90%] max-w-4xl bg-white rounded-lg shadow-lg flex flex-col max-h-[90vh] overflow-hidden">
      <div class="flex justify-between items-start p-5 border-b border-gray-200">
        <div>
          <h2 class="text-xl font-semibold text-[#020B80]">
            {{ props.shift?.subjectName ?? 'Disciplina' }} - {{ props.shift?.name ?? 'Turno' }}
          </h2>
          <p class="text-sm text-[#020B80]/60 mt-1">Listagem dos Alunos pertencentes ao Turno</p>
        </div>
        <button @click="closePopup" class="text-2xl text-[#020B80] -mt-1">×</button>
      </div>
      <div class="flex flex-col flex-grow overflow-hidden">
        <div class="flex flex-wrap justify-between gap-4 p-5">
          <div class="relative w-full max-w-xs">
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
          <div class="flex gap-3">
            <button @click="addStudent"
              class="bg-[#020B80] text-white px-4 py-2 rounded font-medium text-sm">Adicionar</button>
            <button @click="deleteAllStudents"
              class="bg-orange-500 text-white px-4 py-2 rounded font-medium text-sm">Apagar Todos</button>
          </div>
        </div>
        <div class="overflow-y-auto px-5 pb-5 flex-grow max-h-[500px]">
          <table class="w-full table-auto border-collapse">
            <thead>
              <tr class="text-left text-[#020B80]/60 border-b-2 border-[#020B80]/50">
                <th class="py-3 pr-5 w-1/6 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Número</th>
                <th class="py-3 pr-5 w-2/5 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Nome</th>
                <th class="py-3 pr-5 w-1/6 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Ano</th>
                <th class="py-3 pr-5 w-1/6 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in filteredStudents" :key="student.id"
                class="text-[#020B80]/80 border-b border-[#020B80]/30">
                <td class="py-2 pr-6 whitespace-nowrap text-sm text-[#020B80]">{{ student.number }}</td>
                <td class="py-2 pr-6 whitespace-nowrap text-sm text-[#020B80]">{{ student.name }}</td>
                <td class="py-2 pr-6 whitespace-nowrap text-sm text-[#020B80]">{{ student.year }}º</td>
                <td class="py-2 pr-6">
                  <div class="flex justify-end items-center space-x-3">
                    <button @click="deleteStudent(student.id)" class="text-red-600 hover:text-red-900">
                      <svg 
                        class="h-5 w-5" 
                        fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, computed, onMounted, watch } from 'vue'
import { getStudentsByShift } from '@/api/studentAPI'
import type { Student } from '@/types/types'

// ================================= STATE =================================
const props = defineProps<{
  isOpen: boolean,
  shift?: {
    id: number;
    name: string;
    subjectName: string;
  }
  students: Student[]
}>()
const emit = defineEmits(['close', 'add', 'request-delete', 'request-delete-all', 'toggle-menu'])
const students = computed(() => props.students)
const searchQuery = ref('')
const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value
  const query = searchQuery.value.toLowerCase()
  return students.value.filter(student =>
    String(student.number).includes(query) ||
    student.name.toLowerCase().includes(query)
  )
})

// ================================= FUNCTIONS =================================

function closePopup() {
  emit('close')
}
function addStudent() {
  if (props.shift?.id) {
    emit('add', {shiftId : props.shift.id});
  }
}
function deleteStudent(studentId: number) {
  if (props.shift?.id) {
    emit('request-delete', { studentId, shiftId: props.shift.id});
  }
}
function deleteAllStudents() {
  emit('request-delete-all', props.shift?.id)
}
function toggleMenu() {
  emit('toggle-menu')
}
</script>
