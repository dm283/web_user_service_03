<script setup>
import { defineProps, ref, reactive, onMounted, computed } from 'vue';
import 'primeicons/primeicons.css';
// import router from '@/router';
import axios from 'axios';
import { utils, writeFileXLSX, writeFile } from 'xlsx';


const props = defineProps({
  name: String,
  data: Array,
  listTableColumns: Object,
  listItemFileds: Object,
});

const state = reactive({
  // data: [],
  tableFields: [],
  localData: [],
  dataForRender: [],
  currentPage: 1,
  limitRecords: 14,
  initRender: true,
})

// state.tableFields = Object.keys(props.data[0]); //
// for (let xobj of props.data) {  //
//   let clonedObj = {...xobj};
//   state.localData.push(clonedObj);
// };

// const loadAPIData = () => {
//   //
//   onMounted(async () => {
//     try {
//       const response = await axios.get('http://localhost:5000/cities');
//       state.data = response.data;
//       state.tableFields = Object.keys(props.data[0]); //

//       for (let xobj of props.data) {  //
//         let clonedObj = {...xobj};
//         state.localData.push(clonedObj);
//       };

//     } catch (error) {
//       console.error('Error fetching books', error);
//     }
//   });
// }

// loadAPIData();

const isDropDownloadShow = ref(false);

// const isListFilterShow = ref(true);
const isDropSearchShow = ref(false);
const searchBy = ref('all');
const mouseOverSearchDropdown = ref(false);
const searchFieldsList = Object.keys(props.listTableColumns);

// const isDropSortShow = ref(false);
const sortBy = ref('default');
const sortDirection = reactive({});
const sortIcon = reactive({});
const sortArrowsStyle = reactive({});
const filterIcon = reactive({});
const filterIconStyle = reactive({});
const isListFilterShow = reactive({});
for (let field of Object.keys(props.listTableColumns)) {
  sortDirection[field] = 'none';
  sortIcon[field] = 'pi pi-sort';
  sortArrowsStyle[field] = "flex-0 pr-0.5 text-blue-600 cursor-pointer hover:opacity-50";
  filterIcon[field] = 'pi pi-filter';
  filterIconStyle[field] = "flex-0 pr-1 text-emerald-600 cursor-pointer hover:opacity-50";
  isListFilterShow[field] = false;
};

const sortingDataType = ref();
const mouseOverSortDropdown = ref(false);
const sortFieldsList = ['name', 'country', 'established', 'area', 'population'];

const btnStyle = "bg-gray-100 rounded-full w-24 h-8 backdrop-filter backdrop-grayscale drop-shadow-lg hover:shadow-lg";  
const dropdownLiStyle = "h-8 pl-3 py-1.5 cursor-pointer hover:bg-gray-100";

const showItemCard = ref(false)
const selectedItem = ref('')


const loadLocalData = () => {
  // clone data [array of objects] into localData [array of objects]
  state.localData = [];

  for (let xobj of props.data) {
    let clonedObj = {...xobj};
    state.localData.push(clonedObj);
  };

  // apply filters
  // document.getElementById("searchInput"+field).value.toString().toUpperCase()
  for (let field of Object.keys(props.listTableColumns)) {
    if (document.getElementById("searchInput"+field)) {
      let filter = document.getElementById("searchInput"+field).value.toString().toUpperCase();
      if (filter) {
        setFilter(field);
      }
    }
  }

};


const sortNumbers = (direction, field) => {
  // sort numbers
  let x = (direction == 'asc') ? 
    state.localData.sort((a, b) => a[field] - b[field]) : 
    state.localData.sort((a, b) => b[field] - a[field]);
};


const sortStrings = (direction, field) => {
  // sort strings
  state.localData.sort((a, b) => {
    const nameA = (a[field]) ? a[field].toString().toUpperCase() : ''; // ignore upper and lowercase
    const nameB = (b[field]) ? b[field].toString().toUpperCase() : ''; // ignore upper and lowercase
    // const nameB = b[field].toUpperCase(); // ignore upper and lowercase
    if (nameA < nameB) {
      let x = (direction == 'asc') ? -1 : 1;
      return x;
    }
    if (nameA > nameB) {
      let x = (direction == 'asc') ? 1 : -1;
      return x;
    }

    // names must be equal
    return 0;
  });
};


// const clickSortArrow = () => {
//   //
//   if (sortBy.value == 'default') { return };

