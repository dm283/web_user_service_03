<script setup>
import { defineProps, computed, reactive, onMounted, ref } from 'vue';
import axios from 'axios';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import List from '@/components/List.vue';
import FormAddCarpass from './FormAddCarpass.vue';

import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");

  
const props = defineProps({
});

const state = reactive({
  records: [],
  isLoading: true
})
  

async function getData() {
    state.isLoading = true;
    try {
      const response = await axios.get(`http://${backendIpAddress}:${backendPort}/carpasses/`);
      state.records = response.data;
    } catch (error) {
      console.error('Error fetching', error);
    } finally {
      state.isLoading = false;
    }
}

onMounted(async () => {
    await getData()
});


const listTableColumns = {
    'id_enter':'id','ncar':'№ машины','dateen':'Дата въезда',
    'timeen':'Время въезда', 'ntir':'№ документа доставки', 'nkont':'№ контейнера', 
    'contact_name':'Наименование клиента', 'place_n':'№ стоянки', 'dateex':'Дата выезда', 'timeex':'Время выезда'
}

const additionalColumns = {
    'driver':'Перевозчик','drv_man':'ФИО водителя','dev_phone':'Телефон водителя для связи'
}

const listItemFileds = {...listTableColumns, ...additionalColumns};


/////////
const file = ref(null)

// async function formFileSave() {
//   console.log("selected file", file.value.files[0])
//   let formData = new FormData();
//   formData.append('file', file.value.files[0]);
//   const response = await axios.post(`http://${backendIpAddress}:${backendPort}/single-file/`, 
//     formData, {headers: {'Content-Type': 'multipart/form-data'}});
// }


async function downloadFile() {
  //
  const document_id = 28;  
  
  const response = await axios.get(`http://${backendIpAddress}:${backendPort}/download-file/${document_id}`, {responseType: "blob"});
  const filename = decodeURI(response.headers["file-name"])

  var url = window.URL.createObjectURL(new Blob([response.data]));
  var link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

</script>

<template>
  <!-- Show loading spinner while loading is true -->
  <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
    <PulseLoader />
    ЗАГРУЗКА ДАННЫХ...
  </div>

  <!-- Show when loading is done -->
  <div v-else class="flex flex-col md:flex-row p-3 gap-3 ">
    <div class="flex-none w-fit md:w-auto">
      <div class="flex flex-col gap-3">
        <!-- <div class="grid grid-cols-2 gap-3">
          <div class="">
            <Card :label="'Кол-во документов'" :value="state.documents.length" />
          </div>
          <div class="">
            <Card :label="'Добавлено сегодня'" :value="1" />
          </div>
        </div> -->
        <div class="">
          <FormAddCarpass @doc-created="getData" />
        </div>
        <div class="text-center">
          <button @click="downloadFile()" class="border rounded-full p-3 text-white bg-pink-400">
            DOWNLOAD FILE
          </button>
        </div>
      </div>
    </div>
    <div class="flex-auto w-auto md:w-64">
      <div class="">
        <List :name="'Пропуска'" :data="state.records" :listTableColumns="listTableColumns" :listItemFileds="listItemFileds"/>
      </div>
    </div>
  </div>
</template>

<!-- #00E396  #FF69B4  #CD5C5C  #FFA07A  #7B68EE  #00FF7F  #00BFFF -->
