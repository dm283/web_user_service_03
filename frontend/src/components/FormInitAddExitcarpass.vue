<script setup>
// import router from '@/router';
import {ref, reactive, computed, onMounted} from 'vue';
import { useToast } from 'vue-toastification';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';
import axios from 'axios';

import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");


const emit = defineEmits(['docCreated', 'closeModal']) // emit

const props = defineProps({
});

const state = reactive({
  query: '',
  documents: [],
  isLoading: true,
  filteredList: [],
})

const selectedItem = ref('')
const devSelected = ref({});
const showDropDownSelect = ref({});

const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}


onMounted(async () => {
    try {
      state.query = `http://${backendIpAddress}:${backendPort}/car_terminal_for_exit/`;
      const response = await axios.get(state.query, {headers: authHeader()});
      state.documents = response.data;
    } catch (error) {
      console.error('Error fetching docs', error);
    } finally {
      state.isLoading = false;
    }
});

const formInputStyle20 = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 hover:border-blue-400 focus:outline-none focus:border-blue-500'
const formInputStyle21 = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-0 hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer'
const formInputStyle2 = props.isCard ? formInputStyle20 : formInputStyle21
const formInputStyleDis = 'text-base w-full py-1 px-1 mb-2'

const files = ref(null)
const file = ref(null)


const handleSubmit = async () => {
  // form submit handling
  if (!selectedItem.value) {
    return 0;
  };
  emit('docCreated', selectedItem.value); // emit
  emit('closeModal')
};


const setFilter = (field) => {
  // filter setting
  state.filteredList = [];
  for (let rec of state.documents) {
    if ( rec[field].toString().toUpperCase().indexOf(devSelected.value[field]) > -1 ) {
      state.filteredList.push(rec);
    };
  };
  if (state.filteredList.length == 0) {
    for (let xobj of state.documents) {
      let clonedObj = {...xobj};
      state.filteredList.push(clonedObj);
    };
  }
};

</script>


<template>
  <div class="w-3/5 max-h-4/5 bg-white drop-shadow-md rounded-lg overflow-hidden">
    <header class="py-2 pl-6 bg-slate-200 text-black text-lg font-normal">
      Пропуск на выезд
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="emit('closeModal')"></i>
      </div>
    </header>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      <div class="flex">

        <div class="formInputDiv">
          <label class=formLabelStyle>Номер пропуска на въезд</label>
          <div :class=formInputStyle2 class="flex" @click="setFilter('id_enter'); showDropDownSelect.id_enter=true; 
                  console.log(234, showDropDownSelect)">
            <input class="w-64 focus:outline-none" type="text" v-model="devSelected.id_enter" id="dSel" name="dSel" @keyup="setFilter('id_enter')"/>
            <span><i class="pi pi-angle-down" style="font-size: 0.8rem"></i></span>
          </div>
          <div v-if="showDropDownSelect.id_enter" class="bg-slate-100 border border-slate-400 rounded-md shadow-xl w-64 max-h-24 overflow-auto p-1 absolute">
            <div class="px-1.5 py-0.5 cursor-pointer hover:bg-blue-300" v-for="item in state.filteredList" 
              @click="devSelected.id_enter=item.id_enter; devSelected.ncar=item.ncar; selectedItem=item; showDropDownSelect.id_enter=false" >
              {{ item.id_enter }}
            </div>
          </div>
        </div>

        <div class="formInputDiv">
          <label class=formLabelStyle>Номер машины</label>
          <div :class=formInputStyle2 class="flex" @click="setFilter('ncar'); showDropDownSelect.ncar=true">
            <input class="w-64 focus:outline-none" type="text" v-model="devSelected.ncar" id="dSel" name="dSel" @keyup="setFilter('ncar')"/>
            <span><i class="pi pi-angle-down" style="font-size: 0.8rem"></i></span>
          </div>
          <div v-if="showDropDownSelect.ncar" class="bg-slate-100 border border-slate-400 rounded-md shadow-xl w-64 max-h-24 overflow-auto p-1 absolute">
            <div class="px-1.5 py-0.5 cursor-pointer hover:bg-blue-300" v-for="item in state.filteredList" 
              @click="devSelected.ncar=item.ncar; devSelected.id_enter=item.id_enter; selectedItem=item; showDropDownSelect.ncar=false" >
              {{ item.ncar }}
            </div>
          </div>
        </div>

      </div>

      <div class="mt-3 mb-5 py-3 px-5 text-center overflow-auto">
        <div class="float-left space-x-5">
          <button class="formBtn" type="submit">СФОРМИРОВАТЬ</button>
          <button class="formBtn" type="button" @click="selectedItem=''; devSelected.ncar=''; devSelected.id_enter=''">ОЧИСТИТЬ</button>
        </div>
      </div>
    </form>
  </div>

</template>


<style lang="postcss" scoped>

.formInputDiv {
  @apply w-64 mx-5 mb-2
}

.formInputFile {
  @apply text-sm text-slate-400 file:py-2 file:px-4 file:bg-white file:rounded-lg file:border-slate-300 file:text-sm file:font-normal
    file:text-slate-400 hover:file:bg-gray-100 cursor-pointer
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
