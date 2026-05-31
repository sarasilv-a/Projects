<template>
  <div class="bg-white p-6 rounded-lg shadow border border-[#020B80]/50 h-full">
    <div class="mb-4">
      <h2 class="text-lg font-bold text-[#020B80]">Notificações Recentes</h2>
      <p class="text-sm text-[#020B80]/60">Alertas e informações importantes</p>
    </div>
    <div class="space-y-3">
      <div v-for="notification in notifications" :key="notification.id"
        class="border rounded-md p-3 border-[#020B80]/50">
        <div class="flex items-start gap-3">
          <div class="mt-1">
            <div v-if="notification.tipo === 'mudanca'"
              class="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center text-amber-600">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                class="lucide lucide-alert-triangle">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
                <path d="M12 9v4" />
                <path d="M12 17h.01" />
              </svg>
            </div>
            <div v-else class="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                class="lucide lucide-bell">
                <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
                <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
              </svg>
            </div>
          </div>
          <div class="flex-1">
            <div v-if="notification.tipo === 'mudanca'" class="text-sm text-[#020B80]">
              {{ getNotificationMessage(notification) }}
            </div>
            <div v-else class="text-sm text-[#020B80]">
              {{ notification.titulo }}
              <div class="text-xs text-gray-500">{{ notification.descricao }}</div>
            </div>
            <div class="text-xs text-[#020B80]/60 mt-1">
              {{ formatDate(notification.data) }}
            </div>
          </div>
        </div>
      </div>
      <div v-if="notifications.length === 0" class="text-center py-4 text-gray-500">
        Nenhuma notificação disponível
      </div>
    </div>
    <div class="mt-8 flex justify-center border border-[#020B80]/50 rounded-lg hover:bg-blue-50">
      <button class="w-full max-w-xs px-6 py-2 text-[#020B80] text-sm rounded-lg  transition"
        @click="goToAllNotifications">
        Ver todas as notificações
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { useRouter } from 'vue-router'

// ================================= STATE =================================
defineProps<{
  notifications: Array<{
    id: number;
    tipo: string;
    data: string;
    titulo?: string;
    descricao?: string;
    aluno?: string;
    turnoAtual?: string;
    turnoDesejado?: string;
  }>;
}>();
defineEmits(['view-all']);
const router = useRouter()

// ================================= FUNCTIONS =================================
const getNotificationMessage = (notification: any) => {
  if (notification.tipo === 'mudanca') {
    return `${notification.aluno} pediu para mudar a sala de ${notification.turnoAtual} para ${notification.turnoDesejado}`;
  }
  return notification.titulo;
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('pt-PT', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

const goToAllNotifications = () => {
  router.push('/director/notifications')
}
</script>
