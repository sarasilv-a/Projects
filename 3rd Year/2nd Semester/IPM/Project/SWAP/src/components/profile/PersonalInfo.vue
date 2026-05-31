<template>
  <div>
    <h3 class="text-lg font-bold text-indigo-900 mb-4">Informações Pessoais</h3>

    <div class="grid grid-cols-[auto_1fr] gap-y-3 gap-x-4">
      <div>
        <div class="font-bold text-[#020b80]/60">Idade</div>
        <div class="text-sm font-medium">{{ data.age }} anos</div>
      </div>

      <div>
        <div class="font-bold text-[#020b80]/60">Localização</div>
        <div class="text-sm font-medium">{{ data.location }}</div>
      </div>

      <div>
        <div class="font-bold text-[#020b80]/60">Profissão</div>
        <div class="text-sm font-medium">{{ data.profession }}</div>
      </div>

      <div>
        <div class="font-bold text-[#020b80]/60">Educação</div>
        <div class="text-sm font-medium">{{ data.education }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: Object
})
</script>
