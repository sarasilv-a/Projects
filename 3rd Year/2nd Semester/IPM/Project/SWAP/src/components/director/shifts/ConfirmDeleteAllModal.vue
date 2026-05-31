<template>
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
        <div class="bg-white rounded-xl border border-[#020B80]/50 px-6 py-4 w-[350px] text-center shadow-xl">
            <h2 class="text-[#020B80] font-bold underline text-lg mb-2">
                Tem a certeza que quer apagar todos os alunos do turno?
            </h2>
            <p class="text-[#020B80] font-semibold text-md mb-4">
                Esta ação é irreversível.
            </p>
            <div class="flex justify-center gap-4">
                <button class="px-4 py-1 rounded-md border border-[#020B80] text-[#020B80] hover:bg-[#020B80]/10 transition"
                    @click="$emit('cancel')">
                    Não
                </button>
                <button class="px-4 py-1 rounded-md bg-[#020B80] text-white hover:opacity-90 transition"
                    @click="$emit('confirm')">
                    Sim
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= STATE =================================
defineEmits(['cancel', 'confirm']);
</script>
  