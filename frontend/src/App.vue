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


<!-- **************   HEADER    ******************* -->
<nav class="bg-gradient-to-r from-sky-600 to-sky-400 px-5 h-14 text-white overflow-auto">  
  <div class="text-center md:flex md:float-left text-xl">
    <div class="inline-block border-2 border-cyan-50 w-10 h-10 rounded-full pt-1 mt-2 mr-5 cursor-pointer text-cyan-300 hover:border-cyan-300 active:text-cyan-100 active:border-cyan-100">
      <i class="pi pi-bars" style="font-size: 1.3rem" @click="showMenuBar=(showMenuBar) ? false:true"></i>
    </div>
    <div class="inline-block mt-3 px-4 border-r-2">{{ companyName }}</div>
    <div class="inline-block mt-3 px-4">Личный кабинет [ dev ]</div>
  </div>
  <div class="mt-3.5 text-center md:flex md:float-right">
    <div class="inline-block px-4 text-base">{{ login }}</div>
    <div class="header-btn"><i class="pi pi-user" style="font-size: 1.3rem" @click="signOut()"></i></div>
    <div class="header-btn"><i class="pi pi-ellipsis-v" style="font-size: 1.3rem"></i></div>
    <div class="header-btn" @click="showMessengerBar=(showMessengerBar) ? false:true">
      <i class="pi pi-comment" style="font-size: 1.3rem"></i></div>
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
  </div>
</div>
</div>
</div>
</template>


<style lang="postcss" scoped>
.header-btn {
  @apply inline-block mx-3 mt-1 text-cyan-200 cursor-pointer hover:text-cyan-50
}
</style>