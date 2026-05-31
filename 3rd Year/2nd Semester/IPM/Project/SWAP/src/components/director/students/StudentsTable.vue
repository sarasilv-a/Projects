<template>
  <div class="bg-white rounded-lg shadow overflow-hidden border border-[#020B80]/50">
    <h2 class="text-xl font-bold p-4 text-[#020B80]">Lista de Alunos</h2>
    <div class="overflow-x-auto px-10">
      <table class="min-w-full divide-y divide-gray-200 divide-[#020B80]/50">
        <thead class="">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Número</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Nome</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Ano</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Disciplinas
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Ações</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-[#020B80]/50">
          <tr v-for="student in students" :key="student.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#000000]">{{ student.number }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-[#000000]">{{ student.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-[#000000]">{{ student.year }}º</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-[#000000] max-w-xs truncate">
              {{ getSubjectNames(getStudentEnrollments(student.id)) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <div class="flex justify-end space-x-2">
                <button @click="$emit('edit', student)" class="text-[#020B80] hover:opacity-80">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button @click="$emit('delete', student)" class="text-red-600 hover:text-red-900">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import type { Student, Subject, Enrollment } from '@/types/types';

// ================================= STATE =================================
const props = defineProps<{
  students: Student[];
  subjects: Subject[];
  enrollments: Enrollment[];
}>();
defineEmits(['edit', 'delete']);

// ================================= FUNCTIONS =================================
const getStudentEnrollments = (studentId: number): number[] => {
  return props.enrollments
    .filter(enrollment => enrollment.studentId === studentId)
    .map(enrollment => enrollment.subjectId);
};

const getSubjectNames = (subjectIds: number[]): string => {
  const names = subjectIds
    .map(id => props.subjects.find(s => s.id === id)?.name)
    .filter(Boolean) as string[];

  const visible = names.slice(0, 2);
  const extraCount = names.length - visible.length;

  return extraCount > 0
    ? `${visible.join(', ')} +${extraCount}`
    : visible.join(', ');
};

</script>
