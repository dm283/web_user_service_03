<script setup>
import {ref, reactive, computed, onMounted, watch, useTemplateRef} from 'vue';
import { useToast } from 'vue-toastification';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import axios from 'axios';
import FormEAList from './FormEAList.vue';
import FormDoc from './FormDoc.vue';
import FormAskCloseWithoutSave from './FormAskCloseWithoutSave.vue';
import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
import DropdownGeneric from './DropdownGeneric.vue';
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");
import forms_data from './a_forms_data.json';

const toast = useToast();
const userInfo = JSON.parse(localStorage.getItem('userInfo'));
const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}
const userAccessToken = () => {
  let user = JSON.parse(localStorage.getItem('user')); if (user && user.access_token) {return user.access_token} else {return ''}
}
/////
const emit = defineEmits(['docCreated', 'closeModal', 'openEditAfterCreate', 'btnDelete', 'reopenCard', 'notification'])  
const props = defineProps({
  itemType: String,
  itemData: Object,  // card or edit - exists; create - empty
  isCard: Boolean,   // card - true
});

console.log('itemdata =', props.itemData)

const state = reactive({
  // generic refs
  documents: [],
  isLoading: false,
  filteredList: [],
  choosenDocs: [],

  // special refs for entities
  contacts: [],  // batch, testen1
  brokers: [],   // batch, testen1
  carpasses: [],   // batch, testen1
  // history: [],   // batch
})

var itemFields = forms_data[props.itemType]['itemFields']
var postingUrl = forms_data[props.itemType]['postingUrl']
var postPutUrl = forms_data[props.itemType]['postPutUrl']
var getObjUrl = forms_data[props.itemType]['getObjUrl']
var sectionName = forms_data[props.itemType]['sectionName']
var docObjType = forms_data[props.itemType]['docObjType']
var formFields = forms_data[props.itemType]['formFields']

// read list of linked objects (for dropdown)  --  for batch
const getBrokers = async (client_uuid) => {
  if (!client_uuid) { state.brokers = []; return }
  let response = await axios.get(`http://${backendIpAddress}:${backendPort}/related_contact_broker/${client_uuid}`,
        {headers: authHeader()} );
  state.brokers = response.data;
} 

// load data for dropdowns
onMounted(async () => {
try {
  if (props.itemType=='testen1') {
    const response = await axios.get(`http://${backendIpAddress}:${backendPort}/contacts_posted/`, {headers: authHeader()});
    state.contacts = response.data;
    const response2 = await axios.get(`http://${backendIpAddress}:${backendPort}/carpasses_posted_not_archival/`, {headers: authHeader()});
    state.carpasses = response2.data;
  }
} catch (error) { console.error('Error fetching docs', error); } finally { state.isLoading = false; }});

// for dropdowns  -  for batch and testen1  -  !!! MOVE IT TO BACKEND (MAKE THIS FIELDS WITH JOIN) !!!
// if (props.itemData) {
// onMounted(async () => {
//     try {
//       if (props.itemData.contact_uuid) {
//       const response2 = await axios.get(`http://${backendIpAddress}:${backendPort}/contacts_by_uuid/${props.itemData.contact_uuid}`,
//         {headers: authHeader()} );
//       form['contact_name_input'] = response2.data.name + ' (' + response2.data.inn + ')'
//       state.initial_contact_name = response2.data.name + ' (' + response2.data.inn + ')'
//       }
//       if (props.itemData.broker_uuid) {
//       const response2 = await axios.get(`http://${backendIpAddress}:${backendPort}/contacts_by_uuid/${props.itemData.broker_uuid}`,
//         {headers: authHeader()} );
//       form['broker_name_input'] = response2.data.name + ' (' + response2.data.inn + ')'
//       state.initial_broker_name = response2.data.name + ' (' + response2.data.inn + ')'
//       }
//       if (props.itemData.carpass_uuid) {
//       const response3 = await axios.get(`http://${backendIpAddress}:${backendPort}/carpass_by_uuid/${props.itemData.carpass_uuid}`,
//         {headers: authHeader()} );
//       form['carpass_ncar_input'] = response3.data.ncar
//       state.initial_ncar = response3.data.ncar
//       }

