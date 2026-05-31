<template>
    <div class="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50" @click.self="close">
        <div class="bg-white rounded-lg shadow-lg px-10 py-10 text-center max-w-md relative">
            <button @click="close" class="absolute top-1 right-2 text-2xl text-[#020B80]">×</button>
            <h3 class="text-lg font-semibold text-[#020B80]">Sala alterada com sucesso!</h3>
        </div>
    </div>
</template>

<script setup lang="ts">
const emit = defineEmits(['close'])

function close() {
    emit('close')
}
</script>