//   if (sortDirection.value == 'asc') {
//     sortDirection.value = 'desc';
//     sortIcon.value = 'pi pi-arrow-down';
//   }
//   else if (sortDirection.value == 'desc') {
//     sortDirection.value = 'asc';
//     sortIcon.value = 'pi pi-arrow-up';
//   }

//   sortTable(sortingDataType.value);
// };


const clickSortField2 = (field) => {
  //
  sortBy.value = field;

  for (let f of Object.keys(props.listTableColumns)) {
    if (f != field) {
      sortDirection[f] = 'none';
      sortIcon[f] = 'pi pi-sort';
      sortArrowsStyle[f] = "flex-0 pr-0.5 text-blue-600 cursor-pointer hover:opacity-50";
    };
  };

  if (sortDirection[field] == 'none') {
    sortDirection[field] = 'asc';
    sortIcon[field] = 'pi pi-sort-up-fill';
    sortArrowsStyle[field] = "flex-0 pr-0.5 text-orange-300 cursor-pointer hover:opacity-50"
  }
  else if (sortDirection[field] == 'asc') {
    sortDirection[field] = 'desc';
    sortIcon[field] = 'pi pi-sort-down-fill';
    sortArrowsStyle[field] = "flex-0 pr-0.5 text-orange-300 cursor-pointer hover:opacity-50"
  }
  else if (sortDirection[field] == 'desc') {
    sortDirection[field] = 'none';
    sortIcon[field] = 'pi pi-sort';
    sortArrowsStyle[field] = "flex-0 pr-0.5 text-blue-600 cursor-pointer hover:opacity-50";
    sortBy.value = 'default'
  }


  if (typeof(props.data[0][field]) == 'number') {
    sortingDataType.value = 'number';
  }
  else if (typeof(props.data[field]) == 'string') {
    sortingDataType.value = 'string';
  }
  else {
    sortingDataType.value = 'string';
  }
  // console.log('!!! ', props.data[0][field], sortingDataType.value)
  sortTable();
}



// const clickSortField = (field) => {
//   //
//   sortBy.value = field;
//   sortDirection.value = 'asc';
//   sortIcon.value = 'pi pi-arrow-up';

//   if (typeof(state.localData[0][field]) == 'number') {
//     sortingDataType.value = 'number';
//   }
//   else if (typeof(state.localData[0][field]) == 'string') {
//     sortingDataType.value = 'string';
//   }
//   sortTable(sortingDataType.value);
// }


const sortTable = () => {
  // sort table by certain field
  if (sortBy.value == 'default') { 
    loadLocalData();
    // sortIcon.value = 'pi pi-sort-alt';
    return;
  };

  if (sortingDataType.value == 'string') {
    sortStrings(sortDirection[sortBy.value], sortBy.value);
  }
  else if (sortingDataType.value == 'number') {
    sortNumbers(sortDirection[sortBy.value], sortBy.value);
  }
  else {
    return;
  }
};


const toggleDropdown = (dropdownId) => {
  //
  // if (dropdownId == 'search') {
  //   isDropSearchShow.value = (isDropSearchShow.value == true) ? false : true;
  // }
  if (dropdownId == 'download') {
    isDropDownloadShow.value = (isDropDownloadShow.value == true) ? false : true;
  }
  // else if (dropdownId == 'sort') {
  //   isDropSortShow.value = (isDropSortShow.value == true) ? false : true;
  // }
};


// const searchRecord = () => {
//   //   searchBy
//   let newLocalData = [];
//   let searchFieldsList = [];
//   let pushedIds = [];
//   let filter = document.getElementById("searchInput").value.toString().toUpperCase();

//   if (searchBy.value == 'all') {
//     searchFieldsList =  Object.keys(props.listTableColumns);
//   } else {
//     searchFieldsList.push(searchBy.value);
//   }

//   for (let rec of props.data) {
//     for (let field of searchFieldsList) {
//       if ( rec[field].toString().toUpperCase().indexOf(filter) > -1 ) {
//         if (!pushedIds.includes(rec.id)) {
//           newLocalData.push(rec)
//         };
//         pushedIds.push(rec.id);
//       }
//     }
//   };

//   if (newLocalData.length > 0) {
//     state.localData = newLocalData;
//   } else {
//     loadLocalData();
//   };

// };

