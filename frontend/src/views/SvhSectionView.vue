<script setup>
  import SvhSection from '@/components/SvhSection.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <SvhSection
    v-if="routesRolesAccess['svh_section'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
