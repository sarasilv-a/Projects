<template>
    <div class="w-1/2 flex flex-col justify-between px-10 py-12">
        <div class="flex flex-col">
            <h1 class="text-3xl font-bold text-[#020C80] mb-10 text-center">Recover your password</h1>
            <div class="space-y-6">
                <div>
                    <label for="email" class="block mb-2 text-[#020C80] font-semibold">Email</label>
                    <input type="email" id="email" v-model="email" placeholder="xxxxxxx@uminho.pt" :class="[
                        'w-full p-3 rounded border text-sm',
                        showError && !email ? 'border-red-500' : 'border-[rgba(0,13,128,0.5)]'
                    ]" />
                </div>
                <div v-if="showError && !email" class="text-red-500 text-sm">
                    Please fill the email camp
                </div>
                <button @click="recoverPassword"
                    class="w-full py-3 rounded-3xl font-medium text-[#020C80] bg-[rgba(76,146,241,0.5)] hover:bg-[rgba(76,146,241,0.7)] transition duration-300">
                    Recover
                </button>
            </div>
        </div>
        <div class="text-center text-sm mt-8">
            <a href="#" @click.prevent="goToLogin" class="text-[#020C80] font-semibold hover:underline">
                Click to Login
            </a>
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { checkEmailExists } from '@/api/api';

// ================================= STATE =================================
const emit = defineEmits(['email-sent', 'email-not-found']);
const router = useRouter();
const email = ref('');
const showError = ref(false);

// ================================= FUNCTIONS =================================
const recoverPassword = async () => {
    if (!email.value) {
        showError.value = true;
        return;
    }

    showError.value = false;

    const exists = await checkEmailExists(email.value);

    if (!exists) {
        emit('email-not-found');
        return;
    }

    setTimeout(() => {
        emit('email-sent');
    }, 500);
};

const goToLogin = () => {
    router.push('/login');
};
</script>
