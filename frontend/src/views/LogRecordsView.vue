<script setup>
  import Carpasses from '@/components/Carpasses.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <Carpasses :view_type="'log_records'" :list_title="'Журнал действий'"
    v-if="routesRolesAccess['log_records'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
