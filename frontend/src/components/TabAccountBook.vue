<script setup>
import { defineProps, computed, reactive } from 'vue';
import BarHorizont from '@/components/BarHorizont.vue';
import BarChart from '@/components/BarChart.vue';
import Card from '@/components/Card.vue';
import List from '@/components/List.vue';

  
const props = defineProps({
  accountBookBarRecTnvedQuantityDatax: Array,
  accountBookBarRecTnvedQuantityDatay: Array,
  accountBookCardRecProductQuantity: 0,
  accountBookCardRecDtQuantity: 0,
  accountBookListName: String,
  accountBookListAccountBook: Array,
  accountBookListTableColumns: Object,
});

</script>

<template>
  
  <div class="flex flex-col md:flex-row m-2 gap-3 ">

    <div class="flex-none w-fit md:w-auto">
      
      <div class="flex flex-col gap-3">

        <div class="grid grid-cols-2 gap-3">
          <div class="">
            <Card :label="'Количество принятого товара'" :value="accountBookCardRecProductQuantity" />
          </div>
          <div class="">
            <Card :label="'Количество принятых ДТ'" :value="accountBookCardRecDtQuantity" />
          </div>
        </div>

        <div class="">
          <BarChart :name="'bar-h-03'" :title="'Принятые ТНВЭД'" :xtitle="'Группа ТНВЭД'" :ytitle="'Количество'"
          :datax="accountBookBarRecTnvedQuantityDatax"
          :datay="accountBookBarRecTnvedQuantityDatay" 
          :barcolor="'#7B68EE'" 
          />
        </div>

      </div>

    </div>

    <div class="flex-auto w-auto md:w-64">
      <div class="">
        <List :name="accountBookListName" :data="accountBookListAccountBook" :listTableColumns="accountBookListTableColumns" />
      </div>
    </div>

    </div>
  
</template>

<!-- #00E396  #FF69B4  #CD5C5C  #FFA07A  #7B68EE  #00FF7F  #00BFFF -->
