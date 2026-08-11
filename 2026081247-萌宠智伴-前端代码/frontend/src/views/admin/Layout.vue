<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <img src="/images/Admin_Icons/System.png" class="system-icon" alt="system" />
          </div>
          <div class="logo-info">
            <span class="logo-title">管理员端</span>
          </div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/admin" class="nav-single" :class="{ active: route.path === '/admin' }">
          <img src="/images/Admin_Icons/Home.svg" class="nav-icon-img" alt="home" />
          <span>首页</span>
        </router-link>

        <div class="nav-group">
          <div class="nav-title">
            <img src="/images/Admin_Icons/UserManagement .svg" class="nav-icon-img" alt="user" />
            <span>用户管理</span>
          </div>
          <div class="nav-items">
            <router-link to="/admin/students" class="nav-item" :class="{ active: route.path === '/admin/students' }">
              <span>学生管理</span>
            </router-link>
            <router-link to="/admin/teachers" class="nav-item" :class="{ active: route.path === '/admin/teachers' }">
              <span>教师管理</span>
            </router-link>
          </div>
        </div>

        <div class="nav-group">
          <div class="nav-title">
            <img src="/images/Admin_Icons/ForumManagement.svg" class="nav-icon-img" alt="forum" />
            <span>论坛管理</span>
          </div>
          <div class="nav-items">
            <router-link to="/admin/daily-forum" class="nav-item" :class="{ active: route.path === '/admin/daily-forum' }">
              <span>日常论坛</span>
            </router-link>
            <router-link to="/admin/subject-forum" class="nav-item" :class="{ active: route.path === '/admin/subject-forum' }">
              <span>学科论坛</span>
            </router-link>
          </div>
        </div>

        <div class="nav-group">
          <div class="nav-title">
            <img src="/images/Admin_Icons/points.svg" class="nav-icon-img" alt="points" />
            <span>积分管理</span>
          </div>
          <div class="nav-items">
            <router-link to="/admin/points" class="nav-item" :class="{ active: route.path === '/admin/points' }">
              <span>积分概览</span>
            </router-link>
          </div>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="user-card">
          <div class="user-avatar">{{ store.user?.name?.charAt(0) || 'A' }}</div>
          <div class="user-info">
            <span class="user-name">{{ store.user?.name || store.user?.username || '管理员' }}</span>
            <span class="user-role">管理员</span>
          </div>
          <el-button type="danger" size="small" class="logout-btn" @click="handleLogout">退出</el-button>
        </div>
      </div>
    </aside>

    <main class="main-wrapper">
      <header class="topbar">
        <div class="topbar-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
          <div class="breadcrumb">
            <span>Home</span>
            <span class="separator">/</span>
            <span class="current">{{ pageTitle }}</span>
          </div>
        </div>

        <div class="topbar-right">
          <div class="search-bar">
            <input type="text" placeholder="搜索..." />
          </div>

          <el-popover placement="bottom" :width="300" trigger="click">
            <template #reference>
              <div class="icon-btn">
                <span class="dot"></span>
              </div>
            </template>
            <div class="notification-panel">
              <div class="notif-header">
                <span>通知</span>
                <span class="mark">全部已读</span>
              </div>
              <div class="notif-item">
                <div class="notif-icon warning">⚠</div>
                <div class="notif-content">
                  <p>学生积分异常提醒</p>
                  <span>3分钟前</span>
                </div>
              </div>
              <div class="notif-item">
                <div class="notif-icon success">✓</div>
                <div class="notif-content">
                  <p>新帖子审核通过</p>
                  <span>10分钟前</span>
                </div>
              </div>
            </div>
          </el-popover>

          <div class="user-badge">
            <span class="user-badge-name">{{ store.user?.name || store.user?.username || '管理员' }}</span>
          </div>
        </div>
      </header>

      <div class="content-area">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const handleLogout = () => {
  store.logout()
  router.push('/login')
}

