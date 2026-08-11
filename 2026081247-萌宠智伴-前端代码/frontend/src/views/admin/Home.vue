<template>
  <div class="visual-page">
    <div class="header-banner">
      <div class="user-box">
        <div class="avatar-icon">
          <el-icon :size="40"><User /></el-icon>
        </div>
        <div>
          <div class="greeting">早上好</div>
          <div class="username">管理员</div>
        </div>
      </div>

      <div class="center-title">
        <div class="big-text">数据看板</div>
        <div class="subtitle">数据可视化分析平台</div>
      </div>

      <div class="wallet-box">
        <div class="stat-box">
          <div class="stat-label">总积分</div>
          <div class="stat-value">{{ totalScore.toLocaleString() }}</div>
        </div>
        <div class="stat-icon">
          <el-icon :size="28"><Coin /></el-icon>
        </div>
      </div>
    </div>

    <div class="dashboard-container">
      <div class="row">
        <el-card shadow="never" class="card card-violet">
          <template #header>
            <div class="card-title">日常问题 vs 学科问题占比</div>
          </template>
          <div ref="questionChartRef" class="chart-full"></div>
        </el-card>

        <el-card shadow="never" class="card card-purple">
          <template #header>
            <div class="card-title">学生行为合规率</div>
          </template>
          <div ref="gaugeChartRef" class="chart-full"></div>
        </el-card>

        <el-card shadow="never" class="card card-lavender">
          <template #header>
            <div class="card-title">所有班级整体活跃度</div>
          </template>
          <div ref="radarChartRef" class="chart-full"></div>
        </el-card>
      </div>

      <div class="row">
        <el-card shadow="never" class="card card-indigo">
          <template #header>
            <div class="card-title">每日任务完成数</div>
          </template>
          <div ref="progressChartRef" class="chart-full"></div>
        </el-card>

        <el-card shadow="never" class="card card-large card-blue heatmap-card">
          <template #header>
            <div class="card-title">每日在线人数分布</div>
          </template>
          <div ref="heatmapAllChartRef" class="chart-heatmap"></div>
        </el-card>
      </div>

      <div class="row full-row">
        <el-card shadow="never" class="card score-card">
          <template #header>
            <div class="card-title" style="text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px;">
              <img class="wavyline" src="/images/Admin_Icons/wavyline1.jpg" />
              <img class="wavyline" src="/images/Admin_Icons/wavyline1.jpg" />
              <span style="margin: 0 4px;">班风概览</span>
              <img class="wavyline" src="/images/Admin_Icons/wavyline1.jpg" />
              <img class="wavyline" src="/images/Admin_Icons/wavyline1.jpg" />
            </div>
          </template>
          <div class="score-grid">
            <div v-for="item in classScores" :key="item.class" class="score-item" :class="{ topScore: item.score === maxScore }">
              <div class="score-name">{{ item.class }}</div>
              <el-progress :percentage="maxScore ? Math.round(item.score / maxScore * 100) : 0" :color="getScoreColor(maxScore ? item.score / maxScore * 100 : 0)" :stroke-width="14" />
              <div class="score-num">{{ item.score }}分</div>
            </div>
          </div>
        </el-card>
      </div>

      <div class="row">
        <el-card shadow="never" class="card card-sky">
          <template #header>
            <div class="card-title">积分总趋势</div>
          </template>
          <div ref="trendChartRef" class="chart-full"></div>
        </el-card>

        <el-card shadow="never" class="card card-orange-grad">
          <template #header>
            <div class="card-title">班级总积分排名</div>
          </template>
          <div ref="classRankChartRef" class="chart-full"></div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { User, Coin } from '@element-plus/icons-vue'
import { adminApi } from '../../api/admin'

const totalScore = ref(0)

