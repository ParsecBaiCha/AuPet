<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const activeTab = ref('profile')
const newPassword = ref('')
const confirmPassword = ref('')

const tabs = [
  { key: 'profile', label: '个人信息', icon: '/images/Student_Icons/personalinformation.svg' },
  { key: 'pet', label: '宠物信息', icon: '/images/Student_Icons/puppyinformation.svg' },
]

const avatarOptions = [
  '/images/avatars/dz.jpg', '/images/avatars/hx.jpg', '/images/avatars/jsj.jpg',
  '/images/avatars/kg.jpg', '/images/avatars/zw.jpg'
]
const petTypeOptions = [
  '/images/pets/dog1.jpg', '/images/pets/cat1.jpg', '/images/pets/bunny1.jpg',
  '/images/pets/squirrel1.jpg', '/images/pets/koala1.jpg', '/images/pets/hedgehog1.jpg',
  '/images/pets/pup1.jpg', '/images/pets/bird1.jpg', '/images/pets/bear1.jpg',
  '/images/pets/penguin1.jpg',
]
const genderOptions = ['男孩', '女孩']

const saveStudentInfo = () => {
  userStore.updateStudentInfo({
    name: userStore.studentInfo.name, avatar: userStore.studentInfo.avatar,
    class: userStore.studentInfo.class, email: userStore.studentInfo.email,
    phone: userStore.studentInfo.phone, bio: userStore.studentInfo.bio
  })
  alert('个人信息保存成功！')
}

const changePassword = () => {
  if (!newPassword.value || !confirmPassword.value) { alert('请填写完整密码信息'); return }
  if (newPassword.value !== confirmPassword.value) { alert('两次输入的密码不一致'); return }
  alert('密码修改成功！')
  newPassword.value = ''; confirmPassword.value = ''
}

const savePetInfo = () => {
  userStore.updatePetInfo({
    name: userStore.petInfo.name, type: userStore.petInfo.type,
    birthday: userStore.petInfo.birthday, gender: userStore.petInfo.gender, bio: userStore.petInfo.bio
  })
  alert('宠物信息保存成功！')
}
</script>

