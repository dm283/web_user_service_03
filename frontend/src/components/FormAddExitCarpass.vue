<script setup>
// import router from '@/router';
import {ref, reactive, computed, onMounted} from 'vue';
import { useToast } from 'vue-toastification';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import axios from 'axios';

import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");


const emit = defineEmits(['docCreated', 'closeModal']) // emit

const props = defineProps({
  isCreate: Boolean,
  itemData: Object,
  isCard: Boolean,
});

const state = reactive({
  documents: [],
  relatedCarpass: {},
  isLoading: true,
  responseItem: {},
})

const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}

const userAccessToken = () => {
  let user = JSON.parse(localStorage.getItem('user')); if (user && user.access_token) {return user.access_token} else {return ''}
}

// !!! if 'isCreate' - itemData=Carpass;  if 'not isCreate' (card/update) - itemData=Exitcarpass !!!

if (!props.isCreate && props.itemData) {
onMounted(async () => {
    try {
      // load info about parental Carpass
      const response1 = await axios.get(`http://${backendIpAddress}:${backendPort}/carpasses/${props.itemData.id_enter}`, 
        {headers: authHeader()});
      state.relatedCarpass = response1.data;
      // load related documents
      const response2 = await axios.get(`http://${backendIpAddress}:${backendPort}/entity_documents/${props.itemData.uuid}`, 
        {headers: authHeader()});
      state.documents = response2.data;
    } catch (error) {
      console.error('Error fetching docs', error);
    } finally {
      state.isLoading = false;
    }
});
};


const formInputStyleDis = 'text-base w-full py-1 px-1 mb-2'
const formInputStyleAct = 'bg-white border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer'
const formInputStyle = props.isCard ? formInputStyleDis : formInputStyleAct
const formInputStyleErr = 'bg-red-100 border-b-2 border-red-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-red-400 focus:outline-none focus:border-blue-500 cursor-pointer'

const errField = reactive({});
const form = reactive({});
const files = ref(null)

const itemFields = [
  'id_enter',
  'ncar',
  'driver_fio',
  'driver_phone',
  'driver_licence',
  'ndexit',
  'comment',
  'dateex',
  'timeex',
]

if (props.isCreate) {
  form.id_enter = props.itemData.id_enter;
  form.ncar = props.itemData.ncar;
  form.driver_fio = props.itemData.driver_fio
  form.driver_phone = props.itemData.driver_phone
  form.driver_licence = props.itemData.driver_licence
} else if (!props.isCreate) {
  for (let field of itemFields) {form[field] = props.itemData[field]}
};

const file = ref(null)
const toast = useToast();

const postingItem = async () => {
  //
  try {
    if (props.itemData) {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/exitcarpasses_posting/${props.itemData.id}`,
        '', {headers: authHeader()}
      );
      toast.success('Запись проведена');
    } else {
      return;
    }
    emit('docCreated'); emit('closeModal');
  } catch (error) {
    let err = error.response.data.detail;
    
    // special validation
    if (err == 'Отсутствует разрешение на выезд') {
      toast.error('Отсутствует разрешение на выезд');
    };

    // common validation - check required fields are not empty and correct
    let errFlag = 0;
    if (error.response.data.detail.hasOwnProperty('validation_errors')){
      let validation_errors_list = err['validation_errors']
      for (let e of validation_errors_list) { errField[e] = 1; errFlag = 1; }
    }
    if (errFlag) { toast.error('Не корректные/пропущенные данные') }

    console.error('Error posting item', error.response.data);
  };
};

const handleSubmit = async () => {
  // form submit handling (carpass create or update)
  let formData = new FormData();
    
  // item updating
  for (let field of itemFields) { formData.append(field, form[field]) };

  try {
    if (props.isCreate) {
      const response = await axios.post(`http://${backendIpAddress}:${backendPort}/exitcarpasses/`, 
        formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
      toast.success('Пропуск на выезд добавлен');
      state.responseItem = response.data;
    } else {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/exitcarpasses/${props.itemData.id}`, 
        formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
      toast.success('Пропуск на выезд обновлён');
      state.responseItem = response.data;  
    }

    // files uploading
    if (files.value) {
      for (let file of files.value.files) {
        formData.append('file', file);
        formData.append('contact_name', form.contact_name);
        try {
          const response = await axios.put(`http://${backendIpAddress}:${backendPort}/upload_file_for_carpass/${state.responseItem.uuid}`,
            formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        } catch (error) {
          console.error('Error uploading file', error);
          toast.error('File has not been uploaded');
        };
      };
    };

    emit('docCreated'); 
    emit('closeModal');
  } catch (error) {
    console.error('Error adding item', error);
    toast.error('Item has not added');
  };
};


