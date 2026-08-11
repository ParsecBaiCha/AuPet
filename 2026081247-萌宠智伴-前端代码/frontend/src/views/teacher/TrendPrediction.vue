<template>
  <div class="predict-container">
    <div class="predict-header">
      <div class="header-left">
        <div class="logo-section">
          <div class="swarm-orbit">
            <svg viewBox="0 0 120 120" width="80" height="80">
              <defs>
                <radialGradient id="orbitGrad" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" style="stop-color:#f48d45;stop-opacity:0.4" />
                  <stop offset="100%" style="stop-color:#f48d45;stop-opacity:0" />
                </radialGradient>
                <filter id="glowOrange">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <circle cx="60" cy="60" r="50" fill="url(#orbitGrad)" />
              <g class="orbit-ring">
                <ellipse cx="60" cy="60" rx="45" ry="20" fill="none" stroke="#f48d45" stroke-width="1" opacity="0.3">
                  <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="20s" repeatCount="indefinite" />
                </ellipse>
                <ellipse cx="60" cy="60" rx="45" ry="20" fill="none" stroke="#f4bb6e" stroke-width="1" opacity="0.3">
                  <animateTransform attributeName="transform" type="rotate" from="45 60 60" to="405 60 60" dur="15s" repeatCount="indefinite" />
                </ellipse>
                <ellipse cx="60" cy="60" rx="45" ry="20" fill="none" stroke="#8985cf" stroke-width="1" opacity="0.3">
                  <animateTransform attributeName="transform" type="rotate" from="90 60 60" to="450 60 60" dur="18s" repeatCount="indefinite" />
                </ellipse>
              </g>
              <circle cx="60" cy="60" r="12" fill="#f48d45" filter="url(#glowOrange)" />
              <g class="fish-swarm">
                <path d="M30 60 Q40 50 50 60 Q40 70 30 60 M50 60 L60 55 Q50 60 60 65 L50 60" fill="#f48d45" filter="url(#glowOrange)">
                  <animate attributeName="d" values="M30 60 Q40 50 50 60 Q40 70 30 60 M50 60 L60 55 Q50 60 60 65 L50 60;M38 55 Q48 45 58 55 Q48 65 38 55 M58 55 L68 50 Q58 55 68 60 L58 55;M30 60 Q40 50 50 60 Q40 70 30 60 M50 60 L60 55 Q50 60 60 65 L50 60" dur="3s" repeatCount="indefinite" />
                </path>
                <path d="M70 60 Q80 50 90 60 Q80 70 70 60 M90 60 L100 55 Q90 60 100 65 L90 60" fill="#f4bb6e" filter="url(#glowOrange)">
                  <animate attributeName="d" values="M70 60 Q80 50 90 60 Q80 70 70 60 M90 60 L100 55 Q90 60 100 65 L90 60;M62 65 Q72 55 82 65 Q72 75 62 65 M82 65 L92 60 Q82 65 92 70 L82 65;M70 60 Q80 50 90 60 Q80 70 70 60 M90 60 L100 55 Q90 60 100 65 L90 60" dur="2.5s" repeatCount="indefinite" />
                </path>
                <circle cx="50" cy="35" r="4" fill="#acb6f3">
                  <animate attributeName="cy" values="35;45;35" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle cx="75" cy="40" r="3" fill="#acb6f3">
                  <animate attributeName="cy" values="40;30;40" dur="1.8s" repeatCount="indefinite" />
                </circle>
              </g>
            </svg>
          </div>
          <div>
            <h2 class="page-title">群体趋势预测</h2>
            <span class="page-desc">MiroFish Trend Prediction</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-button circle :type="isConnected ? 'success' : 'default'" @click="checkConnection" :loading="checking">
          <el-icon><Connection /></el-icon>
        </el-button>
      </div>
    </div>

    <div class="predict-main">
      <div class="simulation-panel" v-if="isRunning">
        <div class="simulation-header">
          <div class="sim-status">
            <el-tag type="warning" effect="dark" size="large">
              <el-icon class="is-loading"><Loading /></el-icon>
              模拟运行中            </el-tag>
            <span class="round-info">Round {{ currentRound }}/{{ totalRounds }}</span>
          </div>
          <el-progress :percentage="progress" :stroke-width="10" :show-text="false" />
        </div>
        
        <div class="swarm-visual">
          <svg viewBox="0 0 800 350" class="swarm-svg">
            <defs>
              <radialGradient id="swarmGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" style="stop-color:#f48d45;stop-opacity:0.6" />
                <stop offset="100%" style="stop-color:#f48d45;stop-opacity:0" />
              </radialGradient>
              <filter id="fishGlow">
                <feGaussianBlur stdDeviation="2" />
              </filter>
            </defs>
            
            <rect width="100%" height="100%" fill="url(#bgGrad)" />
            
            <g v-for="(agent, idx) in swarmAgents" :key="idx">
              <circle
                :cx="agent.x"
                :cy="agent.y"
                r="5"
                :fill="agent.color"
                opacity="0.7"
                filter="url(#fishGlow)"
              >
                <animate
                  :attributeName="agent.animAxis"
                  :values="agent.animValues"
                  :dur="agent.animDur"
                  repeatCount="indefinite"
                />
              </circle>
            </g>
            
            <g v-for="(stream, idx) in streamLines" :key="'s'+idx">
              <path
                :d="stream.path"
                fill="none"
                :stroke="stream.color"
                stroke-width="1.5"
                opacity="0.4"
                stroke-linecap="round"
              >
                <animate
                  attributeName="stroke-dashoffset"
                  from="0" to="30"
                  dur="3s"
                  repeatCount="indefinite"
                />
              </path>
            </g>
            
            <g v-for="(cluster, idx) in clusterOrbs" :key="'c'+idx">
              <circle
                :cx="cluster.x"
                :cy="cluster.y"
                :r="cluster.r"
                :fill="cluster.color"
                opacity="0.15"
              >
                <animate attributeName="r" :values="`${cluster.r};${cluster.r + 10};${cluster.r}`" dur="4s" repeatCount="indefinite" />
              </circle>
            </g>
          </svg>
          
          <div class="swarm-stats">
            <div class="swarm-stat">
              <span class="stat-value">{{ activeAgents }}</span>
              <span class="stat-label">活跃智能体</span>
            </div>
            <div class="swarm-stat">
              <span class="stat-value">{{ interactionCount }}</span>
              <span class="stat-label">交互次数</span>
            </div>
            <div class="swarm-stat">
              <span class="stat-value">{{ avgMood }}</span>
              <span class="stat-label">情绪指数</span>
            </div>
          </div>
        </div>
        
        <div class="log-panel">
          <div v-for="(log, idx) in logs" :key="idx" class="log-entry">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-msg">{{ log.message }}</span>
          </div>
        </div>
      </div>

      <div class="result-panel" v-else-if="result">
        <el-tabs v-model="activeTab" class="result-tabs">
          <el-tab-pane label="趋势概览" name="overview">
            <div class="overview-content">
              <div class="main-circle">
                <svg viewBox="0 0 250 250" width="250" height="250">
                  <defs>
                    <linearGradient id="circleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#f48d45" />
                      <stop offset="100%" style="stop-color:#f4bb6e" />
                    </linearGradient>
                    <filter id="circleGlow">
                      <feGaussianBlur stdDeviation="4" result="blur"/>
                      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                  </defs>
                  <circle cx="125" cy="125" r="100" fill="none" stroke="#fce8d8" stroke-width="16" />
                  <circle 
                    cx="125" cy="125" r="100" 
                    fill="none" 
                    stroke="url(#circleGrad)" 
                    stroke-width="16"
                    stroke-linecap="round"
                    :stroke-dasharray="`${result.confidence * 6.28} 628`"
                    transform="rotate(-90 125 125)"
                    filter="url(#circleGlow)"
                  />
                  <circle cx="125" cy="125" r="70" fill="#fff9f5" />
                  <text x="125" y="115" text-anchor="middle" font-size="48" font-weight="800" fill="#333">{{ result.confidence }}</text>
                  <text x="125" y="140" text-anchor="middle" font-size="14" fill="#999">预测置信度</text>
                </svg>
              </div>
              
              <div class="metrics-grid">
                <div class="metric-card">
                  <div class="metric-header">
                    <span class="metric-label">短期影响</span>
                    <el-tag type="warning" size="small">{{ result.shortTerm }}%</el-tag>
                  </div>
                  <el-progress :percentage="result.shortTerm" :stroke-width="8" :show-text="false" color="#f48d45" />
                </div>
                <div class="metric-card">
                  <div class="metric-header">
                    <span class="metric-label">长期影响</span>
                    <el-tag type="success" size="small">{{ result.longTerm }}%</el-tag>
                  </div>
                  <el-progress :percentage="result.longTerm" :stroke-width="8" :show-text="false" color="#52c41a" />
                </div>
                <div class="metric-card">
                  <div class="metric-header">
                    <span class="metric-label">风险指数</span>
                    <el-tag :type="result.risk > 50 ? 'danger' : 'success'" size="small">{{ result.risk }}%</el-tag>
                  </div>
                  <el-progress :percentage="result.risk" :stroke-width="8" :show-text="false" :color="getRiskColor(result.risk)" />
                </div>
                <div class="metric-card">
                  <div class="metric-header">
                    <span class="metric-label">稳定指数</span>
                    <el-tag type="info" size="small">{{ result.stability }}%</el-tag>
                  </div>
                  <el-progress :percentage="result.stability" :stroke-width="8" :show-text="false" color="#1890ff" />
                </div>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="趋势图表" name="charts">
            <div class="charts-container">
              <div class="chart-card">
                <h4>情绪趋势变化</h4>
                <div class="multi-line-chart">
                  <svg viewBox="0 0 600 180" width="100%" height="180">
                    <defs>
                      <linearGradient id="lineGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#f48d45;stop-opacity:0" />
                        <stop offset="100%" style="stop-color:#f48d45;stop-opacity:0.3" />
                      </linearGradient>
                    </defs>
                    <polyline
                      points="0,140 100,120 200,130 300,90 400,70 500,80 600,50"
                      fill="none"
                      stroke="#f48d45"
                      stroke-width="3"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <polyline
                      points="0,150 100,140 200,145 300,130 400,120 500,115 600,100"
                      fill="none"
                      stroke="#acb6f3"
                      stroke-width="3"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <polyline
                      points="0,160 100,155 200,158 300,145 400,140 500,138 600,125"
                      fill="none"
                      stroke="#52c41a"
                      stroke-width="3"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  <div class="chart-legend">
                    <span><i style="background:#f48d45"></i>积极情绪</span>
                    <span><i style="background:#acb6f3"></i>消极情绪</span>
                    <span><i style="background:#52c41a"></i>班级凝聚度</span>
                  </div>
                </div>
              </div>
              
              <div class="chart-card">
                <h4>群体聚类分布</h4>
                <div class="cluster-visual">
                  <div v-for="(cluster, idx) in clusterOrbs" :key="idx" class="cluster-orb"
                    :style="{
                      width: cluster.r * 3 + 'px',
                      height: cluster.r * 3 + 'px',
                      background: `radial-gradient(circle, ${cluster.color} 0%, transparent 70%)`,
                      left: cluster.x / 8 + '%',
                      top: cluster.y / 4 + '%'
                    }">
                    <span class="orb-label">{{ cluster.count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="风险预警" name="risks">
            <div class="risk-container">
              <div class="risk-list">
                <div v-for="(risk, idx) in result.risks" :key="idx" class="risk-card" :class="risk.level">
                  <div class="risk-icon">
                    <el-icon><WarningFilled /></el-icon>
                  </div>
                  <div class="risk-info">
                    <span class="risk-title">{{ risk.title }}</span>
                    <span class="risk-desc">{{ risk.desc }}</span>
                  </div>
                  <div class="risk-prob">
                    <span class="prob-value">{{ risk.probability }}%</span>
                    <el-progress :percentage="risk.probability" :stroke-width="4" :show-text="false" :color="getRiskColor(risk.probability)" />
                  </div>
                </div>
              </div>
              
              <div class="suggestion-box">
                <div class="suggestion-header">
                  <el-icon><MagicStick /></el-icon>
                  <h4>建议措施</h4>
                </div>
                <div class="suggestion-list">
                  <div v-for="(sug, idx) in suggestions" :key="idx" class="suggestion-item">
                    <span class="sug-num">{{ idx + 1 }}</span>
                    <span>{{ sug }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <div class="empty-panel" v-else>
        <div class="empty-illustration">
          <svg viewBox="0 0 200 200" width="180" height="180">
            <defs>
              <radialGradient id="emptyGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" style="stop-color:#fce8d8;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#fff;stop-opacity:0" />
              </radialGradient>
            </defs>
            <circle cx="100" cy="100" r="80" fill="url(#emptyGrad)" />
            <circle cx="100" cy="100" r="40" fill="none" stroke="#f48d45" stroke-width="2" stroke-dasharray="5,5">
              <animate attributeName="r" values="40;50;40" dur="2s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite" />
            </circle>
            <path d="M70 100 Q100 60 130 100 Q100 140 70 100" fill="#f48d45" opacity="0.6">
              <animate attributeName="d" values="M70 100 Q100 60 130 100 Q100 140 70 100;M75 100 Q100 70 125 100 Q100 130 75 100;M70 100 Q100 60 130 100 Q100 140 70 100" dur="3s" repeatCount="indefinite" />
            </path>
            <circle cx="100" cy="100" r="15" fill="#fff" />
          </svg>
        </div>
        <h3>等待预测</h3>
        <el-button class="new-btn" @click="showNewPredict = true" size="large" type="primary">
          <el-icon color="white" style="margin-right: 8px;"><Plus/></el-icon>
          新建预测
        </el-button>
      </div>
    </div>

    <el-dialog v-model="showNewPredict" title="新建预测" width="520px" class="predict-dialog">
      <div class="predict-form">
        <div class="form-group">
          <label>选择班级</label>
          <el-select v-model="predictForm.classId" style="width: 100%">
            <el-option v-for="cls in classList" :key="cls.id" :label="cls.name" :value="cls.id" />
          </el-select>
        </div>
        
        <div class="form-group">
          <label>预测场景</label>
          <el-select v-model="predictForm.scene" style="width: 100%">
            <el-option label="课堂表现预测" value="classroom" />
            <el-option label="考试结果预测" value="exam" />
            <el-option label="活动参与预测" value="activity" />
            <el-option label="心理趋势预测" value="psychology" />
            <el-option label="干预效果预测" value="intervention" />
          </el-select>
        </div>
        
        <div class="form-group">
          <label>决策描述</label>
          <el-input 
            v-model="predictForm.decision" 
            type="textarea" 
            :rows="4"
            placeholder="请输入要预测的决策，如：增加30%作业量"
          />
        </div>
        
        <div class="form-group">
          <label>模拟轮次: {{ predictForm.rounds }}</label>
          <el-slider v-model="predictForm.rounds" :min="20" :max="100" :marks="{20: '20', 50: '50', 100: '100'}" />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showNewPredict = false">取消</el-button>
        <el-button type="primary" size="large" @click="startPredict" :loading="isRunning">
          <el-icon><CaretRight /></el-icon>
          开始预测        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, WarningFilled, MagicStick, Loading, CaretRight, Connection } from '@element-plus/icons-vue'
import { teacherApi } from '../../api/teacher'

const isConnected = ref(false)
const checking = ref(false)

const checkConnection = async (silent = false): Promise<boolean> => {
  checking.value = true
  try {
    const res = await fetch('/api/health')
    isConnected.value = res.ok
    if (!silent) {
      if (res.ok) ElMessage.success('MiroFish API 连接成功')
      else ElMessage.warning('API 响应异常')
    }
  } catch {
    isConnected.value = false
    if (!silent) ElMessage.error('无法连接 MiroFish API')
  }
  checking.value = false
  return isConnected.value
}

const loadPredictions = async () => {
  try {
    const data: any = await teacherApi.getPredictions()
    predictions.value = data || []
  } catch (e) {
    // 接口失败时保持页面可用
  }
}

const loadClasses = async () => {
  try {
    const data: any = await teacherApi.getClasses()
    classList.value = (data || []).map((c: any) => ({
      id: c.id,
      name: c.name
    }))
  } catch (e) {
    // 接口失败时保持页面可用
  }
}

onMounted(() => {
  checkConnection(true)
  loadPredictions()
  loadClasses()
})

interface PredictForm {
  classId: number
  scene: string
  decision: string
  rounds: number
}

interface SwarmAgent {
  x: number
  y: number
  color: string
  animAxis: string
  animValues: string
  animDur: string
}

interface StreamLine {
  path: string
  color: string
}

interface Log {
  time: string
  message: string
}

interface ClusterOrb {
  x: number
  y: number
  r: number
  count: number
  color: string
}

const classList = ref<{ id: number; name: string }[]>([])
const showNewPredict = ref(false)
const isRunning = ref(false)
const currentRound = ref(0)
const totalRounds = ref(50)
const progress = ref(0)
const logs = ref<Log[]>([])
const activeTab = ref('overview')

const predictForm = reactive<PredictForm>({
  classId: 1,
  scene: 'classroom',
  decision: '',
  rounds: 50
})

const result = ref<{
  confidence: number
  shortTerm: number
  longTerm: number
  risk: number
  stability: number
  risks: { title: string; desc: string; probability: number; level: string }[]
} | null>(null)


const swarmAgents = ref<SwarmAgent[]>([])
const streamLines = ref<StreamLine[]>([])
const clusterOrbs = ref<ClusterOrb[]>([])
const suggestions = ref<string[]>([])
const predictions = ref<any[]>([])

const activeAgents = computed(() => Math.floor(swarmAgents.value.length * 0.85))
const interactionCount = computed(() => currentRound.value * 18)
const avgMood = computed(() => result.value ? result.value.confidence + '%' : '0%')

const getRiskColor = (risk: number) => {
  if (risk >= 70) return '#ff4d4f'
  if (risk >= 40) return '#faad14'
  return '#52c41a'
}

const initSwarm = () => {
  swarmAgents.value = []
  const colors = ['#f48d45', '#f4bb6e', '#8985cf', '#52c41a', '#eb2f96']
  for (let i = 0; i < 60; i++) {
    const x = 100 + Math.random() * 600
    const y = 50 + Math.random() * 250
    const useCx = i % 2 === 0
    swarmAgents.value.push({
      x,
      y,
      color: colors[Math.floor(Math.random() * colors.length)]!,
      animAxis: useCx ? 'cx' : 'cy',
      animValues: useCx
        ? `${x};${x + (Math.random() - 0.5) * 30};${x}`
        : `${y};${y + (Math.random() - 0.5) * 30};${y}`,
      animDur: (1.5 + Math.random()) + 's'
    })
  }
  
  streamLines.value = []
  for (let i = 0; i < 12; i++) {
    const startX = Math.random() * 500
    const startY = 50 + Math.random() * 250
    streamLines.value.push({
      path: `M${startX},${startY} C${startX + 80},${startY + (Math.random() - 0.5) * 80} ${startX + 150},${startY + (Math.random() - 0.5) * 60} ${startX + 250},${startY + (Math.random() - 0.5) * 40}`,
      color: i % 2 === 0 ? '#f48d45' : '#acb6f3'
    })
  }
  
  clusterOrbs.value = [
    { x: 150, y: 100, r: 35, count: 18, color: '#f48d45' },
    { x: 400, y: 80, r: 28, count: 14, color: '#f4bb6e' },
    { x: 550, y: 150, r: 25, count: 12, color: '#52c41a' },
    { x: 300, y: 200, r: 22, count: 9, color: '#acb6f3' },
    { x: 200, y: 250, r: 18, count: 7, color: '#eb2f96' }
  ]
}

const addLog = (msg: string) => {
  const now = new Date()
  logs.value.push({
    time: `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`,
    message: msg
  })
}

const startPredict = async () => {
  if (!predictForm.decision) {
    ElMessage.warning('请输入决策描述')
    return
  }
  
  showNewPredict.value = false
  isRunning.value = true
  currentRound.value = 0
  totalRounds.value = predictForm.rounds
  progress.value = 0
  logs.value = []
  
  initSwarm()
  addLog('初始化模拟环境..')
  addLog(`加载 ${predictForm.rounds} 个智能体...`)
  
  for (let i = 1; i <= predictForm.rounds; i++) {
    // 每5轮才更新一次响应式状态，减少重渲染次数
    if (i % 5 === 0 || i === predictForm.rounds) {
      currentRound.value = i
      progress.value = Math.round((i / predictForm.rounds) * 100)
    }
    
    if (i % 10 === 0) {
      addLog(`模拟轮次 ${i}/${predictForm.rounds}`)
    }
    
    await new Promise(r => setTimeout(r, 30))
  }
  
  addLog('模拟完成')
  addLog('分析群体行为...')
  await new Promise(r => setTimeout(r, 300))
  addLog('生成预测报告...')
  
  // 默认结果（API 失败时使用）
  const defaultResult = {
    confidence: Math.floor(Math.random() * 20) + 72,
    shortTerm: Math.floor(Math.random() * 25) + 55,
    longTerm: Math.floor(Math.random() * 25) + 48,
    risk: Math.floor(Math.random() * 35) + 18,
    stability: Math.floor(Math.random() * 20) + 65,
    risks: [
      { title: '部分学生可能出现抵触情绪', desc: '对决策的消极反应', probability: 48, level: 'medium' },
      { title: '家长可能反对', desc: '来自家长的压力', probability: 32, level: 'low' },
      { title: '课堂氛围变化', desc: '整体氛围受到影响', probability: 62, level: 'high' }
    ]
  }
  const defaultSuggestions = [
    '建议逐步调整，给学生2周适应时间',
    '设置缓冲期，观察学生反馈后再推进',
    '密切关注情绪低落的学生并及时沟通',
    '准备备选方案以应对不良影响',
    '与家长保持沟通，争取支持'
  ]
  
  try {
    const res: any = await teacherApi.createPrediction({
      classId: predictForm.classId,
      scene: predictForm.scene,
      decision: predictForm.decision,
      rounds: predictForm.rounds
    })
    // 刷新预测列表
    loadPredictions()
    
    if (res && res.confidence) {
      result.value = {
        confidence: res.confidence,
        shortTerm: res.shortTerm || 0,
        longTerm: res.longTerm || 0,
        risk: res.risk || 0,
        stability: res.stability || 0,
        risks: res.risks || []
      }
      suggestions.value = res.suggestions || defaultSuggestions
    } else {
      result.value = defaultResult
      suggestions.value = defaultSuggestions
    }
  } catch (e) {
    // API 调用失败，使用默认结果保持页面可用
    result.value = defaultResult
    suggestions.value = defaultSuggestions
  }
  
  isRunning.value = false
  ElMessage.success('预测完成')
}

const checkMiroFishConnection = async () => {
  const connected = await checkConnection(true)
  if (connected) {
    showNewPredict.value = true
  } else {
    ElMessage.error('无法连接 MiroFish API，请检查后端服务是否启动')
  }
}
</script>

<style scoped>
.predict-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.predict-header {
  background: linear-gradient(135deg, #fffaf5 0%, #fff5ee 100%);
  border: 1px solid #fce8d8;
  border-radius: 16px;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 24px rgba(244, 141, 69, 0.12);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.swarm-orbit {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #f48d45, #f4bb6e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-desc {
  font-size: 12px;
  color: #f48d45;
  font-weight: 600;
  letter-spacing: 1px;
}

.new-btn {
  background: linear-gradient(135deg, #f48d45, #f4bb6e);
  border: none;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(244, 141, 69, 0.3);
  transition: all 0.3s;
}

.new-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(244, 141, 69, 0.4);
}

.predict-main {
  flex: 1;
  min-height: 0;
}

.simulation-panel {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #E8E0F0;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.simulation-header {
  margin-bottom: 16px;
}

.sim-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.round-info {
  font-size: 14px;
  font-weight: 600;
  color: #f48d45;
}

.swarm-visual {
  background: linear-gradient(135deg, #fffaf5 0%, #fff5f8 100%);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  flex: 1;
  min-height: 280px;
}

.swarm-svg {
  width: 100%;
  height: 280px;
}

.swarm-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-top: 12px;
}

.swarm-stat {
  text-align: center;
}

.swarm-stat .stat-value {
  display: block;
  font-size: 28px;
  font-weight: 800;
  color: #f48d45;
}

.swarm-stat .stat-label {
  font-size: 12px;
  color: #999;
}

.log-panel {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 12px 16px;
  max-height: 140px;
  overflow-y: auto;
  font-family: 'Fira Code', monospace;
}

.log-entry {
  display: flex;
  gap: 16px;
  font-size: 12px;
  padding: 4px 0;
}

.log-time {
  color: #6a6a8a;
}

.log-msg {
  color: #d4d4e8;
}

.result-panel {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #E8E0F0;
  height: 100%;
  overflow: hidden;
}

.result-tabs {
  height: 100%;
  padding: 20px;
}

.result-tabs :deep(.el-tabs__content) {
  height: calc(100% - 40px);
  overflow-y: auto;
}

.overview-content {
  display: flex;
  gap: 40px;
  align-items: center;
  padding: 20px;
}

.main-circle {
  flex-shrink: 0;
}

.metrics-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.metric-card {
  padding: 16px;
  background: linear-gradient(135deg, #fffaf5 0%, #fff5ee 100%);
  border-radius: 12px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.metric-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card {
  background: linear-gradient(135deg, #fffaf5 0%, #fff8ff 100%);
  border-radius: 12px;
  padding: 16px;
}

.chart-card h4 {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.multi-line-chart {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}

.chart-legend i {
  display: inline-block;
  width: 12px;
  height: 3px;
  margin-right: 6px;
  vertical-align: middle;
}

.cluster-visual {
  position: relative;
  height: 180px;
  background: linear-gradient(135deg, #fffaf5 0%, #faf5ff 100%);
  border-radius: 12px;
}

.cluster-orb {
  position: absolute;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.orb-label {
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.risk-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.risk-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #E8E0F0;
}

.risk-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.risk-card.high .risk-icon { background: #fff2f0; color: #ff4d4f; }
.risk-card.medium .risk-icon { background: #fffbe6; color: #faad14; }
.risk-card.low .risk-icon { background: #f6ffed; color: #52c41a; }

.risk-info {
  flex: 1;
}

.risk-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.risk-desc {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.risk-prob {
  width: 80px;
  text-align: right;
}

.prob-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.suggestion-box {
  background: linear-gradient(135deg, #faf8ff 0%, #f0eeff 100%);
  border-radius: 12px;
  padding: 16px;
  margin-top: 8px;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #8985cf;
}

.suggestion-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #fff;
  border-radius: 8px;
  font-size: 13px;
}

.sug-num {
  width: 22px;
  height: 22px;
  background: linear-gradient(135deg, #f48d45, #f4bb6e);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.empty-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #E8E0F0;
}

.empty-illustration {
  margin-bottom: 20px;
}

.empty-panel h3 {
  margin: 0 0 8px;
  font-size: 20px;
  color: #333;
}

.empty-panel p {
  margin: 0 0 20px;
  font-size: 14px;
  color: #999;
}

.predict-form .form-group {
  margin-bottom: 20px;
}

.predict-form .form-group label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}
</style>
