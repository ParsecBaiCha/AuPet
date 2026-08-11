<template>
  <div class="dashboard">
    <div class="welcome-banner">
      <div class="banner-content">
        <div class="banner-text">
          <h2>早上好，王小明老师</h2>
          <p>今天有 {{ stats.todayTask }} 个任务要完成，继续加油！</p>
        </div>
        <div class="banner-right">
          <div class="psychological-score">
            <span class="score-label">班级整体心理状态</span>
            <span class="score-value">良好</span>
          </div>
        </div>
      </div>
    </div>

    <div class="warning-banner" v-if="abnormalStudents.length > 0">
      <el-icon><WarningFilled /></el-icon>
      <span>发现 {{ abnormalStudents.length }} 名学生情绪异常，请及时关注</span>
      <el-button type="warning" link @click="$router.push('/intervention')">查看详情</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f48d45 0%, #f4bb6e 100%)">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.studentCount }}</div>
            <div class="stat-label">我的学生</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #acb6f3 0%, #8985cf 100%)">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.classCount }}</div>
            <div class="stat-label">负责班级</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f4bb6e 0%, #f48d45 100%)">
            <el-icon><ChatLineSquare /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.todayTask }}</div>
            <div class="stat-label">今日任务</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card warning-card" @click="$router.push('/intervention')">
          <div class="stat-icon" style="background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%)">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ abnormalStudents.length }}</div>
            <div class="stat-label">异常预警</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title"><el-icon><TrendCharts /></el-icon> 班级心理状态概览</h3>
          </div>
          <div class="psychological-overview">
            <div class="mood-chart">
              <div class="chart-item">
                <span class="chart-label">积极</span>
                <el-progress :percentage="65" :stroke-width="10" color="#52c41a" />
                <span class="chart-value">65%</span>
              </div>
              <div class="chart-item">
                <span class="chart-label">中性</span>
                <el-progress :percentage="25" :stroke-width="10" color="#f4bb6e" />
                <span class="chart-value">25%</span>
              </div>
              <div class="chart-item">
                <span class="chart-label">消极</span>
                <el-progress :percentage="10" :stroke-width="10" color="#ff7875" />
                <span class="chart-value">10%</span>
              </div>
            </div>
            <div class="trend-chart">
              <div class="trend-title">一周心理趋势</div>
              <div class="trend-chart-container">
                <svg class="trend-svg" viewBox="0 0 280 100" preserveAspectRatio="none">
                  <line x1="0" y1="25" x2="280" y2="25" class="grid-line" />
                  <line x1="0" y1="50" x2="280" y2="50" class="grid-line" />
                  <line x1="0" y1="75" x2="280" y2="75" class="grid-line" />
                  
                  <polyline
                    :points="trendLinePoints"
                    class="trend-line"
                    fill="none"
                  />
                  
                  <circle
                    v-for="(day, idx) in weekTrend"
                    :key="'dot-' + idx"
                    :cx="getDotX(idx)"
                    :cy="getDotY(day.value)"
                    r="4"
                    class="trend-dot"
                    :fill="day.color"
                  />
                </svg>
                <div class="bar-labels">
                  <span v-for="(day, idx) in weekTrend" :key="idx" class="bar-label">{{ day.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title"><el-icon><Coin /></el-icon> 积分与互动追踪</h3>
          </div>
          <div class="points-tracking">
            <div class="points-stats">
              <div class="points-item">
                <span class="points-num">+1280</span>
                <span class="points-label">本周加分</span>
              </div>
              <div class="points-item">
                <span class="points-num">-85</span>
                <span class="points-label">本周扣分</span>
              </div>
              <div class="points-item">
                <span class="points-num">156</span>
                <span class="points-label">互动次数</span>
              </div>
            </div>
            <div class="activity-list">
              <div class="activity-title">最近积分变动</div>
              <div class="activity-item" v-for="act in recentActivities" :key="act.name">
                <span class="act-name">{{ act.name }}</span>
                <span class="act-points" :class="act.points > 0 ? 'add' : 'sub'">{{ act.points > 0 ? '+' : '' }}{{ act.points }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="16">
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title">快捷入口</h3>
          </div>
          <div class="quick-links">
            <div class="quick-item" v-for="item in quickItems" :key="item.path" @click="$router.push(item.path)">
              <div class="quick-icon">
                <el-icon><component :is="item.icon" /></el-icon>
              </div>
              <span>{{ item.name }}</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title">今日日程</h3>
          </div>
          <div class="schedule-list">
            <div class="schedule-item" v-for="(item, index) in schedule" :key="index">
              <div class="schedule-time">{{ item.time }}</div>
              <div class="schedule-dot"></div>
              <div class="schedule-content">
                <div class="schedule-title">{{ item.title }}</div>
                <div class="schedule-desc">{{ item.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title">班级积分概览</h3>
            <el-button type="primary" link @click="$router.push('/student/list')">查看详情</el-button>
          </div>
          <div class="class-list">
            <div class="class-item" v-for="cls in classes" :key="cls.id">
              <div class="class-info">
                <span class="class-name">{{ cls.name }}</span>
                <span class="class-students">{{ cls.studentCount }}人</span>
              </div>
              <div class="class-progress">
                <el-progress :percentage="cls.attendence" :stroke-width="6" :show-text="false" />
              </div>
              <div class="class-points">
                <span class="points-value">{{ cls.totalPoints }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title">最近动态</h3>
          </div>
          <div class="activity-list1">
            <div class="activity-item" v-for="(item, index) in activities" :key="index">
              <el-avatar :size="32" :src="item.avatar" />
              <div class="activity-content">
                <div class="activity-text">
                  <span class="activity-author">{{ item.author }}</span>
                  {{ item.action }}
                </div>
                <div class="activity-time">{{ item.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted } from 'vue'
import { User, OfficeBuilding, ChatLineSquare, WarningFilled, TrendCharts, Coin, DataAnalysis, DataLine, ChatDotSquare, Setting } from '@element-plus/icons-vue'
import { teacherApi } from '../../api/teacher'

const stats = reactive({
  studentCount: 0,
  classCount: 0,
  todayTask: 0,
  noticeCount: 0
})

const abnormalStudents = reactive<any[]>([])

const weekTrend = reactive<any[]>([])

const recentActivities = reactive<any[]>([])

const getTrendColor = (value: number) => {
  if (value >= 80) return '#52c41a'
  if (value >= 60) return '#f4bb6e'
  return '#ff7875'
}

const getDotX = (idx: number) => 20 + idx * 40
const getDotY = (value: number) => 100 - value

const trendLinePoints = computed(() => {
  return weekTrend.map((day, idx) => `${getDotX(idx)},${getDotY(day.value)}`).join(' ')
})

const quickItems = [
  { name: '积分管理', icon: User, path: '/student/list' },
  { name: '班级管理', icon: OfficeBuilding, path: '/student/class' },
  { name: '干预管理', icon: WarningFilled, path: '/intervention' },
  { name: '群体智能角色管理', icon: DataAnalysis, path: '/simulate' },
  { name: '群体趋势预测', icon: DataLine, path: '/predict' },
  { name: '交流论坛', icon: ChatDotSquare, path: '/forum' },
  { name: '个人中心', icon: Setting, path: '/profile' }
]

const schedule = reactive<any[]>([])

const classes = reactive<any[]>([])

const activities = reactive<any[]>([])

const loadDashboard = async () => {
  try {
    const data: any = await teacherApi.getDashboard()
    if (data.stats) Object.assign(stats, data.stats)
    if (Array.isArray(data.abnormalStudents)) {
      abnormalStudents.splice(0, abnormalStudents.length, ...data.abnormalStudents)
    }
    if (Array.isArray(data.weekTrend)) {
      const trend = data.weekTrend.map((d: any) => ({ ...d, color: getTrendColor(d.value) }))
      weekTrend.splice(0, weekTrend.length, ...trend)
    }
    if (Array.isArray(data.recentActivities)) {
      recentActivities.splice(0, recentActivities.length, ...data.recentActivities)
    }
    if (Array.isArray(data.schedule)) {
      schedule.splice(0, schedule.length, ...data.schedule)
    }
    if (Array.isArray(data.classes)) {
      classes.splice(0, classes.length, ...data.classes)
    }
    if (Array.isArray(data.activities)) {
      activities.splice(0, activities.length, ...data.activities)
    }
  } catch (e) {
    // 接口失败时保持页面可用，使用默认空值
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard { padding: 0; }

.welcome-banner {
  background: linear-gradient(135deg, #f48d45 0%, #f4bb6e 100%);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(244, 141, 69, 0.3);
}

.banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.banner-text h2 { margin: 0 0 4px 0; font-size: 20px; font-weight: 600; color: #fff; }
.banner-text p { margin: 0; font-size: 13px; color: rgba(255,255,255,0.9); }

.psychological-score {
  background: rgba(255,255,255,0.2);
  padding: 8px 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-label { font-size: 12px; color: rgba(255,255,255,0.9); }
.score-value { font-size: 16px; font-weight: 600; color: #fff; }

.warning-banner {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ff4d4f;
  font-size: 14px;
}

.warning-banner .el-icon { color: #ff4d4f; }

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid #E8E0F0;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: 700; color: #333; }
.stat-label { font-size: 12px; color: #999; margin-top: 2px; }

.stat-card.warning-card { cursor: pointer; transition: transform 0.2s; }
.stat-card.warning-card:hover { transform: translateY(-2px); }

.content-card { background: #fff; border-radius: 10px; border: 1px solid #E8E0F0; height: 269px; box-sizing: border-box; }

.psychological-overview {
  padding: 16px;
  display: flex;
  gap: 24px;
}

.mood-chart { flex: 1; }
.chart-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.chart-label { width: 40px; font-size: 13px; color: #666; }
.chart-item .el-progress { flex: 1; }
.chart-value { width: 36px; font-size: 13px; color: #333; font-weight: 500; text-align: right; }

.trend-chart { flex: 1; border-left: 1px solid #f0f0f0; padding-left: 24px; }
.trend-title { font-size: 13px; color: #999; margin-bottom: 12px; }
.trend-chart-container {
  height: 100px;
  position: relative;
}

.trend-svg {
  width: 100%;
  height: 85px;
}

.grid-line {
  stroke: #f0f0f0;
  stroke-width: 1;
}

.trend-line {
  stroke: #8985cf;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.trend-dot {
  stroke: #fff;
  stroke-width: 2;
}

.bar-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
}

.bar-label { font-size: 12px; color: #999; }

.points-tracking { padding: 16px; }
.points-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.points-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.points-num {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.points-label { font-size: 12px; color: #999; }

.activity-list { font-size: 13px; max-height: 120px; overflow-y: auto; }
.activity-list1 { font-size: 13px; max-height: 100%; overflow-y: auto; }
.activity-title { color: #999; margin-bottom: 8px; }
.activity-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #f5f5f5;
}

.act-points.add { color: #52c41a; }
.act-points.sub { color: #ff4d4f; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #E8E0F0;
}

.card-title { margin: 0; font-size: 14px; font-weight: 600; color: #333; }

.quick-links { display: flex; flex-wrap: wrap; padding: 16px; gap: 12px; height: 160px; box-sizing: border-box; }

.quick-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 8px;
  background: #fafafa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  height: 100%;
}

.quick-item:hover { background: #F5F3FF; }
.quick-icon { width: 36px; height: 36px; border-radius: 8px; background: #F5F3FF; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #f48d45; }
.quick-item span { font-size: 12px; color: #555; }

.schedule-list { padding: 8px 16px; }

.schedule-item { display: flex; align-items: flex-start; gap: 10px; padding: 8px 0; position: relative; }

.schedule-item:not(:last-child)::after {
  content: ''; position: absolute; left: 38px; top: 28px; bottom: -8px; width: 2px; background: #E8E0F0;
}

.schedule-time { font-size: 12px; font-weight: 500; color: #f48d45; min-width: 38px; }
.schedule-dot { width: 8px; height: 8px; border-radius: 50%; background: #f48d45; margin-top: 4px; flex-shrink: 0; }
.schedule-content { flex: 1; }
.schedule-title { font-size: 13px; font-weight: 500; color: #333; }
.schedule-desc { font-size: 11px; color: #999; margin-top: 2px; }

.class-list { padding: 8px 16px; }

.class-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.class-item:last-child { border-bottom: none; }
.class-info { width: 100px; }
.class-name { display: block; font-size: 13px; font-weight: 500; color: #333; }
.class-students { font-size: 11px; color: #999; }
.class-progress { flex: 1; }
.class-points { text-align: right; min-width: 60px; }
.points-value { font-size: 16px; font-weight: 600; color: #f48d45; }

.activity-list { padding: 8px 16px; }

.activity-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; }
.activity-content { flex: 1; }
.activity-text { font-size: 12px; color: #555; }
.activity-author { font-weight: 500; color: #333; }
.activity-time { font-size: 11px; color: #999; margin-top: 2px; }
</style>
