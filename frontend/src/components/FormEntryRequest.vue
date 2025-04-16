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


const emit = defineEmits(['docCreated', 'closeModal'])

const props = defineProps({
  itemData: Object,  // card or edit - exists; create - empty
  isCard: Boolean,   // card - true
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

const formInputStyleDis = 'text-base w-full py-1 px-1 mb-2'
const formInputStyleAct = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer'
const formInputStyle = props.isCard ? formInputStyleDis : formInputStyleAct

const form = reactive({});

const files = ref(null)

const itemFields = [
    'ncar',
    'plan_dateen',
    'plan_timeen_from',
    'plan_timeen_to',
    'drv_man',
    'drv_licence',
    'car_model',
    'entry_type',
    'contact',
    'ntir',
    'ntir_date',
    'customs_doc',
    'customs_doc_date',
    'comment',
  ]

const initEmptyForm = () => {
    form.ncar = '_234РА23'
    form.plan_dateen = ''
    form.plan_timeen_from = ''
    form.plan_timeen_to = ''
    form.drv_man = 'Иванов Сидор'
    form.drv_licence = 'Р456НВ'
    form.car_model = 'Volvo F7'
    form.entry_type = 'Привоз груза'
    form.contact = 111
    form.ntir = 'К345НГ32'
    form.ntir_date = ''
    form.customs_doc = 'П34КНР23'
    form.customs_doc_date = ''
    form.comment = ''
};

if (props.itemData) {
  for (let field of itemFields) {form[field] = props.itemData[field]}
  // form['ncar'] = props.itemData['ncar']
  // form.plan_dateen = props.itemData.plan_dateen
  // form.plan_timeen_from = props.itemData.plan_timeen_from
  // form.plan_timeen_to = props.itemData.plan_timeen_to
  // form.drv_man = props.itemData.drv_man
  // form.drv_licence = props.itemData.drv_licence
  // form.car_model = props.itemData.car_model
  // form.entry_type = props.itemData.entry_type
  // form.contact = props.itemData.contact
  // form.ntir = props.itemData.ntir
  // form.ntir_date = props.itemData.ntir_date
  // form.customs_doc = props.itemData.customs_doc
  // form.customs_doc_date = props.itemData.customs_doc_date
  // form.comment = props.itemData.comment
} else {
  initEmptyForm();
};

const file = ref(null)

const toast = useToast();

const postingItem = async () => {
  //
  try {
    // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/documents/`, newItem);
    if (props.itemData) {
      //const response = await axios.put(`http://${backendIpAddress}:${backendPort}/carpasses_posting/${props.itemData.id}`);
      toast.success('Запись проведёна');
    } else {
      return;
    }

    emit('docCreated');
    emit('closeModal')
  } catch (error) {
    console.error('Error posting item', error);
    toast.error('Ошибка при проводке');
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
  for (let field of itemFields) { formData.append(field, form[field]) }
  // formData.append('ncar', form.ncar)
  // formData.append('plan_dateen', form.plan_dateen)
  // formData.append('plan_timeen_from', form.plan_timeen_from)
  // formData.append('plan_timeen_to', form.plan_timeen_to)
  // formData.append('drv_man', form.drv_man)
  // formData.append('drv_licence', form.drv_licence)
  // formData.append('car_model', form.car_model)
  // formData.append('entry_type', form.entry_type)
  // formData.append('contact', form.contact)
  // formData.append('ntir', form.ntir)
  // formData.append('ntir_date', form.ntir_date)
  // formData.append('customs_doc', form.customs_doc)
  // formData.append('customs_doc_date', form.customs_doc_date)
  // formData.append('comment', form.comment)

  // formData.append('file', file.value.files[0]);
  // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/single-file/`, 
  // formData, {headers: {'Content-Type': 'multipart/form-data'}});

  try {
    // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/documents/`, newItem);
    if (!props.itemData) {
      const response = await axios.post(`http://${backendIpAddress}:${backendPort}/entry_requests/`, 
        formData, {headers: {'Content-Type': 'multipart/form-data'}});
      toast.success('Новая запись добавлена');
    } else {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/entry_requests/${props.itemData.id}`, 
        formData, {headers: {'Content-Type': 'multipart/form-data'}});
      toast.success('Запись обновлёна');      
    }
    emit('docCreated');
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
      Заявка на въезд <span v-if="props.itemData">№ {{ props.itemData.id_entry_request }}</span>
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="emit('closeModal')"></i>
      </div>
    </header>

    <div class="ml-6 mt-3" v-if="props.isCard">
      <div class="inline-block mr-3 text-xs font-bold text-slate-500">Статус:</div>
      <!-- <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-green-600" v-if="props.itemData.status=='exit_permitted'">
        ВЫЕЗД РАЗРЕШЁН</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-500" v-else-if="props.itemData.status=='archival'">
        АРХИВНЫЙ</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-red-600" v-else-if="props.itemData.status=='exit_prohibited'">
        ВЫЕЗД ЗАПРЕЩЁН</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-500" v-else>
        СТОЯНКА</div> -->

      <div class="ml-3 inline-block text-sm font-semibold text-red-400" v-if="!props.itemData.posted">ДОКУМЕНТ НЕ ПРОВЕДЁН</div>
    </div>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      <!-- types:  text, date, time -->
      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Номер машины</label>
          <input type="text" v-model="form.ncar" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Дата въезда</label>
          <input type="date" v-model="form.plan_dateen" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Время въезда с</label>
          <input type="time" v-model="form.plan_timeen_from" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Время въезда по</label>
          <input type="time" v-model="form.plan_timeen_to" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>ФИО водителя</label>
          <input type="text" v-model="form.drv_man" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>№ водительских прав</label>
          <input type="text" v-model="form.drv_licence" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Модель автомобиля</label>
          <input type="text" v-model="form.car_model" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">

        <div class=formInputDiv> <label class=formLabelStyle>Тип въезда</label>
          <select :class=formInputStyle class="bg-white" v-model="form.entry_type" :required="true" :disabled="isCard">
            <option v-for="type in ['Привоз груза', 'Вывоз груза']" :value="type">{{ type }}</option>
          </select>
        </div>

        <!-- <div class=formInputDiv>   <label class=formLabelStyle>Тип въезда</label>
          <input type="text" v-model="form.entry_type" :class=formInputStyle :required="true" :disabled="isCard" />
        </div> -->
        <div class=formInputDiv>   <label class=formLabelStyle>Клиент</label>
          <input type="number" v-model="form.contact" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>№ транспортного документа</label>
          <input type="text" v-model="form.ntir" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Дата транспортного документа</label>
          <input type="date" v-model="form.ntir_date" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>№ таможенного документа</label>
          <input type="text" v-model="form.customs_doc" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Дата таможенного документа</label>
          <input type="date" v-model="form.customs_doc_date" :class=formInputStyle :required="true" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Примечание</label>
          <input type="text" v-model="form.comment" :class=formInputStyle :required="false" :disabled="isCard" />
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
