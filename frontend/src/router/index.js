import { createRouter, createWebHistory } from "vue-router";
import DocumentsView from "@/views/DocumentsView.vue";
import VehiclesView from "@/views/VehiclesView.vue";
import DashboardView from "@/views/DashboardView.vue";
// import ItemView from "@/views/ItemView.vue";
// import AddItemView from "@/views/AddItemView.vue";
// import EditItemView from "@/views/EditItemView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
        path: '/',
        name: 'documents',
        component: DocumentsView,
    },
    {
      path: '/vehicles',
      name: 'vehicles',
      component: VehiclesView,
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
