<script setup>
import { defineProps, computed, reactive, onMounted, ref } from 'vue';
import axios from 'axios';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import ListAdv from '@/components/ListAdv.vue';
import FormAddCarpass from './FormAddCarpass.vue';
import FormDeleteCarpass from './FormDeleteCarpass.vue';
import FormRollbackCarpass from './FormRollbackCarpass.vue';
import FormCarExitPermit from './FormCarExitPermit.vue';
import FormAddExitCarpass from './FormAddExitCarpass.vue';
import FormInitAddExitcarpass from './FormInitAddExitcarpass.vue';
import FormSetDefaultStatus from './FormSetDefaultStatus.vue';
import FormExitProhibited from './FormExitProhibited.vue';
import FormEntryRequest from './FormEntryRequest.vue';
import FormContact from './FormContact.vue';
import FormBroker from './FormBroker.vue';
import FormUser from './FormUser.vue';
import FormDoc from './FormDoc.vue';


import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");


const userInfo = JSON.parse(localStorage.getItem('userInfo'));

const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}

const props = defineProps({
  view_type: String,
  list_title: String,
});

const state = reactive({
  records: [],
  isLoading: true,
  query: '',
  listTableColumns: {},
  additionalColumns: {},
  listItemFileds: {},
})
  
const showDeleteItem = ref(false)
const showRollbackItem = ref(false)
const showCarExitPermit = ref(false)
const showSetDefaultStatus = ref(false)
const showExitProhibited = ref(false)

const showItemCard = ref(false)
const showAddItem = ref(false)
const showUpdateItem = ref(false)

const showCardExitCarpass = ref(false)
const showCreateExitCarpass = ref(false)
const showUpdateExitCarpass = ref(false)
const showAddExitcarpass = ref(false)

const showCardEntryRequest = ref(false)
const showAddEntryRequest = ref(false)
const showUpdateEntryRequest = ref(false)

const showCardContact = ref(false)
const showAddContact = ref(false)
const showUpdateContact = ref(false)

const showCardBroker = ref(false)
const showAddBroker = ref(false)
const showUpdateBroker = ref(false)

const showCardUser = ref(false)
const showAddUser = ref(false)
const showUpdateUser = ref(false)

const showCardDoc = ref(false)
const showAddDoc = ref(false)
const showUpdateDoc = ref(false)

const selectedItem = ref('')
const itemName = ref('')
const file = ref(null)

const modalStyle = "absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center"
const modalStyleSecond = "absolute z-20 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center"

// queries
const query_carpass = userInfo.contact_id==0 ? `http://${backendIpAddress}:${backendPort}/carpasses/`:
  `http://${backendIpAddress}:${backendPort}/carpasses_client/${userInfo.contact_uuid}`

const query_entry_requests = userInfo.contact_id==0 ? `http://${backendIpAddress}:${backendPort}/entry_requests/`:
  `http://${backendIpAddress}:${backendPort}/entry_requests_client/${userInfo.contact_uuid}`

const query_car_terminal = `http://${backendIpAddress}:${backendPort}/car_terminal/`
const query_exitcarpass = `http://${backendIpAddress}:${backendPort}/exitcarpasses/`
const query_contacts = `http://${backendIpAddress}:${backendPort}/contacts/`
const query_brokers = `http://${backendIpAddress}:${backendPort}/brokers/`
const query_users = `http://${backendIpAddress}:${backendPort}/users/`
const query_documents = `http://${backendIpAddress}:${backendPort}/document_records/`


