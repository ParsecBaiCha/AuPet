<template>
  <div class="register-page">
    <div class="register-left">
      <div class="register-form-box">
        <div class="form-header">
          <h1>注册账号</h1>
          <p>加入宠物养成系统，开启成长之旅</p>
        </div>

        <div class="form-content">
          <div class="input-group">
            <label>用户名</label>
            <input
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
            />
          </div>

          <div class="input-group">
            <label>姓名</label>
            <input
              v-model="form.name"
              type="text"
              placeholder="请输入真实姓名"
            />
          </div>

          <div class="input-group">
            <label>身份</label>
            <div class="role-options">
              <label v-for="role in roles" :key="role.value" class="role-label">
                <input
                  type="radio"
                  v-model="form.role"
                  :value="role.value"
                  name="role"
                />
                <span>{{ role.label }}</span>
              </label>
            </div>
          </div>

          <div class="input-group">
            <label>密码</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
            />
          </div>

          <div class="input-group">
            <label>确认密码</label>
            <input
              v-model="form.confirmPassword"
              type="password"
              placeholder="请确认密码"
            />
          </div>

          <div class="input-group checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="parentConsent" />
              <span>我已阅读并同意学生心理健康检测相关说明，作业需要家长知情与授权</span>
            </label>
          </div>

          <button
            class="register-btn"
            :class="{ loading: loading }"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '立即注册' }}
          </button>

          <p class="login-link">
            已有账号？ <router-link to="/login">立即登录</router-link>
          </p>

          <p class="agreement-tip">
            点击注册，视为您同意我们的 <a href="#">使用条款</a> 与 <a href="#">隐私政策</a>。
          </p>
        </div>
      </div>
    </div>

    <div class="register-right"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '../../api/auth'

const router = useRouter()

const form = reactive({
  username: '',
  name: '',
  password: '',
  confirmPassword: '',
  role: 'student',
})
const parentConsent = ref(false)
const loading = ref(false)

const roles = [
  { label: '学生', value: 'student' },
  { label: '教师', value: 'teacher' },
  { label: '管理员', value: 'admin' },
]

async function handleRegister() {
  if (!form.username || !form.name || !form.password || !form.confirmPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (form.password !== form.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  if (!parentConsent.value) {
    ElMessage.warning('请先勾选"我已阅读并同意学生心理健康检测相关说明，作业需要家长知情与授权"')
    return
  }
  loading.value = true
  try {
    await authApi.register({
      username: form.username,
      name: form.name,
      password: form.password,
      role: form.role,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
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

.register-page {
  display: flex;
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: #0a0a0a;
  overflow: hidden;
}

.register-left {
  flex: 0.6;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #ffe0b2;
  height: 100vh;
}

.register-form-box {
  width: 100%;
  max-width: 360px;
}

.form-header {
  margin-bottom: 20px;
  text-align: left;
}

.form-header h1 {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 5px;
  color: #333;
}

.form-header p {
  font-size: 14px;
  color: #666;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.input-group label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.input-group input {
  width: 100%;
  padding: 10px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 10px;
  color: #333;
  font-size: 14px;
  transition: all 0.2s ease;
}

.input-group input:focus {
  outline: none;
  border-color: #ff8c00;
  box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.2);
}

.role-options {
  display: flex;
  gap: 20px;
}

.role-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.role-label input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.register-btn {
  width: 100%;
  padding: 12px;
  background: #ff8c00;
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.register-btn:hover:not(.loading) {
  background: #e6b800;
}

.register-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  color: #666;
  font-size: 13px;
}

.login-link a {
  color: #ff8c00;
  text-decoration: none;
  font-weight: 500;
}

.agreement-tip {
  text-align: center;
  font-size: 12px;
  color: #666;
}

.agreement-tip a {
  color: #ff8c00;
}

.checkbox-group {
  margin: 5px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #333;
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
}

.register-right {
  flex: 1.4;
  background-image: url('/images/login_register/1.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  height: 100vh;
}

@media (max-width: 900px) {
  .register-page {
    flex-direction: column;
  }
  .register-left {
    flex: 1;
  }
  .register-right {
    display: none;
  }
}
</style>
