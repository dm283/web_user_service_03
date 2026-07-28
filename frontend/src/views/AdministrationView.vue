<script setup>
  import Administration from '@/components/Administration.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <Administration
    v-if="routesRolesAccess['administration'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
