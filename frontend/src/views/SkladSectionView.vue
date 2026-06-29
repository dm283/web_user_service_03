<script setup>
  import SkladSection from '@/components/SkladSection.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <SkladSection
    v-if="routesRolesAccess['sklad_section'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
