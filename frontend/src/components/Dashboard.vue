<script setup>
import { ref, defineProps, computed, reactive } from 'vue';
import TabStorageState from '@/components/TabStorageState.vue';
import TabAccountBook from '@/components/TabAccountBook.vue';
import TabReportVehicle from '@/components/TabReportVehicle.vue';
import TabTest from './Documents.vue';

  
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

const emit = defineEmits(['changeTab']) // emit

const openTab = ref(props.tabNumberVar);

const toggleTabs = (tabNumber) => {
  openTab.value = tabNumber;
  emit('changeTab', tabNumber) // emit
};

</script>

<template>
  
  <nav class="border flex bg-blue-50 text-indigo-500">
    <!-- <div :class="{'navTabsSelected': openTab == 1, 'navTabs': openTab != 1}" @click="toggleTabs(1)">
      Состояние склада
    </div> -->
    <!-- <div :class="{'navTabsSelected': openTab == 2, 'navTabs': openTab != 2}" @click="toggleTabs(2)">
      Книга учета
    </div>
    <div :class="{'navTabsSelected': openTab == 3, 'navTabs': openTab != 3}" @click="toggleTabs(3)">
      Отчет ТС
    </div>-->
    <div :class="{'navTabsSelected': openTab == 4, 'navTabs': openTab != 4}" @click="toggleTabs(4)">
      Тест
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
    <div v-if="openTab == 4">
      <TabTest
        />
    </div>
  </div>
  
</template>


<style lang="postcss" scoped>
.navTabs {
  @apply  rounded-t-lg px-5 py-2 cursor-pointer hover:text-indigo-600
}

.navTabsSelected {
    @apply bg-white  rounded-t-lg px-5 py-2 cursor-pointer hover:text-indigo-600
  }
</style>