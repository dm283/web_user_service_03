<script setup>

import { defineProps, computed, reactive, onMounted } from 'vue';
import axios from 'axios';
import data from "../../../backend/config.ini?raw";
import { ConfigIniParser } from "config-ini-parser";
let parser = new ConfigIniParser(); //Use default delimiter
parser.parse(data);
var backendIpAddress = parser.get("main", "backend_ip_address");
var backendPort = parser.get("main", "backend_port");

const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}
  
const props = defineProps({
    label: String,
    field_form: String,
    modelValue: String,
});

const emit = defineEmits(['update:modelValue', 'setFilter', 'setVars', 'clickErase', 'clickDropdown'])

const state = reactive({
  filteredList: [],
  contacts: []
})

// load data for dropdown list
onMounted(async () => {
    try {
      const response = await axios.get(`http://${backendIpAddress}:${backendPort}/contacts_posted/`, {headers: authHeader()});
      state.contacts = response.data;
    } catch (error) { console.error('Error fetching docs', error); } finally { state.isLoading = false; } });


const showDropDownSelect = reactive({}); const form = reactive({});

const formInputStyleDis = 'text-base w-full py-1 px-1 mb-2'
// const postedColor = props.itemData ? (props.itemData.posted ? 'bg-white' : 'bg-yellow-50') : 'bg-white'
const postedColor = 'bg-yellow-50'
const formInputStyleAct = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer' + ' ' + postedColor
// const formInputStyle = props.isCard ? formInputStyleDis : formInputStyleAct
const formInputStyle = formInputStyleAct

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

</script>


<template>
      <div v-if="(!props.isCard)">   
        <label class=formLabelStyle>Клиент</label>

        <!-- input field -->
        <div :class=formInputStyle class="flex">

          <!-- input field -->
          <input v-model="form['contact_name_input']"
            :class=postedColor class="w-64 focus:outline-none cursor-pointer" type="text" placeholder="выберите из списка" 
            :value="props.modelValue"
            @input="emit('update:modelValue', $event.target.value); setFilter('contact_name_input', 'contacts', 'name', 'inn');"
            @click="setFilter('null', 'contacts', 'name'); setVars('contact_name_input', 'reserve_1');"
            :required="true"
          />

          <!-- down-arrow span -->
          <span @click="setFilter('null', 'contacts', 'name'); setVars('contact_name_input', 'reserve_1');">
            <i class="pi pi-angle-down" style="font-size: 0.8rem"></i>
          </span>

          <!-- erase icon span -->
          <span class="ml-1 text-red-400 active:text-black" 
            @click="showDropDownSelect['contact_name_input']=false; emit('clickErase'); form['reserve_1']=null; ">
            <i class="pi pi-times" style="font-size: 0.7rem"></i>
          </span>

        </div>

        <!-- dropdown -->
        <div v-if="showDropDownSelect['contact_name_input']" class=dropDownStyle>
          <div class=dropDownItemStyle v-for="item in state.filteredList" 
            @click="showDropDownSelect['contact_name_input']=false; 
                form['reserve_1']=item['name'];
                emit('update:modelValue', (item['name']+' ('+item['inn']+')'))
                emit('clickDropdown', item['uuid'])"
                >
            {{ item['name'] }} ({{ item['inn'] }})
          </div>
        </div>

      </div>
</template>


<style lang="postcss" scoped>

.formInputDiv {
  @apply w-64 mx-5 mb-2
}
.formLabelStyle {
  @apply mx-1 block text-xs font-bold text-slate-400 
}
.dropDownStyle {
  @apply bg-white border border-slate-400 rounded-md shadow-xl w-64 max-h-24 overflow-auto p-1 absolute z-10
}
.dropDownItemStyle {
  @apply px-1.5 py-0.5 cursor-pointer hover:bg-blue-300
}

</style>
