<script setup>
import { defineProps, computed, reactive } from 'vue';
import BarHorizont from '@/components/BarHorizont.vue';
import BarChart from '@/components/BarChart.vue';
import Card from '@/components/Card.vue';
import List from '@/components/List.vue';

  
const props = defineProps({
  storageStateBarTnvedQuantityDatax: Array,
  storageStateBarTnvedQuantityDatay: Array,
  storageStateCardProductQuantity: 0,
  storageStateCardDtQuantity: 0,
  storageStateListName: String,
  storageStateListProductsStorage: Array,
  storageStateListTableColumns: Object,
});

</script>

<template>
  
  <div class="flex flex-col md:flex-row m-2 gap-3 ">

    <div class="flex-none w-fit md:w-auto">
      
      <div class="flex flex-col gap-3">

        <div class="grid grid-cols-2 gap-3">
          <div class="">
            <Card :label="'Количество товара на складе'" :value="storageStateCardProductQuantity" />
          </div>
          <div class="">
            <Card :label="'Количество ДТ на складе'" :value="storageStateCardDtQuantity" />
          </div>
        </div>

        <div class="">
          <BarHorizont :name="'bar-h-03'" :title="'ТНВЭД на складе'" :xtitle="'Количество'" :ytitle="'Группа ТНВЭД'"
          :datax="storageStateBarTnvedQuantityDatax"
          :datay="storageStateBarTnvedQuantityDatay" 
          :barcolor="'#00E396'" 
          />
        </div>

      </div>

    </div>

    <div class="flex-auto w-auto md:w-64">
      <div class="">
        <List :name="storageStateListName" :data="storageStateListProductsStorage" :listTableColumns="storageStateListTableColumns" />
      </div>
    </div>

  </div>
  
</template>

<!-- #00E396  #FF69B4  #CD5C5C  #FFA07A  #7B68EE  #00FF7F  #00BFFF -->
