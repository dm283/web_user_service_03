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

const userInfo = JSON.parse(localStorage.getItem('userInfo'));

const emit = defineEmits(['docCreated', 'closeModal'])

const props = defineProps({
  itemData: Object,
  isCard: Boolean,
});

const state = reactive({
  documents: [],
  isLoading: true,
  filteredList: [],
  entiryRequests: [],
  contacts: [],
})

const selectedItem = ref('')
const showDropDownSelect = ref({});


const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}

const userAccessToken = () => {
  let user = JSON.parse(localStorage.getItem('user')); if (user && user.access_token) {return user.access_token} else {return ''}
}


if (!props.isCard) {
onMounted(async () => {
    try {
      state.query = `http://${backendIpAddress}:${backendPort}/entry_requests_posted/`;
      const response = await axios.get(state.query, {headers: authHeader()});
      state.entiryRequests = response.data;

      state.query = `http://${backendIpAddress}:${backendPort}/contacts_posted/`;
      const response_2 = await axios.get(state.query, {headers: authHeader()});
      state.contacts = response_2.data;
    } catch (error) {
      console.error('Error fetching docs', error);
    } finally {
      state.isLoading = false;
    }
});
};


if (props.itemData) {
onMounted(async () => {
    try {
      const response = await axios.get(`http://${backendIpAddress}:${backendPort}/entity_documents/${props.itemData.uuid}`, 
        {headers: authHeader()});
      state.documents = response.data;
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
    'ncar',
    'dateen',
    'timeen',
    'ntir',
    'ntir_date',
    'customs_doc',
    'customs_doc_date',
    'nseal',
    'nkont',
    'driver',
    'driver_fio',
    'driver_phone',
    'driver_licence',
    'car_model',
    'entry_type',
    'contact',
    'contact_name',
    'contact_uuid',
    'place_n',
    'radiation',
    'brokenAwning',
    'brokenSeal',
    'comment',
    'dateex',
    'timeex',
  ]

const setFilter = (fieldForm, entity, fieldEntity) => {
  // filter setting
  state.filteredList = [];
  if (form[fieldForm]) { state.formValue = form[fieldForm].toUpperCase() } else { state.formValue = '' };
  for (let rec of state[entity]) {
    if ( rec[fieldEntity].toString().toUpperCase().indexOf(state.formValue) > -1 ) {
      state.filteredList.push(rec);
    };
  };
  if (state.filteredList.length == 0) {
    for (let xobj of state[entity]) {
      let clonedObj = {...xobj};
      state.filteredList.push(clonedObj);
    };
  }
};

const setFormValues = () => {
  for (let field of itemFields) {form[field] = selectedItem.value[field]}
  form.radiation = false; form.brokenAwning = false; form.brokenSeal = false;
}


const getDocs = async () => {
  console.log('getting docs for entryRequest =', selectedItem.value['uuid'])
  let uuid = selectedItem.value['uuid']
  try {
    const response = await axios.get(`http://${backendIpAddress}:${backendPort}/entity_documents/${uuid}`, 
      {headers: authHeader()});
    state.entry_request_docs = response.data;
  } catch (error) {
    console.error('Error fetching entry_request_docs', error);
  }
  console.log('entry_request_docs =', state.entry_request_docs)
}


const setInitialForm = () => {
  //
  if (props.itemData) { // card and update
    for (let field of itemFields) {
      form[field] = props.itemData[field]
      form['contact_name_input'] = props.itemData.contact_name  // fake form field for dropdown list
    }
  } else {  // create
    for (let field of itemFields) {
      form[field] = null
      form['contact_name_input'] = null  // fake form field for dropdown list
    }
    form.ncar = '_234РА23' // template for 'ncar'
    form.radiation = false
    form.brokenAwning = false
    form.brokenSeal = false
    state.entry_request_docs = null
  };
};

setInitialForm();

const file = ref(null)
const toast = useToast();

const postingItem = async () => {
  //
  try {
    if (props.itemData) {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/carpasses_posting/${props.itemData.id}`,
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

  // item updating
  for (let field of itemFields) { formData.append(field, form[field]) };

  try {
    if (!props.itemData) {
      const response = await axios.post(`http://${backendIpAddress}:${backendPort}/carpasses/`, 
        formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
      toast.success('Новый запись добавлена');
      state.responseItem = response.data;
    } else {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/carpasses/${props.itemData.id}`, 
        formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
      toast.success('Запись обновлена');
      state.responseItem = response.data;
    }

    // files uploading
    if (files.value) {
      for (let file of files.value.files) {
        formData.append('file', file);
        formData.append('customer_name', form.contact_name_input); //deprecated
        formData.append('contact_uuid', form.contact_uuid);
        formData.append('post_user_id', userInfo.uuid);
        try {
          const response = await axios.put(`http://${backendIpAddress}:${backendPort}/upload_file_for_carpass/${state.responseItem.uuid}`, 
            formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        } catch (error) {
          console.error('Error uploading file', error);
          toast.error('File has not been uploaded');
        };
      };
    };

    // attaching files of initial entry_request into creating carpass
    if (state.entry_request_docs) {
      for (let doc of state.entry_request_docs) {
        formData.append('doc_id', doc.id);
        formData.append('entity_uuid', state.responseItem.uuid);
        try {
          const response = await axios.put(`http://${backendIpAddress}:${backendPort}/attach_doc_to_additional_entity/`, 
            formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        } catch (error) {
          console.error('Error uploading file', error);
        };        
      }
    }

    emit('docCreated'); emit('closeModal');
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
        <div class="formInputDiv" v-if="!props.isCard">   <label class=formLabelStyle>Номер машины</label>
          <div :class=formInputStyle class="flex" @click="setFilter('ncar', 'entiryRequests', 'ncar'); 
              showDropDownSelect.ncar ? showDropDownSelect.ncar=false : showDropDownSelect.ncar=true;">
            <input class="w-64 focus:outline-none" type="text" v-model="form.ncar" @keyup="setFilter('ncar', 'entiryRequests', 'ncar')" 
              :required="true"/>
            <span><i class="pi pi-angle-down" style="font-size: 0.8rem"></i></span>
          </div>
          <div v-if="showDropDownSelect.ncar" class="bg-slate-100 border border-slate-400 rounded-md shadow-xl w-64 max-h-24 overflow-auto p-1 absolute">
            <div class="px-1.5 py-0.5 cursor-pointer hover:bg-blue-300" v-for="item in state.filteredList" 
              @click="form.ncar=item.ncar; form.contact_name_input=item.contact_name; 
                selectedItem=item; showDropDownSelect.ncar=false; setFormValues(); getDocs()" >
              {{ item.ncar }}
            </div>
          </div>
        </div>
        <div class=formInputDiv v-else>   <label class=formLabelStyle>Номер машины</label>
          <input type="text" v-model="form.ncar" :class="[errField['ncar']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="isCard" />
        </div>

        
        <!-- fake field 'contact_name_input' for dropdown list -->
        <div class="formInputDiv" v-if="!props.isCard">   <label class=formLabelStyle>Клиент</label>
          <div :class=formInputStyle class="flex" @click="setFilter('contact_name_input', 'contacts', 'name'); 
              showDropDownSelect.contact_name_input ? showDropDownSelect.contact_name_input=false : showDropDownSelect.contact_name_input=true;">
            <input class="w-64 focus:outline-none" type="text" v-model="form.contact_name_input" 
              @keyup="setFilter('contact_name_input', 'contacts', 'name')" :required="true"/>
            <span><i class="pi pi-angle-down" style="font-size: 0.8rem"></i></span>
          </div>
          <div v-if="showDropDownSelect.contact_name_input" class="bg-white border border-slate-400 rounded-md shadow-xl w-64 max-h-24 overflow-auto p-1 absolute z-10">
            <div class="px-1.5 py-0.5 cursor-pointer hover:bg-blue-300" v-for="item in state.filteredList" 
              @click="form.contact=item.id; showDropDownSelect.contact_name_input=false; 
                form.contact_name=item.name;form.contact_name_input=item.name;form.contact_uuid=item.uuid;" >
              {{ item.name }}
            </div>
          </div>
        </div>

        <div class=formInputDiv v-else>   <label class=formLabelStyle>Клиент</label>
          <input type="text" v-model="form.contact_name" :class="[errField['contact_name']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="true" />
        </div>

      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Тип въезда</label>
          <select :class="[errField['entry_type']==1 ? formInputStyleErr : formInputStyle]"
            v-model="form.entry_type" :required="false" :disabled="isCard">
            <option v-for="type in ['Привоз груза', 'Вывоз груза']" :value="type">{{ type }}</option>
          </select>
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Дата въезда</label>
          <input type="date" v-model="form.dateen" :class="[errField['dateen']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Время въезда</label>
          <input type="time" v-model="form.timeen" :class="[errField['timeen']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Модель автомобиля</label>
          <input type="text" v-model="form.car_model" :class="[errField['car_model']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Номер транспортного документа</label>
          <input type="text" v-model="form.ntir" :class="[errField['ntir']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Дата транспортного документа</label>
          <input type="date" v-model="form.ntir_date" :class="[errField['ntir_date']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Номер таможенного документа</label>
          <input type="text" v-model="form.customs_doc" :class="[errField['customs_doc']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Дата таможенного документа</label>
          <input type="date" v-model="form.customs_doc_date" :class="[errField['customs_doc_date']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Наименование перевозчика</label>
          <input type="text" v-model="form.driver" :class="[errField['driver']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Номер контейнера</label>
          <input type="text" v-model="form.nkont" :class="[errField['nkont']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Номер пломбы</label>
          <input type="text" v-model="form.nseal" :class="[errField['nseal']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>ФИО водителя</label>
          <input type="text" v-model="form.driver_fio" :class="[errField['driver_fio']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Телефон водителя для связи</label>
          <input type="text" v-model="form.driver_phone" :class="[errField['driver_phone']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Номер водительских прав</label>
          <input type="text" v-model="form.driver_licence" :class="[errField['driver_licence']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">

        <div class=formInputDiv>   <label class=formLabelStyle>Номер стоянки</label>
          <input type="text" v-model="form.place_n" :class="[errField['place_n']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Примечание</label>
          <input type="text" v-model="form.comment" :class=formInputStyle :disabled="isCard" />
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

      <div сlass="" v-if="props.isCard || props.itemData">
      <!-- Show loading spinner while loading is true -->
      <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
        <PulseLoader /> ЗАГРУЗКА ДОКУМЕНТОВ...
      </div>
      <!-- Show when loading is done -->
      <div class="border-t border-slate-300 mx-6 pt-3" v-if="!state.isLoading && state.documents.length>0">
        <label class=formLabelStyle>Документы</label>
        <div class="flex space-x-3 mt-3">
        <div class="border rounded-md p-2 w-15 h-30 text-center text-xs " v-for="document in state.documents">
          <div class="text-blue-500 cursor-pointer" @click="downloadFile(document.id)"><i class="pi pi-file" style="font-size: 1rem"></i></div>
          <div class="">{{ document.filename }}</div>
        </div>
        </div>
        </div>
      </div>


      <!-- Show when carpass is creating fron entry_request and the last one has documents -->
      <div class="border-t border-slate-300 mx-6 pt-3" v-if="state.entry_request_docs">
        <label class=formLabelStyle>Документы</label>
        <div class="flex space-x-3 mt-3">
        <div class="border rounded-md p-2 w-15 h-30 text-center text-xs " v-for="document in state.entry_request_docs">
          <div class="text-blue-500 cursor-pointer" @click="downloadFile(document.id)"><i class="pi pi-file" style="font-size: 1rem"></i></div>
          <div class="">{{ document.filename }}</div>
        </div>
        </div>
      </div>  


      <div v-if="!isCard" class="my-3 py-3 px-5 text-center overflow-auto">
        <div class="float-left space-x-5">
          <button class="formBtn" type="submit">СОХРАНИТЬ</button>
          <button class="formBtn" type="button" @click="setInitialForm();">СБРОСИТЬ</button>
          <input ref="files" name="files" type="file" multiple class="formInputFile"/>
          <!-- <input ref="files" name="files" type="file" multiple class="formInputFile" v-if="props.itemData"/> -->
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
