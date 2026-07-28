<script setup>
  import Carpasses from '@/components/Carpasses.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <Carpasses :view_type="'add_requests_batch_to_sklad'" :list_title="'Заявки размещения партий на склад'"
    v-if="routesRolesAccess['add_requests_batch_to_sklad'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
