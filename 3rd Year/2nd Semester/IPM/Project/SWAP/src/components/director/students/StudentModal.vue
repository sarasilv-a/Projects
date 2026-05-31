<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
    <div class="bg-white rounded-xl border border-[#020B80]/50 p-6 w-[500px] max-h-[95vh] overflow-y-auto">
      <h2 class="text-xl font-bold text-[#020B80] mb-4">
        {{ isEditing ? 'Editar Aluno' : 'Adicionar Aluno' }}
      </h2>
      <form @submit.prevent="saveStudent">
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div class="col-span-1">
            <label class="block text-sm font-medium text-gray-700 mb-1">Número</label>
            <input type="text" v-model="formData.number"
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#020B80]/50"
              :class="{ 'border-red-500': errors.number }" />
            <p v-if="errors.number" class="mt-1 text-sm text-red-600">{{ errors.number }}</p>
          </div>
          <div class="col-span-1">
            <label class="block text-sm font-medium text-gray-700 mb-1">Ano</label>
            <select v-model.number="formData.year"
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#020B80]/50"
              :class="{ 'border-red-500': errors.year }">
              <option value="1">1º Ano</option>
              <option value="2">2º Ano</option>
              <option value="3">3º Ano</option>
            </select>
            <p v-if="errors.year" class="mt-1 text-sm text-red-600">{{ errors.year }}</p>
          </div>
          <div class="col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input type="text" v-model="formData.name"
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#020B80]/50"
              :class="{ 'border-red-500': errors.name }" />
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>
          <div class="col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input type="email" v-model="formData.email"
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#020B80]/50"
              :class="{ 'border-red-500': errors.email }" />
            <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
          </div>
          <div class="col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Cidade</label>
            <input type="text" v-model="formData.city"
              class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#020B80]/50" />
          </div>
          <div class="col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Disciplinas</label>
            <div class="border border-gray-300 rounded-md p-2 max-h-40 overflow-y-auto">
              <div v-for="subject in availableSubjects" :key="subject.id" class="flex items-center mb-2">
                <input type="checkbox" :id="`subject-${subject.id}`" :value="subject.id" v-model="selectedSubjects"
                  class="mr-2" />
                <label :for="`subject-${subject.id}`" class="text-sm">
                  {{ subject.name }} ({{ subject.year }}º ano, {{ subject.semester }}º semestre)
                </label>
              </div>
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            @click="$emit('close')">
            Cancelar
          </button>
          <button type="submit" class="px-4 py-2 bg-[#020B80] text-white rounded-md hover:opacity-90">
            {{ isEditing ? 'Atualizar' : 'Adicionar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref, computed, onMounted } from 'vue';
import type { Student, Subject, Enrollment } from '@/types/types';

// ================================= STATE =================================
const props = defineProps<{
  student?: Student;
  subjects: Subject[];
  enrollments: Enrollment[];
  errors: Record<string, string>;
}>();
const emit = defineEmits(['close', 'save']);
const isEditing = computed(() => !!props.student);
const formData = ref<Partial<Student>>({
  id: props.student?.id || undefined,
  number: props.student?.number || '',
  name: props.student?.name || '',
  email: props.student?.email || '',
  year: props.student?.year ?? 1,
  city: props.student?.city || '',
  password: props.student?.password || '',
  interests: props.student?.interests || '',
  goals: props.student?.goals || '',
  quote: props.student?.quote || '',
  age: props.student?.age || 0,
  occupation: props.student?.occupation || '',
  education: props.student?.education || '',
  challenges: props.student?.challenges || '',
  solutions: props.student?.solutions || '',
  status: props.student?.status || ''
});
const selectedSubjects = ref<number[]>([]);
const availableSubjects = computed(() => {
  return props.subjects.filter(subject => subject.year === Number(formData.value.year));
});

// ================================= DATA =================================
onMounted(() => {
  if (isEditing.value && props.student) {
    const studentEnrollments = props.enrollments
      .filter(e => e.studentId === props.student!.id)
      .map(e => e.subjectId);

    selectedSubjects.value = studentEnrollments;
  }
});

// ================================= FUNCTIONS =================================
function saveStudent() {
  emit('save', {
    student: formData.value,
    enrollments: selectedSubjects.value
  });
}
</script>
