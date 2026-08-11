<template>
  <div class="points-dashboard">
    <div class="summary-section">
      <div class="summary-cards">
        <div v-for="item in metricCards" :key="item.label" class="metric-card" :class="item.theme">
          <img :src="item.icon" class="metric-icon" alt="icon" />
          <div class="metric-content">
            <div class="metric-label">{{ item.label }}</div>
            <div class="metric-value">{{ item.value }}</div>
            <div class="metric-desc">{{ item.desc }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="main-grid">
      <div class="card rule-card">
        <div class="card-header">积分来源占比</div>
        <div ref="rulesChartRef" class="chart"></div>
        <el-divider />
        <div class="rule-scroll-box">
          <div class="rule-title">积分加减规则</div>
          <div class="rule-item" v-for="rule in rules" :key="rule.id">
            <span>{{ rule.name }}</span>
            <el-tag size="small" :type="rule.type === 'add' ? 'success' : 'danger'">
              {{ rule.type === 'add' ? (rule.points === 0 ? '按需加' : `+${rule.points}`) : `-${rule.points}` }}
            </el-tag>
          </div>
        </div>
      </div>

      <div class="right-section">
        <div class="card">
          <div class="card-header">每日积分增长与减少</div>
          <div ref="dailyTrendChartRef" class="chart"></div>
        </div>

        <div class="card class-card">
          <div class="card-header">
            <span>班级积分统计</span>
            <div class="table-filters">
              <el-select v-model="gradeFilter" clearable placeholder="年级筛选">
                <el-option label="全部年级" value="" />
                <el-option v-for="grade in gradeOptions" :key="grade" :label="grade" :value="grade" />
              </el-select>
              <el-select v-model="classFilter" clearable placeholder="班级筛选">
                <el-option label="全部班级" value="" />
                <el-option v-for="item in filteredClassList" :key="item.className" :label="item.className" :value="item.className" />
              </el-select>
            </div>
          </div>
          <el-table :data="filteredClassPoints" border max-height="300">
            <el-table-column prop="className" label="班级" min-width="130" />
            <el-table-column prop="total" label="总积分" min-width="90" />
            <el-table-column prop="count" label="学生人数" min-width="90" />
            <el-table-column prop="avg" label="平均积分" min-width="90" />
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { adminApi } from '../../api/admin'

type ClassPoint = { className: string; total: number; count: number; avg: number }

const gradeFilter = ref('')
const classFilter = ref('')
const rulesChartRef = ref<HTMLElement | null>(null)
const dailyTrendChartRef = ref<HTMLElement | null>(null)

let rulesChart: echarts.ECharts | null = null
let dailyTrendChart: echarts.ECharts | null = null

const dailyPointsData = ref<{ day: string; increase: number; decrease: number }[]>([])

const rules = ref<{ id: number; name: string; type: string; points: number }[]>([])
const ruleDistribution = ref<{ value: number; name: string }[]>([])
const addRules = computed(() => rules.value.filter((rule: any) => rule.type === 'add'))
const reduceRules = computed(() => rules.value.filter((rule: any) => rule.type === 'reduce'))

const classPoints = ref<ClassPoint[]>([])
const getGradeName = (className: string) => {
  const match = className.match(/^(.*?级)/)
  return match ? match[1] : ''
}
const gradeOptions = computed(() => {
  return [...new Set(classPoints.value.map((item) => getGradeName(item.className)).filter(Boolean))]
})
const filteredClassList = computed(() => {
  if (!gradeFilter.value) return classPoints.value
  return classPoints.value.filter((item) => getGradeName(item.className) === gradeFilter.value)
})
const filteredClassPoints = computed<ClassPoint[]>(() => {
  let result = classPoints.value
  if (gradeFilter.value) {
    result = result.filter((item) => getGradeName(item.className) === gradeFilter.value)
  }
  if (classFilter.value) {
    result = result.filter((item) => item.className === classFilter.value)
  }
  return result
})

const studentsData = ref<{ name: string; class: string; points: number }[]>([])

const filteredStudents = computed(() => {
  let result = studentsData.value
  if (gradeFilter.value) {
    result = result.filter((student) => (student.class ? getGradeName(student.class) === gradeFilter.value : false))
  }
  if (classFilter.value) {
    result = result.filter((student) => student.class === classFilter.value)
  }
  return result
})

const filteredTotalPoints = computed(() => {
  return filteredStudents.value.reduce((sum, student) => sum + (student.points || 0), 0)
})

const topClass = computed<ClassPoint | null>(() => {
  if (!filteredClassPoints.value.length) return null
  return [...filteredClassPoints.value].sort((a, b) => b.total - a.total)[0] || null
})

const topStudent = computed<any | null>(() => {
  if (!filteredStudents.value.length) return null
  return [...filteredStudents.value].sort((a, b) => (b.points || 0) - (a.points || 0))[0] || null
})

const metricCards = computed(() => [
  {
    label: '积分规则总数',
    value: rules.value.length,
    desc: `加分 ${addRules.value.length} 条 / 扣分 ${reduceRules.value.length} 条`,
    icon: '/images/Admin_Icons/TotalPointsRules.svg',
    theme: 'pink'
  },
  {
    label: '最高积分班级',
    value: topClass.value?.className ?? '-',
    desc: `总积分 ${topClass.value?.total ?? 0}，平均 ${topClass.value?.avg ?? 0}`,
    icon: '/images/Admin_Icons/Classwiththehighestpoints.svg',
    theme: 'blue'
  },
  {
    label: '最高积分同学',
    value: topStudent.value?.name ?? '-',
    desc: `${topStudent.value?.class ?? '-'}，积分 ${topStudent.value?.points ?? 0}`,
    icon: '/images/Admin_Icons/oprankedstudent.svg',
    theme: 'yellow'
  },
  {
    label: '当前筛选总积分',
    value: filteredTotalPoints.value,
    desc: `学生人数 ${filteredStudents.value.length} 人`,
    icon: '/images/Admin_Icons/TotalPoints.svg',
    theme: 'mint'
  }
])

const renderRulesChart = () => {
  if (!rulesChartRef.value) return
  if (!rulesChart) rulesChart = echarts.init(rulesChartRef.value)
  rulesChart.setOption({
    color: ['#f48d45', '#f4bb6e', '#acb6f3', '#8985cf', '#7370bb'],
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#333', fontSize: 11 },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 8
    },
    series: [
      {
        type: 'pie',
        radius: ['35%', '65%'],
        center: ['40%', '50%'],
        data: ruleDistribution.value,
        label: {
          show: false
        },
        labelLine: {
          show: false
        }
      }
    ]
  })
}

