<template>
    <component
      :is="action ? 'button' : 'router-link'"
      :to="!action ? to : undefined"
      @click="action"
      class="flex items-center w-full px-3 py-3 text-[#020B80] no-underline rounded-lg transition-colors hover:bg-white/10 router-link-active:bg-white/20 router-link-active:font-medium"
    >
      <component :is="icons[icon]" class="h-5 w-5 mr-3" />
      <span>{{ label }}</span>
    </component>
  </template>
  
  <script setup>
  import { h } from 'vue';
  
  const props = defineProps({
    to: String,
    label: String,
    icon: String,
    action: Function // nova prop
  });
  
  const icons = {
    grid: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', stroke: 'currentColor', fill: 'none', strokeWidth: 2, class: 'lucide' }, [
      h('rect', { x: 3, y: 3, width: 7, height: 7 }),
      h('rect', { x: 14, y: 3, width: 7, height: 7 }),
      h('rect', { x: 14, y: 14, width: 7, height: 7 }),
      h('rect', { x: 3, y: 14, width: 7, height: 7 })
    ]),
    calendar: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', stroke: 'currentColor', fill: 'none', strokeWidth: 2, class: 'lucide' }, [
      h('rect', { x: 3, y: 4, width: 18, height: 18, rx: 2 }),
      h('line', { x1: 16, y1: 2, x2: 16, y2: 6 }),
      h('line', { x1: 8, y1: 2, x2: 8, y2: 6 }),
      h('line', { x1: 3, y1: 10, x2: 21, y2: 10 })
    ]),
    clock: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', stroke: 'currentColor', fill: 'none', strokeWidth: 2, class: 'lucide' }, [
      h('circle', { cx: 12, cy: 12, r: 10 }),
      h('polyline', { points: '12 6 12 12 16 14' })
    ]),
    users: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', stroke: 'currentColor', fill: 'none', strokeWidth: 2, class: 'lucide' }, [
      h('path', { d: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' }),
      h('circle', { cx: 9, cy: 7, r: 4 }),
      h('path', { d: 'M23 21v-2a4 4 0 0 0-3-3.87' }),
      h('path', { d: 'M16 3.13a4 4 0 0 1 0 7.75' })
    ]),
    user: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', stroke: 'currentColor', fill: 'none', strokeWidth: 2, class: 'lucide' }, [
      h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
      h('circle', { cx: 12, cy: 7, r: 4 })
    ]),
    logout: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', stroke: 'currentColor', fill: 'none', strokeWidth: 2, class: 'lucide' }, [
      h('path', { d: 'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4' }),
      h('polyline', { points: '16 17 21 12 16 7' }),
      h('line', { x1: 21, y1: 12, x2: 9, y2: 12 })
    ])
  };
  </script>
  