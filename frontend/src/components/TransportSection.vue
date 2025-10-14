<script setup>
import { defineProps, computed, reactive, onMounted, ref } from 'vue';
import axios from 'axios';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import CatalogSection from './CatalogSection.vue';

import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");


const userInfo = JSON.parse(localStorage.getItem('userInfo'));

const props = defineProps({
});

const state = reactive({
  records: [],
  isLoading: true,
  query: '',
  listTableColumns: {},
  additionalColumns: {},
  listItemFileds: {},
})
  
const showItemCard = ref(false)


const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}


</script>

<template>
<div class="bg-white">
  <div class="h-12 pl-5 py-4 text-xl font-normal">Транспортный отдел</div>
  <div class="">
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/entry_requests">
        <CatalogSection :label="'Заявки на въезд ТС'" :icon="'pen-to-square'" :description="'Информация о заявках на въезд ТС'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/carpasses">
        <CatalogSection :label="'Пропуска ТС на въезд'" :icon="'truck'" :description="'Информация о пропусках ТС на въезд'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/car_terminal">
        <CatalogSection :label="'ТС на терминале'" :icon="'car'" :description="'Информация о ТС на терминале'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/exitcarpasses">
        <CatalogSection :label="'Пропуска ТС на выезд'" :icon="'sign-out'" :description="'Информация о пропусках ТС на выезд'" />
      </RouterLink>
    </div>
  </div>
</div>
</template>
