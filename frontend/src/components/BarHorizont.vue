<script setup>
import VueApexCharts from 'vue3-apexcharts';
import { defineProps, computed } from 'vue';
  
const props = defineProps({
    name: String,
    title: String,
    xtitle: String,
    ytitle: String,
    barcolor: String,
    datax: Array,
    datay: Array,
});

// const name = props.name;
const apexcharts = VueApexCharts;

const figureFontFamily = 'ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"'

const options = {
  chart: {
    id: 'basic-bar-horizont',
  },
  plotOptions: {
    bar: {
      horizontal: true,
    }
  },
  title: {
    text: props.title,
    style: {fontFamily: figureFontFamily, fontSize: '20px', fontWeight: 'normal', color: 'black', }
  },
  colors: [props.barcolor],
  xaxis: {
    title: { text: props.xtitle, 
      style: {fontFamily: figureFontFamily, fontSize: '16px', fontWeight: 'normal', color: 'black', }},
    categories: props.datax,
  },
  yaxis: {
    title: { text: props.ytitle, 
      style: {fontFamily: figureFontFamily, fontSize: '16px', fontWeight: 'normal', color: 'black', }},
  },
  dataLabels: {
    style: {
      fontSize: '13px',
      color: 'white',
    }
  },
};


const computedSeries = computed(() => {
  //
  let series = [{
    name: 'Количество',
    data: props.datay,
  }];
  return series;
});

</script>


<template>
  <div class="p-3 border border-gray-200 rounded-lg bg-white drop-shadow-md hover:drop-shadow-lg">
    <apexcharts width="465" height="280" type="bar" :options="options" :series="computedSeries">
    </apexcharts>  
  </div>
</template>
