<script setup>
  import Carpasses from '@/components/Carpasses.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <Carpasses :view_type="'terminal'" :list_title="'ТС на терминале'"
    v-if="routesRolesAccess['car_terminal'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
