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
  <div class="h-12 pl-5 py-4 text-xl font-normal">Справочники</div>
  <div class="">
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/contacts">
        <CatalogSection :label="'Клиенты'" :icon="'address-book'" :description="'Информация о клиентах'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/brokers">
        <CatalogSection :label="'Брокеры'" :icon="'pen-to-square'" :description="'Информация о брокерах'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/carriers">
        <CatalogSection :label="'Перевозчики'" :icon="'truck'" :description="'Информация о перевозчиках'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/drivers">
        <CatalogSection :label="'Водители'" :icon="'users'" :description="'Информация о водителях'" />
      </RouterLink>
    </div>
  </div>
</div>
</template>