const trendChartRef = ref<HTMLElement | null>(null)
const questionChartRef = ref<HTMLElement | null>(null)
const classRankChartRef = ref<HTMLElement | null>(null)
const progressChartRef = ref<HTMLElement | null>(null)
const radarChartRef = ref<HTMLElement | null>(null)
const gaugeChartRef = ref<HTMLElement | null>(null)
const heatmapAllChartRef = ref<HTMLElement | null>(null)

let chartsInstance: echarts.ECharts[] = []

const classScores = ref<{ class: string; score: number }[]>([])

const questionDistribution = ref<Record<string, number>>({})
const behaviorCompliance = ref(0)
const classActivity = ref<Record<string, number>>({})
const trendData = ref<{ day: string; value: number }[]>([])
const classRankData = ref<{ class: string; points: number }[]>([])

const questionColorMap: Record<string, string> = {
  'daily': '#9575cd',
  '语文': '#f48d45',
  '数学': '#f4bb6e',
  '英语': '#acb6f3',
  '科学': '#8985cf',
  '体育': '#7c6ccc',
  '美术': '#5a52b8'
}
const questionNameMap: Record<string, string> = {
  'daily': '日常问题'
}

const getScoreColor = (score: number) => {
  if (score >= 90) return '#7b1fa2'
  if (score >= 80) return '#ce93d8'
  return '#e1bee7'
}

const maxScore = computed(() => classScores.value.length ? Math.max(...classScores.value.map(s => s.score)) : 0)

const initCharts = () => {
  nextTick(() => {
    chartsInstance.forEach(chart => chart.dispose())
    chartsInstance = []
    initTrendChart()
    initQuestionChart()
    initClassRankChart()
    initDailyPostChart()
    initRadarChart()
    initGaugeChart()
    initHeatmapAllChart()
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)
  chartsInstance.push(chart)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, bottom: 30, top: 20 },
    xAxis: { type: 'category', data: trendData.value.map(d => d.day), axisLine: { lineStyle: { color: '#8985cf' } }, axisLabel: { color: '#8985cf', fontSize: 10 } },
    yAxis: { type: 'value', axisLine: { lineStyle: { color: '#8985cf' } }, axisLabel: { color: '#8985cf' }, splitLine: { lineStyle: { color: 'rgba(137,133,207,0.2)' } } },
    series: [{ name: '积分', type: 'line', smooth: true, data: trendData.value.map(d => d.value), lineStyle: { color: '#8985cf', width: 3 }, areaStyle: { color: 'rgba(137,133,207,0.2)' } }]
  })
}

const initQuestionChart = () => {
  if (!questionChartRef.value) return
  const chart = echarts.init(questionChartRef.value)
  chartsInstance.push(chart)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { show: false },
    series: [{ 
      type: 'pie', radius: ['45%', '75%'], 
      label: { show: true, position: 'outside', fontSize: 14, color: '#333', lineHeight: 18, formatter: (params: any) => `${params.name} ${params.percent}%` },
      data: Object.entries(questionDistribution.value).map(([key, value]) => ({
        value: Number(value) || 0,
        name: questionNameMap[key] || key,
        itemStyle: { color: questionColorMap[key] || '#999' }
      }))
    }]
  })
}

const initClassRankChart = () => {
  if (!classRankChartRef.value) return
  const chart = echarts.init(classRankChartRef.value)
  chartsInstance.push(chart)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, bottom: 60, top: 20 },
    xAxis: { type: 'category', data: classRankData.value.map(d => d.class), axisLine: { lineStyle: { color: '#8985cf' } }, axisLabel: { color: '#8985cf', fontSize: 9, rotate: 45 } },
    yAxis: { type: 'value', axisLine: { lineStyle: { color: '#8985cf' } }, axisLabel: { color: '#8985cf' }, splitLine: { lineStyle: { color: 'rgba(137,133,207,0.2)' } } },
    series: [{ type: 'bar', data: classRankData.value.map(d => d.points), itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{offset: 0, color: '#8985cf'}, {offset: 1, color: '#DDE3EC'}] }, borderRadius: [4, 4, 0, 0] } }]
  })
}

