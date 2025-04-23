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
  itemData: Object,
  isCard: Boolean,
});

const state = reactive({
  documents: [],
  isLoading: true
})

if (props.itemData) {
onMounted(async () => {
    try {
      const response = await axios.get(`http://${backendIpAddress}:${backendPort}/entity_documents/${props.itemData.uuid}`);
      state.documents = response.data;
    } catch (error) {
      console.error('Error fetching docs', error);
    } finally {
      state.isLoading = false;
    }
});
};

// const formInputStyle20 = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 hover:border-blue-400 focus:outline-none focus:border-blue-500'
// const formInputStyle21 = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer'
// const formInputStyle2 = props.isCard ? formInputStyle20 : formInputStyle21
const formInputStyleDis = 'text-base w-full py-1 px-1 mb-2'
const formInputStyleAct = 'bg-white border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer'
const formInputStyle = props.isCard ? formInputStyleDis : formInputStyleAct
const formInputStyleErr = 'bg-red-100 border-b-2 border-red-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-red-400 focus:outline-none focus:border-blue-500 cursor-pointer'

const errField = reactive({});
const form = reactive({});
const files = ref(null)

const initEmptyForm = () => {
    form.ncar = '_234РА23'
    form.dateen = ''
    form.timeen = ''
    form.ntir = '14'
    form.nkont = '16'
    form.driver = 'ООО Перевозчик'
    form.drv_man = 'Иванов Сидор'
    form.dev_phone = '322-223-322'
    form.contact = 111
    form.contact_name = 'ООО Контакт'
    form.contact_broker = 222
    form.broker_name = 'ООО Брокер'
    form.place_n = '13'
    form.radiation = false
    form.brokenAwning = false
    form.brokenSeal = false
    form.dateex = ''
    form.timeex = ''
}

if (props.itemData) {
  form.ncar = props.itemData.ncar;
  form.dateen = props.itemData.dateen
  form.timeen = props.itemData.timeen
  form.ntir = props.itemData.ntir
  form.nkont = props.itemData.nkont
  form.driver = props.itemData.driver
  form.drv_man = props.itemData.drv_man
  form.dev_phone = props.itemData.dev_phone
  form.contact = props.itemData.contact
  form.contact_name = props.itemData.contact_name
  form.contact_broker = props.itemData.contact_broker
  form.broker_name = props.itemData.broker_name
  form.place_n = props.itemData.place_n
  form.radiation = props.itemData.radiation
  form.brokenAwning = props.itemData.brokenAwning
  form.brokenSeal = props.itemData.brokenSeal
  form.dateex = props.itemData.dateex
  form.timeex = props.itemData.timeex
} else {
  initEmptyForm();
};

const file = ref(null)

const toast = useToast();

