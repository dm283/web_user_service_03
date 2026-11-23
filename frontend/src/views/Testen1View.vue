<script setup>
  import Carpasses from '@/components/Carpasses.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <Carpasses :view_type="'testen1'" :list_title="'Тестовый раздел 1'"
    v-if="routesRolesAccess['testen1'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
