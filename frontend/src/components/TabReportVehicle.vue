<script setup>
import { defineProps, computed, reactive } from 'vue';
import List from '@/components/List.vue';

  
const props = defineProps({
  reportVehicleListName: String,
  reportVehicleListAccountBook: Array,
  reportVehicleListTableColumns: Object,
});

</script>

<template>
  
  <div class="grid grid-cols-6 gap-3 m-2">

    <div class="col-span-6">
      <div class="">
        <List :name="reportVehicleListName" :data="reportVehicleListAccountBook" :listTableColumns="reportVehicleListTableColumns" />
      </div>
    </div>

  </div>
  
</template>
