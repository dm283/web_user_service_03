<script setup>
  import Carpasses from '@/components/Carpasses.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <Carpasses :view_type="'contacts'" :list_title="'Клиенты'"
    v-if="routesRolesAccess['contacts'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
