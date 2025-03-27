import { createRouter, createWebHistory } from "vue-router";
import DocumentsView from "@/views/DocumentsView.vue";
import CarpassesView from "@/views/CarpassesView.vue";
import CarTerminalView from "@/views/CarTerminalView.vue";
import DashboardView from "@/views/DashboardView.vue";
// import ItemView from "@/views/ItemView.vue";
// import AddItemView from "@/views/AddItemView.vue";
// import EditItemView from "@/views/EditItemView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
        path: '/documents',
        name: 'documents',
        component: DocumentsView,
    },
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
