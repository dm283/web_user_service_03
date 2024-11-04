<script setup>
import VueApexCharts from 'vue3-apexcharts';
import { defineProps, computed, reactive } from 'vue';
import 'primeicons/primeicons.css';

  
const props = defineProps({
    label: String,
    value: Number,
});

</script>


<template>
    <div class="p-2 w-60 h-40 border border-gray-200 rounded-lg drop-shadow-md  
      bg-white hover:drop-shadow-lg text-center flex items-center justify-center">
      <!-- text-center  flex items-center justify-center -->
      <div class="">
        <!-- <div class="text-blue-400">
          <i class="pi pi-briefcase" style="font-size: 1.3rem; "></i>
        </div> -->
        <div class="text-sm font-semibold">{{ label }}</div>

        <div class="text-blue-500 pt-3 text-4xl font-normal">
          {{ value }}
        </div>
        <div class="text-gray-500">единиц</div>

      </div>
    </div>
</template>

