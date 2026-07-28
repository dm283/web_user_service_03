<script setup>
  import Carpasses from '@/components/Carpasses.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));

  // console.log('routesRolesAccess =', routesRolesAccess["tzones"])
  // console.log('userInfo role =', userInfo.role_name)
</script>

<template>
  <Carpasses :view_type="'tzones'" :list_title="'Территории терминала'" 
    v-if="routesRolesAccess['tzones'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
