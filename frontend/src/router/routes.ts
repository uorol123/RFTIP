import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: 'Home' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: 'Login' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: 'Register' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'Dashboard' },
  },
  {
    path: '/data',
    name: 'DataManagement',
    component: () => import('@/views/DataManagement.vue'),
    meta: { title: 'Data Management' },
  },
  {
    path: '/data/:id',
    name: 'FileDetails',
    component: () => import('@/views/FileDetails.vue'),
    meta: { title: 'File Details' },
  },
  {
    path: '/tracks',
    name: 'TrackVisualization',
    component: () => import('@/views/TrackVisualization.vue'),
    meta: { title: 'Track Visualization' },
  },
  {
    path: '/tracks/:id',
    name: 'TrackDetails',
    component: () => import('@/views/TrackDetails.vue'),
    meta: { title: 'Track Details' },
  },
  {
    path: '/zones',
    name: 'ZoneManagement',
    component: () => import('@/views/ZoneManagement.vue'),
    meta: { title: 'No-Fly Zones' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis.vue'),
    meta: { title: 'AI Analysis' },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: 'Profile' },
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404 - Not Found' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
  },
]

export default routes
