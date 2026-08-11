<template>
  <div class="login-page">
    <div class="login-left">
      <div class="login-form-box">
        <div class="form-header">
          <h1>登录您的账号</h1>
          <p>登录以继续使用宠物养成系统</p>
        </div>

        <div class="form-content">
          <div class="input-group">
            <label>用户名</label>
            <input
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="input-group">
            <label>密码</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="input-group checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="parentConsent" />
              <span>我已阅读并同意学生心理健康检测相关说明，作业需要家长知情与授权</span>
            </label>
          </div>

          <div class="button-group">
            <button
              class="login-btn"
              :class="{ loading: loading }"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登录' }}
            </button>

            <button
              class="register-btn"
              @click="goToRegister"
            >
              注册
            </button>
          </div>

          <p class="agreement-tip">
            点击继续，视为您同意我们的 <a href="#">使用条款</a> 与 <a href="#">隐私政策</a>。
          </p>
        </div>
      </div>
    </div>

    <div class="login-right"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '../../api/auth'
import { useAppStore } from '../../stores/app'

const router = useRouter()
const store = useAppStore()

const form = reactive({ username: '', password: '' })
const parentConsent = ref(false)
const loading = ref(false)

async function handleLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  if (!parentConsent.value) {
    ElMessage.warning('请先勾选"我已阅读并同意学生心理健康检测相关说明，作业需要家长知情与授权"')
    return
  }
  loading.value = true
  try {
    const res: any = await authApi.login(form)
    store.setToken(res.token)
    store.setUser(res.user)
    store.persist()
    ElMessage.success('登录成功')
    const role = res.user?.role || 'student'
    router.push(`/${role}`)
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}

function goToRegister() {
  router.push('/register')
}

</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.login-page {
  display: flex;
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: #0a0a0a;
  overflow: hidden;
}

.login-left {
  flex: 0.6;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #ffe0b2;
  height: 100vh;
}

.login-right {
  flex: 1.4;
  background-image: url('/images/login_register/1.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  height: 100vh;
}

.login-form-box {
  width: 100%;
  max-width: 360px;
}

.form-header {
  margin-bottom: 40px;
  text-align: left;
}

.form-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}

.form-header p {
  font-size: 16px;
  color: #666;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 15px;
  color: #333;
  font-weight: 500;
}

.input-group input {
  width: 100%;
  padding: 14px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 10px;
  color: #333;
  font-size: 16px;
  transition: all 0.2s ease;
}

.input-group input:focus {
  outline: none;
  border-color: #ff8c00;
  box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.2);
}

.button-group {
  display: flex;
  gap: 15px;
  margin-top: 8px;
  margin-bottom: 4px;
}

.login-btn {
  flex: 1;
  padding: 14px;
  background: #ff8c00;
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.register-btn {
  flex: 1;
  padding: 14px;
  background: white;
  border: 2px solid #ff8c00;
  border-radius: 10px;
  color: #ff8c00;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.register-btn:hover {
  background: #fff8e6;
}

.login-btn:hover:not(.loading) {
  background: #e6b800;
}

.login-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
}

.agreement-tip {
  font-size: 13px;
  color: #666;
  text-align: center;
}

.agreement-tip a {
  color: #ff8c00;
}

.checkbox-group {
  margin: 15px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #333;
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
}

@media (max-width: 768px) {
  .login-page {
    flex-direction: column;
  }
  .login-right {
    display: none;
  }
  .login-left {
    padding: 20px;
  }
}
</style>