const postingItem = async () => {
  //
  try {
    if (props.itemData) {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/carpasses_posting/${props.itemData.id}`);
      toast.success('Запись проведена');
    } else {
      return;
    }

    emit('docCreated'); emit('closeModal');
  } catch (error) {
    let err = error.response.data.detail;
    
    // special validation
    // if (err == 'Отсутствует разрешение на выезд') {
    //   toast.error('Отсутствует разрешение на выезд');
    // };

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
  formData.append('ncar', form.ncar);
  formData.append('dateen', form.dateen);
  formData.append('timeen', form.timeen);
  formData.append('ntir', form.ntir);
  formData.append('nkont', form.nkont);
  formData.append('driver', form.driver);
  formData.append('drv_man', form.drv_man);
  formData.append('dev_phone', form.dev_phone);
  formData.append('contact', form.contact);
  formData.append('contact_name', form.contact_name);
  formData.append('contact_broker', form.contact_broker);
  formData.append('broker_name', form.broker_name);
  formData.append('place_n', form.place_n);
  formData.append('radiation', form.radiation);
  formData.append('brokenAwning', form.brokenAwning);
  formData.append('brokenSeal', form.brokenSeal);
  formData.append('dateex', form.dateex);
  formData.append('timeex', form.timeex);
  // formData.append('file', file.value.files[0]);
  // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/single-file/`, 
  // formData, {headers: {'Content-Type': 'multipart/form-data'}});

  try {
    // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/documents/`, newItem);
    if (!props.itemData) {
      const response = await axios.post(`http://${backendIpAddress}:${backendPort}/carpasses/`, 
        formData, {headers: {'Content-Type': 'multipart/form-data'}});
      toast.success('Новый пропуск добавлен');
    } else {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/carpasses/${props.itemData.id}`, 
        formData, {headers: {'Content-Type': 'multipart/form-data'}});
      toast.success('Пропуск обновлён');      
    }
    emit('docCreated'); // emit
    emit('closeModal')
  } catch (error) {
    console.error('Error adding item', error);
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
      Пропуск на въезд <span v-if="props.itemData">№ {{ props.itemData.id_enter }}</span>
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="emit('closeModal')"></i>
      </div>
    </header>

    <div class="ml-6 mt-3" v-if="props.isCard">
      <div class="inline-block mr-3 text-xs font-bold text-slate-500">Статус:</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-green-600" v-if="props.itemData.status=='exit_permitted'">
        ВЫЕЗД РАЗРЕШЁН</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-500" v-else-if="props.itemData.status=='archival'">
        АРХИВНЫЙ</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-red-600" v-else-if="props.itemData.status=='exit_prohibited'">
        ВЫЕЗД ЗАПРЕЩЁН</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-500" v-else>
        СТОЯНКА</div>

      <div class="ml-3 inline-block text-sm font-semibold text-red-400" v-if="!props.itemData.posted">ДОКУМЕНТ НЕ ПРОВЕДЁН</div>
    </div>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      
      <div class="flex">

        <div class="formInputDiv">
          <label class=formLabelStyle>Номер машины</label>
          <div :class=formInputStyle class="flex" @click="setFilter('ncar'); showDropDownSelect.ncar=true; 
                  console.log(234, showDropDownSelect)">
            <input class="w-64 focus:outline-none" type="text" v-model="devSelected.ncar" @keyup="setFilter('ncar')"/>
            <span><i class="pi pi-angle-down" style="font-size: 0.8rem"></i></span>
          </div>
          <div v-if="showDropDownSelect.ncar" class="bg-slate-100 border border-slate-400 rounded-md shadow-xl w-64 max-h-24 overflow-auto p-1 absolute">
            <div class="px-1.5 py-0.5 cursor-pointer hover:bg-blue-300" v-for="item in state.filteredList" 
              @click="devSelected.ncar=item.ncar; selectedItem=item; showDropDownSelect.ncar=false" >
              {{ item.ncar }}
            </div>
          </div>
        </div>



        <!-- <div class=formInputDiv>
          <label class=formLabelStyle>Номер машины</label>
          <input type="text" v-model="form.ncar" :class="[errField['ncar']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="isCard" />
        </div> -->
        <div class=formInputDiv>
          <label class=formLabelStyle>Дата въезда</label>
          <input type="date" v-model="form.dateen" :class="[errField['dateen']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Время въезда</label>
          <input
            type="time"
            v-model="form.timeen"
            id="timeen"
            name="timeen"
            :class="[errField['timeen']==1 ? formInputStyleErr : formInputStyle]"
            placeholder=""
            :required="false"
            :disabled="isCard"
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>Номер документа доставки</label>
          <input
            type="text"
            v-model="form.ntir"
            :class="[errField['ntir']==1 ? formInputStyleErr : formInputStyle]"
            :required="false"
            :disabled="isCard"
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Номер контейнера</label>
          <input
            type="text"
            v-model="form.nkont"
            :class="[errField['nkont']==1 ? formInputStyleErr : formInputStyle]"
            :required="false"
            :disabled="isCard"
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Наименование перевозчика</label>
          <input
            type="text"
            v-model="form.driver"
            :class="[errField['driver']==1 ? formInputStyleErr : formInputStyle]"
            :required="false"
            :disabled="isCard"
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>ФИО водителя</label>
          <input
            type="text"
            v-model="form.drv_man"
            :class="[errField['drv_man']==1 ? formInputStyleErr : formInputStyle]"
            :required="false"
            :disabled="isCard"
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Телефон водителя для связи</label>
          <input
            type="text"
            v-model="form.dev_phone"
            :class="[errField['dev_phone']==1 ? formInputStyleErr : formInputStyle]"
            :required="false"
            :disabled="isCard"
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Наименование клиента</label>
          <input
            type="text"
            v-model="form.contact_name"
            :class="[errField['contact_name']==1 ? formInputStyleErr : formInputStyle]"
            :required="false"
            :disabled="isCard"
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>Наименование брокера</label>
          <input
            type="text"
            v-model="form.broker_name"
            :class="[errField['broker_name']==1 ? formInputStyleErr : formInputStyle]"
            :required="false"
            :disabled="isCard"
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Номер стоянки</label>
          <input
            type="text"
            v-model="form.place_n"
            :class="[errField['place_n']==1 ? formInputStyleErr : formInputStyle]"
            :required="false"
            :disabled="isCard"
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <input type="checkbox" v-model='form.radiation' id="radiation" name="radiation" class=formInputCheckboxStyle :disabled="isCard"/>
          <label class=formLabelCheckboxStyle for="radiation">Радиация</label>
        </div>
        <div class=formInputDiv>
          <input type="checkbox" v-model='form.brokenAwning' id="brokenAwning" name="brokenAwning" class=formInputCheckboxStyle :disabled="isCard"/>
          <label class=formLabelCheckboxStyle for="brokenAwning">Порванный тент</label>
        </div>
        <div class=formInputDiv>
          <input type="checkbox" v-model='form.brokenSeal' id="brokenSeal" name="brokenSeal" class=formInputCheckboxStyle :disabled="isCard"/>
          <label class=formLabelCheckboxStyle for="brokenSeal">Повреждённая пломба</label>
        </div>
      </div>


      <div v-if="props.isCard || props.itemData">
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
