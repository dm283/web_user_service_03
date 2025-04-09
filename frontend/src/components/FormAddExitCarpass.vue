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
  isLoading: true
})

if (!props.isCreate && props.itemData) {
onMounted(async () => {
    try {
      // load info about parental Carpass
      const response1 = await axios.get(`http://${backendIpAddress}:${backendPort}/carpasses/${props.itemData.id_enter}`);
      state.relatedCarpass = response1.data;
      // load related documents
      const response2 = await axios.get(`http://${backendIpAddress}:${backendPort}/entity_documents/${props.itemData.uuid}`);
      state.documents = response2.data;
    } catch (error) {
      console.error('Error fetching docs', error);
    } finally {
      state.isLoading = false;
    }
});
};

const formInputStyle20 = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 hover:border-blue-400 focus:outline-none focus:border-blue-500'
const formInputStyle21 = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer'
const formInputStyleErr = 'bg-red-100 border-b-2 border-red-300 text-base w-full py-1 px-1 mb-2 hover:border-red-400 focus:outline-none focus:border-blue-500 cursor-pointer'
const formInputStyle2 = props.isCard ? formInputStyle20 : formInputStyle21
const formInputStyleDis = 'text-base w-full py-1 px-1 mb-2'

const errField = reactive({});
const form = reactive({});
const files = ref(null)

if (props.isCreate) {
  console.log('999creating !!!!!!', props.itemData)
  form.id_enter = props.itemData.id_enter;
  form.ncar = props.itemData.ncar;
  form.drv_man = props.itemData.drv_man
  form.dev_phone = props.itemData.dev_phone
  form.ndexit = ''
  form.comment = ''
  form.dateex = ''
  form.timeex = ''
} else if (!props.isCreate) {
  form.id_enter = props.itemData.id_enter;
  form.ncar = props.itemData.ncar;
  form.drv_man = props.itemData.drv_man
  form.dev_phone = props.itemData.dev_phone
  form.ndexit = props.itemData.ndexit
  form.comment = props.itemData.comment
  form.dateex = props.itemData.dateex
  form.timeex = props.itemData.timeex
};

const file = ref(null)
const toast = useToast();

const postingItem = async () => {
  //
  try {
    // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/documents/`, newItem);
    if (props.itemData) {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/exitcarpasses_posting/${props.itemData.id}`);
      toast.success('Пропуск проведён');
    } else {
      return;
    }

    emit('docCreated'); // emit
    emit('closeModal')
  } catch (error) {
    let err = error.response.data.detail
    // console.log('ответ =', error.response.data.detail)
    if (err.includes('Не установлен номер документа выпуска')) {
      errField['ndexit'] = 1;
      toast.error('Не заполнены обязательные поля');
    };    
    if (err.includes('Не установлена дата выезда')) {
      errField['dateex'] = 1;
      toast.error('Не заполнены обязательные поля');
    };
    if (err.includes('Не установлено время выезда')) {
      errField['timeex'] = 1;
      toast.error('Не заполнены обязательные поля');
    };
    console.error('Error posting item');
    // console.error('Error posting item', error);
  };
};

const handleSubmit = async () => {
  // form submit handling (carpass create or update)
  let formData = new FormData();

  // files uploading
  if (files.value) {
    for (let file of files.value.files) {
    formData.append('file', file);
    formData.append('contact_name', form.contact_name);
    try {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/upload_file_for_carpass/${props.itemData.uuid}`, 
        formData, {headers: {'Content-Type': 'multipart/form-data'}});
    } catch (error) {
      console.error('Error uploading file', error);
      toast.error('File has not been uploaded');
    };
  };
  };
            
  // carpass upgrading
  // formData.append('files', files.value.files);
  formData.append('id_enter', form.id_enter);
  formData.append('ncar', form.ncar);
  formData.append('drv_man', form.drv_man);
  formData.append('dev_phone', form.dev_phone);
  formData.append('ndexit', form.ndexit);
  formData.append('comment', form.comment);
  formData.append('dateex', form.dateex);
  formData.append('timeex', form.timeex);
  // formData.append('file', file.value.files[0]);
  // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/single-file/`, 
  // formData, {headers: {'Content-Type': 'multipart/form-data'}});

  try {
    // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/documents/`, newItem);
    if (props.isCreate) {
      const response = await axios.post(`http://${backendIpAddress}:${backendPort}/exitcarpasses/`, 
        formData, {headers: {'Content-Type': 'multipart/form-data'}});
      toast.success('Пропуск на выезд добавлен');
    } else {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/exitcarpasses/${props.itemData.id}`, 
        formData, {headers: {'Content-Type': 'multipart/form-data'}});
      toast.success('Пропуск на выезд обновлён');      
    }
    emit('docCreated'); // emit
    emit('closeModal')
  } catch (error) {
    console.error('Error adding item');
    //console.error('Error adding item', error);
    toast.error('Item has not added');
  };
};


async function downloadFile(document_id) {
  // downloads file
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
        <div class=formInputDiv>
          <label class=formLabelStyle>№ пропуска на въезд</label>
          <input
            type="text"
            v-model="form.id_enter"
            id="drv_man"
            name="drv_man"
            :class=formInputStyleDis
            placeholder=""
            required
            disabled
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Номер машины</label>
          <input
            type="text"
            v-model="form.ncar"
            id="ncar"
            name="ncar"
            :class=formInputStyleDis
            placeholder=""
            required
            disabled
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>ФИО водителя</label>
          <input
            type="text"
            v-model="form.drv_man"
            id="drv_man"
            name="drv_man"
            :class=formInputStyleDis
            placeholder=""
            required
            disabled
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Телефон водителя для связи</label>
          <input
            type="text"
            v-model="form.dev_phone"
            id="dev_phone"
            name="dev_phone"
            :class=formInputStyleDis
            placeholder=""
            required
            disabled
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>Номер документа выпуска</label>
          <input
            type="text"
            v-model="form.ndexit"
            id="ndexit"
            name="ndexit"
            :class="[errField['ndexit']==1 ? formInputStyleErr : formInputStyle2]"
            placeholder=""
            :disabled="isCard"
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Примечание</label>
          <input
            type="text"
            v-model="form.comment"
            id="comment"
            name="comment"
            :class=formInputStyle2
            placeholder=""
            :disabled="isCard"
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>Дата выезда</label>
          <input
            type="date"
            v-model="form.dateex"
            id="dateex"
            name="dateex"
            :class="[errField['dateex']==1 ? formInputStyleErr : formInputStyle2]"
            placeholder=""
            :disabled="isCard"
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Время выезда</label>
          <input
            type="time"
            v-model="form.timeex"
            id="timeex"
            name="timeex"
            :class="[errField['timeex']==1 ? formInputStyleErr : formInputStyle2]"
            placeholder=""
            :disabled="isCard"
          />
        </div>
      </div>



      <!-- <div class="mx-5 mb-2">
        <label class=formLabelStyle>Файл</label>
        <input ref="file" name="file" type="file" 
          class=formInputFile
        />
      </div> -->

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
        <div class="float-right" v-if="props.itemData">
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
