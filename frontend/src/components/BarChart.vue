<script setup>
import VueApexCharts from 'vue3-apexcharts';
import { defineProps, computed, reactive } from 'vue';
  
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
    id: 'basic-bar'
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
  // fill: {
  //   type: 'gradient',
  //   gradient: {
  //     shade: 'dark',
  //     type: "horizontal",
  //     shadeIntensity: 0.5,
  //     gradientToColors: undefined, // optional, if not defined - uses the shades of same color in series
  //     inverseColors: true,
  //     opacityFrom: 1,
  //     opacityTo: 1,
  //     stops: [0, 50, 100],
  //     colorStops: []
  //   }
  // }
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

<!-- width="500" height="350"    465 now = 473 -->
 <!-- 400 - 280 -->

