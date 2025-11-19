<script setup>
import {ref, reactive, computed, onMounted, watch} from 'vue';
import { useToast } from 'vue-toastification';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import axios from 'axios';
import FormEAList from './FormEAList.vue';
import FormDoc from './FormDoc.vue';
import FormAskCloseWithoutSave from './FormAskCloseWithoutSave.vue';
import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");

const toast = useToast();
const userInfo = JSON.parse(localStorage.getItem('userInfo'));
const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}
const userAccessToken = () => {
  let user = JSON.parse(localStorage.getItem('user')); if (user && user.access_token) {return user.access_token} else {return ''}
}

const msgOkStyle = 'text-green-500'
const msgErrStyle = 'text-red-500'

const file = ref(null)
const res_message = reactive({})

const previewFiles = async (entity) => {
  let formData = new FormData();
  for (let f of file.value.files) {
    formData.append('file', f)
    formData.append('entity', entity)
    try {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/upload_file/`, 
        formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
      console.log('Ok', response.data)
      res_message['msg'] = response.data.detail
      res_message['status'] = 'ok'
    } catch (error) {
      console.error('Error uploading file', error.response.data);
      res_message['msg'] = error.response.data.detail
      res_message['status'] = 'error'

    }; } }


async function downloadFile(file_name) {
  // downloads file
  let query = `http://${backendIpAddress}:${backendPort}/download-file-by-filename/${file_name}`
  const response = await axios.get(query, {responseType: "blob", headers: authHeader()});
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
<div class="p-3">
  <div class="text-xl font-normal mb-5">Загрузка списков Excel</div>
  <div class="inline-block mr-5" >Загрузить список клиентов</div>
  <input ref="file" name="file" type="file" @change="previewFiles('clients')" class="formInputFile inline-block mr-5"/>
  <div class="inline-block mr-5" :class="[res_message['status']=='ok' ? msgOkStyle : msgErrStyle]">
    {{ res_message['msg'] }}
  </div>
  <div class="mt-3"><button class="formBtn" type="button" @click="downloadFile('contacts-upload.xlsx')">Скачать шаблон</button></div>
</div>
</template>

<style lang="postcss" scoped>

.contStyle {
  max-height: 600px;
  overflow-y: auto;
}

.formInputDiv {
  @apply w-64 mx-5 mb-2
}

.formInputFile {
  @apply text-sm text-slate-400 file:py-2 file:px-4 file:bg-white file:rounded-lg file:border-slate-300 file:text-sm file:font-normal
    file:text-slate-400 hover:file:bg-gray-100 cursor-pointer
}

.formBtnExcel {
  @apply bg-white text-slate-400 text-sm font-semibold border border-slate-400 rounded-lg w-64 h-9 hover:text-slate-500 hover:border-slate-500
  active:border-2 active:border-blue-400
}

.formBtn {
  @apply text-slate-400 text-sm font-semibold border border-slate-400 rounded-lg w-32 h-9 hover:text-slate-500 hover:border-slate-500
  active:border-2 active:border-blue-400
}

.formBtn2 {
  @apply text-red-400 text-sm font-semibold border border-slate-400 rounded-lg w-32 h-9 hover:text-slate-500 hover:border-slate-500
}

.formLabelStyle {
  @apply mx-1 block text-xs font-bold text-slate-400 
}

.formLabelCheckboxStyle {
  @apply ml-2 text-xs font-bold text-slate-400 cursor-pointer
}
.formInputCheckboxStyle {
    @apply w-4 h-4 cursor-pointer
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