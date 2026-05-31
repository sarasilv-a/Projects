<template>
    <div class="w-1/2 flex items-center justify-center">
        <div class="w-3/4 max-w-md">
            <h1 class="text-3xl font-bold text-center mb-2 text-[#020C80]">Welcome back</h1>
            <p class="text-center text-[#020b80]/60 mb-8">Login to your Swap account</p>
            <div class="space-y-6">
                <div>
                    <label for="email" class="block mb-2 text-[#020C80] font-semibold">Email</label>
                    <input type="email" id="email" v-model="email" placeholder="xxxxxxx@uminho.pt" :class="[
                        'w-full p-3 rounded border text-sm',
                        showErrors && !email ? 'border-red-500' : 'border-[rgba(0,13,128,0.5)]'
                    ]" />
                </div>
                <div class="relative">
                    <label for="password" class="block mb-2 text-[#020C80] font-semibold">Password</label>
                    <a href="#" @click.prevent="goToRecoverPassword"
                        class="absolute right-0 top-0 text-sm text-[#020C80] hover:underline">
                        Forgot your password?
                    </a>
                    <input type="password" id="password" v-model="password" placeholder="Insert your password here"
                        :class="[
                            'w-full p-3 rounded border text-sm mt-1',
                            showErrors && !password ? 'border-red-500' : 'border-[rgba(0,13,128,0.5)]'
                        ]" />
                </div>
                <div v-if="showErrors && (!email || !password)" class="text-red-500 text-sm">
                    Please fill the camps above
                </div>
                <button @click="handleLogin"
                    class="w-full py-3 rounded-3xl font-medium text-[#020C80] bg-[rgba(76,146,241,0.5)] hover:bg-[rgba(76,146,241,0.7)] transition duration-300">
                    Login
                </button>
            </div>
            <div class="mt-6 text-center text-sm">
                Don't have an account?
                <a href="#" @click.prevent="goToRegister" class="text-[#020C80] font-semibold hover:underline">
                    Sign up
                </a>
            </div>
            <div class="mt-8 text-center text-gray-600 text-sm">
                Check out the best shifts at
                <a href="https://calendario.cesium.di.uminho.pt/" class="text-[#020C80] font-semibold hover:underline">
                    Calendarium
                </a>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// ================================= IMPORT =================================
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useSessionStore } from '@/stores/session';
import { login as apiLogin } from '@/api/api';

// ================================= STATE =================================
const emit = defineEmits(['wrong-credentials']);
const router = useRouter();
const session = useSessionStore();
const email = ref('');
const password = ref('');
const showErrors = ref(false);

// ================================= FUNCTIONS =================================
const handleLogin = async () => {
    showErrors.value = false;

    if (!email.value || !password.value) {
        showErrors.value = true;
        return;
    }

    const result = await apiLogin(email.value, password.value);

    if (result) {
        session.login(String(result.id), result.name, result.type);
        if (result.type === 'student') {
            router.push('/student/schedule');
        } else if (result.type === 'director') {
            router.push('/director/dashboard');
        }
    } else {
        emit('wrong-credentials');
    }
};

const goToRecoverPassword = () => {
    router.push('/recover-password');
};

const goToRegister = () => {
    router.push('/register');
};
</script>
