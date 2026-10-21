<script setup>

import { defineProps, ref, reactive } from 'vue';

const authHeader = () => {
  let user = JSON.parse(localStorage.getItem('user')); 
  if (user && user.access_token) {return { Authorization: 'Bearer ' + user.access_token };} else {return {};}
}
  
const props = defineProps({
    name: String,
    parentFormName: String,
    label: String,
    modelValue: String,
    data: Object,         // set of data (contacts/brokers)
    searchField1: String, // name
    searchField2: String, // inn
    searchValue: String,  // uuid
    setValue: String,     // contact_uuid
    itemData: Object,
    isCard: Boolean,
    isRequired: Boolean,
});

const emit = defineEmits(['update:modelValue', 'clickErase', 'clickDropdown'])

const state = reactive({
  filteredList: [],
  data: []
})

const showDropDown = ref(false); const form = reactive({});

const formInputStyleDis = 'text-base w-full py-1 px-1 mb-2'
const postedColor = props.itemData ? (props.itemData.posted ? 'bg-white' : 'bg-yellow-50') : 'bg-white'
const formInputStyleAct = 'border-b-2 border-blue-300 text-base w-full py-1 px-1 mb-2 \
        hover:border-blue-400 focus:outline-none focus:border-blue-500 cursor-pointer' + ' ' + postedColor
const formInputStyle = props.isCard ? formInputStyleDis : formInputStyleAct

const setFilter = (fieldForm, data, searchField1, searchField2=null) => {
  //
  state.filteredList = [];
  if (form[fieldForm]) { state.formValue = form[fieldForm].toUpperCase() } else { state.formValue = '' };
  for (let rec of data) {
    if ( rec[searchField1].toString().toUpperCase().indexOf(state.formValue) > -1 ) { state.filteredList.push(rec); };
    if (searchField2) {
      if ( rec[searchField2].toString().toUpperCase().indexOf(state.formValue) > -1 ) { 
        if ( !state.filteredList.includes(rec) ) {state.filteredList.push(rec)} }; }
  }; };

const setVars = () => {
  // check if it is needed ??
  if (!form['reserve_1']) { form['reserve_1'] = form['input_field'] }
  if (showDropDown.value) { showDropDown.value=false; form['input_field']=form['reserve_1'] }
  else { showDropDown.value=true; form['input_field']=null }; };


const createFieldValue = (item) => {
  // create custom field for distinct entity
  if (['testen1_contact_uuid'].includes(props.name)) {
    var val = item['name']+' ('+item['inn']+')'
  }
  if (['testen1_broker_uuid'].includes(props.name)) {
    var val = item['broker_name']+' ('+item['broker_inn']+')'
  }
  if (['testen1_carpass_uuid'].includes(props.name)) {
    var val = item['ncar']
  }
  return val
}

</script>


<template>
      <div v-if="(!props.isCard)">   
        <label class=formLabelStyle>{{ props.label }}</label>

        <!-- input field -->
        <div :class=formInputStyle class="flex">

          <!-- input field -->
          <input v-model="form['input_field']"
            :class=postedColor class="w-64 focus:outline-none cursor-pointer" type="text" placeholder="выберите из списка" 
            :value="props.modelValue"
            @input="emit('update:modelValue', $event.target.value); setFilter('input_field', props.data, props.searchField1, props.searchField2);"
            @click="setFilter('null', props.data, props.searchField1); setVars();"
            :required="props.isRequired"
          />

          <!-- down-arrow span -->
          <span @click="setFilter('null', props.data, props.searchField1); setVars();">
            <i class="pi pi-angle-down" style="font-size: 0.8rem"></i>
          </span>

          <!-- erase icon span -->
          <span class="ml-1 text-red-400 active:text-black" 
            @click="showDropDown=false; emit('clickErase', props.name, props.parentFormName, props.setValue); form['reserve_1']=null; ">
            <i class="pi pi-times" style="font-size: 0.7rem"></i>
          </span>

        </div>

        <!-- dropdown -->
        <div v-if="showDropDown" class=dropDownStyle>
          <div class=dropDownItemStyle v-for="item in state.filteredList" 
            @click="showDropDown=false; 
                form['reserve_1']=item[props.searchField1];
                emit('update:modelValue', createFieldValue(item))
                emit('clickDropdown', props.name, props.setValue, item[props.searchValue])"
                >
              {{ createFieldValue(item) }}
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
