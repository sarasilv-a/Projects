<template>
    <div class="w-1/2 flex items-center justify-center">
        <div class="w-3/4 max-w-md">
            <h1 class="text-3xl font-bold text-center mb-8 text-[#020C80]">Register</h1>
            <form @submit.prevent="handleRegister" class="space-y-6">
                <div class="space-y-2">
                    <label for="email" class="block text-[#020B80]">Email</label>
                    <input type="email" id="email" v-model="email" placeholder="xxxxxxxx@uminho.pt"
                        class="w-full p-3 rounded border text-sm"
                        :class="showValidationError && !email ? 'border-red-500' : 'border-[rgba(0,13,128,0.5)]'" />
                </div>
                <div class="space-y-2">
                    <label for="password" class="block text-[#020B80]">Password</label>
                    <input type="password" id="password" v-model="password" placeholder="Insert your password here"
                        class="w-full p-3 rounded border text-sm"
                        :class="showValidationError && !password ? 'border-red-500' : 'border-[rgba(0,13,128,0.5)]'" />
                </div>
                <div class="space-y-2">
                    <label for="confirmPassword" class="block text-[#020B80]">Confirm Password</label>
                    <input type="password" id="confirmPassword" v-model="confirmPassword" placeholder="Confirm password"
                        class="w-full p-3 rounded border text-sm"
                        :class="showValidationError && !confirmPassword ? 'border-red-500' : 'border-[rgba(0,13,128,0.5)]'" />
                </div>
                <div v-if="showValidationError" class="text-red-500 text-sm">
                    Please fill the camps above
                </div>
                <button type="submit"
                    class="w-full py-3 rounded-3xl font-medium text-[#020C80] bg-[rgba(76,146,241,0.5)] hover:bg-[rgba(76,146,241,0.7)] transition duration-300">
                    Register
                </button>
            </form>
            <div class="mt-6 text-center text-sm">
                <p>
                    Already have an account?
                    <router-link to="/login" class="font-medium text-[#020C80] hover:underline">Sign in</router-link>
                </p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { registerStudent } from '@/api/api';

// ================================= STATE =================================
const emit = defineEmits(['show-alert']);
const router = useRouter();
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const showValidationError = ref(false);

// ================================= FUNCTIONS =================================
const handleRegister = async () => {
    if (!email.value || !password.value || !confirmPassword.value) {
        showValidationError.value = true;
        return;
    } else {
        showValidationError.value = false;
    }

    if (password.value !== confirmPassword.value) {
        emit('show-alert', 'passwordMismatch');
        return;
    }

    const result = await registerStudent(email.value, password.value, email.value);

    if (result.success) {
        emit('show-alert', 'success');
    } else if (result.reason === "email_in_use") {
        emit('show-alert', 'emailInUse');
    } else {
        console.error("Error registering.");
    }
};
</script>
