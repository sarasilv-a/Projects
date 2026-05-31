<template>
  <div class="w-[200px] h-screen bg-[#C2D7F4] flex flex-col fixed left-0 top-0 rounded-r-xl shadow-lg">
    <!-- Logo -->
    <div>
      <router-link :to="homeRoute" class="no-underline block">
        <img src="@/assets/swap.png" alt="SWAP Logo" class="w-full" />
      </router-link>
    </div>

    <!-- Menu -->
    <div class="flex-1 flex flex-col px-3 py-4 space-y-1">
      <!-- Director Links -->
      <template v-if="userType === 'director'">
        <SidebarItem to="/director/dashboard" label="Dashboard" icon="grid" />
        <SidebarItem to="/director/schedule" label="Horários" icon="calendar" />
        <SidebarItem to="/director/shifts" label="Turnos" icon="clock" />
        <SidebarItem to="/director/students" label="Alunos" icon="users" />
        <SidebarItem to="/director/profile" label="Perfil" icon="user" />
      </template>

      <!-- Student Links -->
      <template v-else-if="userType === 'student'">
        <SidebarItem to="/student/schedule" label="Horários" icon="calendar" />
        <SidebarItem to="/student/profile" label="Perfil" icon="user" />
      </template>
    </div>

    <!-- Logout -->
    <div class="px-3 pb-5">
      <SidebarItem :action="handleLogout" label="Logout" icon="logout" />
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue';
import SidebarItem from '@/components/sidebar/SidebarItem.vue';

import { useRouter } from "vue-router";
import { useSessionStore } from "@/stores/session";

const props = defineProps({
  userType: {
    type: String,
    default: 'student',
    validator: (value) => ['student', 'director'].includes(value)
  }
});

const homeRoute = computed(() => {
  return props.userType === 'director' ? '/director/dashboard' : '/student/schedule';
});

const router = useRouter();
const session = useSessionStore();

function handleLogout() {
  session.logout();     // <- limpa a sessão
  router.push("/");     // <- redireciona para a home
}
</script>
