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
  <div class="h-12 pl-5 py-4 text-xl font-normal">Диспетчер СВХ</div>
  <div class="">
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/add_batch">
        <CatalogSection :label="'Добавить партию товаров'" :icon="'file-plus'" :description="'Добавление новой партии товаров'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/batches">
        <CatalogSection :label="'Партии товаров'" :icon="'shopping-bag'" :description="'Работа с партиями товаров'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/registration_dt">
        <CatalogSection :label="'Регистрация ДТ'" :icon="'clipboard'" :description="'Регистрация ДТ'" />
      </RouterLink>
    </div>
  </div>
</div>
</template>
