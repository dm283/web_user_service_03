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


const state = reactive({
  data: [],
  isLoading: true,
})

const tabNumberVar = ref(1);  // initial tab number
const filterSubstring = ref('')
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

const token = ref(null);


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

      let query = `http://${backendIpAddress}:${backendPort}/dashboard/` + '?token=' + token.value + filterSubstring.value
      console.log('query =', query)
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
  // updates data from database
  state.isLoading = true;
  await getData();
};


const filterBarShow = () => {
  //
  showFiltersBar.value=(showFiltersBar.value) ? false:true;
}


const applyFilters = async () => {
  // applies filters
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
    if (filters[f].value) {
      filterSubstring.value += f + '=' + filters[f].value + '&'
    }
  }

  state.isLoading = true;
  await getData();   
};


const clearFilters = async () => {
  // clears filters values
  filterAccountBookDateDocFrom.value = '';
  filterAccountBookDateDocTo.value = '';

  filterAccountBookDateEnterFrom.value = ''
  filterAccountBookDateEnterTo.value = ''

  filterReportVehicleDateEnterFrom.value = ''
  filterReportVehicleDateExitTo.value = ''

  state.isLoading = true;
  await applyFilters();
}


const changeTabValue = (n) => {
  // rememberance of tab number from Dashboard component
  tabNumberVar.value = n;
};


onMounted(async () => {
  // initial data getting
  await getData()
});

</script>


<template>
  <div class="relative">

  <!-- Show loading spinner while loading is true -->
  <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
    <PulseLoader />
    ЗАГРУЗКА ДАННЫХ...
  </div>

  <!-- Show when loading is done -->
  <div v-else class="">
    <Dashboard 
      @change-tab="changeTabValue"
      @update-dashboard="updateData"
      @filters-show="filterBarShow"
      :tabNumberVar = "tabNumberVar"
      :updateDateTime = "state.updateDateTime"

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

  <!-- **************   FILTERS SIDEBAR    ******************* -->
  <div v-if="showFiltersBar" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50">
    <div  class="absolute z-20 top-0 right-0 border w-96 h-full bg-white">
    <div class="p-3 bg-gray-200 overflow-auto">
    <div class="float-left text-xl ">
      Фильтры данных
    </div>
    <div class="float-right cursor-pointer hover:text-gray-500" @click="showFiltersBar=false">
      <i class="pi pi-times" style="font-size: 1.5rem"></i>
    </div>
    </div>

    <form @submit.prevent="applyFilters" class="mx-0 mt-3 ">

      <div class="mt-5 mb-2 ml-3 font-semibold">КНИГА УЧЁТА</div>

      <div class="mx-5 mb-2">
        <label class="formLabelStyle">date_doc</label>
        <div class="flex ">
          <div class="pt-1">c</div>
          <input
            type="date"
            v-model="filterAccountBookDateDocFrom"
            id="filterAccountBookDateDocFrom"
            name="filterAccountBookDateDocFrom"
            :class="filterAccountBookDateDocFrom ? 'formInputStyleFilled' : 'formInputStyle'"
            placeholder=""
          />
          <div class="pt-1">по</div>
          <input
            type="date"
            v-model="filterAccountBookDateDocTo"
            id="filterAccountBookDateDocTo"
            name="filterAccountBookDateDocTo"
            :class="filterAccountBookDateDocTo ? 'formInputStyleFilled' : 'formInputStyle'"
            placeholder=""
          />   
        </div>
      </div>

      <div class="mx-5 mb-2">
        <label class="formLabelStyle">Дата приёма</label>
        <div class="flex ">
          <div class="pt-1">c</div>
          <input
            type="date"
            v-model="filterAccountBookDateEnterFrom"
            id="filterAccountBookDateEnterFrom"
            name="filterAccountBookDateEnterFrom"
            :class="filterAccountBookDateEnterFrom ? 'formInputStyleFilled' : 'formInputStyle'"
            placeholder=""
          />
          <div class="pt-1">по</div>
          <input
            type="date"
            v-model="filterAccountBookDateEnterTo"
            id="filterAccountBookDateEnterTo"
            name="filterAccountBookDateEnterTo"
            :class="filterAccountBookDateEnterTo ? 'formInputStyleFilled' : 'formInputStyle'"
            placeholder=""
          />   
        </div>
      </div>

      <hr class="mt-7"> 

      <div class="mt-5 mb-2 ml-3 font-semibold">ОТЧЁТ ТС</div>

      <div class="mx-5 mb-2">
        <label class="formLabelStyle">Дата выдачи - Дата приёма</label>
        <div class="flex ">
          <div class="pt-1">c</div>
          <input
            type="date"
            v-model="filterReportVehicleDateEnterFrom"
            id="filterDateDocFrom"
            name="filterDateDocFrom"
            :class="filterReportVehicleDateEnterFrom ? 'formInputStyleFilled' : 'formInputStyle'"
            placeholder=""
          />
          <div class="pt-1">по</div>
          <input
            type="date"
            v-model="filterReportVehicleDateExitTo"
            id="filterDateDocTo"
            name="filterDateDocTo"
            :class="filterReportVehicleDateExitTo ? 'formInputStyleFilled' : 'formInputStyle'"
            placeholder=""
          />   
        </div>
      </div>

      <hr class="mt-7">

      <div class="mt-7 flex justify-center space-x-5 py-3 px-5 text-center">
        <button
          class="bg-sky-400 text-white font-semibold rounded-full w-60
            drop-shadow-md hover:shadow-lg hover:bg-sky-500"
          type="submit"
        >
        Применить
        </button>
        <button
          class="bg-rose-400 text-white font-semibold rounded-full px-3 py-2 w-60
            drop-shadow-md hover:shadow-lg hover:bg-rose-500"
          type="button"
          @click="clearFilters()"
        >
        Сбросить
        </button>
      </div>
    </form>

  </div>
</div>

</div>
</template>


<style lang="postcss" scoped>
.formLabelStyle {
  @apply mx-1 block text-xs font-bold text-blue-500
}

.formInputStyle {
  @apply border-b-2 border-blue-300 text-gray-300 text-base font-medium w-36 py-1 px-1 mb-2
  hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer
}

.formInputStyleFilled {
  @apply border-b-2 border-blue-300 text-gray-600 text-base font-medium w-36 py-1 px-1 mb-2
  hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer
}
</style>