const renderDailyTrendChart = () => {
  if (!dailyTrendChartRef.value) return
  if (!dailyTrendChart) dailyTrendChart = echarts.init(dailyTrendChartRef.value)
  dailyTrendChart.setOption({
    color: ['#f48d45', '#8985cf'],
    tooltip: { trigger: 'axis' },
    legend: { data: ['积分增长', '积分减少'], top: 0, right: 8 },
    grid: { left: 35, right: 24, bottom: 28, top: 58 },
    xAxis: { type: 'category', data: dailyPointsData.value.map((item) => item.day) },
    yAxis: { type: 'value' },
    series: [
      { name: '积分增长', type: 'line', smooth: true, areaStyle: { opacity: 0.25 }, data: dailyPointsData.value.map((item) => item.increase) },
      { name: '积分减少', type: 'line', smooth: true, areaStyle: { opacity: 0.15 }, data: dailyPointsData.value.map((item) => item.decrease) }
    ]
  })
}

const renderAllCharts = () => {
  renderRulesChart()
  renderDailyTrendChart()
}

const resizeAllCharts = () => {
  rulesChart?.resize()
  dailyTrendChart?.resize()
}

watch(gradeFilter, () => {
  if (classFilter.value && !filteredClassList.value.some((item) => item.className === classFilter.value)) {
    classFilter.value = ''
  }
})

