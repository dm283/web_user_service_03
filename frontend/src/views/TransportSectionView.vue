<script setup>
  import TransportSection from '@/components/TransportSection.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <TransportSection
    v-if="routesRolesAccess['transport_section'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
