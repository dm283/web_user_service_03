<script setup>
import { defineProps, ref, reactive, onMounted, computed } from 'vue';
import axios from 'axios';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import Dashboard from '@/components/Dashboard.vue';

// import from config.ini file in backend folder
import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");
var companyName = parser.get("content", "company_name");
// console.log('backendIpAddress =', backendIpAddress)
// console.log('backendPort =', backendPort)

const state = reactive({
  data: [],
  isLoading: true,
})

const filterSubstring = ref('')

  async function getData() {
  // get data from API
  try {
      state.data = [];

      state.storageState = {};
      state.storageState.barTnvedQuantity = {};
      state.storageState.barTnvedQuantity.datax = [];
      state.storageState.barTnvedQuantity.datay = [];

      state.accountBook = {};
      state.accountBook.barRecTnvedQuantity = {};
      state.accountBook.barRecTnvedQuantity.datax = [];
      state.accountBook.barRecTnvedQuantity.datay = [];

      state.reportVehicle = {};

      let query = `http://${backendIpAddress}:${backendPort}/dashboard/` + filterSubstring.value
      // let query = `http://${backendIpAddress}:${backendPort}/dashboard/` + '?token=' + props.token + filterSubstring.value
      // console.log('query =', query)
      const response = await axios.get(query);
      
      // console.log('API RESPONSE =', response.status)
      // if (response.status == 200) {
      //   isAuthorized.value = true;
      // };


      state.data = response.data;

      state.companyName = state.data['company_name']
      state.updateDateTime = state.data['current_datetime']

      state.storageState.cardProductQuantity = state.data['product_quantity'][0]['product_quantity'];
      state.storageState.cardDtQuantity = state.data['dt_quantity'][0]['dt_quantity'];
      for (let i of state.data['tnved_quantity']) {
        state.storageState.barTnvedQuantity.datax.push(i['g33']);
        state.storageState.barTnvedQuantity.datay.push(i['cnt'])
      }   
      state.storageState.listProductsStorage = state.data['products_on_storage']

      state.accountBook.cardRecProductQuantity = state.data['received_product_quantity'][0]['received_product_quantity'];
      state.accountBook.cardRecDtQuantity = state.data['received_dt_quantity'][0]['received_dt_quantity'];
      for (let i of state.data['received_tnved_quantity']) {
        state.accountBook.barRecTnvedQuantity.datax.push(i['g33']);
        state.accountBook.barRecTnvedQuantity.datay.push(i['cnt'])
      }   
      state.accountBook.listAccountBook = state.data['account_book']

      state.reportVehicle.listreportVehicle = state.data['report_vehicle']

    } catch (error) {
      console.error('Error fetching items', error.response.status);
      if (error.response.status == 401) {
        isAuthorized.value = false;
      }
    } finally {
      state.isLoading = false;
    }
};


async function updateData() {
  //
  state.isLoading = true;
  await getData();
};

const handleSubmit = async () => {
  //
  // console.log('handle submit!') 
  const filters = {
    'filterAccountBookDateDocFrom': filterAccountBookDateDocFrom, 
    'filterAccountBookDateDocTo': filterAccountBookDateDocTo, 
    'filterAccountBookDateEnterFrom': filterAccountBookDateEnterFrom, 
    'filterAccountBookDateEnterTo': filterAccountBookDateEnterTo, 
    'filterReportVehicleDateEnterFrom': filterReportVehicleDateEnterFrom, 
    'filterReportVehicleDateExitTo': filterReportVehicleDateExitTo
  }; 
  filterSubstring.value = '&';
  
  for (let f in filters) {
    // console.log('filters.values =', filters[f].value)
    if (filters[f].value) {
      filterSubstring.value += f + '=' + filters[f].value + '&'
    }
  }
  
  // console.log('filterSubstring = ', filterSubstring.value)

  state.isLoading = true;
  await getData();   
};


onMounted(async () => {
  // initial data getting
  await getData()
});


const storageStateListTableColumns = {
    'gtdnum':'Номер ДТ','name':'Владелец','date_in':'Дата прием','g32':'№ тов.',
    'g31':'Наименование товара','g33_in':'Код ТНВЭД','g31_3':'Кол.доп.ед', 
    'g31_3a':'Ед.изм.', 'g35':'Вес брутто', 'date_chk':'Дата ок.хр.'
}

