<template>
  <div class="app-container">
    <header class="top-header">
      <div class="header-left">
        <span class="logo-text">教师工作台</span>
      </div>
      <div class="header-right">
        <el-badge :value="3" class="icon-badge">
          <el-icon class="header-icon"><Bell /></el-icon>
        </el-badge>
        <el-badge :value="5" class="icon-badge">
          <el-icon class="header-icon"><Message /></el-icon>
        </el-badge>
        <el-dropdown @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
            <div class="user-detail">
              <span class="user-name">{{ store.user?.name || store.user?.username || '教师' }}</span>
              <el-tag size="small" type="danger">资深教师</el-tag>
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人设置</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="main-wrapper">
      <aside class="sidebar">
        <nav class="nav-menu">
          <router-link to="/teacher" class="nav-item" :class="{ active: route.path === '/teacher' }">
            <el-icon><HomeFilled /></el-icon>
            <span>工作台</span>
          </router-link>

          <div class="nav-group">
            <router-link to="/teacher/points" class="nav-item" :class="{ active: route.path === '/teacher/points' }">
              <el-icon><Coin /></el-icon>
              <span>积分管理</span>
            </router-link>
            <router-link to="/teacher/classes" class="nav-item" :class="{ active: route.path === '/teacher/classes' }">
              <el-icon><OfficeBuilding /></el-icon>
              <span>班级管理</span>
            </router-link>
          </div>

          <router-link to="/teacher/group-roles" class="nav-item" :class="{ active: route.path === '/teacher/group-roles' }">
            <el-icon><UserFilled /></el-icon>
            <span>群体智能角色管理</span>
          </router-link>

          <router-link to="/teacher/role-network" class="nav-item" :class="{ active: route.path === '/teacher/role-network' }">
            <el-icon><Connection /></el-icon>
            <span>群体智能角色网络</span>
          </router-link>

          <router-link to="/teacher/trend-prediction" class="nav-item" :class="{ active: route.path === '/teacher/trend-prediction' }">
            <el-icon><DataLine /></el-icon>
            <span>群体趋势预测</span>
          </router-link>

          <router-link to="/teacher/intervention" class="nav-item" :class="{ active: route.path === '/teacher/intervention' }">
            <el-icon><WarningFilled /></el-icon>
            <span>干预管理</span>
          </router-link>

          <router-link to="/teacher/forum" class="nav-item" :class="{ active: route.path === '/teacher/forum' }">
            <el-icon><ChatDotSquare /></el-icon>
            <span>交流论坛</span>
          </router-link>

          <router-link to="/teacher/materials" class="nav-item" :class="{ active: route.path === '/teacher/materials' }">
            <el-icon><FolderOpened /></el-icon>
            <span>资料管理</span>
          </router-link>
        </nav>
      </aside>

      <main class="content-area">
        <div class="content-header">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="content-body">
          <router-view v-slot="{ Component }">
            <keep-alive :max="8">
              <component :is="Component" />
            </keep-alive>
          </router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import {
  HomeFilled, Coin, OfficeBuilding, UserFilled, Connection,
  DataLine, WarningFilled, ChatDotSquare, Bell, Message, FolderOpened
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const handleCommand = (command: string) => {
  if (command === 'profile') {
    router.push('/teacher/settings')
  } else if (command === 'logout') {
    store.logout()
    router.push('/login')
  }
}

const pageTitle = computed(() => {
  const pathMap: Record<string, string> = {
    '/teacher': '工作台',
    '/teacher/points': '积分管理',
    '/teacher/classes': '班级管理',
    '/teacher/group-roles': '群体智能角色管理',
    '/teacher/role-network': '群体智能角色网络',
    '/teacher/trend-prediction': '群体趋势预测',
    '/teacher/intervention': '干预管理',
    '/teacher/forum': '交流论坛',
    '/teacher/materials': '资料管理',
  }
  return pathMap[route.path] || '教师工作台'
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #F0F0FF;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.top-header {
  height: 56px;
  background: #8985cf;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #6d6aab;
}

.header-left { display: flex; align-items: center; }
.logo-text { font-size: 18px; font-weight: 600; color: #f7f3e5; }

.header-right { display: flex; align-items: center; gap: 16px; }
.icon-badge { cursor: pointer; }
.header-icon { font-size: 20px; color: #f7f3e5; transition: color 0.2s; }
.header-icon:hover { color: #fff; }

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 8px;
  border: none;
  transition: background 0.2s;
}
.user-info:hover { background: rgba(255,255,255,0.15); }
.user-detail { display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }
.user-name { font-size: 14px; font-weight: 500; color: #f7f3e5; }

.main-wrapper { flex: 1; display: flex; overflow: hidden; }

.sidebar {
  width: 220px;
  background: #8985cf;
  border-right: 1px solid #6d6aab;
  overflow-y: auto;
  padding: 16px 0;
}

.nav-menu { display: flex; flex-direction: column; }

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  color: #f7f3e5;
  text-decoration: none;
  transition: all 0.2s;
  font-size: 14px;
}
.nav-item:hover { background: rgba(255,255,255,0.15); color: #fff; }
.nav-item.active { background: rgba(255,255,255,0.2); color: #fff; font-weight: 500; }
.nav-item .el-icon { font-size: 18px; }

.nav-group { margin-top: 12px; padding-top: 12px; border-top: 1px solid #6d6aab; }

.content-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.content-header {
  padding: 20px 28px;
  background: #fff;
  border-bottom: 1px solid #E8E0F0;
}
.page-title { margin: 0; font-size: 18px; font-weight: 600; color: #8985cf; }

.content-body { flex: 1; overflow-y: auto; padding: 24px; }
</style>