async function downloadFile(document_id) {
  // downloads file
  const response = await axios.get(`http://${backendIpAddress}:${backendPort}/download-file/${document_id}`, 
    {responseType: "blob", headers: authHeader()});
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
  <div class="w-3/5 max-h-4/5 bg-white drop-shadow-md rounded-lg overflow-hidden">
    <header class="py-2 pl-6 bg-slate-200 text-black text-lg font-normal">
      Пропуск на выезд <span v-if="!props.isCreate">№ {{ props.itemData.id_exit }}</span>
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="emit('closeModal')"></i>
      </div>
    </header>

    <div class="ml-6 mt-3" v-if="!props.isCreate">
      <div class="inline-block mr-3 text-xs font-bold text-slate-500">Статус:</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-green-600" v-if="state.relatedCarpass.status=='exit_permitted'">
        ВЫЕЗД РАЗРЕШЁН</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-500" v-else-if="state.relatedCarpass.status=='archival'">
        АРХИВНЫЙ</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-red-600" v-else-if="state.relatedCarpass.status=='exit_prohibited'">
        ВЫЕЗД ЗАПРЕЩЁН</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-500" v-else>
        СТОЯНКА</div>
      <div class="ml-3 inline-block text-sm font-semibold text-red-400" v-if="!props.itemData.posted">ДОКУМЕНТ НЕ ПРОВЕДЁН</div>
    </div>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      
      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>№ пропуска на въезд</label>
          <input type="text" v-model="form.id_enter" :class=formInputStyleDis required disabled />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Номер машины</label>
          <input type="text" v-model="form.ncar" :class=formInputStyleDis required disabled />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>ФИО водителя</label>
          <input type="text" v-model="form.driver_fio" :class=formInputStyleDis required disabled />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Телефон водителя для связи</label>
          <input type="text" v-model="form.driver_phone" :class=formInputStyleDis required disabled />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Номер водительских прав</label>
          <input type="text" v-model="form.driver_licence" :class=formInputStyleDis required disabled />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Номер документа выпуска</label>
          <input type="text" v-model="form.ndexit" :class="[errField['ndexit']==1 ? formInputStyleErr : formInputStyle]"
            :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Примечание</label>
          <input type="text" v-model="form.comment" :class=formInputStyle :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Дата выезда</label>
          <input type="date" v-model="form.dateex" :class="[errField['dateex']==1 ? formInputStyleErr : formInputStyle]"
            :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Время выезда</label>
          <input type="time" v-model="form.timeex" :class="[errField['timeex']==1 ? formInputStyleErr : formInputStyle]"
            :disabled="isCard" />
        </div>
      </div>


      <div v-if="props.isCard || !props.isCreate">
      <!-- Show loading spinner while loading is true -->
      <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
        <PulseLoader /> ЗАГРУЗКА ДОКУМЕНТОВ...
      </div>
      <!-- Show when loading is done -->
      <div class="ml-6" v-if="!state.isLoading && state.documents.length>0">
        <label class=formLabelStyle>Документы</label>
        <div class="flex space-x-3 mt-3">
        <div class="border rounded-md p-2 w-15 h-30 text-center text-xs " v-for="document in state.documents">
          <div class="text-blue-500 cursor-pointer" @click="downloadFile(document.id)"><i class="pi pi-file" style="font-size: 1rem"></i></div>
          <div class="">{{ document.filename }}</div>
        </div>
        </div>
        </div>
      </div>

      <div v-if="!isCard" class="my-3 py-3 px-5 text-center overflow-auto">
      <!-- <div v-if="!isCard" class="my-3 flex justify-left space-x-5 py-3 px-5 text-center"> -->
        <div class="float-left space-x-5">
          <button class="formBtn" type="submit">СОХРАНИТЬ</button>
          <button class="formBtn" type="reset">ОЧИСТИТЬ</button>
          <input ref="files" name="files" type="file" multiple class="formInputFile" v-if="props.itemData"/>
        </div>
        <div class="float-right" v-if="!props.isCreate">
          <button class="formBtn" type="button" @click="postingItem">ПРОВОДКА</button>
        </div>
      </div>

      <div v-else class="mb-5"></div>

    </form>
  </div>

</template>


<style lang="postcss" scoped>

.formInputDiv {
  @apply w-64 mx-5 mb-2
}

.formInputFile {
  @apply text-sm text-slate-400 file:py-2 file:px-4 file:bg-white file:rounded-lg file:border-slate-300 file:text-sm file:font-normal
    file:text-slate-400 hover:file:bg-gray-100 cursor-pointer
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
