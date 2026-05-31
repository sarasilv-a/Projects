<template>
    <div class="mb-6">
        <h1 class="text-3xl font-bold text-[#020B80]">{{ title }}</h1>
        <p class="text-[#020B80]/60">{{ subtitle }}</p>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    title: string;
    subtitle: string;
}>();
</script>
