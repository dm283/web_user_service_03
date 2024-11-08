import './assets/main.css'
import VueApexCharts from 'vue3-apexcharts'; //
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import router from './router';

import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App);

app.use(router);
app.use(VueApexCharts);  //
app.use(Toast);

app.mount('#app');
