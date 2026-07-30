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

/////////////
const itemFields = [
  'id_enter',
  'ncar',
  'contact_uuid',
  'driver_fio',
  'driver_phone',
  'driver_licence',
  'ndexit',
  'comment',
  'dateex',
  'timeex',
  'comment_checkpoint',
  ]

const emit = defineEmits(['docCreated', 'closeModal', 'openEditAfterCreate', 'btnDelete', 'reopenCard'])

const props = defineProps({
  isCreate: Boolean,
  itemData: Object,
  isCard: Boolean,
});

const state = reactive({
  documents: [],
  isLoading: true,
  filteredList: [],
  relatedCarpass: {},
  choosenDocs: [],
})

const selectedItem = ref('')
const showDropDownSelect = reactive({});
const showEAList = ref(false)
const showAddDoc = ref(false)
const errField = reactive({});
const form = reactive({});
const showAskCloseWithoutSave = ref(false)


if (!props.isCard) {
onMounted(async () => {
  state.isLoading = false;
})
}


// for dropdowns
if (!props.isCreate && props.itemData) {
onMounted(async () => {   
    try {
      const response1 = await axios.get(`http://${backendIpAddress}:${backendPort}/carpasses/${props.itemData.id_enter}`,
        {headers: authHeader()} );
      state.relatedCarpass = response1.data;
    } 
    catch (error) { console.error('Error fetching item', error); } finally { state.isLoading = false; }
}); };

// get documents
if (!props.isCreate && props.itemData) {
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
const postedColor = props.itemData ? (props.itemData.posted ? 'bg-white' : 'bg-yellow-50') : 'bg-white'
const formInputStyleAct = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer' + ' ' + postedColor
const formInputStyle = props.isCard ? formInputStyleDis : formInputStyleAct
const formInputStyle2 = props.itemData.status=='archival' ? formInputStyleDis : formInputStyleAct
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
  if (!props.isCreate && props.itemData) { // card and update
    for (let field of itemFields) {
      form[field] = props.itemData[field]
      // form['contact_name_input'] = state.initial_contact_name  // for dropdowns
    }
  } else {  // create
    for (let field of itemFields) {
      form[field] = null
      // form['contact_name_input'] = null  // fake form field for dropdown list
    }
    form.id_enter = props.itemData.id_enter;
    form.ncar = props.itemData.ncar;
    form.driver_fio = props.itemData.driver_fio
    form.driver_phone = props.itemData.driver_phone
    form.driver_licence = props.itemData.driver_licence
  };
  form['contact_uuid'] = props.itemData.contact_uuid
};

setInitialForm();

