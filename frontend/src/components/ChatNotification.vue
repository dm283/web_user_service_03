<script setup>
  import { ref } from 'vue';

  const emit = defineEmits(['pointState', ])

  const props = defineProps({
    data: Object,
    username: String,
    users: Array,
  });

  const newMsg = ref(false)

  const ws = new WebSocket(`ws://localhost:8000/ws/${props.username}`);
  
  ws.onmessage = function(event) {
    console.log('new msg')
    newMsg.value = true
    emit('pointState', 'open')
  };

</script>


<template>

  <div class=""> 
    <!-- {{ props.data.pointState }} -->
    <div class="-ml-7 -mt-2" v-if="newMsg && ['initial', 'open'].includes(props.data.pointState)" @click="emit('pointState', 'close')" >
      <i class="pi pi-circle-fill" style="color: red; font-size: 0.5rem"></i>
    </div>
  </div>

</template>


<style lang="postcss" scope>
.messageMy {
  @apply float-right border w-11/12 rounded-lg bg-slate-100 py-1 px-3 mb-3 drop-shadow-md
}

.messageFrom {
  @apply float-left border w-11/12 rounded-lg bg-white py-1 px-3 mb-3 drop-shadow-md
}

#dropdownReceiver select {
  /* for Firefox */
  -moz-appearance: none;
  /* for Safari, Chrome, Opera */
  -webkit-appearance: none;
}
</style>
