<template>
  <div class="app-container">
    <div v-if="showTimeWarning" class="time-warning-dialog" @click.self="closeWarning">
      <div class="dialog-content">
        <h3>温馨提醒</h3>
        <p>距离今日使用时长结束还有5分钟，请注意休息！</p>
        <button @click="closeWarning">知道了</button>
      </div>
    </div>

    <div v-if="showTimeUpDialog" class="time-up-dialog">
      <div class="dialog-content">
        <h3>使用时长已到</h3>
        <p>今日学习时间已用完，请休息！</p>
        <button @click="closeTimeUpDialog">确定</button>
      </div>
    </div>

    <aside class="sidebar">
      <div class="sidebar-header">
        <img class="logo-icon" src="/images/Student_Icons/SystemIcons.png" alt="logo" />
        <div class="logo-text">
          <h1>学生端</h1>
        </div>
      </div>

      <nav class="nav-menu">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="nav-item" :class="{ active: route.path === item.path }">
          <img class="nav-icon" :src="item.icon" :alt="item.label" />
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <img class="user-avatar" :src="userStore.studentInfo.avatar" alt="avatar" />
          <div class="user-details">
            <span class="user-name">{{ userStore.studentInfo.name }}</span>
            <span class="user-status">在线</span>
          </div>
        </div>
        <button @click="handleLogout" class="logout-btn">退出</button>
      </div>
    </aside>

    <div class="main-wrap">
      <header class="top-header-bar">
        <div class="header-left">
          <span class="current-page">{{ currentTitle }}</span>
        </div>
        <div class="timer-bar">
          <span class="timer-label">今日剩余时长：</span>
          <span class="timer-value" :class="{ warning: remainingTime <= 300 }">{{ formatTime(remainingTime) }}</span>
        </div>
        <div class="header-right">
          <div class="top-user">
            <img class="top-avatar" :src="userStore.studentInfo.avatar" alt="" />
            <span class="top-name">{{ userStore.studentInfo.name }}</span>
            <span class="top-class">{{ userStore.studentInfo.class }}</span>
          </div>
          <div class="top-pet">
            <img class="top-pet-img" :src="userStore.petInfo.type" alt="" />
            <span class="top-pet-name">我的宠物：{{ userStore.petInfo.name }}</span>
          </div>
        </div>
      </header>

      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const route = useRoute()
const store = useAppStore()
const userStore = useUserStore()

const navItems = [
  { path: '/student', label: '班级首页', icon: '/images/Student_Navigation_Bar/首页.svg' },
  { path: '/student/ai-learning', label: 'AI通识课', icon: '/images/Student_Navigation_Bar/聊天.svg' },
  { path: '/student/my-pet', label: '我的宠物', icon: '/images/Student_Navigation_Bar/携带宠物.svg' },
  { path: '/student/ai-companion', label: '智能情感交流', icon: '/images/Student_Navigation_Bar/聊天.svg' },
  { path: '/student/growth-diary', label: '成长日记', icon: '/images/Student_Navigation_Bar/日记.svg' },
  { path: '/student/tasks', label: '当日任务', icon: '/images/Student_Navigation_Bar/任务.svg' },
  { path: '/student/settings', label: '设置', icon: '/images/Student_Navigation_Bar/设置.svg' },
]

const currentTitle = computed(() => {
  const item = navItems.find(n => n.path === route.path)
  return item?.label || '班级首页'
})

const dailyTimeLimit = ref(3 * 60 * 60)
const remainingTime = ref(3 * 60 * 60)
const showTimeWarning = ref(false)
const showTimeUpDialog = ref(false)
let timer: number | null = null

const formatTime = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const updateRemainingTime = () => {
  remainingTime.value--
  if (remainingTime.value <= 0) {
    showTimeUpDialog.value = true
    if (timer) clearInterval(timer)
  } else if (remainingTime.value === 300) {
    showTimeWarning.value = true
  }
}

const closeWarning = () => { showTimeWarning.value = false }
const closeTimeUpDialog = () => { showTimeUpDialog.value = false }

