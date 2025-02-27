<script setup>
import { defineProps, computed, reactive, onMounted, ref } from 'vue';
import axios from 'axios';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import ListAdv from '@/components/ListAdv.vue';
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
  
const showAddItem = ref(false)

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
  <div v-else>

  <!-- **********************   MODAL ADD CARPASS   ************************** -->
  <div v-if="showAddItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddCarpass @close-modal="showAddItem=false" @doc-created="getData" />

    <!-- <div class="flex-col w-3/5 h-4/5 bg-white rounded-lg">

      <div class="py-3 pl-7 pr-3 bg-gray-200 rounded-t-lg overflow-auto">
        <div class="float-left text-xl">
          {{ props.name }}
        </div>
        <div class="float-right cursor-pointer hover:text-gray-500" @click="showAddItem=false">
          <i class="pi pi-times" style="font-size: 1.5rem"></i>
        </div>
      </div>
      
    </div> -->
  </div>

  
  <div class="flex flex-col md:flex-row p-3 gap-3 ">
    <!-- <div class="flex-none w-fit md:w-auto">
      <div class="flex flex-col gap-3">
        <div class="">
          <FormAddCarpass @doc-created="getData" />
        </div>
        <div class="text-center">
          <button @click="downloadFile()" class="border rounded-full p-3 text-white bg-pink-400">
            DOWNLOAD FILE
          </button>
        </div>
      </div>
    </div> -->
    <div class="flex-auto w-auto md:w-64">
      <div class="">
        <ListAdv @btn-add="showAddItem=true" @btn-edit="console.log('btn edit!!!')" @btn-delete="console.log('btn delete!!!')"
          @btn-refresh="console.log('btn refresh!!!')"
          :name="'Пропуска'" :data="state.records" :listTableColumns="listTableColumns" :listItemFileds="listItemFileds"/>
      </div>
    </div>
  </div>

  </div>
</template>
