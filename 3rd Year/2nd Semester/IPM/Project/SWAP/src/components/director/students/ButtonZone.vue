<template>
    <div class="flex justify-between items-center mb-6">
        <div class="relative">
            <input type="text" :placeholder="searchPlaceholder"
                class="text-[#020B80] placeholder:text-[#020B80]/60  pl-10 pr-4 py-2 border border-[#020B80]/50 rounded-md w-64 focus:outline-none focus:ring-2 focus:ring-[#020B80]/50"
                v-model="searchQuery" @input="$emit('search', searchQuery)" />
            <div class="absolute left-3 top-2.5 text-[#020B80]/60">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </div>
        </div>
        <div class="flex space-x-3">
            <button class="flex items-center px-4 py-2 text-white bg-[#020B80] rounded-md hover:opacity-90 transition"
                @click="$emit('add')">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Adicionar
            </button>
            <button
                class="flex items-center px-4 py-2 bg-white text-[#020B80] border border-[#020B80]/50 rounded-md hover:bg-gray-50 transition"
                @click="$emit('import')">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Importar
            </button>
            <button
                class="flex items-center px-4 py-2 bg-white text-[#020B80] border border-[#020B80]/50 rounded-md hover:bg-gray-50 transition"
                @click="$emit('export')">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Exportar
            </button>
            <button
                class="flex items-center px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 transition"
                @click="$emit('delete-all')">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Apagar Todos
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref } from 'vue';

// ================================= STATE =================================
const props = defineProps<{
    searchPlaceholder: string;
}>();
const searchQuery = ref('');
defineEmits(['search', 'add', 'import', 'export', 'delete-all']);
</script>
