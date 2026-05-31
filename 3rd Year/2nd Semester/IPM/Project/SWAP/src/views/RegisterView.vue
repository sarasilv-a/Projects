<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100">
    <div class="flex w-[900px] h-[550px] bg-white rounded-xl overflow-hidden shadow-lg">
      <RegisterSideImage />
      <RegisterForm @show-alert="handleAlert" />
    </div>
    <AlertPopup v-if="currentAlert === 'emailInUse'" :show="true" title="Email already in use"
      buttonText="Click here to Login" @close="currentAlert = null" @button-click="redirectToLogin">
      This email is already registered.
    </AlertPopup>
    <AlertPopup v-if="currentAlert === 'success'" :show="true" title="Successfully registered"
      buttonText="Click here to Login" @close="currentAlert = null" @button-click="redirectToLogin">
      Your account has been created successfully.
    </AlertPopup>
    <AlertPopup v-if="currentAlert === 'passwordMismatch'" :show="true" title="Passwords do not match"
      buttonText="Click here to try again" @close="currentAlert = null">
      Please ensure your passwords match.
    </AlertPopup>
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import RegisterForm from '@/components/register/RegisterForm.vue';
import RegisterSideImage from '@/components/register/RegisterSideImage.vue';
import AlertPopup from '@/components/reusables/AlertPopup.vue';

// ================================= STATE =================================
const router = useRouter();
const currentAlert = ref<string | null>(null);

// ================================= FUNCTIONS =================================
const handleAlert = (type: string) => {
  currentAlert.value = type;
};

const redirectToLogin = () => {
  router.push('/login');
};
</script>