const initDailyPostChart = () => {
  if (!progressChartRef.value) return
  const chart = echarts.init(progressChartRef.value)
  chartsInstance.push(chart)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['语文', '数学', '英语', '科学', '体育', '美术', '阅读'], top: 0, textStyle: { fontSize: 11 } },
    grid: { left: 40, right: 20, bottom: 30, top: 28 },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'], axisLine: { lineStyle: { color: '#5c6bc0' } }, axisLabel: { color: '#283593' } },
    yAxis: { type: 'value', axisLine: { lineStyle: { color: '#5c6bc0' } }, axisLabel: { color: '#283593' }, splitLine: { lineStyle: { color: 'rgba(92,107,192,0.2)' } } },
    series: [
      { name: '语文', type: 'bar', stack: 'total', data: [8, 10, 6, 12, 14, 11, 9], itemStyle: { color: '#f48d45' } },
      { name: '数学', type: 'bar', stack: 'total', data: [10, 12, 8, 14, 16, 12, 10], itemStyle: { color: '#f4bb6e' } },
      { name: '英语', type: 'bar', stack: 'total', data: [6, 8, 5, 10, 12, 9, 7], itemStyle: { color: '#f7f3e5' } },
      { name: '科学', type: 'bar', stack: 'total', data: [5, 7, 4, 8, 10, 7, 6], itemStyle: { color: '#acb6f3' } },
      { name: '体育', type: 'bar', stack: 'total', data: [4, 6, 3, 7, 8, 6, 5], itemStyle: { color: '#8985cf' } },
      { name: '美术', type: 'bar', stack: 'total', data: [3, 5, 2, 6, 7, 5, 4], itemStyle: { color: '#7c6ccc' } },
      { name: '阅读', type: 'bar', stack: 'total', data: [2, 4, 2, 5, 6, 4, 3], itemStyle: { color: '#5a52b8' } }
    ]
  })
}