//       getBrokers(props.itemData.contact_uuid)

//     } catch (error) { console.error('Error fetching docs', error); } finally { state.isLoading = false; }
// }); };

// get history  -  for batch
// if (props.itemData) {
// onMounted(async () => {
//     try { const response = await axios.get(`http://${backendIpAddress}:${backendPort}/log_records_batch/${props.itemData.uuid}`,
//             {headers: authHeader()});
//       state.history = response.data; } 
//     catch (error) { console.error('Error fetching history', error); } finally { state.isLoading = false; } }); };


// get documents  -  generic
if (props.itemData) {
onMounted(async () => {
  try {
    const response = await axios.get(`http://${backendIpAddress}:${backendPort}/obj_docs/${props.itemData.uuid}`, {headers: authHeader()});
    state.documents = response.data;
  } catch (error) { console.error('Error fetching docs', error); } finally { state.isLoading = false; } }); };


const showEAList = ref(false); const showAddDoc = ref(false)
const errField = reactive({}); const form = reactive({}); const showAskCloseWithoutSave = ref(false)

const formInputStyleDis = 'text-base w-full py-1 px-1 mb-2'
const postedColor = props.itemData ? (props.itemData.posted ? 'bg-white' : 'bg-yellow-50') : 'bg-white'
const formInputStyleAct = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer' + ' ' + postedColor
const formInputStyle = props.isCard ? formInputStyleDis : formInputStyleAct
const formInputStyleErr = 'bg-red-100 border-b-2 border-red-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-red-400 focus:outline-none focus:border-blue-500 cursor-pointer'
const saveBtnStyle0 = 'text-slate-400 text-sm font-semibold border border-slate-400 rounded-lg \
        w-32 h-9 hover:text-slate-500 hover:border-slate-500'
const saveBtnStyle1 = 'bg-red-100 text-slate-500 text-sm font-semibold border border-slate-400 rounded-lg \
        w-32 h-9 hover:text-slate-500 hover:border-slate-500'


const setInitialForm = () => {
  //
  if (props.itemData) { // card and update

    // generic
    for (let field of itemFields) { form[field] = props.itemData[field] }
    
    // custom for batch
    if (props.itemType=='batch') {
      form['contact_name_input'] = state.initial_contact_name
      form['broker_name_input'] = state.initial_broker_name
      form['carpass_ncar_input'] = state.initial_ncar
      form['carpass_ncar_dateen'] = state.initial_ncar_dateen
    }

    // custom for testen1
    if (props.itemType=='testen1') {
      form['contact_name_input'] = props.itemData.contact  //new
      form['broker_name_input'] = props.itemData.broker    //new
      form['carpass_ncar_input'] = props.itemData.ncar     //new
      getBrokers(props.itemData.contact_uuid)              //new
      // form['contact_name_input'] = state.initial_contact_name
      // form['broker_name_input'] = state.initial_broker_name
      // form['carpass_ncar_input'] = state.initial_ncar
    }

  } else {  // create

    // generic
    for (let field of itemFields) { form[field] = null }
    
    // custom for batch
    if (props.itemType=='batch') {
      form['contact_name_input'] = null
      form['broker_name_input'] = null
      form['carpass_ncar_input'] = null
      form['carpass_ncar_dateen'] = null
      form.fito_control = false
      form.vet_control = false
    }

    // custom for testen1
    if (props.itemType=='testen1') {
      form.bool_field = false
      form['contact_name_input'] = null
      form['broker_name_input'] = null
      form['carpass_ncar_input'] = null
    }
  };

  // if (userInfo.contact_id!=0) {  // for the client service
  //   form.contact_uuid = userInfo.contact_uuid
  //   form.contact_name_input = userInfo.contact_name
  // }

};

