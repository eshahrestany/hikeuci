import { createRouter, createWebHistory } from 'vue-router'
import ExampleIndex from '../components/views/ExampleIndex.vue'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: ExampleIndex
    }
]
const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router