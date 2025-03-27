<script setup>
import { ref, defineProps, computed, reactive } from 'vue';
import 'primeicons/primeicons.css';

const props = defineProps({
    label: String,
    icon: String,
    description: String,
    selected: String,
});

const titleStyle = computed(() => {
  return props.selected == '1' ? 'flex text-blue-300' : 'flex'
})

</script>


<template>
  <div class="border-b h-16 py-3 px-3 cursor-pointer hover:text-cyan-300">
    <div :class=titleStyle>
      <div class="mr-3"><i :class="`pi pi-${icon}`" style="font-size: 1.3rem"></i></div>
      <div class="flex-1 text-sm font-semibold">{{ label }}</div>
      <!-- <div class=""><i class="pi pi-chevron-right"></i></div> -->
    </div>
    <div class="mt-1 text-xs text-slate-300">
      {{ description }}
    </div>
  </div>
</template>
