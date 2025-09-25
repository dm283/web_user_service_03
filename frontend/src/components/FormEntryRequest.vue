<script setup>
// import router from '@/router';
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

/////////
const itemFields = [
    'ncar',
    'dateen',
    'timeen',
    'plan_timeen_to',
    'driver_fio',
    'driver_licence',
    'car_model',
    'entry_type',
    // 'contact',
    // 'contact_name',
    'contact_uuid',
    'broker_uuid',
    'ntir',
    'ntir_date',
    'customs_doc',
    'customs_doc_date',
    'warehouse_upload',
    'comment',
  ]

const emit = defineEmits(['docCreated', 'closeModal', 'openEditAfterCreate', 'btnDelete', 'reopenCard'])

const props = defineProps({
  itemData: Object,  // card or edit - exists; create - empty
  isCard: Boolean,   // card - true
});

const state = reactive({
  documents: [],
  isLoading: true,
  filteredList: [],
  contacts: [],
  choosenDocs: [],
})

const showDropDownSelect = reactive({});
const showEAList = ref(false)
const showAddDoc = ref(false)
const errField = reactive({});
const form = reactive({});
const showAskCloseWithoutSave = ref(false)

// for dropdowns
if (!props.isCard) {
onMounted(async () => {
    try {
      const response = await axios.get(`http://${backendIpAddress}:${backendPort}/contacts_posted/`, {headers: authHeader()});
      state.contacts = response.data;
    } catch (error) {
      console.error('Error fetching docs', error);
    } finally {
      state.isLoading = false;
    }
});
};

// for dropdowns
if (props.itemData) {
onMounted(async () => {
    try {
      if (props.itemData.contact_uuid) {
      const res = await axios.get(`http://${backendIpAddress}:${backendPort}/contacts_by_uuid/${props.itemData.contact_uuid}`,
        {headers: authHeader()} );
      form['contact_name_input'] = res.data.name + ' (' + res.data.inn + ')'
      state.initial_contact_name = res.data.name + ' (' + res.data.inn + ')'
      }
    } catch (error) { console.error('Error fetching docs', error); } finally { state.isLoading = false; }
}); };