watch([classFilter, gradeFilter, rules], async () => {
  await nextTick()
  renderAllCharts()
})

onMounted(async () => {
  try {
    const [overviewRes, rankingsRes] = await Promise.all([
      adminApi.getPointOverview(),
      adminApi.getPointRankings()
    ])
    if (overviewRes) {
      if (Array.isArray(overviewRes.rules)) {
        rules.value = overviewRes.rules.map((r: any) => ({
          id: r.id,
          name: r.name || '',
          type: r.type || 'add',
          points: Number(r.points) || 0
        }))
      }
      if (Array.isArray(overviewRes.classPoints)) {
        classPoints.value = overviewRes.classPoints.map((c: any) => ({
          className: c.className || '',
          total: Number(c.total) || 0,
          count: Number(c.count) || 0,
          avg: Number(c.avg) || 0
        }))
      }
      if (Array.isArray(overviewRes.dailyPointsData)) {
        dailyPointsData.value = overviewRes.dailyPointsData.map((d: any) => ({
          day: d.day || '',
          increase: Number(d.increase) || 0,
          decrease: Number(d.decrease) || 0
        }))
      }
      if (Array.isArray(overviewRes.ruleDistribution)) {
        ruleDistribution.value = overviewRes.ruleDistribution.map((r: any) => ({
          value: Number(r.value) || 0,
          name: r.name || ''
        }))
      }
    }
    if (Array.isArray(rankingsRes)) {
      studentsData.value = rankingsRes.map((s: any) => ({
        name: s.name || '',
        class: s.class || s.className || '',
        points: Number(s.points) || 0
      }))
    }
  } catch (e) {
    console.error('获取积分数据失败:', e)
  } finally {
    renderAllCharts()
    window.addEventListener('resize', resizeAllCharts)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeAllCharts)
  rulesChart?.dispose()
  dailyTrendChart?.dispose()
})
</script>

<style scoped>
.points-dashboard {
  display: grid;
  gap: 20px;
}

.main-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 20px;
}

.right-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(137, 133, 207, 0.08);
}

.rule-card {
  display: flex;
  flex-direction: column;
  max-height: 100%;
  overflow: hidden;
}

.class-card {
  flex: 1;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-filters {
  display: flex;
  gap: 10px;
}

.table-filters .el-select {
  width: 100px;
}

.chart {
  width: 100%;
  height: 260px;
}

.rule-scroll-box {
  flex: 1;
  overflow-y: auto;
  margin-top: 12px;
  max-height: 320px;
}

.rule-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: 10px;
  background-color: #f5f3f0;
  font-size: 15px;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.rule-item:hover {
  background: #acb6f3;
  color: #fff;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-section {
  margin-bottom: 8px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin-bottom: 16px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.metric-card {
  min-height: 120px;
  padding: 18px;
  position: relative;
  border-radius: 14px;
  border: none;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 16px;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.metric-icon {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
}

.metric-content {
  flex: 1;
  text-align: right;
}

.metric-label {
  color: #606266;
  font-size: 15px;
}

.metric-value {
  margin-top: 10px;
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.metric-desc {
  margin-top: 6px;
  color: #909399;
  font-size: 14px;
}

.pink { background: linear-gradient(135deg, #9fa8da 0%, #7986cb 100%); color: #fff; }
.pink .metric-label, .pink .metric-value, .pink .metric-desc { color: #fff; }
.blue { background: linear-gradient(135deg, #b39ddb 0%, #9575cd 100%); color: #fff; }
.blue .metric-label, .blue .metric-value, .blue .metric-desc { color: #fff; }
.yellow { background: linear-gradient(135deg, #ce93d8 0%, #ba68c8 100%); color: #fff; }
.yellow .metric-label, .yellow .metric-value, .yellow .metric-desc { color: #fff; }
.mint { background: linear-gradient(135deg, #90caf9 0%, #64b5f6 100%); color: #fff; }
.mint .metric-label, .mint .metric-value, .mint .metric-desc { color: #fff; }
</style>
