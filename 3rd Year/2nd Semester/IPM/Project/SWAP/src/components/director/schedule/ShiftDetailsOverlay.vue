<template>
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
        <div class="bg-white rounded-xl p-6 shadow-lg border-2 border-[#020B80] w-[450px] relative">
            <button @click="$emit('close')"
                class="absolute top-2 right-3 text-gray-400 hover:text-gray-600 text-xl">×</button>
            <h2 class="text-lg font-bold text-[#020B80] mb-2">Detalhes do Turno</h2>
            <hr class="mb-3 border-[#020B80]" />
            <div class="space-y-2 text-[#020B80] text-sm">
                <p><strong>Turno:</strong> {{ turno.name }}</p>
                <p><strong>Tipo:</strong> {{ turno.type }}</p>
                <p><strong>Edifício:</strong> {{ turno.building }}</p>
                <p><strong>Sala:</strong> {{ turno.room }}</p>
                <p><strong>Dia:</strong> {{ formatDay(turno.day) }}</p>
                <p><strong>Início:</strong> {{ turno.start }}</p>
                <p><strong>Fim:</strong> {{ turno.end }}</p>
                <p><strong>Limite:</strong> {{ turno.limit }} aluno(s)</p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= STATE =================================
defineProps<{
    turno: {
        id: number;
        name: string;
        type: string;
        building: string;
        room: string;
        day: number;
        start: string;
        end: string;
        limit: number;
    };
}>();
defineEmits(['close']);

// ================================= FUNCTIONS =================================
const formatDay = (dia: number): string => {
    const map = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'];
    return map[dia - 1] || `Dia ${dia}`;
};
</script>
