import { createRouter, createWebHistory } from 'vue-router'
import Index from '../views/Index.vue'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Index
    }
]
const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router