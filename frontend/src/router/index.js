import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "@/views/DashboardView.vue";
// import ItemView from "@/views/ItemView.vue";
// import AddItemView from "@/views/AddItemView.vue";
// import EditItemView from "@/views/EditItemView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
        path: '/',
        name: 'dashboard',
        component: DashboardView,
    },
    // {
    //   path: '/items/add',
    //   name: 'add-item',
    //   component: AddItemView,
    // },
    // {
    //   path: '/items/edit/:id',
    //   name: 'edit-item',
    //   component: EditItemView,
    // },
    // {
    //   path: '/items/:id',
    //   name: 'item',
    //   component: ItemView,
    // },
  ]
});

export default router;