const clickFilter = (field) => {
  //
  isListFilterShow[field] = (isListFilterShow[field]) ? false : true;
}

const setFilter = (field) => {
  //   searchBy
  let newLocalData = [];
  let searchFieldsList = [];
  let pushedIds = [];
  let filter = document.getElementById("searchInput"+field).value.toString().toUpperCase();

  if (filter) {
    filterIcon[field] = 'pi pi-filter-fill';
    filterIconStyle[field] = "flex-0 pr-1 text-fuchsia-500 cursor-pointer hover:opacity-50";
  }
  else {
    filterIcon[field] = 'pi pi-filter';
    filterIconStyle[field] = "flex-0 pr-1 text-emerald-600 cursor-pointer hover:opacity-50";
  }

  // if (searchBy.value == 'all') {
  //   searchFieldsList =  Object.keys(props.listTableColumns);
  // } else {
  //   searchFieldsList.push(searchBy.value);
  // }

  // searchFieldsList.push(searchBy.value);
  // console.log('props.data[0] = ', props.data[0])
  // console.log('field = ', field)

  const fieldsfiltersDict = {};
  for (let field of Object.keys(props.listTableColumns)) {
    if (document.getElementById("searchInput"+field)) {
      let filterV = document.getElementById("searchInput"+field).value.toString().toUpperCase();
      if (filterV) {
        fieldsfiltersDict[field] = filterV;
      }
    }
  }

  // console.log('fieldsfiltersDict =', fieldsfiltersDict)

  if (Object.keys(fieldsfiltersDict).length == 0) {
    loadLocalData();
    return 0;
  }

  /////////////////
  state.dataForFiltering = [];

  for (let xobj of props.data) {
    let clonedObj = {...xobj};
    state.dataForFiltering.push(clonedObj);
  };

  for (let fieldFiltered of Object.keys(fieldsfiltersDict)) {

    // console.log('fieldFiltered = ', fieldFiltered)
    newLocalData = [];
    pushedIds = [];
    for (let rec of state.dataForFiltering) {

      if ( typeof(rec[fieldFiltered])=='string' ) {
        if ( rec[fieldFiltered].toString().toUpperCase().indexOf(fieldsfiltersDict[fieldFiltered]) > -1 ) {
          if (!pushedIds.includes(rec.id)) {
            newLocalData.push(rec)
          };
          pushedIds.push(rec.id);
        }
      }
      else if ( typeof(rec[fieldFiltered])=='number' ) {
        if ( rec[fieldFiltered].toString() == fieldsfiltersDict[fieldFiltered].toString() ) {
          if (!pushedIds.includes(rec.id)) {
            newLocalData.push(rec)
          };
          pushedIds.push(rec.id);
        }
      }

    };

    // console.log('newLocalData.length =', newLocalData.length)

    state.dataForFiltering = newLocalData;

  };

  state.localData = state.dataForFiltering ;
  // if (newLocalData.length > 0) {
  //   state.localData = newLocalData;
  // } else {
  //   loadLocalData();
  // };

};
  

const checkState = () => {
  //
  if (isDropSearchShow.value == true & !mouseOverSearchDropdown.value) {
    isDropSearchShow.value = false;
  }
  // else if (isDropSortShow.value == true & !mouseOverSortDropdown.value) {
  //   isDropSortShow.value = false;
  // };
};


const computeRenderData = (action) => {
  //
  if (action == 'right') {
    if (state.currentPage < Math.ceil(dataLengthRender() / state.limitRecords)) {
    // if (state.currentPage < (Math.floor(dataLengthRender() / state.limitRecords) + 1)) {
        state.currentPage++;
    }
  }
  else if (action == 'left') {
    if (state.currentPage > 1) {
      state.currentPage--;
    }
  }
  else if (action == 'first') {
    state.currentPage = 1;
  }
  else if (action == 'last') {
    state.currentPage = Math.ceil(dataLengthRender() / state.limitRecords);
    // state.currentPage = Math.floor(dataLengthRender() / state.limitRecords) + 1;
  }
  
}