// get documents
if (props.itemData) {
onMounted(async () => {
    try {
      const response = await axios.get(`http://${backendIpAddress}:${backendPort}/obj_docs/${props.itemData.uuid}`,
        {headers: authHeader()}
      );
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
const saveBtnStyle0 = 'text-slate-400 text-sm font-semibold border border-slate-400 rounded-lg \
        w-32 h-9 hover:text-slate-500 hover:border-slate-500'
const saveBtnStyle1 = 'bg-red-100 text-slate-500 text-sm font-semibold border border-slate-400 rounded-lg \
        w-32 h-9 hover:text-slate-500 hover:border-slate-500'


const setFilter = (fieldForm, entity, fieldEntity1, fieldEntity2=null) => {
  // for dropdowns
  state.filteredList = [];
  if (form[fieldForm]) { state.formValue = form[fieldForm].toUpperCase() } else { state.formValue = '' };
  for (let rec of state[entity]) {
    if ( rec[fieldEntity1].toString().toUpperCase().indexOf(state.formValue) > -1 ) { state.filteredList.push(rec); };
    if (fieldEntity2) {
      if ( rec[fieldEntity2].toString().toUpperCase().indexOf(state.formValue) > -1 ) { 
        if ( !state.filteredList.includes(rec) ) {state.filteredList.push(rec)} }; }
  }; };

const setVars = (inputField, reserveField) => {
  // for dropdowns
  if (!form[reserveField]) { form[reserveField] = form[inputField] }
  if (showDropDownSelect[inputField]) { showDropDownSelect[inputField]=false; form[inputField]=form[reserveField] }
  else { showDropDownSelect[inputField]=true; form[inputField]=null }; };

const setInitialForm = () => {
  //
  if (props.itemData) { // card and update
    for (let field of itemFields) {
      form[field] = props.itemData[field]
      //form['contact_name_input'] = props.itemData.contact_name  // fake form field for dropdown list
      form['contact_name_input'] = state.initial_contact_name  // for dropdowns
    }
  } else {  // create
    for (let field of itemFields) {
      form[field] = null
      form['contact_name_input'] = null  // fake form field for dropdown list
    }
    form.warehouse_upload = false
  };

  if (userInfo.contact_id!=0 & userInfo.type=='V') {  // for the client service
    // form.contact = userInfo.contact_id
    // form.contact_name = userInfo.contact_name
    form.contact_uuid = userInfo.contact_uuid
    form.contact_name_input = userInfo.contact_name
  }

  if (userInfo.contact_id!=0 & userInfo.type=='B') {  // for lk_broker
    form.broker_uuid = userInfo.contact_uuid
  }
};

setInitialForm();

var isNV = {};
var isNeedSave = ref(false);

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
  try {
    if (props.itemData) {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/entry_requests_posting/${props.itemData.id}`,
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
  for (let field of itemFields) { formData.append(field, form[field]) };

  try {
    if (!props.isCard) {
      if (!props.itemData) {
        const response = await axios.post(`http://${backendIpAddress}:${backendPort}/entry_requests/`, 
          formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        toast.success('Новая запись добавлена');
        state.responseItem = response.data;
      } else {
        const response = await axios.put(`http://${backendIpAddress}:${backendPort}/entry_requests/${props.itemData.id}`, 
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
        formData2.append('obj_type_name', 'Заявки на въезд ТС');
        formData2.append('obj_type', 'Заявка на въезд ТС');
        formData2.append('contact_uuid', form.contact_uuid);
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
    
    emit('closeModal'); emit('openEditAfterCreate', state.responseItem, 'Заявки на въезд ТС')
  } catch (error) {
    console.error('Error adding item', error);
    toast.error('Item has not added');
  };
};


async function downloadFile(document_record_uuid) {
  // downloads file
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

const attachFileSys = async () => {
  showAddDoc.value=true
}

const attachFileEA = async () => {
  showEAList.value=true
}

const setChoosenDocs = async (items) => {
  state.choosenDocs = state.choosenDocs.concat(items)
  for (let item of items) {
    item.filename = item.doc_name  //
    state.documents.push(item)     //
  }
  isNeedSave.value = true // new
}

const closeIt = async () => {
  if (isNeedSave.value) { showAskCloseWithoutSave.value = true }
  else { emit('docCreated'); emit('closeModal'); }
}

const reattachFile = async (doc_uuid, obj_uuid) => {
  emit('btnDelete', {'doc_uuid': doc_uuid, 'obj_uuid': obj_uuid}, 'открепить_документ')
}

const refreshCard = async () => {
  let query = `http://${backendIpAddress}:${backendPort}/entry_request_by_uuid/${props.itemData.uuid}`
  let response = await axios.get(query, {headers: authHeader()});
  let item = response.data;
  let reopenType = props.isCard ? 'card' : 'edit'
  emit('closeModal'); emit('reopenCard', reopenType, item, 'Заявки на въезд ТС')
}

</script>


<template>
  <!-- <div class="w-3/5 max-h-4/5 bg-white drop-shadow-md rounded-lg overflow-hidden"> -->
  <div class="w-3/5 bg-white drop-shadow-md rounded-lg overflow-hidden">
    <header class="py-2 pl-6 bg-slate-200 text-black text-lg font-normal">
      Заявка на въезд <span v-if="props.itemData">#{{ props.itemData.id_entry_request }}</span>
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="closeIt()"></i>
      </div>
      <div v-if="props.itemData" class="absolute top-2 right-12 cursor-pointer hover:text-gray-500">
        <i class="pi pi-refresh" style="font-size: 1rem" @click="refreshCard()"></i>
      </div>
    </header>

    <div class=contStyle>

    <div class="ml-6 mt-3" v-if="props.isCard">
      <div class="inline-block mr-3 text-xs font-bold text-slate-500">Статус:</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-400" v-if="props.itemData.status=='entered'">
        ТРАНСПОРТ ВЪЕХАЛ</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-green-500" v-else-if="props.itemData.status=='open'">
        ЗАЯВКА ОТКРЫТА</div>

      <div class="ml-3 inline-block text-sm font-semibold text-red-400" v-if="!props.itemData.posted">ЗАПИСЬ НЕ ПРОВЕДЕНА</div>
    </div>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      <!-- types:  text, date, time -->
      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Номер машины</label>
          <input type="text" v-model="form.ncar" :class="[errField['ncar']==1 ? formInputStyleErr : formInputStyle]" 
          :required="true" :disabled="isCard" />
        </div>

        <!-- <div class="formInputDiv" v-if="(!props.isCard) & (userInfo.contact_id==0 || userInfo.type=='B')">   <label class=formLabelStyle>Клиент</label>
          <div :class=formInputStyle class="flex" @click="setFilter('null', 'contacts', 'name'); setVars('contact_name_input', 'reserve_1');">
            <input class="w-64 focus:outline-none" type="text" v-model="form.contact_name_input" 
                @keyup="setFilter('contact_name_input', 'contacts', 'name')" :required="true"/>
            <span><i class="pi pi-angle-down" style="font-size: 0.8rem"></i></span>
          </div>
          <div v-if="showDropDownSelect['contact_name_input']" class="bg-white border border-slate-400 rounded-md shadow-xl w-64 max-h-24 overflow-auto p-1 absolute z-10">
            <div class="px-1.5 py-0.5 cursor-pointer hover:bg-blue-300" v-for="item in state.filteredList" 
                @click="showDropDownSelect['contact_name_input']=false; 
                  form['reserve_1']=item.name;form['contact_name_input']=item.name;form['contact_uuid']=item.uuid;" >
                {{ item.name }}
            </div>
          </div>
        </div> -->

        <div class="formInputDiv" v-if="(!props.isCard) & (userInfo.contact_id==0 || userInfo.type=='B')">   <label class=formLabelStyle>Клиент</label>
            <div :class=formInputStyle class="flex">
              <input class="w-64 focus:outline-none cursor-pointer" type="text" placeholder="выберите из списка" v-model="form.contact_name_input" 
                @click="setFilter('null', 'contacts', 'name'); setVars('contact_name_input', 'reserve_1');"
                @keyup="setFilter('contact_name_input', 'contacts', 'name', 'inn')" :required="true"/>
              <span @click="setFilter('null', 'contacts', 'name'); setVars('contact_name_input', 'reserve_1');">
                <i class="pi pi-angle-down" style="font-size: 0.8rem"></i></span>
              <span class="ml-1 text-red-400 active:text-black" @click="showDropDownSelect['contact_name_input']=false; 
                  form['reserve_1']=null;form['contact_name_input']=null;form['contact_uuid']=null;">
                <i class="pi pi-times" style="font-size: 0.7rem"></i></span>
            </div>
          <div v-if="showDropDownSelect['contact_name_input']" class="bg-white border border-slate-400 rounded-md shadow-xl w-64 max-h-24 overflow-auto p-1 absolute z-10">
            <div class="px-1.5 py-0.5 cursor-pointer hover:bg-blue-300" v-for="item in state.filteredList" 
                @click="showDropDownSelect['contact_name_input']=false; 
                  form['reserve_1']=item.name;form['contact_name_input']=(item.name+' ('+item.inn+')');form['contact_uuid']=item.uuid" >
                {{ item.name }} ({{ item.inn }})
            </div>
          </div>
        </div>

        <div class=formInputDiv v-else>   <label class=formLabelStyle>Клиент</label>
          <input type="text" v-model="form.contact_name_input" :class="[errField['contact_uuid']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="true" />
        </div>

        <div class=formInputDiv>   <label class=formLabelStyle>Тип въезда</label>
          <select :class="[errField['entry_type']==1 ? formInputStyleErr : formInputStyle]"
            v-model="form.entry_type" :required="false" :disabled="isCard">
            <option v-for="type in ['Привоз груза', 'Вывоз груза']" :value="type">{{ type }}</option>
          </select>
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Дата въезда</label>
          <input type="date" v-model="form.dateen" :class="[errField['dateen']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Время въезда с</label>
          <input type="time" v-model="form.timeen" :class="[errField['timeen']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Время въезда по</label>
          <input type="time" v-model="form.plan_timeen_to" :class="[errField['plan_timeen_to']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>ФИО водителя</label>
          <input type="text" v-model="form.driver_fio" :class="[errField['driver_fio']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>№ водительских прав</label>
          <input type="text" v-model="form.driver_licence" :class="[errField['driver_licence']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Модель автомобиля</label>
          <input type="text" v-model="form.car_model" :class="[errField['car_model']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>№ транспортного документа</label>
          <input type="text" v-model="form.ntir" :class="[errField['ntir']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Дата транспортного документа</label>
          <input type="date" v-model="form.ntir_date" :class="[errField['ntir_date']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>№ таможенного документа</label>
          <input type="text" v-model="form.customs_doc" :class="[errField['customs_doc']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Дата таможенного документа</label>
          <input type="date" v-model="form.customs_doc_date" :class="[errField['customs_doc_date']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Примечание</label>
          <input type="text" v-model="form.comment" :class="[errField['comment']==1 ? formInputStyleErr : formInputStyle]"
          :required="false" :disabled="isCard" />
        </div>
        <div class="pt-2 formInputDiv">
          <input type="checkbox" v-model='form.warehouse_upload' id="warehouse_upload" name="warehouse_upload" class=formInputCheckboxStyle :disabled="isCard"/>
          <label class=formLabelCheckboxStyle for="warehouse_upload">Выгрузка на склад</label>
        </div>
      </div>


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

        <!-- <div class="flex space-x-3 mt-3" v-if="!state.isLoading && state.documents.length>0">
          <div class="border rounded-md p-1 w-20 h-30 text-center text-xs" v-for="document in state.documents">
            <div class="overflow-auto">
              <div class="float-left text-blue-500 cursor-pointer" @click="downloadFile(document.uuid)"><i class="pi pi-file" style="font-size: 1.5rem"></i></div>
              <div class="float-right text-rose-400 cursor-pointer" @click="reattachFile(document.uuid, props.itemData.uuid)">
                <i class="pi pi-times-circle" style="font-size: 0.8rem"></i></div>
            </div>
            <div class="w-18 text-wrap text-slate-700">{{ document.doc_name }}</div>
          </div>
        </div> -->

        <div class="mb-5" v-if="!state.isLoading">
          <div v-if="state.documents.length>0" class="border rounded-md mt-2 overflow-hidden">
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
              <tr class="border-t text-slate-500 text-xs" v-for="document in state.documents">
                <td class="text-center"><div class="pl-0.5 text-blue-500 cursor-pointer" 
                    @click="downloadFile(document.uuid)">
                  <i class="pi pi-download" style="font-size: 0.8rem"></i></div></td>
                <td class="text-center">{{ document.doc_name }}</td>
                <td class="text-center">{{ document.doc_id }}</td>
                <td class="text-center">{{ document.doc_date }}</td>
                <td class="text-center">{{ document.file_name }}</td>
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
