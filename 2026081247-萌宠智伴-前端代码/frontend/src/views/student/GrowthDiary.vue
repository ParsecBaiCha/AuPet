<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'
import { studentApi } from '../../api/student'

const userStore = useUserStore()

interface MoodEntry { date: string; mood: string; note: string }
const moodEntries = ref<Record<string, MoodEntry>>({})

interface Goal { id: number; title: string; completed: boolean; deadline: string }
const goals = ref<Goal[]>([])

interface Achievement { id: number; title: string; icon: string; description: string; unlocked: boolean }
const achievements = ref<Achievement[]>([])

const pointHistory = ref([
  { date: '', points: 0 },
])

const selectedDate = ref(new Date().toISOString().split('T')[0] || '')
const newNote = ref('')
const newGoal = ref('')
const currentMood = ref('/images/Mood_Diary/happy.jpg')

const moodList = [
  { emoji: '/images/Mood_Diary/happy.jpg', name: '开心' }, { emoji: '/images/Mood_Diary/relax.jpg', name: '愉快' },
  { emoji: '/images/Mood_Diary/puzzled.jpg', name: '一般' }, { emoji: '/images/Mood_Diary/sad.jpg', name: '难过' },
  { emoji: '/images/Mood_Diary/angry.jpg', name: '生气' }, { emoji: '/images/Mood_Diary/shock.jpg', name: '困倦' },
]

const weekDays = computed(() => {
  const days = []
  const today = new Date()
  const weekDayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    const dateStr = date.toISOString().split('T')[0] || ''
    days.push({ date: dateStr, day: date.getDate(), weekDay: weekDayNames[date.getDay()] || '周一', entry: moodEntries.value[dateStr] || null })
  }
  return days
})

const getMoodEmoji = (day: any) => day.entry?.mood || '/images/Mood_Diary/happy.jpg'

const getMoodBg = (day: any) => {
  if (!day.entry) return 'rgba(255, 250, 235, 0.3)'
  const moodColors: Record<string, string> = {
    '/images/Mood_Diary/happy.jpg': 'rgba(76, 175, 80, 0.2)', '/images/Mood_Diary/relax.jpg': 'rgba(33, 150, 243, 0.2)',
    '/images/Mood_Diary/puzzled.jpg': 'rgba(158, 158, 158, 0.2)', '/images/Mood_Diary/sad.jpg': 'rgba(244, 67, 54, 0.2)'
  }
  return moodColors[day.entry.mood] || 'rgba(255, 250, 235, 0.3)'
}

const maxPoints = computed(() => Math.max(...pointHistory.value.map(p => p.points), 100))

const addNote = async () => {
  if (!newNote.value.trim()) return
  const date = selectedDate.value
  const mood = currentMood.value
  const noteText = newNote.value
  const entry = moodEntries.value[date] || { date, mood, note: '' }
  entry.note = noteText
  entry.mood = mood
  moodEntries.value[date] = entry
  newNote.value = ''
  try {
    await studentApi.recordEmotion({ date, mood, note: noteText })
  } catch (e) {
    // 失败保持本地已更新状态，不阻塞用户
  }
}

const setMood = (mood: string) => {
  currentMood.value = mood
  const date = selectedDate.value
  const entry = moodEntries.value[date] || { date, mood: '/images/Mood_Diary/happy.jpg', note: '' }
  entry.mood = mood
  moodEntries.value[date] = entry
  // 记录心情到后端（失败不影响本地体验）
  studentApi.recordEmotion({ date, mood }).catch(() => {})
}

const addGoal = () => {
  if (!newGoal.value.trim()) return
  const deadline = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] || ''
  goals.value.push({ id: Date.now(), title: newGoal.value, completed: false, deadline })
  newGoal.value = ''
}

const toggleGoal = (goal: Goal) => { goal.completed = !goal.completed }

onMounted(async () => {
  try {
    const data: any = await studentApi.getDiaries()
    if (data) {
      if (data.moodEntries) moodEntries.value = data.moodEntries
      if (Array.isArray(data.goals)) goals.value = data.goals
      if (Array.isArray(data.achievements)) achievements.value = data.achievements
      if (Array.isArray(data.pointHistory)) pointHistory.value = data.pointHistory
    }
  } catch (e) {
    // API 失败时保持页面可用
  }
})
</script>

