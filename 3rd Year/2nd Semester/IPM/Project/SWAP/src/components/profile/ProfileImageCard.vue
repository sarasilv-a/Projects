<template>
    <div class="w-full lg:w-[200px] pr-0 lg:pr-8 flex flex-col items-center mb-10">
        <img :src="data.profileImage" alt="Foto de perfil" class="w-32 h-32 rounded-full object-cover mb-4" />
        <h2 class="text-xl font-bold text-[#020b80] mb-1">{{ data.name }}</h2>
        <p class="text-sm text-[#020b80]/60">{{ data.id }}</p>
    </div>
</template>

<script setup>
defineProps({
    data: Object
})
</script>
