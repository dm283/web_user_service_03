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


const emit = defineEmits(['docCreated', 'closeModal']) // emit

const props = defineProps({
  itemData: Object,
});

const form = reactive({});

const initEmptyForm = () => {
    form.ncar = ''
    form.dateen = ''
    form.timeen = ''
    form.ntir = ''
    form.nkont = ''
    form.driver = ''
    form.drv_man = ''
    form.dev_phone = ''
    form.contact = 111
    form.contact_name = ''
    form.contact_broker = 222
    form.broker_name = ''
    form.place_n = ''
    form.dateex = ''
    form.timeex = ''
}

if (props.itemData) {
  form.ncar = props.itemData.ncar;
  form.dateen = props.itemData.dateen
  form.timeen = props.itemData.timeen
  form.ntir = props.itemData.ntir
  form.nkont = props.itemData.nkont
  form.driver = props.itemData.driver
  form.drv_man = props.itemData.drv_man
  form.dev_phone = props.itemData.dev_phone
  form.contact = props.itemData.contact
  form.contact_name = props.itemData.contact_name
  form.contact_broker = props.itemData.contact_broker
  form.broker_name = props.itemData.broker_name
  form.place_n = props.itemData.place_n
  form.dateex = props.itemData.dateex
  form.timeex = props.itemData.timeex
} else {
  initEmptyForm();
};

const file = ref(null)

const toast = useToast();

const handleSubmit = async () => {

  let formData = new FormData();

  formData.append('ncar', form.ncar);
  formData.append('dateen', form.dateen);
  formData.append('timeen', form.timeen);
  formData.append('ntir', form.ntir);
  formData.append('nkont', form.nkont);
  formData.append('driver', form.driver);
  formData.append('drv_man', form.drv_man);
  formData.append('dev_phone', form.dev_phone);
  formData.append('contact', form.contact);
  formData.append('contact_name', form.contact_name);
  formData.append('contact_broker', form.contact_broker);
  formData.append('broker_name', form.broker_name);
  formData.append('place_n', form.place_n);
  formData.append('dateex', form.dateex);
  formData.append('timeex', form.timeex);
  // formData.append('file', file.value.files[0]);
  // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/single-file/`, 
  // formData, {headers: {'Content-Type': 'multipart/form-data'}});

  try {
    // const response = await axios.post(`http://${backendIpAddress}:${backendPort}/documents/`, newItem);
    if (!props.itemData) {
      const response = await axios.post(`http://${backendIpAddress}:${backendPort}/carpasses/`, 
        formData, {headers: {'Content-Type': 'multipart/form-data'}});
      toast.success('Новый пропуск добавлен');
    } else {
      const response = await axios.put(`http://${backendIpAddress}:${backendPort}/carpasses/${props.itemData.id}`, 
        formData, {headers: {'Content-Type': 'multipart/form-data'}});
      toast.success('Пропуск обновлён');      
    }


    emit('docCreated'); // emit
    emit('closeModal')
  } catch (error) {
    console.error('Error adding item', error);
    toast.error('Item has not added');
  };
};


</script>

<template>
  <div class="w-3/5 max-h-4/5 bg-white drop-shadow-md rounded-lg overflow-hidden">
  
    <header class="py-2 pl-6 bg-slate-200 text-black text-lg font-normal">
      Пропуск
      <div class="absolute top-2 right-4 cursor-pointer hover:text-gray-500">
        <i class="pi pi-times" style="font-size: 1rem" @click="emit('closeModal')"></i>
      </div>
    </header>
    
    <form @submit.prevent="handleSubmit" enctype="multipart/form-data" class="mx-0 mt-5">
      
      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>Номер машины</label>
          <input
            type="text"
            v-model="form.ncar"
            id="ncar"
            name="ncar"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Дата въезда</label>
          <input
            type="date"
            v-model="form.dateen"
            id="dateen"
            name="dateen"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Время въезда</label>
          <input
            type="time"
            v-model="form.timeen"
            id="timeen"
            name="timeen"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>Номер документа доставки</label>
          <input
            type="text"
            v-model="form.ntir"
            id="ntir"
            name="ntir"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Номер контейнера</label>
          <input
            type="text"
            v-model="form.nkont"
            id="nkont"
            name="nkont"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Наименование перевозчика</label>
          <input
            type="text"
            v-model="form.driver"
            id="driver"
            name="driver"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>ФИО водителя</label>
          <input
            type="text"
            v-model="form.drv_man"
            id="drv_man"
            name="drv_man"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Телефон водителя для связи</label>
          <input
            type="text"
            v-model="form.dev_phone"
            id="dev_phone"
            name="dev_phone"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Наименование клиента</label>
          <input
            type="text"
            v-model="form.contact_name"
            id="contact_name"
            name="contact_name"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>Наименование брокера</label>
          <input
            type="text"
            v-model="form.broker_name"
            id="broker_name"
            name="broker_name"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Номер стоянки</label>
          <input
            type="text"
            v-model="form.place_n"
            id="place_n"
            name="place_n"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
      </div>

      <div class="flex">
        <div class=formInputDiv>
          <label class=formLabelStyle>Дата выезда</label>
          <input
            type="date"
            v-model="form.dateex"
            id="dateex"
            name="dateex"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
        <div class=formInputDiv>
          <label class=formLabelStyle>Время выезда</label>
          <input
            type="time"
            v-model="form.timeex"
            id="timeex"
            name="timeex"
            class=formInputStyle
            placeholder=""
            required
          />
        </div>
      </div>

      <!-- <div class="mx-5 mb-2">
        <label class=formLabelStyle>Файл</label>
        <input ref="file" name="file" type="file" 
          class=formInputFile
        />
      </div> -->

      <!-- <div class="mx-5 mb-2">
        <label class=formLabelStyle>Дата документа</label>
        <input
          type="date"
          v-model="form.established"
          id="established"
          name="established"
          class=formInputStyle
          placeholder=""
          required
        />
      </div> -->

      <!-- <div class="mx-5 mb-4">
        <input
          type="checkbox"
          v-model='form.isCapital'
          id="isCapital"
          name="isCapital"
          class=formInputCheckboxStyle
        />
        <label class=formLabelCheckboxStyle 
          @click="form.isCapital=(form.isCapital==true) ? false : true ;">Capital</label>
      </div> -->


      <div class="my-3 flex justify-left space-x-5 py-3 px-5 text-center">
        <button
          class="formBtn"
          type="submit"
        >
        СОХРАНИТЬ
        </button>
        <button
          class="formBtn"
          type="reset"
          @click=""
        >
        ОЧИСТИТЬ
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
