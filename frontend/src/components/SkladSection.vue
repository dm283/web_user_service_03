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
  <div class="h-12 pl-5 py-4 text-xl font-normal">Складская группа</div>
  <div class="">
    <!-- <div class="block">
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/requests_batch_to_sklad">
        <CatalogSection :label="'Заявки размещения партий'" :icon="'directions'" :description="'Заявки размещения партий на склад'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="">
        <CatalogSection :label="'Заявки выдачи (выезда)'" :icon="'directions-alt'" :description="'в работе'" />
      </RouterLink>
    </div>
    </div> -->

    <div class="block">
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/add_cert_goods_accept">
        <CatalogSection :label="'Создать акт приёма'" :icon="'plus-circle'" :description="'Создание нового акта'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="/certs_goods_accept">
        <CatalogSection :label="'Принятые партии товаров'" :icon="'box'" :description="'Акты приёма товаров на склад'" />
      </RouterLink>
    </div>
    </div>

    <div class="block">
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="">
        <CatalogSection :label="'Создать акт выдачи'" :icon="'plus-circle'" :description="'в работе'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="">
        <CatalogSection :label="'Выдача партий товара'" :icon="'arrow-circle-right'" :description="'в работе'" />
      </RouterLink>
    </div>
    </div>

    <div class="block">
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="">
        <CatalogSection :label="'Остатки товаров по складу '" :icon="'database'" :description="'в работе'" />
      </RouterLink>
    </div>
    <div class="inline-block mt-5 ml-5">
      <RouterLink to="">
        <CatalogSection :label="'Услуги склада'" :icon="'briefcase'" :description="'в работе'" />
      </RouterLink>
    </div>
    </div>

  </div>
</div>
</template>
