<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import { studentApi } from '../../api/student'
import SeniorHome from './SeniorHome.vue'

const userStore = useUserStore()

interface ClassPet {
  id: number; studentName: string; petName: string; petImage: string
  points: number; level: string; progress: number
}

const classPets = ref<ClassPet[]>([])
const isSenior = computed(() => userStore.educationStage === 'senior')

const getLevelColor = (level: string) => {
  const colors: Record<string, string> = { 'S': '#f4bb6e', 'A': '#f48d45', 'B': '#8985cf', 'C': '#4caf50' }
  return colors[level] || '#999'
}

onMounted(async () => {
  try {
    const data: any = await studentApi.getDashboard()
    if (data) {
      // 填充全局学生/宠物信息（字段名适配映射在 store 内完成）
      userStore.applyDashboard(data)
      if (Array.isArray(data.classPets)) {
        classPets.value = data.classPets
      }
    }
  } catch (e) {
    // API 失败时保持页面可用，使用空数据
  }
})
</script>

<template>
<SeniorHome v-if="isSenior" :class-pets="classPets" />
<div v-else class="class-home">
  <!-- Dashboard header with user info -->
  <div class="dashboard">
    <div class="dashboard-left">
      <img class="avatar" :src="userStore.studentInfo.avatar" alt="avatar" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
      <div class="user-info">
        <span class="user-name">{{ userStore.studentInfo.name }}</span>
        <span class="class-name">{{ userStore.studentInfo.class }}</span>
      </div>
    </div>
    <div class="dashboard-center">
      <img class="pet-icon" :src="userStore.petInfo.type" alt="pet" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
      <div class="pet-info">
        <span class="pet-name">{{ userStore.petInfo.name }}</span>
      </div>
    </div>
  </div>

  <div class="pets-grid">
    <div v-for="pet in classPets" :key="pet.id" class="pet-card">
      <img class="pet-avatar" :src="pet.petImage" :alt="pet.petName" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
      <div class="pet-info">
        <span class="pet-name">{{ pet.petName }}</span>
        <span class="student-name">{{ pet.studentName }}</span>
      </div>
      <div class="pet-stats">
        <div class="stat-item">
          <span class="stat-label">积分</span>
          <span class="stat-value">{{ pet.points }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">等级</span>
          <span class="stat-value level" :style="{ color: getLevelColor(pet.level) }">{{ pet.level }}</span>
        </div>
      </div>
      <div class="progress-section">
        <div class="progress-label">任务完成度</div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: pet.progress + '%' }"></div>
        </div>
        <div class="progress-text">{{ pet.progress }}%</div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.class-home { padding: 12px; }
.dashboard { background: rgba(255, 250, 235, 0.98); border-radius: 12px; padding: 12px 20px; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.12); }
.dashboard-left { display: flex; align-items: center; gap: 15px; }
.dashboard-left .avatar { width: 60px; height: 60px; object-fit: cover; border-radius: 8px; }
.dashboard-left .user-info { display: flex; flex-direction: row; gap: 10px; }
.dashboard-left .user-name { font-size: 18px; font-weight: bold; color: #333; }
.dashboard-left .class-name { font-size: 14px; font-weight: 500; }
.dashboard-center { display: flex; align-items: center; gap: 15px; }
.dashboard-center .pet-icon { width: 50px; height: 50px; object-fit: contain; }
.dashboard-center .pet-info { display: flex; align-items: center; gap: 10px; }
.dashboard-center .pet-name { font-size: 18px; font-weight: bold; color: #f48d45; }
.pets-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
.pet-card { background: rgba(255, 250, 235, 0.98); border-radius: 8px; padding: 6px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); display: flex; flex-direction: column; }
.pet-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25); }
.pet-avatar { width: 90%; height: 200px; object-fit: contain; margin: 0 auto 4px; transition: all 0.3s ease; border-radius: 6px; background: #fff8dc; }
.pet-card:hover .pet-avatar { transform: scale(1.02); }
.pet-info { margin-bottom: 3px; display: flex; align-items: center; justify-content: center; gap: 4px; white-space: nowrap; }
.pet-name { font-size: 14px; color: #333; font-weight: bold; }
.student-name { color: #999; font-size: 11px; }
.pet-stats { display: flex; justify-content: space-around; margin-bottom: 4px; padding: 4px; background: #FFE4B5; border-radius: 4px; }
.stat-item { display: flex; flex-direction: column; gap: 1px; }
.stat-label { font-size: 8px; color: #999; }
.stat-value { font-size: 11px; font-weight: bold; color: #f48d45; }
.stat-value.level { font-size: 11px; }
.progress-section { margin-top: auto; }
.progress-label { font-size: 8px; color: #999; margin-bottom: 2px; }
.progress-bar { height: 4px; background: #e0e0e0; border-radius: 2px; overflow: hidden; margin-bottom: 2px; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #8985cf 0%, #acb6f3 100%); border-radius: 2px; transition: width 0.5s ease; }
.progress-text { font-size: 10px; font-weight: bold; color: #f48d45; }
@media (max-width: 1200px) { .pets-grid { grid-template-columns: repeat(4, 1fr); } }
@media (max-width: 900px) { .pets-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 600px) { .pets-grid { grid-template-columns: repeat(2, 1fr); } .pet-avatar { height: 110px; } }
</style>
