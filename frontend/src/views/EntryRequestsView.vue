<script setup>
  import Carpasses from '@/components/Carpasses.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <Carpasses :view_type="'entryRequest'" :list_title="'Заявки на въезд ТС'"
    v-if="routesRolesAccess['entry_requests'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
