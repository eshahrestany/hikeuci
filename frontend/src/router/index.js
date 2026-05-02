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
    path: '/unsubscribe',
    name: 'Unsubscribe',
    component: () => import('../views/public/Unsubscribe.vue'),
  },
  {
    path: '/admin',
    component: () => import('../views/admin/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        meta: { title: 'HikeUCI Dashboard' },
        component: () => import('../views/admin/Dashboard.vue'),
      },
      {
        path: 'trails',
        name: 'Dashboard Trails',
        meta: { title: 'HikeUCI Dashboard Trails' },
        component: () => import('../views/admin/DashboardTrails.vue'),
      },
      {
        path: 'members',
        name: 'Dashboard Members',
        meta: { title: 'HikeUCI Dashboard Members' },
        component: () => import('../views/admin/DashboardMembers.vue'),
      },
      {
        path: 'officers',
        name: 'Dashboard Officers',
        meta: { title: 'HikeUCI Dashboard Officers', requiresOwner: true },
        component: () => import('../views/admin/DashboardOfficers.vue'),
      },
      {
        path: 'history',
        name: 'Dashboard History',
        meta: { title: 'HikeUCI Dashboard History' },
        component: () => import('../views/admin/HikeHistory.vue'),
      },
      {
        path: 'emails',
        name: 'Dashboard Emails',
        meta: { title: 'HikeUCI Dashboard Emails' },
        component: () => import('../views/admin/DashboardEmails.vue'),
      },
      {
        path: 'trails/:trailId',
        name: 'Trail Detail',
        meta: { title: 'HikeUCI Trail Detail' },
        component: () => import('../views/admin/TrailDetail.vue'),
        props: true,
      },
      {
        path: 'history/hikes/:hikeId',
        name: 'Hike Detail',
        meta: { title: 'HikeUCI Hike Detail' },
        component: () => import('../views/admin/HikeDetail.vue'),
        props: true,
      },
      {
        path: 'history/members/:memberId',
        name: 'Member History',
        meta: { title: 'HikeUCI Member History' },
        component: () => import('../views/admin/MemberHistory.vue'),
        props: true,
      },
    ]
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
  } else if (to.meta.requiresOwner && !state.user?.is_owner) {
    next({name: 'Dashboard'})
  } else {
    next()
  }
})

export default router