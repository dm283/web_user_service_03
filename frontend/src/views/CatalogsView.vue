<script setup>
  import Catalogs from '@/components/Catalogs.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <Catalogs
    v-if="routesRolesAccess['catalogs'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
