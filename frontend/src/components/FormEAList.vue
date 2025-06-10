<script setup>
// import router from '@/router';
import {ref, reactive, computed, onMounted} from 'vue';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import { useToast } from 'vue-toastification';
import axios from 'axios';
import ListAdv from '@/components/ListAdv.vue';

import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");

const toast = useToast();

const emit = defineEmits(['docCreated', 'closeModal', 'returnedDocs']) // emit

const props = defineProps({
});

const state = reactive({
  choosenDocs: [],
  records: [],
  isLoading: true,
  query: '',
  listTableColumns: {},
  additionalColumns: {},
  listItemFileds: {},
})

const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}


state.query = `http://${backendIpAddress}:${backendPort}/document_records/`
state.listTableColumns = {
    'doc_name':'Наименование','doc_id':'Номер','doc_date':'Дата','contact_uuid':'Контрагент','created_datetime':'Дата загрузки'
  };
state.additionalColumns = {  };
state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};


async function getData() {
    state.isLoading = true;
    try {     
      const response = await axios.get(state.query, {headers: authHeader()});
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


const chooseDoc = (item) => {
  if (item) { state.choosenDocs.push(item) }
}

const returnToObjForm = () => {
  // console.log('return with', state.choosenDocs.length, 'documents')
  emit('returnedDocs', state.choosenDocs); emit('closeModal');
}

</script>

<template>
  <div class="w-74 max-h-4/5 bg-white drop-shadow-md rounded-lg overflow-hidden">
  
    <header class="py-2 pl-6 bg-slate-200 text-black text-lg font-normal">
      Электронный архив
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="emit('closeModal')"></i>
      </div>
    </header>

    <button class="formBtn" type="button" @click="returnToObjForm()">ПРИВЯЗАТЬ</button>

    <div class="flex">
      <div class="" v-for="doc in state.choosenDocs">
        <div class="">{{ doc.doc_name }}</div>
      </div>
    </div>

  <!-- Show loading spinner while loading is true -->
  <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
    <PulseLoader />
    ЗАГРУЗКА ДАННЫХ...
  </div>

  <!-- Show when loading is done -->
  <div v-else>
  <div class="flex flex-col md:flex-row p-3 gap-3 ">
    <div class="flex-auto w-auto md:w-64">
      <div class="">
        <ListAdv @btn-choose="chooseDoc"
          :name="'Электронный архив'" :data="state.records" :listTableColumns="state.listTableColumns" :listItemFileds="state.listItemFileds"/>
      </div>
    </div>
  </div>
  </div>

  </div>

</template>


<style lang="postcss" scoped>

.formInputDiv {
  @apply w-64 mx-5 mb-2
}

.formInputFile {
  @apply mt-2 block w-full text-sm text-slate-500 
            file:my-0.5 file:ml-0.5 file:mr-4 file:py-2 file:px-4
            file:ring-1 file:ring-gray-200 file:rounded-full file:border-0 file:text-sm file:font-normal
            file:bg-gray-50 file:text-gray-600 hover:file:bg-gray-100 cursor-pointer
}

.formBtn {
  @apply text-slate-400 text-sm font-semibold border border-slate-400 rounded-lg w-32 h-9 hover:text-slate-500 hover:border-slate-500
}

.formLabelStyle {
  @apply mx-1 block text-xs font-bold text-slate-400 
}
.formInputStyle {
  @apply border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer
}
.formLabelCheckboxStyle {
  @apply ml-3 text-base font-semibold text-gray-400 cursor-pointer
}
.formInputCheckboxStyle {
    @apply ml-1 w-4 h-4 cursor-pointer
}


/* number formtype without arrows  -   Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
/* number formtype without arrows  -   Firefox */
input[type=number] {
  -moz-appearance: textfield;
}
</style>
