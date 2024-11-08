<script setup>
import { defineProps, ref, reactive, onMounted, computed } from 'vue';
import 'primeicons/primeicons.css';
// import router from '@/router';
import axios from 'axios';
import { RouterView } from 'vue-router';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import { useToast } from 'vue-toastification';

import Navbar from './components/Navbar.vue';
// import Dashboard from './components/Dashboard.vue';
import Chat from './components/Chat.vue';
import MenuSection from './components/MenuSection.vue';


// import from config.ini file in backend folder
import data from "../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");
var companyName = parser.get("content", "company_name");
// console.log('backendIpAddress =', backendIpAddress)
// console.log('backendPort =', backendPort)


const toast = useToast();

const state = reactive({
  data: [],
  isLoading: true,
})

const token = ref('')
// const filterSubstring = ref('')
const isAuthorized = ref(false)
const login = ref('');
const password = ref('');
const authFormMessage = ref('')
const showFiltersBar = ref(false);
const showMessengerBar = ref(false);
const showMenuBar = ref(true);


async function getData() {
  //
  try {
    state.users = [];

    let query_users = `http://${backendIpAddress}:${backendPort}/users/`
    const response_users = await axios.get(query_users)
    for (let u of response_users.data) {
      state.users.push(u['login'])
    }
  } catch (error) {
    console.error('Error fetching items', error.response.status);
    if (error.response.status == 401) {
      isAuthorized.value = false;
    }
  } finally {
    state.isLoading = false;
  }
};


// async function getData() {
//   //
//   try {
//       state.data = [];

//       state.storageState = {};
//       state.storageState.barTnvedQuantity = {};
//       state.storageState.barTnvedQuantity.datax = [];
//       state.storageState.barTnvedQuantity.datay = [];

//       state.accountBook = {};
//       state.accountBook.barRecTnvedQuantity = {};
//       state.accountBook.barRecTnvedQuantity.datax = [];
//       state.accountBook.barRecTnvedQuantity.datay = [];

//       state.reportVehicle = {};

//       state.users = [];

//       let query_users = `http://${backendIpAddress}:${backendPort}/users/`
//       const response_users = await axios.get(query_users)
//       for (let u of response_users.data) {
//         state.users.push(u['login'])
//       }

//       let query = `http://${backendIpAddress}:${backendPort}/dashboard/` + '?token=' + token.value + filterSubstring.value
//       //let query = 'http://localhost:8000/dashboard/' + '?token=' + token.value + filterSubstring.value
//       // console.log('query =', query)
//       const response = await axios.get(query);
      
//       // console.log('API RESPONSE =', response.status)
//       // if (response.status == 200) {
//       //   isAuthorized.value = true;
//       // };


//       state.data = response.data;

//       state.companyName = state.data['company_name']
//       state.updateDateTime = state.data['current_datetime']

//       state.storageState.cardProductQuantity = state.data['product_quantity'][0]['product_quantity'];
//       state.storageState.cardDtQuantity = state.data['dt_quantity'][0]['dt_quantity'];
//       for (let i of state.data['tnved_quantity']) {
//         state.storageState.barTnvedQuantity.datax.push(i['g33']);
//         state.storageState.barTnvedQuantity.datay.push(i['cnt'])
//       }   
//       state.storageState.listProductsStorage = state.data['products_on_storage']

//       state.accountBook.cardRecProductQuantity = state.data['received_product_quantity'][0]['received_product_quantity'];
//       state.accountBook.cardRecDtQuantity = state.data['received_dt_quantity'][0]['received_dt_quantity'];
//       for (let i of state.data['received_tnved_quantity']) {
//         state.accountBook.barRecTnvedQuantity.datax.push(i['g33']);
//         state.accountBook.barRecTnvedQuantity.datay.push(i['cnt'])
//       }   
//       state.accountBook.listAccountBook = state.data['account_book']

//       state.reportVehicle.listreportVehicle = state.data['report_vehicle']

//     } catch (error) {
//       console.error('Error fetching items', error.response.status);
//       if (error.response.status == 401) {
//         isAuthorized.value = false;
//       }
//     } finally {
//       state.isLoading = false;
//     }
// };