<template>
<div class="settings-page">
  <div class="settings-container">
    <div class="settings-tabs">
      <button v-for="tab in tabs" :key="tab.key" class="tab-btn" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
        <img class="tab-icon-img" :src="tab.icon" />
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>

    <div class="settings-content">
      <!-- Profile Tab -->
      <div v-if="activeTab === 'profile'" class="settings-panel">
        <h2>个人信息</h2>
        <div class="avatar-section">
          <img class="current-avatar" :src="userStore.studentInfo.avatar" alt="avatar" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
          <div class="avatar-options">
            <button v-for="avatar in avatarOptions" :key="avatar" class="avatar-btn" :class="{ selected: userStore.studentInfo.avatar === avatar }" @click="userStore.studentInfo.avatar = avatar">
              <img :src="avatar" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
            </button>
          </div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label>学生姓名</label><input v-model="userStore.studentInfo.name" type="text" /></div>
          <div class="form-group"><label>所在班级</label><input v-model="userStore.studentInfo.class" type="text" /></div>
          <div class="form-group"><label>邮箱</label><input v-model="userStore.studentInfo.email" type="email" /></div>
          <div class="form-group"><label>手机号</label><input v-model="userStore.studentInfo.phone" type="text" /></div>
        </div>
        <div class="form-group full-width"><label>个人简介</label><textarea v-model="userStore.studentInfo.bio" rows="3"></textarea></div>

        <div class="section-divider">
          <h3>修改密码</h3>
          <div class="form-group"><label>新密码</label><input v-model="newPassword" type="password" placeholder="请输入新密码" /></div>
          <div class="form-group"><label>确认密码</label><input v-model="confirmPassword" type="password" placeholder="请再次输入新密码" /></div>
          <button class="save-btn" @click="changePassword">修改密码</button>
        </div>

        <div class="section-divider">
          <div class="time-limit-row">
            <h3>每日使用时长限制（3小时）</h3>
          </div>
        </div>

        <button class="save-btn" @click="saveStudentInfo">保存信息</button>
      </div>

      <!-- Pet Tab -->
      <div v-if="activeTab === 'pet'" class="settings-panel">
        <h2>宠物信息</h2>
        <div class="pet-preview">
          <img class="pet-avatar" :src="userStore.petInfo.type" alt="pet" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
          <span class="pet-name">{{ userStore.petInfo.name }}</span>
        </div>
        <div class="avatar-section">
          <div class="section-label">选择宠物类型</div>
          <div class="avatar-options">
            <button v-for="type in petTypeOptions" :key="type" class="avatar-btn pet-type" :class="{ selected: userStore.petInfo.type === type }" @click="userStore.petInfo.type = type">
              <img :src="type" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
            </button>
          </div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label>宠物名字</label><input v-model="userStore.petInfo.name" type="text" /></div>
          <div class="form-group"><label>宠物生日</label><input v-model="userStore.petInfo.birthday" type="date" /></div>
          <div class="form-group">
            <label>宠物性别</label>
            <div class="radio-group">
              <label class="radio-item" v-for="gender in genderOptions" :key="gender">
                <input type="radio" :value="gender" v-model="userStore.petInfo.gender" /><span>{{ gender }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="form-group full-width"><label>宠物简介</label><textarea v-model="userStore.petInfo.bio" rows="3"></textarea></div>
        <button class="save-btn" @click="savePetInfo">保存信息</button>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.settings-page { padding: 12px; }
.settings-container { display: flex; flex-direction: column; gap: 20px; }
.settings-tabs { background: rgba(255, 250, 235, 0.98); border-radius: 15px; padding: 15px 20px; display: flex; gap: 15px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); overflow-x: auto; }
.tab-btn { display: flex; align-items: center; gap: 10px; padding: 12px 24px; border: none; background: transparent; border-radius: 12px; cursor: pointer; transition: all 0.3s ease; flex-shrink: 0; font-size: 15px; color: #666; }
.tab-btn:hover { background: rgba(137, 133, 207, 0.1); color: #ffb74d; }
.tab-btn.active { background: #ffb74d; color: white; }
.tab-icon-img { width: 24px; height: 24px; object-fit: contain; }
.tab-label { font-size: 15px; font-weight: 500; }
.settings-content { flex: 1; background: rgba(255, 250, 235, 0.98); border-radius: 15px; padding: 30px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); }
.settings-panel h2 { color: #ffb74d; margin-bottom: 25px; font-size: 22px; }
.avatar-section { margin-bottom: 25px; display: flex; flex-direction: column; align-items: center; }
.current-avatar { width: 100px; height: 100px; object-fit: cover; border-radius: 50%; margin-bottom: 15px; border: 3px solid #ffb74d; }
.avatar-options { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; max-width: 520px; margin: 0 auto; }
.avatar-btn { width: 70px; height: 70px; border: 2px solid #e0e0e0; border-radius: 50%; background: white; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; padding: 0; }
.avatar-btn img { width: 100%; height: 100%; object-fit: cover; }
.avatar-btn.pet-type { width: 80px; height: 80px; border-radius: 10px; }
.avatar-btn:hover { border-color: #ffb74d; transform: scale(1.08); }
.avatar-btn.selected { border-color: #ffb74d; background: rgba(137, 133, 207, 0.1); box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1); }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group.full-width { grid-column: span 2; }
.form-group label { font-size: 14px; color: #333; font-weight: 500; }
.form-group input, .form-group textarea { padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 14px; transition: all 0.3s ease; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: #ffb74d; }
.radio-group { display: flex; gap: 20px; }
.radio-item { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.radio-item input { width: 18px; height: 18px; }
.save-btn { width: 100%; padding: 12px; background: #ffb74d; color: white; border: none; border-radius: 12px; font-size: 15px; font-weight: 500; cursor: pointer; margin-top: 10px; }
.save-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2); }
.section-divider { margin-top: 25px; padding-top: 20px; border-top: 1px solid #eee; }
.section-divider h3 { font-size: 16px; color: #333; margin-bottom: 15px; }
.time-limit-row { display: flex; align-items: center; justify-content: space-between; }
.pet-preview { display: flex; flex-direction: column; align-items: center; margin-bottom: 25px; padding: 25px; background: rgba(255, 183, 77, 0.1); border-radius: 15px; }
.pet-preview .pet-avatar { width: 100px; height: 100px; object-fit: contain; margin-bottom: 10px; }
.pet-name { font-size: 20px; color: #ffb74d; font-weight: bold; }
.section-label { font-size: 14px; color: #666; margin-bottom: 12px; font-weight: 500; }
@media (max-width: 768px) { .settings-tabs { flex-wrap: wrap; justify-content: center; } .form-grid { grid-template-columns: 1fr; } .form-group.full-width { grid-column: span 1; } }
</style>
