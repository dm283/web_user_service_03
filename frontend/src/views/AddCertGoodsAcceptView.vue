<script setup>
  import Carpasses from '@/components/Carpasses.vue';
  import InitView from "@/views/InitView.vue";
  import routesRolesAccess from '@/assets/routes_roles_access.json';
  const userInfo = JSON.parse(localStorage.getItem('userInfo'));
</script>

<template>
  <Carpasses :view_type="'add_cert_goods_accept'" :list_title="'Принятые партии товара'"
    v-if="routesRolesAccess['add_cert_goods_accept'].includes(userInfo.role_name)"/>
  <InitView v-else />
</template>
