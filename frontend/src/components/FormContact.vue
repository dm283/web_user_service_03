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
  itemData: Object,  // card or edit - exists; create - empty
  isCard: Boolean,   // card - true
});

const itemFields = [
    'linked_broker_uuid',
    'name',
    'inn',
    'type',
    'fio',
    'email',
    'idtelegram',
    'comment',
  ]

const state = reactive({
  documents: [],
  isLoading: true,
  brokers: [],
  related_brokers: [],
  new_brokers: [],
})

const showDropDownSelect = reactive({});
const errField = reactive({});
const form = reactive({});
const files = ref(null)
const file = ref(null)
const toast = useToast();

const formInputStyleDis = 'text-base w-full py-1 px-1 mb-2'
const formInputStyleAct = 'bg-white border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer'
const formInputStyle = props.isCard ? formInputStyleDis : formInputStyleAct
const formInputStyleErr = 'bg-red-100 border-b-2 border-red-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-red-400 focus:outline-none focus:border-blue-500 cursor-pointer'


const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}

const userAccessToken = () => {
  let user = JSON.parse(localStorage.getItem('user')); if (user && user.access_token) {return user.access_token} else {return ''}
}

onMounted(async () => {
    try {
      const response = await axios.get(`http://${backendIpAddress}:${backendPort}/brokers_posted/`, {headers: authHeader()});
      state.brokers = response.data;
    } catch (error) {
      console.error('Error fetching docs', error);
    } finally {
      state.isLoading = false;
    }
});

if (props.itemData) {
onMounted(async () => {
    try {
      const response = await axios.get(`http://${backendIpAddress}:${backendPort}/entity_documents/${props.itemData.uuid}`,
        {headers: authHeader()}
      );
      state.documents = response.data;

      const response1 = await axios.get(`http://${backendIpAddress}:${backendPort}/related_contact_broker/${props.itemData.uuid}`,
        {headers: authHeader()}
      );
      state.related_brokers = response1.data;

      if (props.itemData.linked_broker_uuid) {
      const response2 = await axios.get(`http://${backendIpAddress}:${backendPort}/contacts_by_uuid/${props.itemData.linked_broker_uuid}`,
        {headers: authHeader()}
      );
      state.linked_broker_name = response2.data.name;
      form['linked_broker_name_input'] = response2.data.name
      }

    } catch (error) {
      console.error('Error fetching docs', error);
    } finally {
      state.isLoading = false;
    }
});
};


const setFilter = (fieldForm, entity, fieldEntity) => {
  // filter setting
  state.filteredList = [];
  if (form[fieldForm]) { state.formValue = form[fieldForm].toUpperCase() } else { state.formValue = '' };
  for (let rec of state[entity]) {
    if ( rec[fieldEntity].toString().toUpperCase().indexOf(state.formValue) > -1 ) {
      state.filteredList.push(rec);
    };
  };

  // if (state.filteredList.length == 0) {
  //   for (let xobj of state[entity]) {
  //     let clonedObj = {...xobj};
  //     state.filteredList.push(clonedObj);
  //   };
  // }
};


const setVars = (inputField, reserveField) => {
  //
  if (!form[reserveField]) {
    form[reserveField] = form[inputField]
  }
  if (showDropDownSelect[inputField]) { 
    showDropDownSelect[inputField]=false 
    form[inputField]=form[reserveField]
  }
  else { 
    showDropDownSelect[inputField]=true 
    form[inputField]=null
  };
};

const setInitialForm = () => {
  //
  if (props.itemData) { // card and update
    for (let field of itemFields) {
      form[field] = props.itemData[field]
    }
  } else {  // create
    for (let field of itemFields) {
      form[field] = null
      form['linked_broker_name_input'] = null  // fake form field for dropdown list
    }
    form['type'] = 'V' // template for 'ncar'
  };

  state.new_brokers = []
  // if (userInfo.contact_id!=0) {  // for the client service
  //   form.contact = userInfo.contact_id
  //   form.contact_name = userInfo.contact_name
  //   form.contact_name_input = userInfo.contact_name
  // }
};

setInitialForm();

