<script setup>
  import Carpasses from '@/components/Carpasses.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <div v-if="routesRolesAccess['parking_map'].includes(userInfo.role_name)">
    <div class="ml-5 py-5">План парковки ТС (раздел в работе)</div>
    <div class="ml-5 pb-5">
      <img src="@/assets/parking-map.png">
    </div>
  </div>
  <InitView v-else />

</template>
