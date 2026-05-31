<script lang="ts" setup>
import { RouterView } from 'vue-router'
import './index.css'
</script>

<template>
  <RouterView :key="$route.fullPath" />
</template>