const postingItem = async () => {
  //
  try {
    if (props.itemData) {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/contacts_posting/${props.itemData.id}`,
        '', {headers: authHeader()});
      toast.success('Запись проведёна');
    } else {
      return;
    }
    emit('docCreated'); emit('closeModal');
  } catch (error) {
    let err = error.response.data.detail;
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
  // form submit handling (item create or update)
  let formData = new FormData();
  
  // item updating
  for (let field of itemFields) { formData.append(field, form[field]) };

  try {
    if (!props.itemData) {
      const response = await axios.post(`http://${backendIpAddress}:${backendPort}/contacts/`, 
        formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
      toast.success('Новая запись добавлена');
      state.responseItem = response.data;
    } else {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/contacts/${props.itemData.id}`, 
        formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
      toast.success('Запись обновлёна');      
      state.responseItem = response.data;
    }

    if (state.new_brokers.length>0) {
      for (let broker of state.new_brokers){
        let formData2 = new FormData();
        formData2.append('contact_uuid', state.responseItem.uuid);
        formData2.append('broker_uuid', broker.uuid);
        formData2.append('user_uuid_create', userInfo.uuid);
        try {
          const response = await axios.post(`http://${backendIpAddress}:${backendPort}/create_related_contact_broker/`, 
            formData2, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        } catch (error) {
          console.error('Error posting', error);
        }
      }
    }


    // files uploading
    if (files.value) {
      for (let file of files.value.files) {
        formData.append('file', file);
        formData.append('customer_name', form.contact_name_input); //deprecated
        formData.append('contact_uuid', state.responseItem.uuid);
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
      Клиент <span v-if="props.itemData">№ {{ props.itemData.id }}</span>
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="emit('closeModal')"></i>
      </div>
    </header>

    <div class="ml-6 mt-3" v-if="props.isCard">
      <!-- <div class="inline-block mr-3 text-xs font-bold text-slate-500">Статус:</div> -->
      <div class="inline-block text-sm font-semibold text-red-400" v-if="!props.itemData.posted">ЗАПИСЬ НЕ ПРОВЕДЕНА</div>
    </div>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Наименование</label>
          <input type="text" v-model="form.name" :class="[errField['name']==1 ? formInputStyleErr : formInputStyle]" 
          :required="true" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>ИНН</label>
          <input type="number" v-model="form.inn" :class="[errField['inn']==1 ? formInputStyleErr : formInputStyle]" 
          :required="false" :disabled="isCard" />
        </div>        
      </div>
      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>ФИО</label>
          <input type="text" v-model="form.fio" :class="[errField['fio']==1 ? formInputStyleErr : formInputStyle]" 
          :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>email</label>
          <input type="email" v-model="form.email" :class="[errField['email']==1 ? formInputStyleErr : formInputStyle]" 
          :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>idtelegram</label>
          <input type="text" v-model="form.idtelegram" :class="[errField['idtelegram']==1 ? formInputStyleErr : formInputStyle]" 
          :required="false" :disabled="isCard" />
        </div>    
      </div>
      <div class="flex">
       <div class=formInputDiv>   <label class=formLabelStyle>Комментарий</label>
          <input type="text" v-model="form.comment" :class="[errField['comment']==1 ? formInputStyleErr : formInputStyle]" 
          :required="false" :disabled="isCard" />
        </div>   
      </div>

      <div class="flex">
        <div class="formInputDiv" v-if="(!props.isCard)">   <label class=formLabelStyle>Добавить брокера</label>
          <div :class=formInputStyle class="flex" @click="setFilter('null', 'brokers', 'name'); setVars('linked_broker_name_input', 'reserve_1');">
            <input class="w-64 focus:outline-none" type="text" v-model="form.linked_broker_name_input" 
                @keyup="setFilter('linked_broker_name_input', 'brokers', 'name')" :required="false"/>
            <span><i class="pi pi-angle-down" style="font-size: 0.8rem"></i></span>
          </div>
          <div v-if="showDropDownSelect['linked_broker_name_input']" class="bg-white border border-slate-400 rounded-md shadow-xl w-64 max-h-24 overflow-auto p-1 absolute z-10">
            <div class="px-1.5 py-0.5 cursor-pointer hover:bg-blue-300" v-for="item in state.filteredList" 
                @click="showDropDownSelect['linked_broker_name_input']=false; 
                  state.new_brokers.push({'name': item.name, 'inn': item.inn, 'uuid': item.uuid});
                  form['reserve_1']=item.name;form['linked_broker_name_input']=item.name;form['linked_broker_uuid']=item.uuid" >
                {{ item.name }}
            </div>
          </div>
        </div>
        <!-- <div class=formInputDiv v-else>   <label class=formLabelStyle>Брокер</label>
          <input type="text" v-model="form.linked_broker_name_input" :class="[errField['contact_name']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="true" />
        </div> -->
        <div></div>
      </div>


      <div class="mx-5 px-1 mb-5"> <label class=formLabelStyle>Брокеры</label>
        <div class="border rounded-md mt-2 overflow-hidden">
        <table class="w-full">
          <thead>
            <tr class="bg-slate-50 text-slate-500 font-semibold text-xs">
              <td class="text-center">Наименование</td>
              <td class="text-center">ИНН</td>
            </tr>
          </thead>
          <tbody>
            <tr class="border-t text-slate-500 text-xs" v-for="broker in state.related_brokers">
              <td class="text-center">{{ broker.broker_name }}</td>
              <td class="text-center">{{ broker.broker_inn }}</td>
            </tr>
            <tr class="border-t text-blue-500 text-xs" v-for="broker in state.new_brokers">
              <td class="text-center">{{ broker.name }}</td>
              <td class="text-center">{{ broker.inn }}</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>



      <div v-if="props.isCard || props.itemData">
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


      <div v-if="!isCard" class="my-3 py-3 px-5 text-center overflow-auto">
      <!-- <div v-if="!isCard" class="my-3 flex justify-left space-x-5 py-3 px-5 text-center"> -->
        <div class="float-left space-x-5">
          <button class="formBtn" type="submit">СОХРАНИТЬ</button>
          <button class="formBtn" type="button" @click="setInitialForm()">СБРОСИТЬ</button>
          <!-- <input ref="files" name="files" type="file" multiple class="formInputFile"/> -->
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