const accountBookListTableColumns = {
  'gtdnum': 'Номер ДТ', 'name': 'Владелец', 'date_in': 'Дата приема','time_in': 'Время приема',
    'date_chk': 'Дата ок.хр.','g32': '№ тов.','g31': 'Наименование товара','g33_in': 'Код ТНВЭД',
    'g35': 'Вес брутто', 'g31_3': 'Кол.доп.ед', 'g31_3a': 'Ед.изм.', 'doc_num_out': '№ ДТ выдачи',
    'gtdregime_out': 'Режим выдачи', 'date_out': 'Дата выдачи', 'g35_out': 'Выдача брутто',
    'g31_3_out': 'Выд.доп.ед'
}

const reportVehicleListTableColumns = {
  'id':'№ п/п', 'gtdnum':'Номер ДТ', 'g32':'№ тов.', 'g33_in':'Код ТНВЭД', 'g31':'Наименование товара', 'g35':'Вес брутто',
    'g31_3':'Кол.доп.ед', 'g31_3a':'Ед.изм.', 'date_in':'Дата приема', 'place':'Скл.номер', 'date_chk':'Дата ок.хр.', 
       'exp_date':'Срок годности', 'gtdregime_out':'Режим выдачи', 'doc_num_out':'№ ДТ выдачи', 'g33_out':'Код ТНВЭД выдачи',
    'g35_out':'Выдача брутто', 'g31_3_out':'Выд.доп.ед', 'date_out':'Дата выдачи', 
    'g35ost_':'Остаток брутто', 'g31_3ost_':'Остаток Доп.ед',
}


const filterAccountBookDateDocFrom = ref();
const filterAccountBookDateDocTo = ref();

const filterAccountBookDateEnterFrom = ref()
const filterAccountBookDateEnterTo = ref()

const filterReportVehicleDateEnterFrom = ref()
const filterReportVehicleDateExitTo = ref()

const showFiltersBar = ref(false);
const mouseOverFiltersBar = ref(false);


const clearFilters = async () => {
  filterAccountBookDateDocFrom.value = '';
  filterAccountBookDateDocTo.value = '';

  filterAccountBookDateEnterFrom.value = ''
  filterAccountBookDateEnterTo.value = ''

  filterReportVehicleDateEnterFrom.value = ''
  filterReportVehicleDateExitTo.value = ''

  state.isLoading = true;
  await handleSubmit();
}

const tabNumberVar = ref(1);  // initial tab number
const changeTabValue = (n) => {
  // rememberance of tab number from Dashboard component
  tabNumberVar.value = n;
};

</script>


<template>
  <!-- Show loading spinner while loading is true -->
  <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
    <PulseLoader />
    ЗАГРУЗКА ДАННЫХ...
  </div>

  <!-- Show when loading is done -->
  <div v-else class="">
    <Dashboard 
      @change-tab="changeTabValue"
      :tabNumberVar = "tabNumberVar"

      :storageStateBarTnvedQuantityDatax = "state.storageState.barTnvedQuantity.datax" 
      :storageStateBarTnvedQuantityDatay="state.storageState.barTnvedQuantity.datay" 
      :storageStateCardProductQuantity="state.storageState.cardProductQuantity" 
      :storageStateCardDtQuantity="state.storageState.cardDtQuantity" 
      :storageStateListName="'Товары на складе'" 
      :storageStateListProductsStorage="state.storageState.listProductsStorage" 
      :storageStateListTableColumns="storageStateListTableColumns"

      :accountBookBarRecTnvedQuantityDatax = "state.accountBook.barRecTnvedQuantity.datax" 
      :accountBookBarRecTnvedQuantityDatay="state.accountBook.barRecTnvedQuantity.datay" 
      :accountBookCardRecProductQuantity="state.accountBook.cardRecProductQuantity" 
      :accountBookCardRecDtQuantity="state.accountBook.cardRecDtQuantity" 
      :accountBookListName="'Книга учета'" 
      :accountBookListAccountBook="state.accountBook.listAccountBook" 
      :accountBookListTableColumns="accountBookListTableColumns"

      :reportVehicleListName="'Отчет ТС'" 
      :reportVehicleListAccountBook="state.reportVehicle.listreportVehicle" 
      :reportVehicleListTableColumns="reportVehicleListTableColumns"
    /> 
  </div>
</template>