const dataRender = () => {
  // if the content is rendering for the first time, local data array is creating
  if (state.initRender) {
    state.initRender = false;
    loadLocalData();
  }

  return state.localData.slice(state.limitRecords*(state.currentPage-1), state.limitRecords*state.currentPage) 

  // if (state.localData.length > 0) {
  //   return state.localData.slice(state.limitRecords*(state.currentPage-1), state.limitRecords*state.currentPage) 
  // } 
  // else {
  //   // loadLocalData();
  //   return state.localData.slice(state.limitRecords*(state.currentPage-1), state.limitRecords*state.currentPage) 
  //   //return props.data.slice(state.limitRecords*(state.currentPage-1), state.limitRecords*state.currentPage)
  // }
};

const dataLengthRender= () => {
  //
  return state.localData.length
  // if (state.localData.length > 0) {
  //   return state.localData.length
  // } 
  // else {
  //   return props.data.length
  // }
}


const exportFile = (dataSet, fileName, fileType) => {
  //
  if (!dataSet) return;

  // leave in dataset only columns from listTableColumns and rename cols in rus
  let dataForExport = []
  for (let rec of dataSet) {
    let modifiedRec = {}
    for (let field of Object.keys(props.listTableColumns)) {
      modifiedRec[props.listTableColumns[field]] = rec[field]
    }
    dataForExport.push(modifiedRec)
  }

  //const ws = utils.json_to_sheet(dataSet);
  const ws = utils.json_to_sheet(dataForExport);
  const wb = utils.book_new();
  utils.book_append_sheet(wb, ws, "dashboard_data");

  if (fileType == 'xlsx') {
    writeFileXLSX(wb, fileName.trim() + ".xlsx");
  } 
  else if (fileType == 'xls') {
    writeFile(wb, fileName.trim() + ".xls");
  }
  else if (fileType == 'csv') {
    writeFile(wb, fileName.trim() + ".csv", { FS: ";" });
  }    
};

</script>



<template>

<div class="" > <!-- v-if="props.data[0]" necessary div for waiting data from root component!!! -->

<!-- **********************   MODAL ITEM DETAILS   ************************** -->
<div v-if="showItemCard" class="absolute z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50
  flex items-center justify-center">
  <div class="flex-col w-3/5 h-4/5 bg-white rounded-lg">

    <div class="py-3 pl-7 pr-3 bg-gray-200 rounded-t-lg overflow-auto">
      <div class="float-left text-xl">
        {{ props.name }}
      </div>
      <div class="float-right cursor-pointer hover:text-gray-500" @click="showItemCard=false">
        <i class="pi pi-times" style="font-size: 1.5rem"></i>
      </div>
    </div>
    
    
    <div class="h-4/5 m-7 text-sm overflow-auto">
      <table class="w-full">
        <tr class="" v-for="field in Object.keys(props.listItemFileds)">
          <td class="w-60 py-1 border-b font-semibold">
            {{ props.listItemFileds[field] }}
          </td>
          <td class="border-b">
            {{ selectedItem[field] }}
          </td>
        </tr>
      </table>
    </div>



  </div>
</div>


<div @click="checkState()" class="listArea min-w-96 max-w-max m-0 px-3 py-2 border border-gray-200 rounded-lg
  bg-white drop-shadow-md hover:drop-shadow-lg overflow-auto">

<!-- {{ props.listTableColumns }} -->

<!-- *******************************  NAV AREA  ************************* --> 
<nav class="overflow-auto">
  <div class="inline-block">
    <div class="text-xl font-normal">{{ props.name }}</div>
  </div>

  <div class="float-right">
  <!-- ***************   PAGINATION BLOCK   ********************* -->
  <div id="paginationBlock" class="inline-block mr-3">
  <div class="space-x-1.5">
    <div class="paginationBtn" @click="computeRenderData('first')">
      <i class="pi pi-angle-double-left" style="font-size: 1rem"></i>
    </div>
    <div class="paginationBtn" @click="computeRenderData('left')">
      <i class="pi pi-angle-left" style="font-size: 1rem"></i>
    </div>
    {{ state.limitRecords*(state.currentPage-1)+1 }}-{{ 
      (state.limitRecords*state.currentPage < dataLengthRender()) 
      ? state.limitRecords*state.currentPage : dataLengthRender() }} of {{ dataLengthRender() }}
    <div class="paginationBtn" @click="computeRenderData('right')">
      <i class="pi pi-angle-right" style="font-size: 1rem"></i>
    </div>
    <div class="paginationBtn" @click="computeRenderData('last')">
      <i class="pi pi-angle-double-right" style="font-size: 1rem"></i>
    </div>
  </div>
  </div>

  <!-- DOWNLOAD BUTTON DROPDOWN -->
  <div class="inline-block mr-1">
    <button class="w-8 h-8 rounded-lg bg-green-400 text-white hover:opacity-75" 
      @click="toggleDropdown('download')">
      <i class="pi pi-download" style="font-size: 1rem"></i>
    </button>
    <div v-show="isDropDownloadShow" class="mt-1 -ml-11 w-20 border rounded-md border-gray-300 
      bg-white text-xs font-semilbold absolute z-10 overflow-hidden">
      <ul @click="toggleDropdown('download')">
        <li class="h-8 pl-3 py-1.5 uppercase cursor-pointer hover:bg-gray-100" 
           @click="exportFile(dataSet=state.localData, fileName='dashboard_data', fileType=option)" v-for="option in ['xlsx', 'xls', 'csv']">{{ option }}</li>
      </ul>
    </div>
  </div>

