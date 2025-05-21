<script setup>
import { ref, defineProps, computed, reactive } from 'vue';
import 'primeicons/primeicons.css';

const props = defineProps({
    label: String,
    icon: String,
    description: String,
});

</script>


<template>
  <div class="bg-white border rounded-lg shadow-md w-96 h-20 py-3 px-5 text-blue-400 cursor-pointer hover:shadow-lg hover:text-indigo-500">
    <div class="float-left mt-1 mr-5">
      <i :class="`pi pi-${icon}`" style="font-size: 2.5rem"></i>
    </div>
    <div class="float-left">
      <div class="text-slate-700 text-base font-semibold">{{ label }}</div>
      <div class="mt-1 text-slate-500 text-sm">{{ description }}</div>
    </div>
  </div>
</template>
