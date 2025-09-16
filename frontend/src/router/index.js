import {createRouter, createWebHistory} from 'vue-router'
import Index from '../views/public/Index.vue'
import NotFound from '../views/public/NotFound.vue'

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
    path: '/vote',
    name: 'Vote',
    component: () => import('../views/public/Vote.vue'),
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('../views/public/Signup.vue'),
  },
  {
    path: '/waiver',
    name: 'Waiver',
    component: () => import('../views/public/Waiver.vue'),
  },
  {
    'path': '/esign-policy',
    name: 'EsignPolicy',
    component: () => import('../views/public/EsignPolicy.vue'),
  },
  {
    'path': '/privacy-policy',
    name: 'PrivacyPolicy',
    component: () => import('../views/public/PrivacyPolicy.vue'),
  },
  {
    path: '/admin',
    name: 'Dashboard',
    component: () => import('../views/admin/Dashboard.vue'),
    meta: {requiresAuth: true},
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
  },
]
const router = createRouter({
  history: createWebHistory(),
  routes,
});

import {useAuth} from '../lib/auth.js'

router.beforeEach((to, from, next) => {
  const {state} = useAuth()
  if (to.meta.requiresAuth && !state.user) {
    next({name: 'SignIn', query: {redirect: to.fullPath}})
  } else {
    next()
  }
})

export default router