</div>

<!-- search area ************************* --> 
<!-- <div class="inline-block">
<div id="searchArea" class="flex mr-5 w-96 border border-gray-100 rounded-full shadow-md hover:shadow-lg">

  <div class="flex-0 bg-gray-100 h-8 rounded-l-full" 
    @mouseover="mouseOverSearchDropdown=true" @mouseleave="mouseOverSearchDropdown=false">
    <button id="btn-6" @click="toggleDropdown('search')" class="border-l rounded-l-full px-3 h-8">
      <div class="inline-block mr-1">{{ props.listTableColumns[searchBy] || 'Все столбцы' }}</div>
      <i class="pi pi-angle-down" style="font-size: 0.7rem"></i>
    </button>
    <div v-show="isDropSearchShow" class="absolute z-10 bg-white text-sm font-semibold mt-1 ml-1 w-44
       border-gray-500 rounded-md overflow-hidden backdrop-filter backdrop-grayscale drop-shadow-lg">
      <ul @click="toggleDropdown('search')">
        <li class="border-b border-gray-300 pl-3 py-1.5 cursor-pointer hover:bg-gray-100" @click="searchBy='all'">Все столбцы</li>
        <li :class=dropdownLiStyle @click="searchBy=elem" v-for="elem in searchFieldsList">{{ props.listTableColumns[elem] }}</li>
      </ul>
    </div>
  </div>

  <div class="mt-1.5 flex-0 pl-2 text-gray-600"><i class="pi pi-search"></i></div>
  <input class="flex-1 h-8 pl-3 border-r rounded-r-full focus:outline-none" type="text" id="searchInput" @keyup="searchRecord()" 
    placeholder="Search" title="Type in a name">

</div>
</div> -->

<!-- sort area ************************* --> 
<!-- <div class="inline-block">
<div id="sortArea" class="flex mr-5">

  <div class="flex-0" @mouseover="mouseOverSortDropdown=true" @mouseleave="mouseOverSortDropdown=false">
    <button id="btn-4" @click="toggleDropdown('sort')" class="bg-gray-100 rounded-full px-3 mr-1 h-8
      backdrop-filter backdrop-grayscale drop-shadow-lg hover:shadow-lg">
      <div class="inline-block mr-1" v-if="sortBy=='default'">Sort by</div>
      <div class="inline-block mr-1 capitalize" v-else>{{ sortBy }}</div>
      <i class="pi pi-angle-down" style="font-size: 0.7rem"></i>
    </button>
    <div v-show="isDropSortShow" class="absolute z-10 bg-white text-sm font-semibold mt-1 ml-1 w-40 
       border-gray-500 rounded-md overflow-hidden backdrop-filter backdrop-grayscale drop-shadow-lg">
      <ul @click="toggleDropdown('sort')">
        <li class="border-b border-gray-300 pl-3 py-1.5 cursor-pointer hover:bg-gray-100" @click="clickSortField('default')">Default</li>
        <li :class=dropdownLiStyle @click="clickSortField(field)" v-for="field in sortFieldsList">{{ field }}</li>
      </ul>
    </div>
  </div>  

  <button id="btn-5" class="flex-1 bg-gray-100 rounded-full w-8 h-8 backdrop-filter backdrop-grayscale drop-shadow-lg hover:shadow-lg" 
    @click="clickSortArrow()">
    <i :class=sortIcon style="font-size: 0.8rem; color: orange"></i>
  </button>
</div>
</div> -->

