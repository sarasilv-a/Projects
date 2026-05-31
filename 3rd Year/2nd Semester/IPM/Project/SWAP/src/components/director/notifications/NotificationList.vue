<template>
    <div class="w-1/2 flex flex-col bg-white rounded-lg border border-[#020B80]/50 overflow-hidden">
        <div class="flex justify-between items-center p-3 border-b">
            <h2 class="font-bold text-[#020B80]">Lista de Notificações</h2>
            <span class="font-bold text-[#020B80] px-2 py-1 rounded-full text-xs">
                {{ notificacoes?.length || 0 }}
            </span>
        </div>
        <div class="flex-1 overflow-y-auto">
            <div class="divide-y" v-if="notificacoes && notificacoes.length > 0">
                <div v-for="(notificacao, index) in notificacoes" :key="index"
                    class="p-3 cursor-pointer transition-colors hover:bg-gray-50"
                    :class="{ 'bg-[#4C92F1]/30': selected === index }" @click="$emit('select', index)">
                    <div class="flex justify-between">
                        <div>
                            <h3 class="font-bold text-[#000000]">
                                {{ notificacao.type === 'Change' ? 'Pedido de Mudança de Turno' : 'Prazo Importante' }}
                            </h3>
                            <p class="text-sm mt-1 text-[#000000]">
                                {{ notificacao.message }}
                            </p>
                            <p class="text-xs mt-2 text-[#000000]/70">
                                {{ notificacao.date }}
                            </p>
                        </div>
                        <div class="self-center">
                            <ChevronRight class="h-5 w-5 text-[#020B80]" />
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="p-4 text-[#020B80]/60 text-sm text-center">Sem notificações disponíveis</div>
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ChevronRight } from 'lucide-vue-next';
import type { Notification } from '@/types/types';

// ================================= STATE =================================
defineProps<{
    notificacoes: Notification[];
    selected: number | null;
    getStudentName: (id: number) => string;
    getSubjectName: (shiftId: number) => string;
    getShiftName: (id: number) => string;
}>();
defineEmits(['select']);
</script>
