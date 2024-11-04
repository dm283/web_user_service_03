<script setup>
import VueApexCharts from 'vue3-apexcharts';
import { defineProps, computed } from 'vue';
  
const props = defineProps({
    name: String,
    title: String,
    xtitle: String,
    ytitle: String,
    color: String,
    datax: Array,
    datay: Array,
});

// const name = props.name;
const apexcharts = VueApexCharts;

const options = {
  chart: {
    id: 'basic-line'
  },
  title: {
    text: props.title,
    style: {fontSize: '20px', fontWeight: 'bold', color: 'DarkSlategray', }
  },
  colors: [props.color],
  xaxis: {
    title: { text: props.xtitle, 
      style: {fontSize: '14px', fontWeight: 'bold', color: 'DarkSlategray', }},
    categories: props.datax,
  },
  yaxis: {
    title: { text: props.ytitle, 
      style: {fontSize: '14px', fontWeight: 'bold', color: 'DarkSlategray', }},
  },
  dataLabels: {
    enabled: true,
    style: {
      fontSize: '13px',
      color: 'white',
    }
  },
  markers: {
          size: 5
        },
};


const computedSeries = computed(() => {
  //
  let series = [{
    name: 'количество',
    data: props.datay,
  }];
  return series;
});

</script>


<template>
  <div class="inline-block drop-shadow-lg border border-gray-400 bg-gray-50 
    rounded-md m-5 p-3 hover:bg-gray-100">
    <apexcharts width="400" height="280" type="line" :options="options" :series="computedSeries"
    ></apexcharts>  
  </div>
</template>


<!-- width="500" height="350" -->
 <!-- 400 - 280 -->