<template>
    <div>
        <h3 class="text-lg font-bold text-[#020b80] mb-4">Citação</h3>
        <blockquote class="border-l-4 border-[#020b80] bg-gray-100 p-4 rounded italic text-[000000]">
            {{ quote }}
        </blockquote>
    </div>
</template>

<script setup>
defineProps({
    quote: String
})
</script>