const initRadarChart = () => {
  if (!radarChartRef.value) return
  const chart = echarts.init(radarChartRef.value)
  chartsInstance.push(chart)
  chart.setOption({
    radar: { 
      radius: '80%', center: ['50%', '50%'],
      indicator: [
        { name: '出勤率', max: 100 },
        { name: '课堂参与度', max: 100 },
        { name: '作业完成率', max: 100 },
        { name: '纪律表现', max: 100 },
        { name: '积分获取', max: 100 }
      ],
      axisName: { color: '#1565c0', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(21,101,192,0.3)' } },
      splitArea: { areaStyle: { color: ['rgba(21,101,192,0.05)', 'rgba(21,101,192,0.1)'] } }
    },
    series: [{ type: 'radar', data: [{ value: [classActivity.value['出勤率'] || 0, classActivity.value['课堂参与度'] || 0, classActivity.value['作业完成率'] || 0, classActivity.value['纪律表现'] || 0, classActivity.value['积分获取'] || 0], areaStyle: { color: 'rgba(21,101,192,0.3)' }, lineStyle: { color: '#1565c0', width: 2 } }] }]
  })
}

const initGaugeChart = () => {
  if (!gaugeChartRef.value) return
  const chart = echarts.init(gaugeChartRef.value)
  chartsInstance.push(chart)
  chart.setOption({
    series: [{
      type: 'gauge', startAngle: 180, endAngle: 0, min: 0, max: 100, radius: '95%', center: ['50%', '55%'],
      axisLine: { lineStyle: { width: 16, color: [[0.3, '#f48d45'], [0.7, '#f4bb6e'], [1, '#7c6ccc']] } },
      pointer: { length: '60%', width: 8, itemStyle: { color: '#8985cf' } },
      axisTick: { show: true, length: 8, lineStyle: { color: '#8985cf', width: 2 } },
      splitLine: { show: true, length: 12, lineStyle: { color: '#8985cf', width: 3 } },
      axisLabel: { show: true, distance: 15, color: '#8985cf', fontSize: 11, formatter: '{value}' },
      detail: { show: true, color: '#8985cf', fontSize: 28, fontWeight: 'bold', offsetCenter: [0, '75%'], formatter: '{value}%' },
      title: { show: true, offsetCenter: [0, '40%'], color: '#8985cf', fontSize: 14 },
      data: [{ value: behaviorCompliance.value || 0, name: '学生行为合规率' }]
    }]
  })
}

const initHeatmapAllChart = () => {
  if (!heatmapAllChartRef.value) return
  const chart = echarts.init(heatmapAllChartRef.value)
  chartsInstance.push(chart)
  const hours = ['6时', '8时', '10时', '12时', '14时', '16时', '18时', '20时', '22时']
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const data = [
    [0,0,15], [1,0,68], [2,0,85], [3,0,45], [4,0,78], [5,0,92], [6,0,88], [7,0,65], [8,0,35],
    [0,1,18], [1,1,72], [2,1,88], [3,1,48], [4,1,82], [5,1,95], [6,1,90], [7,1,68], [8,1,38],
    [0,2,12], [1,2,65], [2,2,82], [3,2,42], [4,2,76], [5,2,90], [6,2,85], [7,2,62], [8,2,32],
    [0,3,20], [1,3,75], [2,3,90], [3,3,50], [4,3,85], [5,3,98], [6,3,92], [7,3,70], [8,3,40],
    [0,4,16], [1,4,70], [2,4,86], [3,4,46], [4,4,80], [5,4,94], [6,4,89], [7,4,66], [8,4,36],
    [0,5,8], [1,5,25], [2,5,35], [3,5,55], [4,5,70], [5,5,75], [6,5,80], [7,5,58], [8,5,42],
    [0,6,5], [1,6,20], [2,6,30], [3,6,50], [4,6,68], [5,6,72], [6,6,78], [7,6,55], [8,6,38]
  ]
  chart.setOption({
    tooltip: { trigger: 'item' },
    grid: { left: 50, right: 60, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLine: { lineStyle: { color: '#0277bd' } }, axisLabel: { color: '#0277bd', fontSize: 11 } },
    yAxis: { type: 'category', data: days, axisLine: { lineStyle: { color: '#0277bd' } }, axisLabel: { color: '#0277bd', fontSize: 11 } },
    visualMap: { min: 0, max: 100, calculable: true, orient: 'vertical', right: 10, top: 'center', height: '70%', inRange: { color: ['#e3f2fd', '#64b5f6', '#1565c0'] }, textStyle: { color: '#0277bd', fontSize: 11 } },
    series: [{ type: 'heatmap', data: data as any, itemStyle: { borderRadius: 4, borderColor: '#fff' }, label: { show: true, color: '#fff', fontSize: 10 } }]
  })
}

const resizeCharts = () => chartsInstance.forEach(chart => chart.resize())

onMounted(async () => {
  try {
    const [dashRes, trendRes] = await Promise.all([
      adminApi.getDashboard(),
      adminApi.getPointTrend()
    ])
    if (dashRes) {
      totalScore.value = parseInt(String(dashRes.totalScore)) || 0
      if (Array.isArray(dashRes.classScores)) {
        classScores.value = dashRes.classScores.map((c: any) => ({
          class: c.class || c.className || '',
          score: Number(c.score) || 0
        }))
      }
      if (dashRes.questionDistribution) {
        questionDistribution.value = dashRes.questionDistribution
      }
      if (typeof dashRes.behaviorCompliance === 'number') {
        behaviorCompliance.value = dashRes.behaviorCompliance
      }
      if (dashRes.classActivity) {
        classActivity.value = dashRes.classActivity
      }
    }
    if (trendRes) {
      if (Array.isArray(trendRes.trend)) {
        trendData.value = trendRes.trend.map((t: any) => ({
          day: t.day || '',
          value: Number(t.value) || 0
        }))
      }
      if (Array.isArray(trendRes.classRank)) {
        classRankData.value = trendRes.classRank.map((c: any) => ({
          class: c.class || c.className || '',
          points: Number(c.points) || 0
        }))
      }
    }
  } catch (e) {
    console.error('获取看板数据失败:', e)
  } finally {
    initCharts()
    window.addEventListener('resize', resizeCharts)
  }
})

onUnmounted(() => {
  chartsInstance.forEach(chart => chart.dispose())
  window.removeEventListener('resize', resizeCharts)
})
</script>

<style scoped>
.visual-page {
  width: 100%;
  min-height: 100vh;
  background: #f5f3f0;
  padding: 12px;
  box-sizing: border-box;
}

.header-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f48d45 0%, #f4bb6e 100%);
  color: #fff;
  padding: 28px 40px;
  border-radius: 20px;
  margin-bottom: 20px;
  box-shadow: 0 8px 30px rgba(244, 141, 69, 0.25);
}