// async function updateData() {
//   //
//   state.isLoading = true;
//   await getData();
// };

// const handleSubmit = async () => {
//   //
//   // console.log('handle submit!') 
//   const filters = {
//     'filterAccountBookDateDocFrom': filterAccountBookDateDocFrom, 
//     'filterAccountBookDateDocTo': filterAccountBookDateDocTo, 
//     'filterAccountBookDateEnterFrom': filterAccountBookDateEnterFrom, 
//     'filterAccountBookDateEnterTo': filterAccountBookDateEnterTo, 
//     'filterReportVehicleDateEnterFrom': filterReportVehicleDateEnterFrom, 
//     'filterReportVehicleDateExitTo': filterReportVehicleDateExitTo
//   }; 
//   filterSubstring.value = '&';
  
//   for (let f in filters) {
//     // console.log('filters.values =', filters[f].value)
//     if (filters[f].value) {
//       filterSubstring.value += f + '=' + filters[f].value + '&'
//     }
//   }
  
//   // console.log('filterSubstring = ', filterSubstring.value)

//   state.isLoading = true;
//   await getData();   
// };


// onMounted(async () => {
//     await getData()
// });


// const storageStateListTableColumns = {
//     'gtdnum':'Номер ДТ','name':'Владелец','date_in':'Дата прием','g32':'№ тов.',
//     'g31':'Наименование товара','g33_in':'Код ТНВЭД','g31_3':'Кол.доп.ед', 
//     'g31_3a':'Ед.изм.', 'g35':'Вес брутто', 'date_chk':'Дата ок.хр.'
// }

// const accountBookListTableColumns = {
//   'gtdnum': 'Номер ДТ', 'name': 'Владелец', 'date_in': 'Дата приема','time_in': 'Время приема',
//     'date_chk': 'Дата ок.хр.','g32': '№ тов.','g31': 'Наименование товара','g33_in': 'Код ТНВЭД',
//     'g35': 'Вес брутто', 'g31_3': 'Кол.доп.ед', 'g31_3a': 'Ед.изм.', 'doc_num_out': '№ ДТ выдачи',
//     'gtdregime_out': 'Режим выдачи', 'date_out': 'Дата выдачи', 'g35_out': 'Выдача брутто',
//     'g31_3_out': 'Выд.доп.ед'
// }

// const reportVehicleListTableColumns = {
//   'id':'№ п/п', 'gtdnum':'Номер ДТ', 'g32':'№ тов.', 'g33_in':'Код ТНВЭД', 'g31':'Наименование товара', 'g35':'Вес брутто',
//     'g31_3':'Кол.доп.ед', 'g31_3a':'Ед.изм.', 'date_in':'Дата приема', 'place':'Скл.номер', 'date_chk':'Дата ок.хр.', 
//        'exp_date':'Срок годности', 'gtdregime_out':'Режим выдачи', 'doc_num_out':'№ ДТ выдачи', 'g33_out':'Код ТНВЭД выдачи',
//     'g35_out':'Выдача брутто', 'g31_3_out':'Выд.доп.ед', 'date_out':'Дата выдачи', 
//     'g35ost_':'Остаток брутто', 'g31_3ost_':'Остаток Доп.ед',
// }


// const filterAccountBookDateDocFrom = ref();
// const filterAccountBookDateDocTo = ref();

// const filterAccountBookDateEnterFrom = ref()
// const filterAccountBookDateEnterTo = ref()

// const filterReportVehicleDateEnterFrom = ref()
// const filterReportVehicleDateExitTo = ref()

// const showFiltersBar = ref(false);
// const mouseOverFiltersBar = ref(false);

// const showMessengerBar = ref(false);
// const showMenuBar = ref(true);

// // const formInputStyle2 = ref(
// //   (filterAccountBookDateDocFrom.value) ? 
// //   'border-b-2 border-blue-300 text-green-300 text-base font-medium w-36 py-1 px-1 mb-2 \
// //   hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer' :
// //   'border-b-2 border-blue-300 text-red-300 text-base font-medium w-36 py-1 px-1 mb-2 \
// //   hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer'
// // );

