<script setup>
import { defineProps, computed, reactive, onMounted, ref } from 'vue';
import axios from 'axios';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import ListAdv from '@/components/ListAdv.vue';
import FormAddCarpass from './FormAddCarpass.vue';
import FormDeleteCarpass from './FormDeleteCarpass.vue';
import FormRollbackCarpass from './FormRollbackCarpass.vue';
import FormCarExitPermit from './FormCarExitPermit.vue';
import FormAddExitCarpass from './FormAddExitCarpass.vue';

import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");

  
const props = defineProps({
  view_type: String,
  list_title: String,
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
const showAddItem = ref(false)
const showUpdateItem = ref(false)
const showDeleteItem = ref(false)
const showRollbackItem = ref(false)
const showCarExitPermit = ref(false)
const showCardExitCarpass = ref(false)
const showCreateExitCarpass = ref(false)
const showUpdateExitCarpass = ref(false)

const selectedItem = ref('')
const itemName = ref('')


if (props.view_type == 'enter') {
  state.query = `http://${backendIpAddress}:${backendPort}/carpasses/`;
  state.listTableColumns = {
    'id_enter':'id','ncar':'№ машины','dateen':'Дата въезда',
    'timeen':'Время въезда', 'ntir':'№ документа доставки', 'nkont':'№ контейнера', 
    'contact_name':'Наименование клиента', 'place_n':'№ стоянки', 'dateex':'Дата выезда', 'timeex':'Время выезда'
  };
  state.additionalColumns = {
      'driver':'Перевозчик','drv_man':'ФИО водителя','dev_phone':'Телефон водителя для связи'
  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
} else if (props.view_type == 'terminal') {
  state.query = `http://${backendIpAddress}:${backendPort}/car_terminal/`;
  state.listTableColumns = {
    'id_enter':'id','ncar':'№ машины','dateen':'Дата въезда',
    'timeen':'Время въезда', 'ntir':'№ документа доставки', 'nkont':'№ контейнера', 
    'contact_name':'Наименование клиента', 'place_n':'№ стоянки', 'dateex':'Дата выезда', 'timeex':'Время выезда'
  };
  state.additionalColumns = {
      'driver':'Перевозчик','drv_man':'ФИО водителя','dev_phone':'Телефон водителя для связи'
  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
} else if (props.view_type == 'exitCarpass') {
  state.query = `http://${backendIpAddress}:${backendPort}/exitcarpasses/`;
  state.listTableColumns = {
    'id_exit':'id', 'id_enter':'Пропуск на въезд', 'ncar':'№ машины',
    'drv_man':'ФИО водителя','dev_phone':'Телефон водителя для связи',
    'ndexit':'№ документа выпуска',
    'dateex':'Дата выезда', 'timeex':'Время выезда'
  };
  state.additionalColumns = {
      'comment':'Примечание'
  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
};


async function getData() {
    state.isLoading = true;
    try {     
      const response = await axios.get(state.query);
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



const editItem = (item, name) => {
  // opens modal for editing item
  selectedItem.value = item;
  if (name == 'Пропуска ТС на въезд') {
    showUpdateItem.value = true;
  } else if (name == 'Пропуска ТС на выезд') {
    showUpdateExitCarpass.value = true;
  }
};

const deleteItem = (item, name) => {
  //
  selectedItem.value = item;
  itemName.value = name;
  showDeleteItem.value = true;
}

const itemCard = (item, name) => {
  //
  selectedItem.value = item;
  if (name == 'Пропуска ТС на въезд' || name == 'ТС на терминале') {
    showItemCard.value = true;
  } else if (name == 'Пропуска ТС на выезд') {
    showCardExitCarpass.value = true;
  }
}

const rollbackItem = (item, name) => {
  //
  selectedItem.value = item;
  itemName.value = name;
  showRollbackItem.value = true;
};

const printItem = (item) => {
  //
  downloadFile(item.id);
};

const setStatusExit = (item) => {
  //
  showCarExitPermit.value = true;
  selectedItem.value = item;
};

const createExitCarpass = (item) => {
  //
  showCreateExitCarpass.value = true;
  selectedItem.value = item;
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
    <FormDeleteCarpass @close-modal="showDeleteItem=false" @doc-created="getData" :itemName="itemName" :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL ROLLBACK CARPASS   ************************** -->
  <div v-if="showRollbackItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormRollbackCarpass @close-modal="showRollbackItem=false" @doc-created="getData" :itemName="itemName" :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL CAR EXIT PERMIT   ************************** -->
  <div v-if="showCarExitPermit" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormCarExitPermit @close-modal="showCarExitPermit=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL EXITCARPASS CARD   ************************** -->
  <div v-if="showCardExitCarpass" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddExitCarpass @close-modal="showCardExitCarpass=false" @doc-created="getData" :itemData="selectedItem" :isCard="true"/>
  </div>


  <!-- **********************   MODAL EXITCARPASS ADD   ************************** -->
  <div v-if="showCreateExitCarpass" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddExitCarpass @close-modal="showCreateExitCarpass=false" @doc-created="getData" :isCreate=true :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL EXITCARPASS EDIT  ************************** -->
  <div v-if="showUpdateExitCarpass" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddExitCarpass @close-modal="showUpdateExitCarpass=false" @doc-created="getData" :isCreate=false :itemData="selectedItem"/>
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
        <ListAdv @btn-add="showAddItem=true" @btn-edit="editItem" @btn-delete="deleteItem" @btn-createexitcarpass="createExitCarpass"
          @btn-refresh="getData" @btn-itemcard="itemCard" @btn-rollback="rollbackItem" @btn-print="printItem" @btn-setstatusexit="setStatusExit"
          :name="props.list_title" :data="state.records" :listTableColumns="state.listTableColumns" :listItemFileds="state.listItemFileds"/>
      </div>
    </div>
  </div>

  </div>
</template>
