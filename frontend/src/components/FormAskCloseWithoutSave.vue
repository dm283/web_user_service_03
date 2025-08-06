<script setup>
// import router from '@/router';
import {ref, reactive, computed} from 'vue';
import { useToast } from 'vue-toastification';
import axios from 'axios';

import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");

const toast = useToast();

const emit = defineEmits(['docCreated', 'closeModal']) // emit

</script>


<template>
  <div class="w-74 max-h-4/5 bg-white drop-shadow-md rounded-lg overflow-hidden">

    <div class="mt-5 ml-5">Закрыть без сохранения ?</div>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      
      <div class="my-3 flex justify-left space-x-5 py-3 px-5 text-center">
        <button
          class="formBtn"
          type="button"
           @click="emit('docCreated'); emit('closeModal')"
        >
        ДА
        </button>
        <button
          class="formBtn"
          type="button"
          @click="emit('closeModal')"
        >
        НЕТ
        </button>
      </div>

    </form>
  </div>

</template>


<style lang="postcss" scoped>

.formInputDiv {
  @apply w-64 mx-5 mb-2
}

.formInputFile {
  @apply mt-2 block w-full text-sm text-slate-500 
            file:my-0.5 file:ml-0.5 file:mr-4 file:py-2 file:px-4
            file:ring-1 file:ring-gray-200 file:rounded-full file:border-0 file:text-sm file:font-normal
            file:bg-gray-50 file:text-gray-600 hover:file:bg-gray-100 cursor-pointer
}

.formBtn {
  @apply text-slate-400 text-sm font-semibold border border-slate-400 rounded-lg w-32 h-9 hover:text-slate-500 hover:border-slate-500
}

.formLabelStyle {
  @apply mx-1 block text-xs font-bold text-slate-400 
}
.formInputStyle {
  @apply border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer
}
.formLabelCheckboxStyle {
  @apply ml-3 text-base font-semibold text-gray-400 cursor-pointer
}
.formInputCheckboxStyle {
    @apply ml-1 w-4 h-4 cursor-pointer
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
