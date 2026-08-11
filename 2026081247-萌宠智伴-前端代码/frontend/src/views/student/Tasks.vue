<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { studentApi } from '../../api/student'

interface Task {
  id: number; title: string; description: string; points: number
  completed: boolean; category: string; deadline: string; teacher: string
}

const dailyTasks = ref<Task[]>([])
const weeklyTasks = ref<Task[]>([])

const filterCategory = ref('全部')
const categories = ['全部', '语文', '数学', '英语', '科学', '体育', '美术', '阅读']

const filteredTasks = computed(() => {
  if (filterCategory.value === '全部') return dailyTasks.value
  return dailyTasks.value.filter(task => task.category === filterCategory.value)
})


const getCategoryIcon = (category: string) => {
  const icons: Record<string, string> = {
    '语文': '/images/Student_Icons/Chinese.jpg', '数学': '/images/Student_Icons/Math.jpg', '英语': '/images/Student_Icons/English.jpg',
    '科学': '/images/Student_Icons/Science.jpg', '体育': '/images/Student_Icons/PE.jpg', '美术': '/images/Student_Icons/Art.jpg', '阅读': '/images/Student_Icons/read.jpg'
  }
  return icons[category] || '/images/Student_Icons/TaskMaster.jpg'
}

const toggleTask = async (task: Task) => {
  const previous = task.completed
  // 乐观更新，提升交互流畅度
  task.completed = !task.completed
  try {
    await studentApi.updateTask(task.id, { completed: task.completed })
  } catch (e) {
    // 接口失败时回滚状态（错误提示由全局拦截器处理）
    task.completed = previous
  }
}

onMounted(async () => {
  try {
    const data: any = await studentApi.getTasks()
    if (data) {
      if (Array.isArray(data.dailyTasks)) dailyTasks.value = data.dailyTasks
      if (Array.isArray(data.weeklyTasks)) weeklyTasks.value = data.weeklyTasks
    }
  } catch (e) {
    // API 失败时保持页面可用
  }
})
</script>

<template>
<div class="daily-task-page">
  <div class="header-section">
    <p class="task-count">今日老师共发布了 {{ dailyTasks.length }} 个任务</p>
    <div class="filter-section">
      <button v-for="cat in categories" :key="cat" :class="{ active: filterCategory === cat }" @click="filterCategory = cat" class="filter-btn">{{ cat }}</button>
    </div>
  </div>

  <div class="tasks-section">
    <h2>老师发布的任务</h2>
    <div class="tasks-list">
      <div v-for="task in filteredTasks" :key="task.id" class="task-card" :class="{ completed: task.completed }" @click="toggleTask(task)">
        <div class="task-category">
          <img class="task-category-icon" :src="getCategoryIcon(task.category)" />
        </div>
        <div class="task-info">
          <h3 class="task-title">{{ task.title }}</h3>
          <p class="task-description">{{ task.description }}</p>
        </div>
        <div class="task-right">
          <span class="task-teacher">{{ task.teacher }}</span>
          <span class="task-points-value">+{{ task.points }}积分</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Weekly Tasks -->
  <div class="tasks-section weekly">
    <h2>本周任务</h2>
    <div class="tasks-list">
      <div v-for="task in weeklyTasks" :key="task.id" class="task-card" :class="{ completed: task.completed }" @click="toggleTask(task)">
        <div class="task-category">
          <img class="task-category-icon" :src="getCategoryIcon(task.category)" />
        </div>
        <div class="task-info">
          <h3 class="task-title">{{ task.title }}</h3>
          <p class="task-description">{{ task.description }}</p>
        </div>
        <div class="task-right">
          <span class="task-teacher">{{ task.teacher }}</span>
          <span class="task-points-value">+{{ task.points }}积分</span>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.daily-task-page { padding: 12px; max-width: 1000px; margin: 0 auto; }
.header-section { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 15px; }
.task-count { font-size: 16px; color: #333; font-weight: bold; padding: 10px 15px; background: rgba(255, 250, 235, 0.98); border-radius: 8px; }
.filter-section { display: flex; gap: 10px; flex-wrap: wrap; }
.filter-btn { padding: 10px 20px; background: rgba(255, 250, 235, 0.98); border: 2px solid #e0e0e0; border-radius: 25px; font-size: 14px; color: #666; cursor: pointer; transition: all 0.3s ease; }
.filter-btn:hover { border-color: #8985cf; color: #8985cf; }
.filter-btn.active { background: #8985cf; border-color: #8985cf; color: white; }
.tasks-section { background: rgba(255, 250, 235, 0.98); border-radius: 5px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); }
.tasks-section h2 { color: #8985cf; margin-bottom: 20px; font-size: 18px; }
.tasks-list { display: flex; flex-direction: column; gap: 15px; }
.task-card { display: flex; align-items: center; justify-content: space-between; gap: 15px; padding: 12px 20px; background: white; border-radius: 5px; transition: all 0.3s ease; border: 2px solid #f0f0f0; cursor: pointer; }
.task-card:hover { border-color: #ffb74d; }
.task-card.completed { opacity: 0.7; background: #e8f5e9; }
.task-card.completed .task-title { text-decoration: line-through; color: #999; }
.task-category-icon { width: 90px; height: 90px; object-fit: cover; flex-shrink: 0; }
.task-info { flex: 1; margin: 5px 0; }
.task-title { font-size: 14px; color: #333; font-weight: bold; }
.task-description { font-size: 12px; color: #666; margin: 3px 0; }
.task-right { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.task-teacher { font-size: 11px; color: #4caf50; }
.task-points-value { font-size: 13px; color: #ff9800; font-weight: 500; }
</style>
