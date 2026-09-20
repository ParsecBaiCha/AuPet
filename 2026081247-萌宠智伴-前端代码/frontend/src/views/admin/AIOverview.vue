<template>
  <div class="ai-overview">
    <!-- 时间范围 -->
    <el-card class="toolbar-card" shadow="never">
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="toolbar-label">时间范围</span>
          <el-radio-group v-model="days" @change="loadOverview">
            <el-radio-button :value="7">近 7 天</el-radio-button>
            <el-radio-button :value="30">近 30 天</el-radio-button>
            <el-radio-button :value="90">近 90 天</el-radio-button>
          </el-radio-group>
        </div>
        <el-button text type="primary" :loading="loading" @click="loadOverview">刷新</el-button>
      </div>
    </el-card>

    <el-alert
      v-if="!loading && !hasTrendData"
      class="empty-alert"
      type="info"
      :closable="false"
      show-icon
      title="所选时间范围内还没有 AI 研习记录"
      description="学生开始 AI 学习、测验或对话后，这里会显示相应的统计数据。"
    />

    <!-- 指标卡片 -->
    <div class="kpi-grid" v-loading="loading">
      <el-card v-for="card in kpiCards" :key="card.label" class="kpi-card" shadow="hover">
        <div class="kpi-label">{{ card.label }}</div>
        <div class="kpi-value" :class="card.theme">{{ card.value }}</div>
        <div class="kpi-extra">{{ card.extra }}</div>
      </el-card>
    </div>

    <!-- 使用趋势（纯 CSS 柱状条） -->
    <el-card class="trend-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>近 {{ days }} 天使用趋势</span>
          <span class="card-sub">单位：学习人次</span>
        </div>
      </template>

      <template v-if="hasTrendData">
        <div class="trend-chart">
          <div
            v-for="item in trend"
            :key="item.date"
            class="trend-col"
            :title="`${item.date}：${item.visits} 人次`"
          >
            <span v-if="item.visits > 0 && days <= 30" class="trend-value">{{ item.visits }}</span>
            <div
              class="trend-bar"
              :class="{ 'trend-bar-peak': item.visits > 0 && item.visits === trendMax }"
              :style="{ height: barHeight(item.visits) }"
            ></div>
          </div>
        </div>
        <div class="trend-axis">
          <span>{{ trendStart }}</span>
          <span class="trend-axis-mid">{{ trendMaxText }}</span>
          <span>{{ trendEnd }}</span>
        </div>
      </template>
      <el-empty v-else description="当前时间范围内没有使用记录" :image-size="80" />
    </el-card>

    <!-- 按学段分布 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="card-header"><span>按学段分布</span></div>
      </template>
      <el-table :data="byGrade" v-loading="loading" border empty-text="暂无学段数据" style="width: 100%">
        <el-table-column label="学段" min-width="120">
          <template #default="{ row }">{{ gradeText(row.gradeLevel) }}</template>
        </el-table-column>
        <el-table-column label="学习人次" min-width="240">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="percentOf(row.visits, gradeMax.visits)"
                :stroke-width="12"
                color="#8985cf"
                :show-text="false"
              />
              <span class="progress-text">{{ row.visits }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="参与学生" min-width="240">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="percentOf(row.students, gradeMax.students)"
                :stroke-width="12"
                color="#f48d45"
                :show-text="false"
              />
              <span class="progress-text">{{ row.students }}</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 按班级排行 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>按班级排行</span>
          <span class="card-sub">学习人次前 8 名</span>
        </div>
      </template>
      <el-table :data="byClass" v-loading="loading" border empty-text="暂无班级数据" style="width: 100%">
        <el-table-column prop="className" label="班级" min-width="180" />
        <el-table-column prop="visits" label="学习人次" min-width="120" />
        <el-table-column prop="students" label="参与学生数" min-width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { adminApi } from '../../api/admin'

interface Kpis {
  visits: number
  students: number
  quizCount: number
  avgScore: number | null
  passRate: number | null
  chats: number
  flaggedChats: number
  books: number
}

interface GradeRow {
  gradeLevel: string
  visits: number
  students: number
}

interface ClassRow {
  classId: number
  className: string
  visits: number
  students: number
}

interface TrendPoint {
  date: string
  visits: number
}

const GRADE_TEXT: Record<string, string> = {
  lower_primary: '小学低年级',
  upper_primary: '小学高年级',
  middle_school: '初中',
  high_school: '高中'
}

const days = ref(30)
const loading = ref(false)

const emptyKpis = (): Kpis => ({
  visits: 0,
  students: 0,
  quizCount: 0,
  avgScore: null,
  passRate: null,
  chats: 0,
  flaggedChats: 0,
  books: 0
})

const kpis = ref<Kpis>(emptyKpis())
const courseTotal = ref(0)
const coursePublished = ref(0)
const pendingChats = ref(0)
const pendingMaterials = ref(0)
const byGrade = ref<GradeRow[]>([])
const byClass = ref<ClassRow[]>([])
const trend = ref<TrendPoint[]>([])

const toNumber = (value: unknown): number => {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

const toNumberOrNull = (value: unknown): number | null => {
  if (value === null || value === undefined || value === '') return null
  const n = Number(value)
  return Number.isFinite(n) ? n : null
}

const formatNumber = (value: number): string => (value || 0).toLocaleString('zh-CN')

const dashNumber = (value: number | null): string => (value === null ? '—' : formatNumber(value))

const percentText = (value: number | null): string => (value === null ? '—' : `${value}%`)

const gradeText = (value: string): string => GRADE_TEXT[value] || (value && value !== 'unknown' ? value : '未设置')

const kpiCards = computed(() => [
  {
    label: '学习人次',
    value: formatNumber(kpis.value.visits),
    extra: `近 ${days.value} 天累计`,
    theme: 'theme-purple'
  },
  {
    label: '参与学生',
    value: formatNumber(kpis.value.students),
    extra: '有 AI 研习记录的学生',
    theme: 'theme-purple'
  },
  {
    label: '测验次数',
    value: formatNumber(kpis.value.quizCount),
    extra: '完成 AI 测验的次数',
    theme: 'theme-purple'
  },
  {
    label: '测验平均分',
    value: dashNumber(kpis.value.avgScore),
    extra: `及格率 ${percentText(kpis.value.passRate)}`,
    theme: 'theme-orange'
  },
  {
    label: 'AI 对话条数',
    value: formatNumber(kpis.value.chats),
    extra: `命中关键词 ${formatNumber(kpis.value.flaggedChats)} 条`,
    theme: 'theme-purple'
  },
  {
    label: '绘本阅读',
    value: formatNumber(kpis.value.books),
    extra: '阅读绘本的页次',
    theme: 'theme-purple'
  },
  {
    label: '课程总数',
    value: formatNumber(courseTotal.value),
    extra: `已上架 ${formatNumber(coursePublished.value)} 门`,
    theme: 'theme-purple'
  },
  {
    label: '待审内容',
    value: formatNumber(pendingChats.value + pendingMaterials.value),
    extra: `对话 ${formatNumber(pendingChats.value)} / 资料 ${formatNumber(pendingMaterials.value)}`,
    theme: 'theme-orange'
  }
])

const trendMax = computed(() => trend.value.reduce((max, item) => Math.max(max, item.visits), 0))

const hasTrendData = computed(() => trend.value.length > 0 && trendMax.value > 0)

const barHeight = (visits: number): string => {
  if (!trendMax.value) return '2px'
  const percent = Math.round((visits / trendMax.value) * 100)
  return `${Math.max(visits > 0 ? 4 : 2, percent)}%`
}

const trendStart = computed(() => trend.value[0]?.date || '')
const trendEnd = computed(() => trend.value[trend.value.length - 1]?.date || '')
const trendMaxText = computed(() => (trendMax.value > 0 ? `峰值 ${trendMax.value} 人次` : ''))

const gradeMax = computed(() => ({
  visits: byGrade.value.reduce((max, item) => Math.max(max, item.visits), 0),
  students: byGrade.value.reduce((max, item) => Math.max(max, item.students), 0)
}))

const percentOf = (value: number, max: number): number => {
  if (!max || max <= 0) return 0
  return Math.min(100, Math.round((value / max) * 100))
}

const loadOverview = async () => {
  loading.value = true
  try {
    const res: any = await adminApi.getAIOverview({ days: days.value })
    const k = res?.kpis || {}
    kpis.value = {
      visits: toNumber(k.visits),
      students: toNumber(k.students),
      quizCount: toNumber(k.quizCount),
      avgScore: toNumberOrNull(k.avgScore),
      passRate: toNumberOrNull(k.passRate),
      chats: toNumber(k.chats),
      flaggedChats: toNumber(k.flaggedChats),
      books: toNumber(k.books)
    }
    courseTotal.value = toNumber(res?.courses?.total)
    coursePublished.value = toNumber(res?.courses?.published)
    pendingChats.value = toNumber(res?.pending?.chats)
    pendingMaterials.value = toNumber(res?.pending?.materials)
    byGrade.value = Array.isArray(res?.byGrade)
      ? res.byGrade.map((item: any) => ({
          gradeLevel: item?.gradeLevel || '',
          visits: toNumber(item?.visits),
          students: toNumber(item?.students)
        }))
      : []
    byClass.value = Array.isArray(res?.byClass)
      ? res.byClass.map((item: any) => ({
          classId: toNumber(item?.classId),
          className: item?.className || '未分班',
          visits: toNumber(item?.visits),
          students: toNumber(item?.students)
        }))
      : []
    trend.value = Array.isArray(res?.trend)
      ? res.trend.map((item: any) => ({
          date: item?.date ? String(item.date) : '',
          visits: toNumber(item?.visits)
        }))
      : []
  } catch (e) {
    kpis.value = emptyKpis()
    courseTotal.value = 0
    coursePublished.value = 0
    pendingChats.value = 0
    pendingMaterials.value = 0
    byGrade.value = []
    byClass.value = []
    trend.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOverview()
})
</script>

<style scoped>
.ai-overview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar-card,
.kpi-card,
.trend-card,
.section-card {
  border-radius: 14px;
  border: none;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.toolbar-label {
  font-size: 13px;
  color: #606266;
}

.empty-alert {
  border-radius: 12px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  min-height: 120px;
}

.kpi-card :deep(.el-card__body) {
  padding: 18px;
}

.kpi-label {
  font-size: 14px;
  color: #606266;
}

.kpi-value {
  margin-top: 10px;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
  color: #333;
}

.theme-purple {
  color: #8985cf;
}

.theme-orange {
  color: #f48d45;
}

.kpi-extra {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-sub {
  font-size: 12px;
  font-weight: 400;
  color: #909399;
}

.trend-chart {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 200px;
  padding: 8px 4px 0;
  overflow-x: auto;
}

.trend-col {
  flex: 1 0 auto;
  min-width: 6px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}

.trend-value {
  font-size: 10px;
  color: #909399;
  line-height: 1;
}

.trend-bar {
  width: 100%;
  min-height: 2px;
  border-radius: 3px 3px 0 0;
  background: linear-gradient(180deg, #acb6f3 0%, #8985cf 100%);
  transition: height 0.3s ease, filter 0.2s ease;
}

.trend-bar-peak {
  background: linear-gradient(180deg, #f7ad74 0%, #f48d45 100%);
}

.trend-col:hover .trend-bar {
  filter: brightness(1.12);
}

.trend-axis {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 10px;
  padding: 0 4px;
  font-size: 12px;
  color: #909399;
}

.trend-axis-mid {
  color: #acb6f3;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-cell :deep(.el-progress) {
  flex: 1;
}

.progress-text {
  width: 52px;
  text-align: right;
  font-size: 13px;
  color: #606266;
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
