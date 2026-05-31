<template>
  <div v-if="show" class="fixed top-4 right-4 z-50 max-w-md p-4 bg-white rounded-lg shadow-lg border-t-4 border-[#020B80]">
    <div class="flex justify-between items-center">
      <h3 class="font-semibold text-[#020B80]">{{ title }}</h3>
      <button @click="$emit('close')" class="text-gray-400 hover:text-gray-500">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    <p v-if="message" class="mt-1 text-sm text-gray-600">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean;
  title: string;
  message?: string;
}>();

defineEmits(['close']);
</script>