// // const formInputStyle11 = ref('border-b-2 border-blue-300 text-green-300 text-base font-medium w-36 py-1 px-1 mb-2 \
// //   hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer')
// //   const formInputStyle12 = ref('border-b-2 border-blue-300 text-red-300 text-base font-medium w-36 py-1 px-1 mb-2 \
// //   hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer')

// const testA = ref(true)

// const clearFilters = async () => {
//   filterAccountBookDateDocFrom.value = '';
//   filterAccountBookDateDocTo.value = '';

//   filterAccountBookDateEnterFrom.value = ''
//   filterAccountBookDateEnterTo.value = ''

//   filterReportVehicleDateEnterFrom.value = ''
//   filterReportVehicleDateExitTo.value = ''

//   state.isLoading = true;
//   await handleSubmit();
// }

const authSubmit = async () => {
  //
  try {
    const response = await axios.post(
      `http://${backendIpAddress}:${backendPort}/signin?` + 'login=' + login.value + '&password=' + password.value
    );
    token.value = response.data.your_new_token;

    if (response.status == 202) {
      isAuthorized.value = true;
    };

    state.isLoading = true;
    await getData();
  } catch (error) {
    // console.error('unaccepted', error);
    authFormMessage.value = 'Некорректный логин или пароль.'
    isAuthorized.value = false;
  };
};

const signOut = async () => {
  //
  try {
    let query = `http:///${backendIpAddress}:${backendPort}/dashboard/signout` + '?token=' + token.value
    const response = await axios.post(query);
  
    if (response.data.message == 'signed out') {
      login.value = '';
      password.value = '';
      isAuthorized.value = false;
    }
  } catch (error) {
    console.error('unable to sign out', error);
  }
};

// const tabNumberVar = ref(4);  // initial tab number
// const changeTabValue = (n) => {
//   // rememberance of tab number from Dashboard component
//   tabNumberVar.value = n;
// };


</script>


<template>
<!--    ===============================    AUTHENTIFICATION PAGE    ===============================    -->
<div v-if="!isAuthorized" class="flex">
    
  <div class="mt-40 mx-auto bg-gray-50 border rounded-lg overflow-hidden">
    <div class="py-2 px-5 bg-blue-400 text-center text-white text-lg">
      Дашборд | Витрина таможенного склада
    </div>
    <form @submit.prevent="authSubmit" class="mx-5 mt-2 ">
      <div class="my-2">
        <label class="block mb-2">Логин</label>
        <input
            type="text"
            v-model="login"
            id="login"
            name="login"
            class="border rounded-lg w-full h-8 p-3"
            placeholder=""
            required
            v-on:focus="authFormMessage=''"
          />
      </div>
      <div class="my-2">
        <label class="block mb-2">Пароль</label>
        <input
            type="password"
            v-model="password"
            id="password"
            name="password"
            class="border rounded-lg w-full h-8 p-3"
            placeholder=""
            required
            v-on:focus="authFormMessage=''"
          />
      </div>
      <div class="my-5 text-center">
        <button
          class="bg-green-500 text-white font-semibold rounded-full px-3 py-2 w-60
            shadow-md hover:shadow-lg hover:bg-green-600"
          type="submit"
        >
        Вход
        </button>
      </div>
    </form>
    <div class="mb-3 text-red-500 text-center">
      {{ authFormMessage }}
    </div>
  </div>
</div>


<!--    ===============================    CONTENT PAGE    ===============================    -->
<div v-if="isAuthorized" class="">

  <!-- **************   MESSENGER SIDEBAR    ******************* -->
  <div v-if="showMessengerBar" class="absolute z-10 w-screen h-full bg-black bg-opacity-50">
    <div class="absolute z-20 top-0 right-0 w-96 h-full bg-white">
      <div class="p-3 bg-green-400 overflow-auto">
      <div class="float-left text-xl text-white">
        <i class="pi pi-comment" style="font-size: 1.3rem"></i>
        <span class="ml-5">Корпоративный чат</span>
      </div>
      <div class="float-right cursor-pointer text-white hover:text-gray-500" @click="showMessengerBar=false">
        <i class="pi pi-times" style="font-size: 1.5rem"></i>
      </div>
      </div>

      <div class="relative">
      <Chat :username="login" :users="state.users" />
    </div>

    </div>

  </div>


  <!-- **************   FILTERS SIDEBAR    ******************* -->
  <div v-if="showFiltersBar" class="absolute z-10 w-screen h-full bg-black bg-opacity-50">
    <div  class="absolute z-20 top-0 right-0 border w-96 h-full bg-white">
    <div class="p-3 bg-gray-200 overflow-auto">
    <div class="float-left text-xl ">
      Фильтры данных
    </div>
    <div class="float-right cursor-pointer hover:text-gray-500" @click="showFiltersBar=false">
      <i class="pi pi-times" style="font-size: 1.5rem"></i>
    </div>
    </div>

    <form @submit.prevent="handleSubmit" class="mx-0 mt-3 ">

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


