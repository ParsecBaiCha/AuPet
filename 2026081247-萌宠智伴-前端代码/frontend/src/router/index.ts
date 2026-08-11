import { createRouter, createWebHistory } from 'vue-router'
import { useAppStore } from '../stores/app'

const routes = [
  { path: '/', redirect: '/login' },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/Register.vue'),
  },
  {
    path: '/student',
    component: () => import('../views/student/Layout.vue'),
    meta: { roles: ['student'] },
    children: [
      { path: '', name: 'StudentHome', component: () => import('../views/student/Home.vue') },
      { path: 'my-pet', name: 'MyPet', component: () => import('../views/student/MyPet.vue') },
      { path: 'ai-learning', name: 'AILearning', component: () => import('../views/student/AILearning.vue') },
      { path: 'ai-companion', name: 'AICompanion', component: () => import('../views/student/AICompanion.vue') },
      { path: 'growth-diary', name: 'GrowthDiary', component: () => import('../views/student/GrowthDiary.vue') },
      { path: 'tasks', name: 'StudentTasks', component: () => import('../views/student/Tasks.vue') },
      { path: 'settings', name: 'StudentSettings', component: () => import('../views/student/Settings.vue') },
    ],
  },
  {
    path: '/teacher',
    component: () => import('../views/teacher/Layout.vue'),
    meta: { roles: ['teacher'] },
    children: [
      { path: '', name: 'TeacherHome', meta: { title: '工作台', icon: 'DataBoard' }, component: () => import('../views/teacher/Home.vue') },
      { path: 'points', name: 'TeacherPoints', meta: { title: '积分管理', icon: 'Coin' }, component: () => import('../views/teacher/PointManagement.vue') },
      { path: 'classes', name: 'ClassManagement', meta: { title: '班级管理', icon: 'School' }, component: () => import('../views/teacher/ClassManagement.vue') },
      { path: 'group-roles', name: 'GroupRoleManagement', meta: { title: '群体智能角色管理', icon: 'UserFilled' }, component: () => import('../views/teacher/GroupRoleManagement.vue') },
      { path: 'role-network', name: 'RoleNetwork', meta: { title: '群体智能角色网络', icon: 'Connection' }, component: () => import('../views/teacher/RoleNetwork.vue') },
      { path: 'trend-prediction', name: 'TrendPrediction', meta: { title: '群体趋势预测', icon: 'TrendCharts' }, component: () => import('../views/teacher/TrendPrediction.vue') },
      { path: 'intervention', name: 'Intervention', meta: { title: '干预管理', icon: 'WarningFilled' }, component: () => import('../views/teacher/Intervention.vue') },
      { path: 'forum', name: 'TeacherForum', meta: { title: '交流论坛', icon: 'ChatDotRound' }, component: () => import('../views/teacher/Forum.vue') },
    ],
  },
  {
    path: '/admin',
    component: () => import('../views/admin/Layout.vue'),
    meta: { roles: ['admin'] },
    children: [
      { path: '', name: 'AdminHome', meta: { title: '首页', icon: 'DataBoard' }, component: () => import('../views/admin/Home.vue') },
      { path: 'students', name: 'AdminStudents', meta: { title: '学生管理', icon: 'UserFilled' }, component: () => import('../views/admin/StudentManagement.vue') },
      { path: 'teachers', name: 'AdminTeachers', meta: { title: '教师管理', icon: 'Avatar' }, component: () => import('../views/admin/TeacherManagement.vue') },
      { path: 'daily-forum', name: 'DailyForum', meta: { title: '日常论坛管理', icon: 'ChatDotRound' }, component: () => import('../views/admin/DailyForum.vue') },
      { path: 'subject-forum', name: 'SubjectForum', meta: { title: '学科论坛管理', icon: 'Notebook' }, component: () => import('../views/admin/SubjectForum.vue') },
      { path: 'points', name: 'AdminPoints', meta: { title: '积分概览', icon: 'Coin' }, component: () => import('../views/admin/PointOverview.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const store = useAppStore()
  store.load()
  const token = store.token
  const user = store.user

  if (to.meta.roles && !token) {
    return next('/login')
  }

  if (to.meta.roles && user && !(to.meta.roles as string[]).includes(user.role)) {
    return next(`/${user.role}`)
  }

  if ((to.path === '/login' || to.path === '/register') && token && user) {
    return next(`/${user.role}`)
  }

  next()
})

export default router
