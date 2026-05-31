<template>
    <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
        <div class="bg-white rounded-lg shadow-lg w-full max-w-2xl overflow-hidden">

            <div class="p-6">
                <!-- Header -->
                <div class="flex justify-between items-start border-b border-gray-200">
                    <div>
                        <h2 class="text-2xl font-bold text-[#020B80]">Trocar sala - {{ shift?.name }}</h2>
                        <p class="text-gray-700 mt-2">Pesquise e selecione a sala para a qual quer alterar.</p>
                    </div>
                    <button @click="closePopup" class="text-2xl text-[#020B80] -mt-1">×</button>
                </div>
                <div class="flex justify-between items-end mt-6 mb-6 gap-4 flex-wrap">
                    <!-- Pesquisa -->
                    <div class="relative w-full max-w-xs">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
                            class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#020B80] fill-current">
                            <path d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/>
                        </svg>
                        <input
                        type="text"
                        v-model="searchQuery"
                        placeholder="Pesquisar salas..."
                        class="w-full pl-9 pr-3 py-2 border border-[#020B80]/50 rounded-md text-sm placeholder-[#020B80]/60" />
                    </div>

                    <!-- Informação da sala -->
                    <div v-if="shift" class="text-sm text-gray-500 leading-tight">
                        <p><span class="font-semibold">Sala Atual:</span> {{ shift.building }} {{ shift.room }}</p>
                        <p><span class="font-semibold">Capacidade:</span> {{ shift.limit }}</p>
                    </div>
                </div>
                <!-- Tabela -->
                <div class="max-h-[300px] overflow-y-auto border-b border-[#020B80]">
                    <table class="min-w-full divide-y divide-gray/50">
                        <thead>
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Edifício</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Sala</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-[#020B80]/60 uppercase tracking-wider">Capacidade</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-[#020B80]/50">
                            <tr
                                v-for="room in filteredRooms"
                                :key="`${room.building}-${room.room}`"
                                class="hover:bg-gray-50 cursor-pointer"
                                :class="{ 'bg-blue-50': selectedRoom?.building === room.building && selectedRoom?.room === room.room }"
                                @click="selectRoom(room)"
                            >
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ room.building }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ room.room }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ room.capacity }}</td>
                            </tr>
                            <tr v-if="filteredRooms.length === 0">
                                <td colspan="3" class="px-6 py-4 text-center text-sm text-gray-500">Nenhuma sala encontrada</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="text-right mt-4">
                    <button
                        @click="changeRoom"
                        class="bg-[#020B80] text-white px-5 py-2 rounded"
                    >
                        Alterar
                    </button>
                </div>
            </div>
        </div>  
    </div>
</template>
  
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';

// Define types
interface Room {
    building: string;
    room: string;
    capacity: number;
}

interface ShiftInfo {
    id: number;
    name: string;
    building: string;
    room: string;
    limit: number;
}

const props = defineProps<{
    isOpen: boolean;
    shift: ShiftInfo | null;
}>();

const emit = defineEmits(['close', 'change-room'])
const rooms = ref<Room[]>([]);
const selectedRoom = ref<Room | null>(null);
const searchQuery = ref('');

const currentRoom = computed(() => {
    if (!props.shift) return { building: '', room: '' , limit: 0};
    return {
        building: props.shift.building,
        room: props.shift.room,
        limit: props.shift.limit
    };
});

const filteredRooms = computed(() => {
    if (!searchQuery.value) return rooms.value;

    const query = searchQuery.value.toLowerCase();
    return rooms.value.filter(room => 
        room.building.toLowerCase().includes(query) || 
        room.room.toLowerCase().includes(query) ||
        `${room.building} ${room.room}`.toLowerCase().includes(query)
    );
});

watch(() => props.isOpen, (newVal) => {
  if (!newVal) {
    selectedRoom.value = null;
    searchQuery.value = '';
  }
});

onMounted(async () => {
    rooms.value = [
        { building: 'B1', room: '101', capacity: 25 },
        { building: 'B1', room: '105', capacity: 20 },
        { building: 'B1', room: '115', capacity: 15 },
        { building: 'B2', room: '005', capacity: 30 },
        { building: 'B3', room: '201', capacity: 40 },
        { building: 'B3', room: '202', capacity: 30 },
    ];
});

function closePopup() {
    emit('close')
}

function selectRoom(room: Room) {
    const isSelected =
        selectedRoom.value?.building === room.building &&
        selectedRoom.value?.room === room.room;

    selectedRoom.value = isSelected ? null : room;
}

function changeRoom() {
    if (!selectedRoom.value || !props.shift) {
        alert('Por favor selecione uma sala antes de continuar.');
        return;
    }
    emit('change-room', {
        shiftId: props.shift.id,
        newBuilding: selectedRoom.value.building,
        newRoom: selectedRoom.value.room,
        newLimit: selectedRoom.value.capacity

    });
}
</script>
  