<!-- filters area *************************  -->
<!-- <div id="filtersArea" class="inline-block mr-5">
  <button id='btn-1' :class=btnStyle>
    <i class="pi pi-filter" style="font-size: 0.8rem; color: blue"></i>
    <span class="ml-2">Filter</span>
  </button>
</div> -->

<!-- refresh area *************************  -->
<!-- <div id="refreshArea" class="inline-block mr-5">
  <button id='btn-2' :class=btnStyle>
    <i class="pi pi-refresh" style="font-size: 0.8rem; color: magenta"></i>
    <span class="ml-2">Refresh</span>
  </button>
</div> -->

<!-- add element area ************************* --> 
<!-- <div id="addElementArea" class="inline-block mr-5">
  <RouterLink to="/items/add">
    <button id='btn-3' :class=btnStyle @click="console.log('add element')">
      <i class="pi pi-plus" style="font-size: 0.8rem; color: green"></i>
      <span class="ml-2">Add</span>
    </button>
  </RouterLink>
</div> -->

</nav>

<!-- table area ************************* --> 
<section class="mt-2 border rounded-lg overflow-auto">
<table class="">
  <thead>
    <tr class="h-8 bg-blue-400 text-sm font-semibold text-white text-center">
      <td class="border" v-for="(field, index) in Object.keys(props.listTableColumns)">
      
        <div class="relative">
          <div class="flex px-2 py-2 min-w-max">
            <div :class=sortArrowsStyle[field] @click="clickSortField2(field)"><i :class=sortIcon[field] style="font-size: 0.7rem"></i></div>
            <div :class=filterIconStyle[field] @click="clickFilter(field)"><i :class=filterIcon[field] style="font-size: 0.7rem"></i></div>
            <div class="flex-1">{{ props.listTableColumns[field] }}</div>
          </div>

          <div v-show="isListFilterShow[field]" class="absolute text-black text-sm font-semibold mt-1 ml-1
            border-4 border-indigo-500 rounded-lg shadow-lg overflow-hidden">
            <input class="h-8 pl-3" type="text" :id="'searchInput'+field"  
              placeholder="Filter value" title="" @keyup="setFilter(field)">
          </div>
        </div>

      </td>
    </tr>
  </thead>
  <tbody>
    <tr v-if="dataLengthRender()==0"><td><div class="h-11"></div></td></tr>
    <tr class="border-t text-xs font-normal text-center cursor-pointer hover:bg-gray-100" 
        @click="selectedItem=item; showItemCard=true" v-for="item in dataRender()">
      <td class="" v-for="field in Object.keys(props.listTableColumns)">
        <!-- boolean columns -->
        <div class="" v-if="typeof(item[field])=='boolean' & item[field]==true"><i class="pi pi-check-square"></i></div>
        <div class="" v-else-if="typeof(item[field])=='boolean' & item[field]==false"><i class="pi pi-stop"></i></div>
        <!-- date columns
        <div class="" v-else-if="field=='established'">
          {{ item[field].slice(8, 10) }}/{{ item[field].slice(5, 7) }}/{{ item[field].slice(0, 4) }}
        </div> -->
        <!-- date columns -->
        <div class="px-2 py-2 min-w-max" v-else-if="['Дата', 'Время'].some(el => props.listTableColumns[field].includes(el))">  
          <!-- {{ item[field].slice(0,20) }} -->  <!-- min-w-max -->
          {{ item[field] }}
        </div>
        <!-- string columns -->
        <div class="px-2 py-2 text-left max-w-48 truncate" v-else-if="typeof(item[field])=='string'">
          <!-- {{ item[field].slice(0,20) }} -->  <!-- min-w-max -->
          {{ item[field] }}
        </div>
        <!-- other columns -->
        <div class="px-2 py-2 min-w-max" v-else>{{ item[field] }}</div>
      </td>
    </tr>
  </tbody>
</table>
</section>

</div>
</div>
</template>


<style lang="postcss" scope>
.listArea {
  height: 620px;
}

.paginationBtn {
  @apply bg-gray-50 hover:bg-gray-100 inline-block cursor-pointer w-8 h-8 border rounded-lg text-center py-1
}

#btn-1:hover, #btn-2:hover, #btn-3:hover,
#btn-4:hover, #btn-5:hover, #btn-6:hover {
  background-color: #E4E4E7;
  color: #18181B;
}
</style>