// set values from choosen entry_request
const setFormValues = () => {
  for (let field of itemFields) {form[field] = selectedItem.value[field]}
}

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
  if (isNeedSave.value) { toast.warning('Сохраните данные перед проводкой'); return  }  // 12.2.26
  
  try {
    if (props.itemData) {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/exitcarpasses_posting/${props.itemData.uuid}`,
        '', {headers: authHeader()});
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
  for (let field of itemFields) { formData.append(field, form[field]) };

  try {
    if (!props.isCard) {
      if (props.isCreate) {
        const response = await axios.post(`http://${backendIpAddress}:${backendPort}/exitcarpasses/`, 
          formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        toast.success('Новый запись добавлена');
        state.responseItem = response.data;
      } else {
        const response = await axios.put(`http://${backendIpAddress}:${backendPort}/exitcarpasses/${props.itemData.uuid}`, 
          formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
        toast.success('Запись обновлена');
        state.responseItem = response.data;
      }
    }

    // attach files from EA (creates record in related_docs table)
    state.obj_uuid = props.isCard ? props.itemData.uuid : state.responseItem.uuid
    if (state.choosenDocs) {
      for (let doc of state.choosenDocs){
        let formData2 = new FormData();
        formData2.append('obj_type_name', 'Пропуска ТС на выезд');
        formData2.append('obj_type', 'Пропуск ТС на выезд');
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

    emit('closeModal'); emit('openEditAfterCreate', state.responseItem, 'Пропуска ТС на выезд')
  } catch (error) {
    console.error('Error adding item', error);
    toast.error(error.response.data.detail);
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

const getDocs = async () => {
  // load docs of initial entry_request
  let uuid = selectedItem.value['uuid']
  try {
    const response = await axios.get(`http://${backendIpAddress}:${backendPort}/obj_docs/${uuid}`,
      {headers: authHeader()});
    state.entry_request_docs = response.data;
    setChoosenDocs(response.data)
  } catch (error) {
    console.error('Error fetching entry_request_docs', error);
  }
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
  if (isNeedSave.value) { console.log('IS NEEDED SAVE IS TRUE +++++++'); showAskCloseWithoutSave.value = true }
  else { emit('docCreated'); emit('closeModal'); }
}

const reattachFile = async (doc_uuid, obj_uuid) => {
  emit('btnDelete', {'doc_uuid': doc_uuid, 'obj_uuid': obj_uuid}, 'открепить_документ')
}

const refreshCard = async () => {
  let query = `http://${backendIpAddress}:${backendPort}/exitcarpass_by_uuid/${props.itemData.uuid}`
  let response = await axios.get(query, {headers: authHeader()});
  let item = response.data;
  let reopenType = props.isCard ? 'card' : 'edit'
  emit('closeModal'); emit('reopenCard', reopenType, item, 'Пропуска ТС на выезд')
}

const carExit = async () => {
  // выпуск (выезд) ТС
  let formData = new FormData();
  formData.append('comment_checkpoint', form.comment_checkpoint)
  try {
    const response = await axios.put(`http://${backendIpAddress}:${backendPort}/car_exit/${props.itemData.uuid}`, 
      formData, {headers: {'Content-Type': 'multipart/form-data', Authorization: 'Bearer '+userAccessToken()}});
    toast.success('ТС выпущено');
    state.responseItem = response.data;
  } catch (error) {
    console.error('Error exiting car', error);
    toast.error(error.response.data.detail);
  }
  emit('closeModal'); emit('reopenCard', 'card', state.responseItem, 'Пропуска ТС на выезд')
}

</script>


<template>
  <div class="w-3/5 bg-white drop-shadow-md rounded-lg overflow-hidden"
    :class="[(!props.isCreate && props.itemData) ? (props.itemData.posted ? 'bg-white' : 'bg-yellow-50') : 'bg-white']">
    <header class="py-2 pl-6 bg-slate-200 text-black text-lg font-normal">
      Пропуск на выезд <span v-if="!props.isCreate && props.itemData">#{{ props.itemData.id_exit }}</span>
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="closeIt()"></i>
      </div>
      <div v-if="props.itemData" class="absolute top-2 right-12 cursor-pointer hover:text-gray-500">
        <i class="pi pi-refresh" style="font-size: 1rem" @click="refreshCard()"></i>
      </div>
    </header>

    <div class=contStyle >

    <div class="ml-6 mt-3" v-if="!props.isCreate && props.itemData">
      <div class="inline-block mr-3 text-xs font-bold text-slate-500">Статус:</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-green-600" v-if="state.relatedCarpass.status=='exit_permitted'">
        ВЫЕЗД РАЗРЕШЁН</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-500" v-else-if="state.relatedCarpass.status=='archival'">
        АРХИВНЫЙ</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-red-600" v-else-if="state.relatedCarpass.status=='exit_prohibited'">
        ВЫЕЗД ЗАПРЕЩЁН</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-amber-600" v-else-if="state.relatedCarpass.status=='for_exit'">
        К ВЫЕЗДУ</div>
      <div class="inline-block text-sm font-semibold text-white rounded-md px-1 bg-blue-500" v-else>
        СТОЯНКА</div>

      <div class="ml-3 inline-block text-sm font-semibold text-red-400" v-if="!props.isCreate && !props.itemData.posted">ЗАПИСЬ НЕ ПРОВЕДЕНА</div>
    </div>

    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      
      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>№ пропуска на въезд</label>
          <input type="text" v-model="form.id_enter" :class="[errField['id_enter']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="true" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Номер машины</label>
          <input type="text" v-model="form.ncar" :class="[errField['ncar']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="true" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>ФИО водителя</label>
          <input type="text" v-model="form.driver_fio" :class="[errField['driver_fio']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="true" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Телефон водителя для связи</label>
          <input type="text" v-model="form.driver_phone" :class="[errField['driver_phone']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="true" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>№ водительских прав/паспорта</label>
          <input type="text" v-model="form.driver_licence" :class="[errField['driver_licence']==1 ? formInputStyleErr : formInputStyle]"
            :required="true" :disabled="true" />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>   <label class=formLabelStyle>Номер документа выпуска</label>
          <input type="text" v-model="form.ndexit" :class="[errField['ndexit']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
        <div class=formInputDiv>   <label class=formLabelStyle>Комментарий диспетчера</label>
          <input type="text" v-model="form.comment" :class="[errField['comment']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="isCard" />
        </div>
      </div>

      <div v-if="!isCard" class="mb-3 px-5 text-center overflow-auto">
        <div class="float-left space-x-5">
          <!-- <button class="formBtn" type="submit">СОХРАНИТЬ</button> -->
          <button :class="[isNeedSave ? saveBtnStyle1 : saveBtnStyle0]" type="submit">СОХРАНИТЬ</button>
          <button class="formBtn" type="button" @click="setInitialForm();">СБРОСИТЬ</button>
        </div>
        <div class="float-right" v-if="!props.isCreate && props.itemData">
          <button class="formBtn" type="button" @click="postingItem">ПРОВОДКА</button>
        </div>
      </div>
      <div v-else class="mb-5"></div>


      <div v-if="userInfo.role_name=='checkpoint' | itemData.status=='archival'" class="border-t-2 border-slate-300 mx-6 pt-3 mb-4">
        <label class="mx-1 text-sm font-semibold text-blue-500">СЕКЦИЯ КПП</label>
        <div class="flex -ml-6 mt-3">
        <button v-if="userInfo.role_name=='checkpoint' && itemData.status!='archival'" class="ml-6 mr-3 formBtn" 
          type="button" @click="carExit()">ВЫЕЗД ТС</button>

        <div class=formInputDiv>   <label class=formLabelStyle>Комментарий охраны</label>
          <input type="text" v-model="form.comment_checkpoint" :class=formInputStyle2 :required="false" :disabled="itemData.status=='archival'" />
        </div>

        <div v-if="isCard && itemData.status=='archival'" class=formInputDiv>   <label class=formLabelStyle>Дата выезда</label>
          <input type="date" v-model="form.dateex" :class="[errField['dateex']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="true" />
        </div>
        <div v-if="isCard && itemData.status=='archival'" class=formInputDiv>   <label class=formLabelStyle>Время выезда</label>
          <input type="time" v-model="form.timeex" :class="[errField['timeex']==1 ? formInputStyleErr : formInputStyle]"
            :required="false" :disabled="true" />
        </div>



        </div>

      </div>




      <div class="border-t-2 border-slate-300 mx-6 pt-3 mb-4">
        <div class="space-x-5 overflow-auto">
          <label class="mx-1 text-sm font-semibold text-blue-500">ДОКУМЕНТЫ</label>
          <!-- <button v-if="isCard" class="float-right formBtn" type="submit">СОХРАНИТЬ</button> -->
          <button v-if="isCard" class="float-right" :class="[isNeedSave ? saveBtnStyle1 : saveBtnStyle0]" type="submit">СОХРАНИТЬ</button>
          <button class="float-right formBtn" type="button" @click="attachFileEA()">ЭЛ. АРХИВ</button>
          <button class="float-right formBtn" type="button" @click="attachFileSys()">ЗАГРУЗИТЬ</button>
        </div>
        <!-- Show loading spinner while loading is true -->
        <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
          <PulseLoader /> ЗАГРУЗКА ДОКУМЕНТОВ...
        </div>

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
