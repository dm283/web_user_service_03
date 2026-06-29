<script setup>
  import UploadListsExcelWindow from '@/components/UploadListsExcelWindow.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <UploadListsExcelWindow
    v-if="routesRolesAccess['upload_lists_excel'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
