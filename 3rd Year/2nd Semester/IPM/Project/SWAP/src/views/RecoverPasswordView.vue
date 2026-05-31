<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100 font-sans">
    <div class="flex w-[900px] h-[550px] bg-white rounded-xl overflow-hidden shadow-xl">
      <RecoverForm @email-sent="showEmailSent = true" @email-not-found="showEmailNotFound = true" />
      <RecoverSideImage />
    </div>
    <AlertPopup :show="showEmailSent" title="An email was sent for confirmation" buttonText="Click here to Login"
      @close="handleEmailSentClose" />
    <AlertPopup :show="showEmailNotFound" title="Email not found" buttonText="Click here to try again"
      @close="showEmailNotFound = false" />
  </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import RecoverForm from '@/components/recover/RecoverForm.vue';
import RecoverSideImage from '@/components/recover/RecoverSideImage.vue';
import AlertPopup from '@/components/reusables/AlertPopup.vue';

// ================================= STATE =================================
const router = useRouter();
const showEmailSent = ref(false);
const showEmailNotFound = ref(false);

// ================================= FUNCTIONS =================================
const handleEmailSentClose = () => {
  showEmailSent.value = false;
  router.push('/login');
};
</script>