<!-- **************   HEADER    ******************* -->
<nav class="bg-gradient-to-r from-sky-600 to-sky-400 px-5 h-14 text-white overflow-auto">  
  <div class="text-center md:flex md:float-left text-xl">
    <div class="inline-block border-2 border-cyan-50 w-10 h-10 rounded-full pt-1 mt-2 mr-5 cursor-pointer text-cyan-300 hover:border-cyan-300 active:text-cyan-100 active:border-cyan-100">
      <i class="pi pi-bars" style="font-size: 1.3rem" @click="showMenuBar=(showMenuBar) ? false:true"></i>
    </div>
    <div class="inline-block mt-3 px-4 border-r-2">{{ companyName }}</div>
    <!-- <div class="inline-block px-4 border-r-2">Dashboard</div> -->
    <div class="inline-block mt-3 px-4">Личный кабинет [ dev ]</div>
  </div>
  <div class="mt-3.5 text-center md:flex md:float-right">
    <!-- <div class="inline-block px-4 text-base">{{ state.updateDateTime }}</div> -->
    <div class="inline-block px-4 text-base">{{ login }}</div>
    <div class="header-btn"><i class="pi pi-user" style="font-size: 1.3rem" @click="signOut()"></i></div>
    <!-- <div class="header-btn"><i class="pi pi-refresh" style="font-size: 1.3rem" @click="updateData()"></i></div> -->
    <div class="header-btn"><i class="pi pi-ellipsis-v" style="font-size: 1.3rem"></i></div>
    <div class="header-btn" @click="showMessengerBar=(showMessengerBar) ? false:true">
      <i class="pi pi-comment" style="font-size: 1.3rem"></i></div>
    <!-- <div class="header-btn" @click="showFiltersBar=(showFiltersBar) ? false:true">
      <i class="pi pi-filter" style="font-size: 1.3rem"></i></div> -->
  </div>
</nav>


<!-- **************   MAIN MENU SIDEBAR    ******************* -->
<div v-if="showMenuBar" class="w-60 h-full fixed bg-sky-700 text-white">
  <div class="">
    <RouterLink to="/">
      <MenuSection :label="'Документы'" :icon="'file'" :description="'Загрузка документов'"/>
    </RouterLink>
    <RouterLink to="/dashboard">
      <MenuSection :label="'Дашборд'" :icon="'th-large'" :description="'Информация о состоянии склада'"/>
    </RouterLink>
    <RouterLink to="/vehicles">
      <MenuSection :label="'Транспортные средства'" :icon="'truck'" :description="'Информация о ТС'"/>
    </RouterLink>
  </div>
</div>

<div class="flex">

  <!-- PSEUDO-DIV BEHIND SIDEBAR FOR MARGINING OF CONTENT DIV -->
  <div v-if="showMenuBar" class="w-60"></div>

  <div class="flex-1">
  <!-- Show loading spinner while loading is true -->
  <div v-if="state.isLoading" class="text-center text-gray-500 py-6">
    <PulseLoader />
    ЗАГРУЗКА ДАННЫХ...
  </div>

  <!-- Show when loading is done -->
  <div v-else class="bg-gray-50 ">
    <RouterView />

    <!-- <Dashboard 
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
    />  -->
  </div>
</div>
</div>
</div>
</template>


<style lang="postcss" scoped>
.header-btn {
  @apply inline-block mx-3 mt-1 text-cyan-200 cursor-pointer hover:text-cyan-50
}

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