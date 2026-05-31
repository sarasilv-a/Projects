<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50" @click.self="close">
    <div class="bg-white rounded-xl p-6 w-80 shadow-xl relative text-center">
      <div class="absolute top-2 right-3 text-gray-600 text-xl cursor-pointer" @click="close">×</div>
      <h2 class="text-xl font-semibold text-[#1a237e] mb-4">{{ title }}</h2>
      <div class="mb-5">
        <slot></slot>
      </div>
      <button
        class="bg-[#6c8dff] hover:bg-[#5a75d6] text-white rounded-full px-6 py-2 w-4/5 text-sm transition"
        @click="handleButtonClick"
      >
        {{ buttonText }}
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Alert'
  },
  buttonText: {
    type: String,
    default: 'OK'
  }
});

const emit = defineEmits(['close', 'button-click']);

const close = () => {
  emit('close');
};

const handleButtonClick = () => {
  emit('button-click');
  emit('close');
};
</script>
