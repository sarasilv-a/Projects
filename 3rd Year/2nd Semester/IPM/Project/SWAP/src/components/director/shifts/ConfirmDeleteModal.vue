<template>
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
        <div class="bg-white rounded-xl border border-[#020B80]/50 px-6 py-4 w-[350px] text-center shadow-xl">
            <h2 class="text-[#020B80] font-bold text-lg mb-2">Confirmar Exclusão</h2>
            <p class="text-gray-600 mb-4">
                Tem certeza que deseja excluir este aluno? Esta ação não pode ser desfeita.
            </p>
            <div class="flex justify-center gap-4">
                <button class="px-4 py-1 rounded-md border border-[#020B80] text-[#020B80] hover:bg-[#020B80]/10 transition"
                    @click="$emit('cancel')">
                    Cancelar
                </button>
                <button class="px-4 py-1 rounded-md bg-[#020B80] text-white hover:opacity-90 transition"
                    @click="$emit('confirm')">
                    Confirmar
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
defineEmits(['cancel', 'confirm']);
</script>
  