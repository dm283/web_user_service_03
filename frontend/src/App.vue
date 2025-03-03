<script setup>
import { defineProps, ref, reactive, onMounted, computed } from 'vue';
import 'primeicons/primeicons.css';
// import router from '@/router';
import axios from 'axios';
import { RouterView } from 'vue-router';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import { useToast } from 'vue-toastification';

import Navbar from './components/Navbar.vue';
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


const toast = useToast();

const state = reactive({
  data: [],
  isLoading: true,
})

const token = ref('')
const isAuthorized = ref(false)
const login = ref('');
const password = ref('');
const authFormMessage = ref('')
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

</script>


<template>
<!--    ===============================    AUTHENTIFICATION PAGE    ===============================    -->
<div v-if="!isAuthorized" class="flex">
    
  <div class="mt-40 mx-auto border rounded-lg overflow-hidden">
    <div class="py-2 px-5 bg-gradient-to-r from-sky-800 to-sky-600 text-center text-white text-lg">
      Альта-Софт | Управление терминалом
    </div>
    <form @submit.prevent="authSubmit" class="mx-5 mt-5">
      <div class="my-2">
        <label class=formLabelStyle>Логин</label>
        <input
            type="text"
            v-model="login"
            id="login"
            name="login"
            class=formInputStyle
            placeholder=""
            required
            v-on:focus="authFormMessage=''"
          />
      </div>
      <div class="my-2">
        <label class=formLabelStyle>Пароль</label>
        <input
            type="password"
            v-model="password"
            id="password"
            name="password"
            class=formInputStyle
            placeholder=""
            required
            v-on:focus="authFormMessage=''"
          />
      </div>
      <div class="mt-5 mb-6 text-center">
        <button
          class="text-slate-400 text-sm font-semibold border border-slate-400 rounded-lg w-32 h-9 hover:text-slate-500 hover:border-slate-500"
          type="submit"
        >
        ВХОД
        </button>
        <!-- bg-green-500 text-white font-semibold rounded-full px-3 py-2 w-60 shadow-md hover:shadow-lg hover:bg-green-600 -->
      </div>
    </form>
    <div class="mb-5 text-red-500 text-center">
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


<!-- **************   HEADER    ******************* -->
<nav class="bg-gradient-to-r from-sky-800 to-sky-600 px-5 h-14 text-white overflow-auto">  
  <div class="text-center md:flex md:float-left text-xl">
    <div class="inline-block w-10 h-10 rounded-full pt-1.5 mt-2 mr-5 cursor-pointer 
      text-cyan-300 hover:bg-sky-700 active:text-cyan-100">
      <i class="pi pi-bars" style="font-size: 1.3rem" @click="showMenuBar=(showMenuBar) ? false:true"></i>
    </div>
    <div class="inline-block mt-3 px-4 border-r-2">{{ companyName }}</div>
    <div class="inline-block mt-3 px-4">Управление терминалом</div>
  </div>
  <div class="mt-3.5 text-center md:flex md:float-right">
    <div class="inline-block px-4 text-base">{{ login }}</div>
    <div class="header-btn"><i class="pi pi-user" style="font-size: 1.3rem" @click="signOut()"></i></div>
    <div class="header-btn"><i class="pi pi-ellipsis-v" style="font-size: 1.3rem"></i></div>
    <div class="header-btn"><i class="pi pi-bell" style="font-size: 1.3rem"></i></div>
    <!-- <div class="header-btn" @click="showMessengerBar=(showMessengerBar) ? false:true">
      <i class="pi pi-comment" style="font-size: 1.3rem"></i></div> -->
    <div class="header-btn"><div class="-mt-0.5">RU</div></div>
  </div>
</nav>


<!-- **************   MAIN MENU SIDEBAR    ******************* -->
<div v-if="showMenuBar" class="w-60 h-full fixed bg-sky-700 text-white">
  <div class="">
    <RouterLink to="/carpasses">
      <MenuSection :label="'Пропуска'" :icon="'truck'" :description="'Информация о пропусках ТС'"/>
    </RouterLink>
    <RouterLink to="/">
      <MenuSection :label="'Документы'" :icon="'file'" :description="'Загрузка документов'"/>
    </RouterLink>
    <RouterLink to="/dashboard">
      <MenuSection :label="'Дашборд'" :icon="'th-large'" :description="'Информация о состоянии склада'"/>
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
  </div>
</div>
</div>
</div>
</template>


<style lang="postcss" scoped>
.formLabelStyle {
  @apply mx-1 block text-xs font-bold text-slate-400 
}
.formInputStyle {
  @apply border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer
}
.header-btn {
  @apply inline-block mx-3 mt-1 text-cyan-200 cursor-pointer hover:text-cyan-50
}
</style>