<script setup>
  import { ref} from 'vue';

  const props = defineProps({
    username: String,
    users: Array,
  });


  const client_id = ref(Date.now())
  const messageText = ref(null)
  const messages = ref([])
  const selectedUser = ref(null)

  const ws = new WebSocket(`ws://localhost:8000/ws/${props.username}`);
  // const ws = new WebSocket(`ws://localhost:8000/ws/${client_id.value}`);
  
  ws.onmessage = function(event) {
    const message = event.data  // JSON.parse(event.data);
    messages.value.push(message);
  };

  function sendMessage(event) {
    //
    if (!selectedUser.value) {
      return 1
    }
    const messageData = { receiver: selectedUser.value, message: messageText.value}
    ws.send(JSON.stringify(messageData))

    //ws.send(messageText.value)
    messageText.value = null;
  }

  function defineUsersForChat() {
    //
    let usersForChat = []
    for (let u of props.users) {
      if (u !== props.username) {
        usersForChat.push(u)
      }
    }

    return usersForChat
  }

</script>


<template>
  <section class="my-3 mx-5">

  <!-- <div class="flex mb-3 text-slate-500">
    <div class="border-2 border-slate-400 h-10 w-10 rounded-full p-2"><i class="pi pi-user" style="font-size: 1.3rem"></i></div>
    <div class="ml-3 mt-1.5 ">{{ username }}</div>
  </div> -->

  <div id="dropdownReceiver" class="flex text-slate-600 mb-5">
    <label class="mr-2 mt-1.5 text-xs font-bold text-slate-400" for="chat-select">Адресат</label>

    <select class="flex-1 border-b-2 border-blue-300 bg-white text-center cursor-pointer hover:border-blue-400" v-model="selectedUser">
      <!-- <option value="">--Please choose a chat--</option> -->
      <option :value=user v-for="user in defineUsersForChat()">{{  user }}</option>
    </select>
  </div>

  <div class="mb-5">
  <form action="" @submit.prevent="sendMessage()">
    <div class="flex">
    <input class="flex-1 border-2 border-slate-400 h-10 w-auto rounded-full px-3 focus:border-none" type="text" v-model="messageText" placeholder="Сообщение" />
    <button class="ml-2 mt-1 pt-0.5 pr-0.5 bg-slate-400 rounded-full h-8 w-8 text-white hover:bg-slate-500" type="submit">
      <i class="pi pi-send" style="font-size: 1rem"></i>
    </button>
    </div>
  </form>
  </div>

  <hr> 

  <div class="mt-5 overflow-auto">
    <div :class="(message[0] !== '[') ? 'messageMy' : 'messageFrom'"
    v-for="message in messages">
      {{ message }}
    </div>
  </div>

  </section>
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
