import { createRouter, createWebHistory } from "vue-router";
import DocumentsView from "@/views/DocumentsView.vue";
import CarpassesView from "@/views/CarpassesView.vue";
import CarTerminalView from "@/views/CarTerminalView.vue";
import ExitcarpassesView from "@/views/ExitcarpassesView.vue";
import DashboardView from "@/views/DashboardView.vue";
import EntryRequestsView from "@/views/EntryRequestsView.vue";
import ParkingMapView from "@/views/ParkingMapView.vue";
// import ItemView from "@/views/ItemView.vue";
// import AddItemView from "@/views/AddItemView.vue";
// import EditItemView from "@/views/EditItemView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'carpasses',
      component: CarpassesView,
    },
    {
      path: '/car_terminal',
      name: 'car_terminal',
      component: CarTerminalView,
    },
    {
      path: '/exitcarpasses',
      name: 'exitcarpasses',
      component: ExitcarpassesView,
    },
    {
      path: '/entry_requests',
      name: 'entry_requests',
      component: EntryRequestsView,
    },
    {
      path: '/parking_map',
      name: 'parking_map',
      component: ParkingMapView,
    },
    {
      path: '/documents',
      name: 'documents',
      component: DocumentsView,
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
    },
    // {
    //   path: '/items/:id',
    //   name: 'item',
    //   component: ItemView,
    // },
  ]
});

export default router;
