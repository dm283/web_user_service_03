<script setup>
import { ref } from 'vue';
// import from config.ini file in backend folder
import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var companyName = parser.get("content", "company_name");
const userInfo = JSON.parse(localStorage.getItem('userInfo'));
const headerColor = ref('')
// headerColor.value = userInfo.contact_id == 0 ? "bg-gradient-to-r from-sky-800 to-sky-600  text-white" : 
//       "bg-gradient-to-r from-teal-800 to-teal-600  text-white"
headerColor.value = "bg-white text-gray-800"

</script>

<template>
  <div class="bg-white">
  <div :class=headerColor class="shadow-md mx-auto mt-32 px-5 w-fit h-20 overflow-auto 
    text-center text-2xl border border-gray-300 rounded-xl">
    <div class="inline-block mt-5 px-4 pb-1.5 border-r-2">{{ companyName }}</div>
    <div v-if="userInfo.contact_id != 0" class="inline-block mt-5 px-4 pb-1.5 border-r-2">{{ userInfo.contact_name }}</div>
    <div class="inline-block mt-5 px-4">Управление терминалом</div>
  </div>
  </div>
</template>
