<template>
  <div class="bg-white p-6 rounded-lg shadow border border-[#020B80]/50">
    <div class="mb-4">
      <h2 class="text-lg font-bold text-[#020B80]">Próximos Eventos</h2>
      <p class="text-sm text-[#020B80]/60">Datas importantes do calendário</p>
    </div>
    <div class="space-y-3">
      <div v-for="event in events" :key="event.id" class="flex items-start gap-3">
        <div class="bg-[#D9D9D9] text-[#020B80] p-2 rounded">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="lucide lucide-calendar-days">
            <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
            <line x1="16" x2="16" y1="2" y2="6" />
            <line x1="8" x2="8" y1="2" y2="6" />
            <line x1="3" x2="21" y1="10" y2="10" />
            <path d="M8 14h.01" />
            <path d="M12 14h.01" />
            <path d="M16 14h.01" />
            <path d="M8 18h.01" />
            <path d="M12 18h.01" />
            <path d="M16 18h.01" />
          </svg>
        </div>
        <div>
          <div class="font-medium text-[#020B80]">{{ event.title }}</div>
          <div class="text-sm text-[#020B80]/60">{{ event.date }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ================================= STATE =================================
defineProps<{
  events: Array<{
    id: number;
    title: string;
    date: string;
  }>;
}>();
</script>