setInitialForm();

var isNV = {}; var isNeedSave = ref(false);

watch(form, (nV, oV) => {
  if (nV) {
    for (let field of itemFields) {
      if (props.itemData) {  // edit card
        if (form[field] == '' & props.itemData[field] == null) { isNV[field] = false; continue; }
        if (form[field] != props.itemData[field]) {
          isNV[field] = true;
        } else { isNV[field] = false; }
      }
      else {  // create card
        if (form[field]) { isNV[field] = true; } else { isNV[field] = false; }
      }
    }
  }
  isNeedSave.value = false
  for (let field of itemFields) { if (isNV[field] == true) { 
    isNeedSave.value = true; break; 
  } }
});


const postingItem = async () => {
  //
  if (isNeedSave.value) { toast.warning('Сохраните данные перед проводкой'); return  }
  try {
    if (props.itemData) {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/${postingUrl}/${props.itemData.uuid}`,
        '', {headers: authHeader()});
      toast.success('Запись проведёна');
      //emit('notification', 'проводка', 'партия_товаров', response.data.id, response.data.contact_uuid)
    } else { return; }
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
  for (let field of itemFields) { formData.append(field, form[field]) };

  try {
    if (!props.isCard) {
      if (!props.itemData) {
        const response = await axios.post(`http://${backendIpAddress}:${backendPort}/${postPutUrl}/`, 
          formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        toast.success('Новая запись добавлена');
        state.responseItem = response.data;
      } else {
        const response = await axios.put(`http://${backendIpAddress}:${backendPort}/${postPutUrl}/${props.itemData.uuid}`, 
          formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        toast.success('Запись обновлёна');      
        state.responseItem = response.data;
      }
    }

    // attach files from EA (creates record in related_docs table)
    state.obj_uuid = props.isCard ? props.itemData.uuid : state.responseItem.uuid
    if (state.choosenDocs) {
      for (let doc of state.choosenDocs){
        let formData2 = new FormData();
        formData2.append('obj_type_name', sectionName);
        formData2.append('obj_type', docObjType);
        formData2.append('contact_uuid', form.contact_uuid);
        // formData2.append('broker_uuid', form.broker_uuid);  // check is it exist?
        formData2.append('obj_uuid', state.obj_uuid);
        formData2.append('user_uuid', userInfo.uuid);
        formData2.append('doc_uuid', doc.uuid);
        try {
          const response = await axios.post(`http://${backendIpAddress}:${backendPort}/create_related_docs_record/`, 
            formData2, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        } catch (error) {
          console.error('Error posting', error);
        }
      }
    }

    for (let field of itemFields) { 
      isNV[field] = false; 
      errField[field] = 0; 
      if (props.itemData) { props.itemData[field] = form[field] }
    }
    isNeedSave.value = false;
    
    emit('closeModal'); emit('openEditAfterCreate', state.responseItem, sectionName)
  } catch (error) {
    console.error('Error adding item', error);
    toast.error('Ошибка записи');
  };
};


async function downloadFile(document_record_uuid) {
  // downloads file - generic
  let query = `http://${backendIpAddress}:${backendPort}/download-file/${document_record_uuid}`
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

const attachFileSys = async () => { showAddDoc.value=true }
const attachFileEA = async () => { showEAList.value=true }

const setChoosenDocs = async (items) => {
  state.choosenDocs = state.choosenDocs.concat(items)
  for (let item of items) {
    item.filename = item.doc_name
    state.documents.push(item)
  }
  isNeedSave.value = true
}

const closeIt = async () => {
  if (isNeedSave.value) { showAskCloseWithoutSave.value = true }
  else { emit('docCreated'); emit('closeModal'); }
}

const reattachFile = async (doc_uuid, obj_uuid) => {
  emit('btnDelete', {'doc_uuid': doc_uuid, 'obj_uuid': obj_uuid}, 'открепить_документ')
}

const refreshCard = async () => {
  let query = `http://${backendIpAddress}:${backendPort}/${getObjUrl}/${props.itemData.uuid}`
  let response = await axios.get(query, {headers: authHeader()});
  let item = response.data;
  let reopenType = props.isCard ? 'card' : 'edit'
  emit('closeModal'); emit('reopenCard', reopenType, item, sectionName)
}

const clickDropdown = async (dropdownName, setValue, searchValue, data=null) => {
  //
  form[setValue] = searchValue

  // additional actions for distinct dropdown
  if (dropdownName == 'testen1_contact_uuid') {
    getBrokers(form['contact_uuid']); form['broker_name_input']=null; form['broker_uuid']=null
  }
}

const clickDropdownErase = async (dropdownName, parentFormName, setValue, data=null) => {
  //
  form[parentFormName] = null
  form[setValue] = null

  // additional actions for distinct dropdown
  if (dropdownName == 'testen1_contact_uuid') {
    getBrokers(null); form['broker_name_input']=null; form['broker_uuid']=null
  }
}

</script>


<template>
  <div class="w-3/5 max-h-4/5 drop-shadow-md rounded-lg overflow-hidden" 
    :class="[props.itemData ? (props.itemData.posted ? 'bg-white' : 'bg-yellow-50') : 'bg-white']">
    
    <header class="py-2 pl-6 bg-slate-200 text-black text-lg font-normal">
      {{ docObjType }} <span v-if="props.itemData">#{{ props.itemData.id }}</span>
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="closeIt()"></i>
      </div>
      <div v-if="props.itemData" class="absolute top-2 right-12 cursor-pointer hover:text-gray-500">
        <i class="pi pi-refresh" style="font-size: 1rem" 
        @click="refreshCard()"></i>
      </div>
    </header>

    <div class=contStyle>

    <div class="ml-6 mt-3" v-if="props.itemData">
      <div class="inline-block mr-3 text-sm font-semibold text-white rounded-md px-1 bg-red-400" v-if="!props.itemData.posted">
        ЗАПИСЬ НЕ ПРОВЕДЕНА</div>
    
      <!-- <div class="inline-block mr-3 text-xs font-bold text-slate-500">Статус:</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-500" v-if="props.itemData.status=='на СВХ'">
        на СВХ</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-amber-500" v-else-if="props.itemData.status=='Там.офор.'">
        Там.офор.</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-amber-400" v-else-if="props.itemData.status=='Ч.офор.'">
        Ч.офор.</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-green-500" v-else-if="props.itemData.status=='Выпуск'">
        Выпуск</div> -->

    </div>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">

      <!-- <div class="flex relative">

      <div class="formInputDiv" v-if="(!props.isCard)">
        <DropdownCustom2
          v-model="form['contact_name_input']"
          :modelValue="form['contact_name_input']" @update:modelValue="$event => (foo = $event)"
          :parentFormName="'contact_name_input'"
          :name="'testen1_contact_uuid'"
          :label="'Клиент'"
          :data="state.contacts"
          :searchField1="'name'"
          :searchField2="'inn'"
          :searchValue="'uuid'"
          :setValue="'contact_uuid'"
          :isRequired="true"

          :itemData="props.itemData"
          :isCard="props.isCard"
          @click-dropdown="clickDropdown"
          @click-erase="clickDropdownErase"        
        />
      </div>
      <div class=formInputDiv v-else>   <label class=formLabelStyle>Клиент</label>
        <input type="text" v-model="form['contact_name_input']" :class="[errField['contact_uuid']==1 ? formInputStyleErr : formInputStyle]"
          :required="true" :disabled="true" />
      </div>

      <div class="formInputDiv" v-if="(!props.isCard)">
        <DropdownCustom2
          v-model="form['broker_name_input']"
          :modelValue="form['broker_name_input']" @update:modelValue="$event => (foo = $event)"
          :parentFormName="'broker_name_input'"
          :name="'testen1_broker_uuid'"
          :label="'Брокер'"
          :data="state.brokers"
          :searchField1="'broker_name'"
          :searchField2="'broker_inn'"
          :searchValue="'broker_uuid'"
          :setValue="'broker_uuid'"
          :isRequired="false"

          :itemData="props.itemData"
          :isCard="props.isCard"
          @click-dropdown="clickDropdown"
          @click-erase="clickDropdownErase"        
        />
      </div>
      <div class=formInputDiv v-else>   <label class=formLabelStyle>Брокер</label>
        <input type="text" v-model="form.broker_name_input" :class="[errField['broker_uuid']==1 ? formInputStyleErr : formInputStyle]"
          :required="true" :disabled="true" />
      </div>

      <div class="formInputDiv" v-if="(!props.isCard)">
        <DropdownCustom2
          v-model="form['carpass_ncar_input']"
          :modelValue="form['carpass_ncar_input']" @update:modelValue="$event => (foo = $event)"
          :parentFormName="'carpass_ncar_input'"
          :name="'testen1_carpass_uuid'"
          :label="'Номер машины'"
          :data="state.carpasses"
          :searchField1="'ncar'"
          :searchField2=null
          :searchValue="'uuid'"
          :setValue="'carpass_uuid'"
          :isRequired="false"

          :itemData="props.itemData"
          :isCard="props.isCard"
          @click-dropdown="clickDropdown"
          @click-erase="clickDropdownErase"        
        />
      </div>
      <div class=formInputDiv v-else>   <label class=formLabelStyle>Номер машины</label>
        <input type="text" v-model="form.carpass_ncar_input" :class="[errField['carpass_uuid']==1 ? formInputStyleErr : formInputStyle]"
          :required="true" :disabled="true" />
      </div>

      </div> -->


      <!-- <div class="flex relative" v-for="div of formDrops">
        <div class=formInputDiv v-for="field of div">

          <div v-if="field['field_type']=='dropdown' && !props.isCard">
            <DropdownCustom2
              v-model="form[field['field']]"
              :modelValue="form[field['field']]" @update:modelValue="$event => (foo = $event)"
              :parentFormName="field['field']"
              :name="field['name']"
              :label="field['label']"
              :data="state[field['data_state']]"
              :searchField1="field['searchField1']"
              :searchField2="field['searchField2']"
              :searchValue="field['searchValue']"
              :setValue="field['setValue']""
              :isRequired="field['isRequired']"

              :itemData="props.itemData"
              :isCard="props.isCard"
              @click-dropdown="clickDropdown"
              @click-erase="clickDropdownErase"        
            />
          </div>
          <div v-if="field['field_type']=='dropdown' && props.isCard">   
            <label class=formLabelStyle>{{ field['label'] }}</label>
            <input :type="field['input_type']" v-model="form[field['field']]" 
              :class="[errField[field['searchValue']]==1 ? formInputStyleErr : formInputStyle]"
              :required="field['isRequired']" :disabled="true" />
          </div>
        </div>
      </div> -->


      <!-- FIELDS BLOCK -->
      <div class="flex relative" v-for="div of formFields">
        <div class=formInputDiv v-for="field of div">
          
          <div v-if="field['field_type']=='dropdown' && !props.isCard">
            <DropdownGeneric
              v-model="form[field['field']]"
              :modelValue="form[field['field']]" @update:modelValue="$event => (foo = $event)"
              :parentFormName="field['field']"
              :name="field['name']"
              :label="field['label']"
              :data="state[field['data_state']]"
              :searchField1="field['searchField1']"
              :searchField2="field['searchField2']"
              :searchValue="field['searchValue']"
              :setValue="field['setValue']""
              :isRequired="field['isRequired']"
              :itemData="props.itemData"
              :isCard="props.isCard"
              @click-dropdown="clickDropdown"
              @click-erase="clickDropdownErase"        
            />
          </div>
          <div v-else-if="field['field_type']=='dropdown' && props.isCard">   
            <label class=formLabelStyle>{{ field['label'] }}</label>
            <input :type="field['input_type']" v-model="form[field['field']]" 
              :class="[errField[field['searchValue']]==1 ? formInputStyleErr : formInputStyle]"
              :required="field['isRequired']" :disabled="true" />
          </div>

          <div v-else-if="field['field_type']=='checkbox'">
            <input :type="field['field_type']" v-model="form[field['form_field']]"
              id="form[field['form_field']]" name="form[field['form_field']]"
              class=formInputCheckboxStyle :disabled="field['field_disabled']=='isCard'?props.isCard:field['field_disabled']" />
            <label class=formLabelCheckboxStyle for="form[field['form_field']]">{{ field['field_label'] }}</label>
          </div>
          <div v-else-if="'float_step' in field">   <!-- float field -->
            <label class=formLabelStyle>{{ field['field_label'] }}</label>
            <input :type="field['field_type']" :step="field['float_step']" v-model="form[field['form_field']]" 
              :class="[errField[field['form_field']]==1 ? formInputStyleErr : formInputStyle]"
              :required="field['field_required']" :disabled="field['field_disabled']=='isCard'?props.isCard:field['field_disabled']" />
          </div>
          <div v-else>   
            <label class=formLabelStyle>{{ field['field_label'] }}</label>
            <input :type="field['field_type']" v-model="form[field['form_field']]" 
              :class="[errField[field['form_field']]==1 ? formInputStyleErr : formInputStyle]"
              :required="field['field_required']" :disabled="field['field_disabled']=='isCard'?props.isCard:field['field_disabled']" />
          </div>
        </div>
      </div>


      <!-- HANDLING BLOCK -->
      <div v-if="!isCard" class="mb-3 px-5 text-center overflow-auto">
        <div class="float-left space-x-5">
          <button :class="[isNeedSave ? saveBtnStyle1 : saveBtnStyle0]" type="submit">СОХРАНИТЬ</button>
          <button class="formBtn" type="button" @click="setInitialForm()">СБРОСИТЬ</button>
        </div>
        <div class="float-right" v-if="props.itemData">
          <button class="formBtn" type="button" @click="postingItem">ПРОВОДКА</button>
        </div>
      </div>
      <div v-else class="mb-5"></div>

      
      <!-- DOCUMENTS BLOCK -->
      <div class="border-t-2 border-slate-300 mx-6 pt-3 mb-4">
        <div class="space-x-5 overflow-auto">
          <label class="mx-1 text-sm font-semibold text-blue-500">ДОКУМЕНТЫ</label>
          <button v-if="isCard" class="float-right" :class="[isNeedSave ? saveBtnStyle1 : saveBtnStyle0]" type="submit">СОХРАНИТЬ</button>
          <button class="float-right formBtn" type="button" @click="attachFileEA()">ЭЛ. АРХИВ</button>
          <button class="float-right formBtn" type="button" @click="attachFileSys()">ЗАГРУЗИТЬ</button>
        </div>
        <!-- Show loading spinner while loading is true -->
        <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
          <PulseLoader /> ЗАГРУЗКА ДОКУМЕНТОВ...
        </div>

        <!-- Show when loading is done -->
        <!-- <div class="flex space-x-3 mt-3" v-if="!state.isLoading && state.documents.length>0">
          <div class="border rounded-md p-2 w-15 h-30 text-center text-xs " v-for="document in state.documents">
            <div class="text-blue-500 cursor-pointer" @click="downloadFile(document.uuid)"><i class="pi pi-file" style="font-size: 1rem"></i></div>
            <div class="">{{ document.doc_name }}</div>
          </div>
        </div> -->

        <div class="mb-5" v-if="!state.isLoading">
          <div v-if="state.documents.length>0" class="border rounded-md mt-2 overflow-x-hidden max-h-40">
          <table class="w-full">
            <thead>
              <tr class="bg-slate-50 text-slate-500 font-semibold text-xs">
                <td class="text-center"></td>
                <td class="text-center">Наименование</td>
                <td class="text-center">Номер</td>
                <td class="text-center">Дата документа</td>
                <td class="text-center">Файл</td>
                <td class="text-center">Добавил [пользователь]</td>
                <td class="text-center">Добавил [контрагент]</td>
                <td class="text-center">Дата-время прикрепления</td>
                <td class="text-center"></td>
              </tr>
            </thead>
            <tbody>
              <tr class="bg-white border-t text-slate-500 text-xs" v-for="document in state.documents">
                <td class="text-center"><div class="pl-0.5 text-blue-500 cursor-pointer" 
                    @click="downloadFile(document.uuid)">
                  <i class="pi pi-download" style="font-size: 0.8rem"></i></div></td>
                <td class="text-center max-w-48 overflow-hidden">{{ document.doc_name }}</td>
                <td class="text-center">{{ document.doc_id }}</td>
                <td class="text-center">{{ document.doc_date }}</td>
                <td class="text-center max-w-48 overflow-hidden">{{ document.file_name }}</td>
                <td class="text-center">{{ document.login }}</td>
                <td class="text-center">{{ document.contact }}</td>
                <td class="text-center">{{ document.attachment_datetime }}</td>
                <td class="text-center"><div class="pr-0.5 text-rose-400 cursor-pointer" 
                    v-if="document.contact_uuid==userInfo.contact_uuid"
                    @click="reattachFile(document.uuid, props.itemData.uuid)">
                  <i class="pi pi-trash" style="font-size: 0.8rem"></i></div>
                  <div class="pr-0.5 text-slate-400" v-else><i class="pi pi-trash" style="font-size: 0.8rem"></i></div>
                </td>
              </tr>
            </tbody>
          </table>
          </div>
          <div class="max-w-max px-1 bg-slate-50 text-slate-500 font-semibold text-xs" v-else>нет прикреплённых документов</div>
        </div>
      </div>

      <!-- HISTORY BLOCK - for batch -->
      <!-- <div v-if="props.itemData" class="border-t-2 border-slate-300 mx-6 pt-3 mb-4">
        <label class="mx-1 text-sm font-semibold text-blue-500">ИСТОРИЯ</label>
        
        <div class="mb-5" v-if="!state.isLoading">
          <div v-if="state.history.length>0" class="border rounded-md mt-2 overflow-x-hidden max-h-40">
          <table class="w-full">
            <thead>
              <tr class="bg-slate-50 text-slate-500 font-semibold text-xs">
                <td class="text-center">Действие</td>
                <td class="text-center">Пользователь</td>
                <td class="text-center">Дата</td>
                <td class="text-center">Время</td>
              </tr>
            </thead>
            <tbody>
              <tr class="bg-white border-t text-slate-500 text-xs" v-for="event in state.history">
                <td class="text-center">{{ event.action }}</td>
                <td class="text-center">{{ event.user_login }}</td>
                <td class="text-center">{{ event.created_date }}</td>
                <td class="text-center">{{ event.created_time }}</td>
              </tr>
            </tbody>
          </table>
          </div>
          <div class="max-w-max px-1 bg-slate-50 text-slate-500 font-semibold text-xs" v-else>нет истории</div>
        </div>
      </div> -->

    </form>
  </div>
  </div>

  <!-- **********************   MODAL EA LIST   ************************** -->
  <div v-if="showEAList" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormEAList @close-modal="showEAList=false" @returned-docs="setChoosenDocs" />
  </div>

  <!-- **********************   MODAL DOC ADD   ************************** -->
  <div v-if="showAddDoc" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormDoc @close-modal="showAddDoc=false" @doc-created="" @returned-docs="setChoosenDocs" />
  </div>

  <!-- **********************   MODAL ASK CLOSE WITHOUT SAVE   ************************** -->
  <div v-if="showAskCloseWithoutSave" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAskCloseWithoutSave @close-modal="showAskCloseWithoutSave=false" @doc-created="emit('docCreated'); emit('closeModal');" />
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