.user-box { display: flex; align-items: center; gap: 16px; }
.avatar-icon {
  width: 56px; height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.greeting { font-size: 13px; opacity: 0.9; }
.username { font-size: 20px; font-weight: 600; }
.center-title { text-align: center; }
.big-text { font-size: 36px; font-weight: 700; }
.subtitle { font-size: 13px; opacity: 0.85; }
.wallet-box { display: flex; align-items: center; gap: 16px; }
.stat-label { font-size: 12px; opacity: 0.9; }
.stat-value { font-size: 28px; font-weight: 700; }
.stat-icon {
  width: 48px; height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dashboard-container { display: flex; flex-direction: column; gap: 16px; }
.row { display: flex; gap: 16px; width: 100%; }
.full-row { width: 100%; }

.card {
  flex: 1;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}
.card:hover { transform: translateY(-4px); }
.card-large { flex: 1.5; }

.card-header { padding: 16px 20px 12px; border-bottom: 1px solid rgba(255,255,255,0.2); }
.card-title { font-size: 15px; font-weight: 600; color: #fff; }

.card-violet { background: linear-gradient(135deg, #e1d5f3 0%, #d4c6eb 100%); }
.card-violet .card-title { color: #5e35b1; }
.card-purple { background: linear-gradient(135deg, #f3e5f5 0%, #e8d4ef 100%); }
.card-purple .card-title { color: #7b1fa2; }
.card-lavender { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); }
.card-lavender .card-title { color: #1565c0; }
.card-indigo { background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%); }
.card-indigo .card-title { color: #283593; }
.card-blue { background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%); }
.card-blue .card-title { color: #0277bd; }
.card-sky { background: #DDE3EC; }
.card-sky .card-title { color: #333; }
.card-orange-grad { background: #DDE3EC; }
.card-orange-grad .card-title { color: #333; }

.chart-full { width: 100%; min-height: 280px; }
.card-large .chart-full { min-height: 380px; }
.chart-heatmap { width: 100%; height: 380px; }

.score-card { background: #fff; color: #333; border: 1px solid rgba(137,133,207,0.15); }
.score-card .card-header { border-bottom: 1px solid rgba(137,133,207,0.15); }
.score-card .card-title { color: #f4bb6e; font-size: 30px; text-align: center; font-weight: 700; }

.score-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; padding: 0px; }
.score-item {
  text-align: center;
  padding: 16px 12px;
  background: #f5f3f0;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(137,133,207,0.1);
}
.score-item.topScore { background: #FFD89C; }
.score-name { font-size: 14px; font-weight: 600; color: #333; text-align: center; }
.score-num { margin-top: 10px; font-size: 16px; font-weight: 700; color: #444; }
:deep(.el-card__header) {
  padding: 8px 20px 8px;
  border-bottom: 1px solid rgba(255,255,255,0.2);
}
.wavyline { height: 40px; object-fit: contain; }
</style>
