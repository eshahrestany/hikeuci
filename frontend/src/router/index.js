import { createRouter, createWebHistory } from 'vue-router'
import Index from '../views/public/Index.vue'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Index
    },
    {
        path: '/login',
        name: 'SignIn',
        component: () => import('../views/public/SignIn.vue'),
    },
    {
        path: '/admin',
        name: 'Dashboard',
        component: () => import('../views/admin/Dashboard.vue'),
        meta: { requiresAuth: true },
    },
]
const router = createRouter({
  history: createWebHistory(),
  routes,
});

import { useAuth } from '../lib/auth.js'
router.beforeEach((to, from, next) => {
  const { state } = useAuth()
  if (to.meta.requiresAuth && !state.user) {
    next({ name: 'SignIn', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router