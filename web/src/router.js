import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './views/Dashboard.vue'
import DepartmentList from './views/DepartmentList.vue'
import DepartmentDetail from './views/DepartmentDetail.vue'
import EmployeeList from './views/EmployeeList.vue'
import EmployeeEdit from './views/EmployeeEdit.vue'
import AttendanceList from './views/AttendanceList.vue'
import AttendanceSettings from './views/AttendanceSettings.vue'
import Login from './views/Login.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/departments',
    name: 'DepartmentList',
    component: DepartmentList,
    meta: { requiresAuth: true }
  },
  {
    path: '/departments/:id',
    name: 'DepartmentDetail',
    component: DepartmentDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/employees',
    name: 'EmployeeList',
    component: EmployeeList,
    meta: { requiresAuth: true }
  },
  {
    path: '/employees/new',
    name: 'EmployeeNew',
    component: EmployeeEdit,
    meta: { requiresAuth: true }
  },
  {
    path: '/employees/:id',
    name: 'EmployeeEdit',
    component: EmployeeEdit,
    meta: { requiresAuth: true }
  },
  {
    path: '/attendance',
    name: 'AttendanceList',
    component: AttendanceList,
    meta: { requiresAuth: true }
  },
  {
    path: '/attendance-settings',
    name: 'AttendanceSettings',
    component: AttendanceSettings,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router 