const pageTitle = computed(() => {
  const pathMap: Record<string, string> = {
    '/admin': '首页',
    '/admin/students': '学生管理',
    '/admin/teachers': '教师管理',
    '/admin/daily-forum': '日常论坛',
    '/admin/subject-forum': '学科论坛',
    '/admin/points': '积分概览',
  }
  return (route.meta?.title as string) || pathMap[route.path] || '管理员端'
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }
body { background: #f5f3f0; }
a { text-decoration: none; }
</style>

<style scoped>
.app-container { display: flex; min-height: 100vh; }

.sidebar {
  width: 260px;
  background: #8985cf;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0; top: 0; bottom: 0;
  z-index: 100;
}
.sidebar-header { padding: 24px 20px; border-bottom: 1px solid rgba(255,255,255,0.15); }
.logo { display: flex; align-items: center; gap: 12px; }
.logo-icon {
  width: 52px; height: 52px;
  background: rgba(255,255,255,0.25);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.logo-icon .system-icon { width: 52px; height: 52px; object-fit: cover; }
.logo-info { display: flex; flex-direction: column; }
.logo-title { font-size: 22px; font-weight: 700; color: #fff; letter-spacing: 0.5px; }

.sidebar-nav { flex: 1; padding: 20px 16px; overflow-y: auto; }
.nav-group { margin-bottom: 20px; }
.nav-title {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px; color: rgba(255,255,255,0.9);
  font-size: 14px; font-weight: 600;
  border-radius: 8px; background: rgba(255,255,255,0.1);
  margin-bottom: 6px;
}
.nav-title .nav-icon-img { width: 22px; height: 22px; }
.nav-items { padding-left: 8px; }

.nav-single {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 18px; margin-bottom: 10px;
  color: rgba(255,255,255,0.9); font-size: 16px; font-weight: 600;
  border-radius: 10px; background: rgba(255,255,255,0.15);
  transition: all 0.3s ease;
}
.nav-single:hover { background: rgba(255,255,255,0.25); color: #fff; }
.nav-single.active {
  background: rgba(255,255,255,0.3); color: #fff; position: relative;
}
.nav-single.active::before {
  content: ''; position: absolute; left: 0; top: 50%;
  transform: translateY(-50%);
  width: 4px; height: 24px; background: #fff;
  border-radius: 0 4px 4px 0;
}
.nav-icon-img { width: 22px; height: 22px; flex-shrink: 0; }

.nav-item {
  display: flex; align-items: center;
  padding: 10px 14px 10px 34px;
  color: rgba(255,255,255,0.75); font-size: 13px; font-weight: 500;
  border-radius: 8px; transition: all 0.3s ease; cursor: pointer; position: relative;
}
.nav-item:hover { background: rgba(255,255,255,0.1); color: #fff; }
.nav-item.active { background: rgba(255,255,255,0.2); color: #fff; }
.nav-item.active::before {
  content: ''; position: absolute; left: 0; top: 50%;
  transform: translateY(-50%);
  width: 3px; height: 20px; background: #fff;
  border-radius: 0 3px 3px 0;
}

.sidebar-footer { padding: 16px 20px; border-top: 1px solid rgba(255,255,255,0.15); }
.user-card {
  display: flex; align-items: center; gap: 10px;
  padding: 10px; background: rgba(255,255,255,0.1);
  border-radius: 12px; color: #fff;
  transition: all 0.3s; flex-wrap: wrap;
}
.user-card:hover { background: rgba(255,255,255,0.2); }
.logout-btn { flex: 0 0 auto; background: rgba(255,255,255,0.3); border-color: rgba(255,255,255,0.3); color: #fff; }
.logout-btn:hover { background: rgba(255,255,255,0.4); border-color: rgba(255,255,255,0.4); }
.user-avatar {
  width: 36px; height: 36px;
  background: rgba(255,255,255,0.3); border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600;
}
.user-info { flex: 1; display: flex; flex-direction: column; }
.user-name { font-size: 13px; font-weight: 600; }
.user-role { font-size: 11px; color: rgba(255,255,255,0.6); }

.main-wrapper { flex: 1; margin-left: 260px; display: flex; flex-direction: column; min-height: 100vh; }

.topbar {
  height: 70px; background: #fff; border-bottom: 1px solid #f0ebe3;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 28px; position: sticky; top: 0; z-index: 50;
}
.topbar-left { display: flex; flex-direction: column; }
.page-title { font-size: 20px; font-weight: 700; color: #333; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #999; margin-top: 2px; }
.breadcrumb .current { color: #8985cf; }
.separator { color: #ccc; }

.topbar-right { display: flex; align-items: center; gap: 12px; }
.search-bar {
  display: flex; align-items: center; gap: 8px;
  background: #f7f3e5; padding: 8px 16px; border-radius: 22px;
  transition: all 0.3s;
}
.search-bar:focus-within { background: #fff; box-shadow: 0 0 0 2px #acb6f3; }
.search-bar input {
  border: none; background: transparent; outline: none;
  width: 140px; font-size: 13px; color: #333;
}
.search-bar input::placeholder { color: #acb6f3; }
.icon-btn {
  width: 40px; height: 40px;
  background: #f7f3e5; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; position: relative; transition: all 0.3s;
}
.icon-btn:hover { background: #acb6f3; }
.bell-icon { font-size: 18px; }
.dot {
  position: absolute; top: 8px; right: 8px;
  width: 8px; height: 8px; background: #f48d45; border-radius: 50%;
}
.user-badge { font-size: 14px; color: #333; font-weight: 500; }
.user-badge-name { color: #8985cf; }

.notification-panel { padding: 0; }
.notif-header {
  display: flex; justify-content: space-between;
  padding: 12px 16px; border-bottom: 1px solid #f0ebe3;
  font-size: 14px; font-weight: 600; color: #333;
}
.mark { font-size: 12px; color: #acb6f3; cursor: pointer; }
.notif-item {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 14px 16px; border-bottom: 1px solid #f0ebe3;
  cursor: pointer;
}
.notif-item:last-child { border-bottom: none; }
.notif-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}
.notif-icon.warning { background: #fff7e6; color: #faad14; }
.notif-icon.success { background: #e6fff4; color: #52c41a; }
.notif-content p { font-size: 13px; color: #333; margin-bottom: 4px; }
.notif-content span { font-size: 11px; color: #999; }

.content-area { flex: 1; padding: 24px 28px; }
</style>
