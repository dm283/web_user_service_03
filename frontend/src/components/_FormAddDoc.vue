<script setup>
// import router from '@/router';
import {ref, reactive} from 'vue';
import { useToast } from 'vue-toastification';
import axios from 'axios';

import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");


const emit = defineEmits(['docCreated']) // emit

const form = reactive({
  docName: '',
  guidConsignment: '',
  customerName: '',
});

const file = ref(null)

const initEmptyForm = () => {
    form.docName = ''
    form.guidConsignment = ''
    form.customerName = ''
}

initEmptyForm();

const toast = useToast();

const handleSubmit = async () => {
  // const newItem = {
  //   doc_name: form.docName,
  //   guid_consignment: form.guidConsignment,
  //   customer_name: form.customerName,
  //   file: file.value.files[0],
  // };

  let formData = new FormData();
  formData.append('doc_name', form.docName);
  formData.append('guid_consignment', form.guidConsignment);
  formData.append('customer_name', form.customerName);
  formData.append('file', file.value.files[0]);
  // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/single-file/`, 
  // formData, {headers: {'Content-Type': 'multipart/form-data'}});

  try {
    // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/documents/`, newItem);
    const response = await axios.post(`http://${backendIpAddress}:${backendPort}/document/`, 
      formData, {headers: {'Content-Type': 'multipart/form-data'}});

    toast.success('Новый документ добавлен');
    initEmptyForm();
    emit('docCreated') // emit
  } catch (error) {
    console.error('Error adding item', error);
    toast.error('Item has not added');
  };
};


</script>

<template>
  
  <div class="w-80 bg-white drop-shadow-md rounded-lg overflow-hidden hover:drop-shadow-lg">

    <header class="py-2 pl-6 bg-slate-200 text-black text-lg font-normal">
      Новый документ
      <!-- <div class="absolute top-2 right-4">
        <RouterLink
          to="/"
          class="hover:text-lime-600">
          <i class="pi pi-times" style="font-size: 1rem"></i>
        </RouterLink>
      </div> -->
    </header>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      
      <div class="mx-5 mb-2">
        <label class=formLabelStyle>Наименование документа</label>
        <input
          type="text"
          v-model="form.docName"
          id="docName"
          name="docName"
          class=formInputStyle
          placeholder=""
          required
        />
      </div>

      <div class="mx-5 mb-2">
        <label class=formLabelStyle>Партия товаров</label>
        <input
          type="number"
          step="1"
          v-model="form.guidConsignment"
          id="guidConsignment"
          name="guidConsignment"
          class=formInputStyle
          placeholder=""
          required
        />
      </div>

      <div class="mx-5 mb-2">
        <label class=formLabelStyle>Заказчик</label>
        <input
          type="text"
          v-model="form.customerName"
          id="customerName"
          name="customerName"
          class=formInputStyle
          placeholder=""
          required
        />
      </div>


      <div class="mx-5 mb-2">
        <label class=formLabelStyle>Файл</label>
        <input ref="file" name="file" type="file" 
          class=formInputFile
        />
      </div>

      <!-- <div class="mx-5 mb-2">
        <label class=formLabelStyle>Дата документа</label>
        <input
          type="date"
          v-model="form.established"
          id="established"
          name="established"
          class=formInputStyle
          placeholder=""
          required
        />
      </div> -->

      <!-- <div class="mx-5 mb-4">
        <input
          type="checkbox"
          v-model='form.isCapital'
          id="isCapital"
          name="isCapital"
          class=formInputCheckboxStyle
        />
        <label class=formLabelCheckboxStyle 
          @click="form.isCapital=(form.isCapital==true) ? false : true ;">Capital</label>
      </div> -->


      <div class="my-3 flex justify-center space-x-5 py-3 px-5 text-center">
        <button
          class="formBtn bg-teal-400 hover:bg-teal-500"
          type="submit"
        >
        Сохранить
        </button>
        <button
          class="formBtn bg-orange-300 hover:bg-orange-400"
          type="reset"
          @click=""
        >
        Очистить
        </button>
      </div>

    </form>
  </div>

</template>


<style lang="postcss" scoped>

.formInputFile {
  @apply mt-2 block w-full text-sm text-slate-500 
            file:my-0.5 file:ml-0.5 file:mr-4 file:py-2 file:px-4
            file:ring-1 file:ring-gray-200 file:rounded-full file:border-0 file:text-sm file:font-normal
            file:bg-gray-50 file:text-gray-600 hover:file:bg-gray-100 cursor-pointer
}

.formBtn {
@apply text-white font-semibold rounded-full px-3 pt-1.5 pb-2 w-32
  drop-shadow-md hover:shadow-lg 
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
