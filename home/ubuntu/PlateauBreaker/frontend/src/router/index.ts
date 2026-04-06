import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import Records from '@/views/Records.vue'
import Analysis from '@/views/Analysis.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: 'Dashboard' },
  },
  {
    path: '/records',
    name: 'Records',
    component: Records,
    meta: { title: 'Health Records' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis,
    meta: { title: 'Plateau Analysis' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'PlateauBreaker'} — PlateauBreaker`
})

export default router
