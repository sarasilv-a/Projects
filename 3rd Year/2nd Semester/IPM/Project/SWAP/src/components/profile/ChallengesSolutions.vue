<template>
    <div>
        <h3 class="text-lg font-bold text-[#020b80] mb-4">Desafios e Soluções</h3>

        <h4 class="text-base font-bold text-[#020b80]/60 mt-4 mb-1">Desafios</h4>
        <p class="text-sm font-medium">{{ data.challenges }}</p>

        <h4 class="text-base font-bold text-[#020b80]/60 mt-4 mb-1">Soluções</h4>
        <p class="text-sm font-medium">{{ data.solutions }}</p>
    </div>
</template>

<script setup>
defineProps({
    data: Object
})
</script>