<template>
<div class="diary-page">
  <div class="content-grid">
    <!-- Week Mood -->
    <div class="week-mood-section">
      <div class="section-header"><h3>近一周心情</h3></div>
      <div class="week-mood-cards">
        <div v-for="day in weekDays" :key="day.date" class="mood-card" :class="{ 'has-entry': day.entry, 'selected': day.date === selectedDate }" :style="{ background: getMoodBg(day) }" @click="selectedDate = day.date || selectedDate">
          <div class="mood-date">
            <span class="week-day">{{ day.weekDay }}</span>
            <span class="day-num">{{ day.day }}</span>
          </div>
          <img class="mood-img" :src="getMoodEmoji(day)" />
          <div class="mood-note" v-if="day.entry">{{ day.entry.note.substring(0, 15) }}{{ day.entry.note.length > 15 ? '...' : '' }}</div>
        </div>
      </div>
    </div>

    <!-- Diary -->
    <div class="diary-section">
      <div class="section-header"><h3>日记内容 - {{ selectedDate }}</h3></div>
      <div class="diary-content">
        <div class="mood-selector">
          <span class="mood-label">选择心情：</span>
          <div class="mood-options">
            <button v-for="mood in moodList" :key="mood.emoji" class="mood-btn" :class="{ active: currentMood === mood.emoji }" @click="setMood(mood.emoji)">
              <img class="mood-icon" :src="mood.emoji" :alt="mood.name" />
            </button>
          </div>
        </div>
        <div class="diary-note" v-if="moodEntries[selectedDate]?.note"><p>{{ moodEntries[selectedDate]?.note }}</p></div>
        <div class="add-note">
          <input v-model="newNote" placeholder="写下今天的心情..." @keyup.enter="addNote" />
          <button @click="addNote">添加</button>
        </div>
      </div>
    </div>

    <!-- Goals -->
    <div class="goals-section">
      <div class="section-header"><h3>我的目标</h3></div>
      <div class="goals-list">
        <div v-for="goal in goals" :key="goal.id" class="goal-item" :class="{ completed: goal.completed }" @click="toggleGoal(goal)">
          <div class="goal-checkbox"><span v-if="goal.completed">✓</span></div>
          <div class="goal-info">
            <span class="goal-title">{{ goal.title }}</span>
            <span class="goal-deadline">截止: {{ goal.deadline }}</span>
          </div>
        </div>
        <div class="add-goal">
          <input v-model="newGoal" placeholder="添加新目标..." @keyup.enter="addGoal" />
          <button @click="addGoal">+</button>
        </div>
      </div>
    </div>

    <!-- Achievements -->
    <div class="achievements-section">
      <div class="section-header"><h3>成就墙</h3></div>
      <div class="achievements-grid">
        <div v-for="achievement in achievements" :key="achievement.id" class="achievement-card" :class="{ locked: !achievement.unlocked }">
          <img class="achievement-icon" :src="achievement.icon" />
          <div class="achievement-info">
            <h4>{{ achievement.title }}</h4>
            <p>{{ achievement.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Points Chart -->
    <div class="chart-section">
      <div class="section-header"><h3>积分明细</h3></div>
      <div class="chart-container">
        <div class="y-axis">
          <span v-for="i in 5" :key="i">{{ Math.round(maxPoints / 5 * (6 - i)) }}</span>
        </div>
        <div class="chart-area">
          <div class="chart-grid">
            <div v-for="i in 5" :key="i" class="grid-line"></div>
          </div>
          <div class="chart-bars">
            <div v-for="(item, index) in pointHistory" :key="index" class="bar-container">
              <div class="bar" :style="{ height: (item.points / maxPoints * 100) + '%' }">
                <span class="bar-value">{{ item.points }}</span>
              </div>
              <span class="bar-label">{{ item.date.split('-')[2] }}日</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.diary-page { padding: 12px; }
.content-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.week-mood-section { grid-column: span 2; background: rgba(255, 250, 235, 0.98); border-radius: 15px; padding: 25px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); }
.section-header { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid white; }
.section-header h3 { color: #ffb74d; font-size: 18px; }
.week-mood-cards { display: grid; grid-template-columns: repeat(7, 1fr); gap: 15px; }
.mood-card { border-radius: 15px; padding: 20px 15px; text-align: center; cursor: pointer; transition: all 0.3s ease; border: 2px solid transparent; display: flex; flex-direction: column; align-items: center; gap: 10px; }
.mood-card:hover { transform: translateY(-5px); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); }
.mood-card.selected { border-color: #ffb74d; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12); }
.mood-date { display: flex; flex-direction: column; gap: 3px; }
.week-day { font-size: 12px; color: #666; }
.day-num { font-size: 24px; font-weight: bold; color: #333; }
.mood-img { width: 40px; height: 40px; object-fit: contain; }
.mood-note { font-size: 11px; color: #666; line-height: 1.4; }
.diary-section, .goals-section, .achievements-section, .chart-section { background: rgba(255, 250, 235, 0.98); border-radius: 5px; padding: 25px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); }
.mood-selector { margin-bottom: 15px; }
.mood-label { font-size: 14px; color: #666; display: block; margin-bottom: 10px; }
.mood-options { display: flex; gap: 10px; flex-wrap: wrap; }
.mood-btn { width: 50px; height: 50px; border: 2px solid #e0e0e0; border-radius: 5px; background: white; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; padding: 5px; }
.mood-icon { width: 36px; height: 36px; object-fit: contain; }
.mood-btn:hover { transform: scale(1.1); border-color: #ffb74d; }
.mood-btn.active { border-color: #ffb74d; background: rgba(137, 133, 207, 0.1); box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1); }
.diary-note { background: white; padding: 15px; border-radius: 5px; margin-bottom: 15px; }
.diary-note p { color: #333; font-size: 14px; line-height: 1.6; }
.add-note, .add-goal { display: flex; gap: 10px; }
.add-note input, .add-goal input { flex: 1; padding: 10px 15px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 14px; }
.add-note button, .add-goal button { padding: 10px 20px; background: #ffb74d; color: white; border: none; border-radius: 5px; cursor: pointer; }
.goals-list { display: flex; flex-direction: column; gap: 10px; }
.goal-item { display: flex; align-items: center; gap: 15px; padding: 15px; background: white; border-radius: 5px; cursor: pointer; transition: all 0.3s ease; }
.goal-item.completed { opacity: 0.6; }
.goal-item.completed .goal-title { text-decoration: line-through; }
.goal-checkbox { width: 24px; height: 24px; border: 2px solid #ffb74d; border-radius: 5px; display: flex; align-items: center; justify-content: center; font-size: 14px; color: #ffb74d; }
.goal-item.completed .goal-checkbox { background: #ffb74d; color: white; }
.goal-info { flex: 1; display: flex; align-items: center; justify-content: space-between; }
.goal-title { font-size: 14px; color: #333; }
.goal-deadline { font-size: 12px; color: #999; }
.achievements-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
.achievement-card { display: flex; align-items: center; gap: 15px; padding: 15px; background: #ffb74d; border-radius: 5px; color: white; transition: all 0.3s ease; }
.achievement-card.locked { background: #e0e0e0; opacity: 0.6; }
.achievement-icon { width: 50px; height: 50px; object-fit: contain; border-radius: 8px; }
.achievement-info h4 { font-size: 16px; margin-bottom: 5px; font-weight: bold; }
.achievement-info p { font-size: 12px; opacity: 0.8; }
.chart-container { display: flex; gap: 10px; height: 200px; }
.y-axis { display: flex; flex-direction: column; justify-content: space-between; align-items: flex-end; font-size: 11px; color: #999; padding-right: 10px; }
.chart-area { flex: 1; position: relative; background: white; border-radius: 5px; padding: 10px; }
.chart-grid { position: absolute; top: 10px; left: 10px; right: 10px; bottom: 30px; display: flex; flex-direction: column; justify-content: space-between; }
.grid-line { border-bottom: 1px dashed #e0e0e0; }
.chart-bars { position: absolute; top: 10px; left: 10px; right: 10px; bottom: 30px; display: flex; justify-content: space-around; align-items: flex-end; }
.bar-container { display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.bar { width: 30px; background: linear-gradient(180deg, #ffb74d 0%, #ff9800 100%); border-radius: 5px 5px 0 0; position: relative; transition: height 0.5s ease; min-height: 20px; }
.bar-value { position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: 11px; font-weight: bold; color: #ffb74d; }
.bar-label { font-size: 11px; color: #666; margin-top: 5px; }
@media (max-width: 900px) { .content-grid { grid-template-columns: 1fr; } .week-mood-section { grid-column: span 1; } .week-mood-cards { grid-template-columns: repeat(4, 1fr); } .achievements-grid { grid-template-columns: 1fr; } }
</style>
