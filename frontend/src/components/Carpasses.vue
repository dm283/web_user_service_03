<script setup>
import { defineProps, computed, reactive, onMounted, ref } from 'vue';
import axios from 'axios';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import ListAdv from '@/components/ListAdv.vue';
import FormAddCarpass from './FormAddCarpass.vue';
import FormDeleteCarpass from './FormDeleteCarpass.vue';
import FormRollbackCarpass from './FormRollbackCarpass.vue';

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
  
const showItemCard = ref(false)
const showAddItem = ref(false)
const showUpdateItem = ref(false)
const showDeleteItem = ref(false)
const showRollbackItem = ref(false)
const selectedItem = ref('')

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


async function downloadFile(document_id) {
  //
  // const document_id = 28;  
  
  const response = await axios.get(`http://${backendIpAddress}:${backendPort}/download_carpass/${document_id}`, {responseType: "blob"});
  const filename = decodeURI(response.headers["file-name"])

  var url = window.URL.createObjectURL(new Blob([response.data]));
  var link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};


// async function downloadFile(document_id) {
//   //
//   const fileDataUrl = `http://${backendIpAddress}:${backendPort}/download_carpass/16`
//   const pdfFileWindow = window.open(fileDataUrl)
//   pdfFileWindow.print()
// };



const editItem = (item) => {
  //
  showUpdateItem.value = true;
  selectedItem.value = item;
};

const deleteItem = (item) => {
  //
  showDeleteItem.value = true;
  selectedItem.value = item;
}

const itemCard = (item) => {
  showItemCard.value = true;
  selectedItem.value = item;
}

const rollbackItem = (item) => {
  //
  showRollbackItem.value = true;
  selectedItem.value = item;
}

const printItem = (item) => {
  //
  downloadFile(item.id);

};

</script>

<template>
  <!-- Show loading spinner while loading is true -->
  <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
    <PulseLoader />
    ЗАГРУЗКА ДАННЫХ...
  </div>

  <!-- Show when loading is done -->
  <div v-else>

  <!-- **********************   MODAL CARPASS CARD   ************************** -->
  <div v-if="showItemCard" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddCarpass @close-modal="showItemCard=false" @doc-created="getData" :itemData="selectedItem" :isCard="true"/>
  </div>


  <!-- **********************   MODAL ADD CARPASS   ************************** -->
  <div v-if="showAddItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddCarpass @close-modal="showAddItem=false" @doc-created="getData"/>
  </div>


  <!-- **********************   MODAL EDIT CARPASS   ************************** -->
  <div v-if="showUpdateItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddCarpass @close-modal="showUpdateItem=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>

  
  <!-- **********************   MODAL DELETE CARPASS   ************************** -->
  <div v-if="showDeleteItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormDeleteCarpass @close-modal="showDeleteItem=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL ROLLBACK CARPASS   ************************** -->
  <div v-if="showRollbackItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormRollbackCarpass @close-modal="showRollbackItem=false" @doc-created="getData" :itemData="selectedItem"/>
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
        <ListAdv @btn-add="showAddItem=true" @btn-edit="editItem" @btn-delete="deleteItem"
          @btn-refresh="getData" @btn-itemcard="itemCard" @btn-rollback="rollbackItem" @btn-print="printItem"
          :name="'Пропуска'" :data="state.records" :listTableColumns="listTableColumns" :listItemFileds="listItemFileds"/>
      </div>
    </div>
  </div>

  </div>
</template>
