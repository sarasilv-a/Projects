<template>
    <div>
        <h3 class="text-lg font-bold text-[#020b80] mb-4">Interesses e Objetivos</h3>

        <h4 class="text-base font-bold text-[#020b80]/60 mt-4 mb-1">Interesses</h4>
        <p class="text-sm font-medium">{{ data.interests }}</p>

        <h4 class="text-base font-bold text-[#020b80]/60 mt-4 mb-1">Objetivos</h4>
        <p class="text-sm font-medium">{{ data.objectives }}</p>
    </div>
</template>

<script setup>
defineProps({
    data: Object
})
</script>