onMounted(() => {
  store.load()
  const savedRemaining = localStorage.getItem('studentRemainingTime')
  if (savedRemaining) {
    remainingTime.value = parseInt(savedRemaining)
  }
  if (remainingTime.value > 0) {
    timer = window.setInterval(() => {
      updateRemainingTime()
      localStorage.setItem('studentRemainingTime', remainingTime.value.toString())
    }, 1000)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function handleLogout() {
  store.logout()
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
:root {
  --sidebar-width: 220px;
  --header-height: 60px;
}
.app-container {
  min-height: 100vh;
  background: #FFF8DC;
  display: flex;
}
.timer-bar {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #ffb74d 0%, #ff9800 100%);
  padding: 8px 20px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
}
.timer-label { color: white; font-size: 14px; font-weight: 500; }
.timer-value { color: white; font-size: 18px; font-weight: bold; }
.timer-value.warning { color: #ff0000; animation: blink 1s infinite; }
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.time-warning-dialog, .time-up-dialog {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}
.dialog-content {
  background: white; padding: 30px; border-radius: 15px;
  text-align: center; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  min-width: 300px;
}
.dialog-content h3 { color: #ff9800; margin-bottom: 15px; font-size: 20px; }
.dialog-content p { color: #333; font-size: 16px; margin-bottom: 20px; }
.dialog-content button {
  background: #ff9800; color: white; border: none;
  padding: 10px 30px; border-radius: 20px; font-size: 16px; cursor: pointer;
}
.main-wrap {
  margin-left: var(--sidebar-width);
  width: calc(100% - var(--sidebar-width));
  display: flex;
  flex-direction: column;
}
.sidebar {
  position: fixed; left: 0; top: 0;
  width: var(--sidebar-width); height: 100vh;
  background: #f48d45;
  display: flex; flex-direction: column;
  z-index: 100;
}
.sidebar-header {
  padding: 24px 20px;
  display: flex; align-items: center; gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.3);
}
.logo-icon { width: 80px; height: 80px; object-fit: contain; border-radius: 50%; }
.logo-text h1 { font-size: 20px; color: #fff; font-weight: bold; margin: 0; }
.nav-menu { flex: 1; padding: 16px 12px; overflow-y: auto; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px; color: rgba(255,255,255,0.9);
  text-decoration: none; border-radius: 8px;
  transition: all 0.2s; cursor: pointer; margin-bottom: 4px;
}
.nav-item:hover { background: rgba(255,255,255,0.2); color: #fff; }
.nav-item.active { background: rgba(255,255,255,0.25); color: #fff; }
.nav-icon { width: 24px; height: 24px; object-fit: contain; }
.nav-item.active .nav-icon { filter: brightness(0) invert(1); }
.nav-label { font-size: 14px; }
.sidebar-footer { padding: 16px; border-top: 1px solid rgba(255,255,255,0.3); }
.user-info { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.user-avatar { width: 40px; height: 40px; border-radius: 8px; object-fit: cover; }
.user-details { display: flex; flex-direction: column; }
.user-name { color: #fff; font-size: 14px; font-weight: 500; }
.user-status { color: rgba(255,255,255,0.8); font-size: 12px; }
.logout-btn {
  width: 100%; padding: 10px; background: rgba(255,255,255,0.2);
  border: none; color: #fff; border-radius: 8px; cursor: pointer; font-size: 14px;
}
.logout-btn:hover { background: rgba(220,38,38,0.3); }
.top-header-bar {
  height: var(--header-height);
  background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; position: sticky; top: 0; z-index: 99; position: relative;
}
.current-page { font-size: 16px; font-weight: 600; color: #333; }
.header-left { flex: 1; }
.header-right { display: flex; align-items: center; gap: 30px; }
.top-user { display: flex; align-items: center; gap: 8px; }
.top-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }
.top-name { font-size: 14px; color: #333; font-weight: 500; }
.top-class { font-size: 12px; color: #999; }
.top-pet {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; background: #fff0e6; border-radius: 20px;
}
.top-pet-img { width: 24px; height: 24px; object-fit: contain; }
.top-pet-name { font-size: 13px; color: #f48d45; font-weight: 500; }
.main-content {
  height: calc(100vh - var(--header-height));
  padding: 16px; background: #FFF8DC;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
