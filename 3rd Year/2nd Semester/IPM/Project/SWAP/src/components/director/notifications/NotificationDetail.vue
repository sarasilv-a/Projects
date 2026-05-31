<template>
    <div class="w-1/2 flex flex-col bg-white rounded-lg border border-[#020B80]/50">
        <div class="p-3 border-b">
            <h2 class="font-bold text-[#020B80]">Detalhes do Pedido</h2>
        </div>
        <div class="flex-1 overflow-y-auto">
            <template v-if="notificacao">
                <div v-if="notificacao.type === 'Change'" class="p-4">
                    <h3 class="text-lg font-bold text-[#000000]">
                        {{ getStudentName(notificacao.studentId) }} -
                        {{ getSubjectName(notificacao.currentShift) }}
                    </h3>
                    <div class="mt-2">
                        <span class="bg-[#020B80]/10 text-[#020B80] px-3 py-1 rounded-full text-sm">Pedido de
                            Mudança</span>
                    </div>
                    <div class="mt-4 bg-[#4c92f1]/30 p-3 rounded-lg">
                        <h4 class="font-bold text-[#020B80]">Pedido de Mudança de Turno</h4>
                        <div class="mt-2 grid grid-cols-2 gap-2">
                            <div>
                                <p class="text-sm text-[#020B80]">Disciplina</p>
                                <p class="font-bold text-[#000000]">
                                    {{ getSubjectName(notificacao.currentShift) }}
                                </p>
                            </div>
                            <div>
                                <p class="text-sm text-[#020B80]">Turno Atual -> Pretendido</p>
                                <p class="font-bold text-[#000000]">
                                    {{ notificacao.currentShift }} -> {{ notificacao.wantedShift }}
                                </p>
                            </div>
                        </div>
                        <div class="mt-2">
                            <p class="text-sm text-[#020B80]">Mensagem do Aluno</p>
                            <p class="text-sm mt-1 text-[#000000]">
                                "{{ notificacao.message }}"
                            </p>
                        </div>
                    </div>
                    <div class="mt-3">
                        <h4 class="font-bold mb-2 text-[#000000]">Turnos Disponíveis</h4>
                        <div class="max-h-48 overflow-y-auto pr-1 border rounded-lg">
                            <div class="space-y-0">
                                <div v-for="(turno, idx) in turnos" :key="idx"
                                    class="p-2 border-b last:border-b-0 cursor-pointer transition-colors"
                                    :class="{ 'bg-[#4C92F1]/30': turno.id === notificacao.wantedShift }"
                                    @click="$emit('update-turno', turno.id)">
                                    <div class="flex justify-between">
                                        <div>
                                            <p class="font-semibold text-[#000000]">
                                                {{ getSubjectName(turno.id) }} - {{ turno.name }}
                                            </p>
                                            <p class="text-sm text-[#000000]">{{ turno.start }} - {{ turno.end }}</p>
                                        </div>
                                        <div class="flex items-center">
                                            <span class="text-sm" :class="{
                                                'text-green-600': turno.limit < 30,
                                                'text-red-600': turno.limit >= 30
                                            }">
                                                {{ turno.limit }}/30
                                            </span>
                                            <span v-if="turno.id === notificacao.wantedShift"
                                                class="ml-2 text-xs text-blue-600">
                                                Turno pretendido
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-4 flex gap-4">
                        <button class="flex-1 py-2 border border-gray-300 rounded-md text-gray-700"
                            @click="$emit('rejeitar', notificacao?.id)">
                            Rejeitar
                        </button>
                        <button class="flex-1 py-2 rounded-md text-white bg-[#4C92F1]"
                            @click="$emit('aprovar', notificacao?.studentId, notificacao?.wantedShift, notificacao?.id)">
                            Aprovar
                        </button>
                    </div>
                </div>
                <div v-else-if="notificacao.type === 'Deadline'" class="p-4">
                    <h3 class="text-lg font-semibold text-[#020B80]">Informação sobre Prazos</h3>
                    <div class="mt-4 bg-blue-50 p-4 rounded-lg">
                        <p class="text-sm text-[#020B80]">{{ notificacao.message }}</p>
                        <p class="text-sm mt-2 font-medium text-[#020B80]">
                            Data limite: {{ notificacao.date }}
                        </p>
                    </div>
                </div>
            </template>
            <div v-else class="p-4 text-center text-[#020B80]/60">
                Selecione uma notificação para ver os detalhes
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { computed } from 'vue';
import type { Notification, Shift } from '@/types/types';

// ================================= STATE =================================
const props = defineProps<{
    notificacoes: Notification[];
    selectedNotificacao: number | null;
    turnos: Shift[];
    getStudentName: (id: number) => string;
    getSubjectName: (shiftId: number) => string;
}>();
defineEmits(['update-turno', 'aprovar', 'rejeitar']);

// ================================= FUNCTIONS =================================
const notificacao = computed(() => {
    if (props.selectedNotificacao === null) return null;
    return props.notificacoes[props.selectedNotificacao] ?? null;
});
</script>
