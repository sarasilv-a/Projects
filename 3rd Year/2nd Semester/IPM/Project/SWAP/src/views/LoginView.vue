<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100 font-sans">
    <div class="flex w-[900px] h-[550px] bg-white rounded-xl overflow-hidden shadow-xl">
      <LoginForm @wrong-credentials="showWrongCredentials = true" />
      <LoginSideImage />
    </div>
    <AlertPopup :show="showWrongCredentials" title="Wrong credentials" buttonText="Click here to Login"
      @close="showWrongCredentials = false" />
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref } from 'vue';
import LoginForm from '@/components/login/LoginForm.vue';
import LoginSideImage from '@/components/login/LoginSideImage.vue';
import AlertPopup from '@/components/reusables/AlertPopup.vue';

// ================================= STATE =================================
const showWrongCredentials = ref(false);
</script>