if (props.view_type == 'enter') {
  state.query = query_carpass;
  state.listTableColumns = {
    'id_enter':'№','ncar':'№ ТС','dateen':'Дата въезда', 'timeen':'Время въезда', 'contact_name':'Клиент', 
    'place_n':'№ стоянки', 'dateex':'Дата выезда', 'timeex':'Время выезда'
  };
  state.additionalColumns = {  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
} 
else if (props.view_type == 'terminal') {
  state.query = query_car_terminal;
  state.listTableColumns = {
    'id_enter':'№','ncar':'№ ТС','dateen':'Дата въезда', 'timeen':'Время въезда', 'contact_name':'Клиент', 
    'place_n':'№ стоянки', 'dateex':'Дата выезда', 'timeex':'Время выезда'
  };
  state.additionalColumns = {  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
} 
else if (props.view_type == 'exitCarpass') {
  state.query = query_exitcarpass;
  state.listTableColumns = {
    'id_exit':'№', 'id_enter':'№ пропуска на въезд', 'ncar':'№ ТС', 'driver_fio':'ФИО водителя','driver_phone':'Телефон водителя для связи',
    'ndexit':'№ документа выпуска', 'dateex':'Дата выезда', 'timeex':'Время выезда'
  };
  state.additionalColumns = {  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
}
else if (props.view_type == 'entryRequest') {
  state.query = query_entry_requests;
  state.listTableColumns = {
    'dateen':'Дата въезда','timeen':'Время въезда с','plan_timeen_to':'Время въезда по','ncar':'№ ТС',
    'contact_name':'Клиент','entry_type':'Тип въезда'
  };
  state.additionalColumns = {  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
}
else if (props.view_type == 'contacts') {
  state.query = query_contacts;
  state.listTableColumns = {
    'name':'Наименование','inn':'ИНН', 'fio':'ФИО','email':'email','idtelegram':'idtelegram'
  };
  state.additionalColumns = {  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
}
else if (props.view_type == 'brokers') {
  state.query = query_brokers;
  state.listTableColumns = {
    'name':'Наименование','inn':'ИНН', 'fio':'ФИО','email':'email','idtelegram':'idtelegram'
  };
  state.additionalColumns = {  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
}
else if (props.view_type == 'users') {
  state.query = query_users;
  state.listTableColumns = {
    'login':'Логин','email':'email', 'contact_uuid':'Контрагент','type':'Тип контрагента'
  };
  state.additionalColumns = {  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
}
else if (props.view_type == 'documents') {
  state.query = query_documents;
  state.listTableColumns = {
    'doc_name':'Наименование','doc_id':'Номер','doc_date':'Дата','created_datetime':'Дата загрузки'
  };
  state.additionalColumns = {  };
  state.listItemFileds = {...state.listTableColumns, ...state.additionalColumns};
}


async function getData() {
    state.isLoading = true;
    try {     
      const response = await axios.get(state.query, {headers: authHeader()});
      state.records = response.data;
    } catch (error) {
      console.error('Error fetching', error);
    } finally {
      state.isLoading = false;
    }
}

onMounted(async () => {
    await getData()
});


async function downloadFile(document_id, section) {
  //
  const response = await axios.get(`http://${backendIpAddress}:${backendPort}/download_carpass/${section}/${document_id}`, 
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
};

async function openItemCard(obj) {
  // open object card (modal) from document cart
  if (obj.obj_type_name == 'Заявки на въезд ТС') { 
    state.query_item_for_card = `http://${backendIpAddress}:${backendPort}/entry_request_by_uuid/${obj.obj_uuid}`
  }
  else if (obj.obj_type_name == 'Пропуска ТС на въезд') { 
    state.query_item_for_card = `http://${backendIpAddress}:${backendPort}/carpass_by_uuid/${obj.obj_uuid}`
  }
  state.item_for_card = await axios.get(state.query_item_for_card, {headers: authHeader()})
  itemCard(state.item_for_card.data, obj.obj_type_name)
}

const itemCard = (item, name) => {
  //
  selectedItem.value = item;
  if (name == 'Пропуска ТС на въезд' || name == 'ТС на терминале') { showItemCard.value = true }
  else if (name == 'Пропуска ТС на выезд') { showCardExitCarpass.value = true }
  else if (name == 'Заявки на въезд ТС') { showCardEntryRequest.value = true }
  else if (name == 'Клиенты') { showCardContact.value = true }
  else if (name == 'Брокеры') { showCardBroker.value = true }
  else if (name == 'Пользователи') { showCardUser.value = true }
  else if (name == 'Электронный архив') { showCardDoc.value = true }
};

const addItem = (section) => {
  //
  if (section == 'Пропуска ТС на въезд') { showAddItem.value = true; } 
  else if (section == 'Пропуска ТС на выезд') { showAddExitcarpass.value = true; }
  else if (section == 'Заявки на въезд ТС') { showAddEntryRequest.value = true; }
  else if (section == 'Клиенты') { showAddContact.value = true; }
  else if (section == 'Брокеры') { showAddBroker.value = true; }
  else if (section == 'Пользователи') { showAddUser.value = true; }
  else if (section == 'Электронный архив') { showAddDoc.value = true; }
}

const editItem = (item, name) => {
  // opens modal for editing item
  selectedItem.value = item;
  if (name == 'Пропуска ТС на въезд') { showUpdateItem.value = true } 
  else if (name == 'Пропуска ТС на выезд') { showUpdateExitCarpass.value = true }
  else if (name == 'Заявки на въезд ТС') { showUpdateEntryRequest.value = true }
  else if (name == 'Клиенты') { showUpdateContact.value = true }
  else if (name == 'Брокеры') { showUpdateBroker.value = true }
  else if (name == 'Пользователи') { showUpdateUser.value = true }
  else if (name == 'Электронный архив') { showUpdateDoc.value = true }
};

const deleteItem = (item, name) => {
  //
  selectedItem.value = item;
  itemName.value = name;
  showDeleteItem.value = true;
};

const rollbackItem = (item, section) => {
  //
  selectedItem.value = item;
  itemName.value = section;
  showRollbackItem.value = true;
};

const printItem = (item, section) => {
  //
  downloadFile(item.id, section);
};

const setStatusExit = (item) => {
  //
  showCarExitPermit.value = true;
  selectedItem.value = item;
};

const setDefaultStatus = (item) => {
  //
  showSetDefaultStatus.value = true;
  selectedItem.value = item;
};

const statusExitProhibited = (item) => {
  //
  showExitProhibited.value = true;
  selectedItem.value = item;
};

const createExitCarpass = (item) => {
  //
  showCreateExitCarpass.value = true;
  selectedItem.value = item;
};

</script>

<template>
  <!-- Show loading spinner while loading is true -->
  <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
    <PulseLoader />
    ЗАГРУЗКА ДАННЫХ...
  </div>

  <!-- Show when loading is done -->
  <div v-else>

  <!-- **********************   MODAL CARPASS CARD   ************************** -->
  <div v-if="showItemCard" :class="[state.item_for_card ? modalStyleSecond : modalStyle]">
    <FormAddCarpass @close-modal="showItemCard=false" @doc-created="getData" :itemData="selectedItem" :isCard="true"/>
  </div>
  <!-- **********************   MODAL ADD CARPASS   ************************** -->
  <div v-if="showAddItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddCarpass @close-modal="showAddItem=false" @doc-created="getData"/>
  </div>
  <!-- **********************   MODAL EDIT CARPASS   ************************** -->
  <div v-if="showUpdateItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddCarpass @close-modal="showUpdateItem=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>

  
  <!-- **********************   MODAL DELETE CARPASS   ************************** -->
  <div v-if="showDeleteItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormDeleteCarpass @close-modal="showDeleteItem=false" @doc-created="getData" :itemName="itemName" :itemData="selectedItem"/>
  </div>

  <!-- **********************   MODAL ROLLBACK CARPASS   ************************** -->
  <div v-if="showRollbackItem" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormRollbackCarpass @close-modal="showRollbackItem=false" @doc-created="getData" :itemName="itemName" :itemData="selectedItem"/>
  </div>

  <!-- **********************   MODAL CAR EXIT PERMIT   ************************** -->
  <div v-if="showCarExitPermit" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormCarExitPermit @close-modal="showCarExitPermit=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>

  <!-- **********************   MODAL SET DEFAULT STATUS   ************************** -->
  <div v-if="showSetDefaultStatus" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormSetDefaultStatus @close-modal="showSetDefaultStatus=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>

  <!-- **********************   MODAL EXIT PROHIBITED   ************************** -->
  <div v-if="showExitProhibited" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormExitProhibited @close-modal="showExitProhibited=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL EXITCARPASS CARD   ************************** -->
  <div v-if="showCardExitCarpass" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddExitCarpass @close-modal="showCardExitCarpass=false" @doc-created="getData" :itemData="selectedItem" :isCard="true"/>
  </div>
  <!-- **********************   MODAL EXITCARPASS ADD   ************************** -->
  <div v-if="showCreateExitCarpass" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddExitCarpass @close-modal="showCreateExitCarpass=false" @doc-created="getData" :isCreate=true :itemData="selectedItem"/>
  </div>
  <!-- **********************   MODAL EXITCARPASS EDIT  ************************** -->
  <div v-if="showUpdateExitCarpass" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormAddExitCarpass @close-modal="showUpdateExitCarpass=false" @doc-created="getData" :isCreate=false :itemData="selectedItem"/>
  </div>
  <!-- **********************   MODAL INIT ADDING EXITCARPASS  ************************** -->
  <div v-if="showAddExitcarpass" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormInitAddExitcarpass @close-modal="showAddExitcarpass=false" @doc-created="createExitCarpass" />
  </div>


  <!-- **********************   MODAL ENTRY_REQUEST CARD   ************************** -->
  <div v-if="showCardEntryRequest" :class="[state.item_for_card ? modalStyleSecond : modalStyle]" >
    <FormEntryRequest @close-modal="showCardEntryRequest=false" @doc-created="getData" :itemData="selectedItem" :isCard="true"/>
  </div>
  <!-- **********************   MODAL ENTRY_REQUEST ADD   ************************** -->
  <div v-if="showAddEntryRequest" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormEntryRequest @close-modal="showAddEntryRequest=false" @doc-created="getData" />
  </div>
  <!-- **********************   MODAL ENTRY_REQUEST EDIT  ************************** -->
  <div v-if="showUpdateEntryRequest" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormEntryRequest @close-modal="showUpdateEntryRequest=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL CONTACT CARD   ************************** -->
  <div v-if="showCardContact" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormContact @close-modal="showCardContact=false" @doc-created="getData" :itemData="selectedItem" :isCard="true"/>
  </div>
  <!-- **********************   MODAL CONTACT ADD   ************************** -->
  <div v-if="showAddContact" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormContact @close-modal="showAddContact=false" @doc-created="getData" />
  </div>
  <!-- **********************   MODAL CONTACT EDIT  ************************** -->
  <div v-if="showUpdateContact" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormContact @close-modal="showUpdateContact=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL BROKER CARD   ************************** -->
  <div v-if="showCardBroker" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormBroker @close-modal="showCardBroker=false" @doc-created="getData" :itemData="selectedItem" :isCard="true"/>
  </div>
  <!-- **********************   MODAL BROKER ADD   ************************** -->
  <div v-if="showAddBroker" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormBroker @close-modal="showAddBroker=false" @doc-created="getData" />
  </div>
  <!-- **********************   MODAL BROKER EDIT  ************************** -->
  <div v-if="showUpdateBroker" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormBroker @close-modal="showUpdateBroker=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL USER CARD   ************************** -->
  <div v-if="showCardUser" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormUser @close-modal="showCardUser=false" @doc-created="getData" :itemData="selectedItem" :isCard="true"/>
  </div>
  <!-- **********************   MODAL USER ADD   ************************** -->
  <div v-if="showAddUser" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormUser @close-modal="showAddUser=false" @doc-created="getData" />
  </div>
  <!-- **********************   MODAL USER EDIT  ************************** -->
  <div v-if="showUpdateUser" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormUser @close-modal="showUpdateUser=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>


  <!-- **********************   MODAL DOC CARD   ************************** -->
  <div v-if="showCardDoc" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormDoc @close-modal="showCardDoc=false" @doc-created="getData" @open-itemcard="openItemCard" :itemData="selectedItem" :isCard="true"/>
  </div>
  <!-- **********************   MODAL DOC ADD   ************************** -->
  <div v-if="showAddDoc" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormDoc @close-modal="showAddDoc=false" @doc-created="getData" />
  </div>
  <!-- **********************   MODAL DOC EDIT  ************************** -->
  <div v-if="showUpdateDoc" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
    <FormDoc @close-modal="showUpdateDoc=false" @doc-created="getData" :itemData="selectedItem"/>
  </div>


  <div class="flex flex-col md:flex-row p-3 gap-3 ">
    <div class="flex-auto w-auto md:w-64">
      <div class="">
        <ListAdv @btn-add="addItem" @btn-edit="editItem" @btn-delete="deleteItem" @btn-createexitcarpass="createExitCarpass"
          @btn-refresh="getData" @btn-itemcard="itemCard" @btn-rollback="rollbackItem" @btn-print="printItem" 
          @btn-setstatusexit="setStatusExit" @btn-cancelstatusexit="setDefaultStatus" @btn-exitprohibited="statusExitProhibited"
          :name="props.list_title" :data="state.records" :listTableColumns="state.listTableColumns" :listItemFileds="state.listItemFileds"/>
      </div>
    </div>
  </div>

  </div>
</template>
