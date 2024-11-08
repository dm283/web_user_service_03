<script setup>
import { ref, defineProps, computed, reactive } from 'vue';
import TabStorageState from '@/components/TabStorageState.vue';
import TabAccountBook from '@/components/TabAccountBook.vue';
import TabReportVehicle from '@/components/TabReportVehicle.vue';

  
const props = defineProps({
  tabNumberVar: 1,
  storageStateBarTnvedQuantityDatax: Array,
  storageStateBarTnvedQuantityDatay: Array,
  storageStateCardProductQuantity: 0,
  storageStateCardDtQuantity: 0,
  storageStateListProductsStorage: Array,
  storageStateListName: String,
  storageStateListTableColumns: Object,

  accountBookBarRecTnvedQuantityDatax: Array,
  accountBookBarRecTnvedQuantityDatay: Array,
  accountBookCardRecProductQuantity: 0,
  accountBookCardRecDtQuantity: 0,
  accountBookListAccountBook: Array,
  accountBookListName: String,
  accountBookListTableColumns: Object,

  reportVehicleListAccountBook: Array,
  reportVehicleListName: String,
  reportVehicleListTableColumns: Object,
});

const emit = defineEmits(['changeTab'])

const openTab = ref(props.tabNumberVar);

const toggleTabs = (tabNumber) => {
  openTab.value = tabNumber;
  emit('changeTab', tabNumber)
};

</script>


<template>
<nav class="flex bg-blue-50">
  <div class="border-b flex-1 flex text-indigo-500">
    <div :class="{'navTabsSelected': openTab == 1, 'navTabs': openTab != 1}" @click="toggleTabs(1)">
      Состояние склада
    </div>
    <div :class="{'navTabsSelected': openTab == 2, 'navTabs': openTab != 2}" @click="toggleTabs(2)">
      Книга учета
    </div>
    <div :class="{'navTabsSelected': openTab == 3, 'navTabs': openTab != 3}" @click="toggleTabs(3)">
      Отчет ТС
    </div>
  </div>
  <div class="border-b flex space-x-1 px-3 py-1">
    <div class="dashboardNavBtn text-teal-500 hover:text-teal-600"><i class="pi pi-refresh" style="font-size: 1rem" @click="updateData()"></i></div>
    <div class="dashboardNavBtn text-blue-500 hover:text-blue-600" @click="showFiltersBar=(showFiltersBar) ? false:true">
      <i class="pi pi-filter" style="font-size: 1rem"></i></div>
  </div>
</nav>

  <div id="dashboardContent" class="">
    <div v-if="openTab == 1">
      <TabStorageState
        :storageStateBarTnvedQuantityDatax="storageStateBarTnvedQuantityDatax" 
        :storageStateBarTnvedQuantityDatay="storageStateBarTnvedQuantityDatay" 
        :storageStateCardProductQuantity="storageStateCardProductQuantity" 
        :storageStateCardDtQuantity="storageStateCardDtQuantity"
        :storageStateListName="storageStateListName" 
        :storageStateListProductsStorage="storageStateListProductsStorage" 
        :storageStateListTableColumns="storageStateListTableColumns"
      />
    </div>
    <div v-if="openTab == 2">
      <TabAccountBook
        :accountBookBarRecTnvedQuantityDatax="accountBookBarRecTnvedQuantityDatax" 
        :accountBookBarRecTnvedQuantityDatay="accountBookBarRecTnvedQuantityDatay" 
        :accountBookCardRecProductQuantity="accountBookCardRecProductQuantity" 
        :accountBookCardRecDtQuantity="accountBookCardRecDtQuantity"
        :accountBookListName="accountBookListName" 
        :accountBookListAccountBook="accountBookListAccountBook" 
        :accountBookListTableColumns="accountBookListTableColumns"
      />
    </div>
    <div v-if="openTab == 3">
      <TabReportVehicle 
        :reportVehicleListName="reportVehicleListName" 
        :reportVehicleListAccountBook="reportVehicleListAccountBook" 
        :reportVehicleListTableColumns="reportVehicleListTableColumns"
        />
    </div>
  </div>
</template>


<style lang="postcss" scoped>
.navTabs {
  @apply border rounded-t-lg h-10 px-5 py-1.5 cursor-pointer hover:text-indigo-600
}

.navTabsSelected {
    @apply border bg-white h-10 rounded-t-lg px-5 py-1.5 cursor-pointer hover:text-indigo-600
  }

.dashboardNavBtn {
    @apply pt-1 w-8 h-8 border rounded-lg bg-white text-center cursor-pointer hover:ring-1
  }
</style>