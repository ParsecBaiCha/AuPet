<template>
  <div class="agent-container">
    <div class="agent-header">
      <div class="header-left">
        <div class="logo-section">
          <div class="fish-tank">
            <svg viewBox="0 0 200 80" width="120" height="48">
              <defs>
                <linearGradient id="waterGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#acb6f3;stop-opacity:0.3" />
                  <stop offset="100%" style="stop-color:#8985cf;stop-opacity:0.1" />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <rect x="0" y="0" width="200" height="80" rx="40" fill="url(#waterGrad)" />
              <g class="fish-group">
                <path class="fish fish1" d="M30 40 Q40 30 50 40 Q40 50 30 40 M50 40 L60 35 Q50 40 60 45 L50 40" fill="#8985cf" filter="url(#glow)">
                  <animate attributeName="transform" type="translate" values="0,0; 80,0; 0,0" dur="6s" repeatCount="indefinite" />
                </path>
                <path class="fish fish2" d="M30 40 Q40 30 50 40 Q40 50 30 40 M50 40 L60 35 Q50 40 60 45 L50 40" fill="#f48d45" filter="url(#glow)">
                  <animate attributeName="transform" type="translate" values="30,10; 110,-10; 30,10" dur="7s" repeatCount="indefinite" />
                </path>
                <path class="fish fish3" d="M30 40 Q40 30 50 40 Q40 50 30 40 M50 40 L60 35 Q50 40 60 45 L50 40" fill="#f4bb6e" filter="url(#glow)">
                  <animate attributeName="transform" type="translate" values="60,-5; 140,5; 60,-5" dur="5s" repeatCount="indefinite" />
                </path>
              </g>
              <circle cx="160" cy="40" r="3" fill="#fff" opacity="0.5">
                <animate attributeName="opacity" values="0.5;1;0.5" dur="1s" repeatCount="indefinite" />
              </circle>
            </svg>
          </div>
          <div>
            <h2 class="page-title">群体智能角色网络</h2>
            <span class="page-desc">MiroFish&DeBERTa Intelligence</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-button circle :type="isConnected ? 'success' : 'default'" @click="checkConnection" :loading="checking">
          <el-icon><Connection /></el-icon>
        </el-button>
      </div>
    </div>

    <div class="agent-main">
      <aside class="config-panel">
        <div class="panel-card config-card">
          <div class="panel-title">
            <el-icon><Setting /></el-icon>
            智能体配置          </div>

          <div class="form-group">
            <label>选择班级</label>
            <el-select v-model="config.classId" placeholder="请选择班级" style="width: 100%">
              <el-option v-for="cls in classList" :key="cls.id" :label="cls.name" :value="cls.id" />
            </el-select>
          </div>

          <div class="form-group">
            <label>智能体数量 {{ config.agentCount }}</label>
            <el-slider v-model="config.agentCount" :min="5" :max="50" :show-stops="true" />
          </div>

          <div class="form-group">
            <label>生成模式</label>
            <el-radio-group v-model="config.mode" class="mode-group">
              <el-radio-button label="auto">自动</el-radio-button>
              <el-radio-button label="manual">手动</el-radio-button>
            </el-radio-group>
          </div>

          <el-button type="primary" @click="generateAgents" :loading="generating" class="btn-generate" size="large">
            <el-icon><CaretRight /></el-icon>
            生成智能体          </el-button>
        </div>

        <div class="panel-card stats-card">
          <div class="stat-grid">
            <div class="stat-box">
              <span class="stat-num">{{ agents.length }}</span>
              <span class="stat-label">智能体</span>
            </div>
            <div class="stat-box">
              <span class="stat-num">{{ links.length }}</span>
              <span class="stat-label">连接</span>
            </div>
            <div class="stat-box">
              <span class="stat-num">{{ clusterCount }}</span>
              <span class="stat-label">聚类</span>
            </div>
          </div>
        </div>
      </aside>

      <main class="content-area">
        <div class="network-container">
          <div class="network-header">
            <h3>智能体关系网络</h3>
            <div class="network-controls">
              <el-button-group>
                <el-button size="small" @click="zoomIn"><el-icon><ZoomIn /></el-icon></el-button>
                <el-button size="small" @click="zoomOut"><el-icon><ZoomOut /></el-icon></el-button>
                <el-button size="small" @click="resetView"><el-icon><Refresh /></el-icon></el-button>
              </el-button-group>
            </div>
          </div>
          
          <div class="network-canvas" ref="networkCanvas">
            <svg :viewBox="`0 0 ${canvasSize} ${canvasSize}`" class="network-svg">
              <defs>
                <radialGradient id="nodeGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" style="stop-color:#8985cf;stop-opacity:0.8" />
                  <stop offset="100%" style="stop-color:#8985cf;stop-opacity:0" />
                </radialGradient>
                <filter id="blurFilter">
                  <feGaussianBlur stdDeviation="3" />
                </filter>
              </defs>
              
              <rect width="100%" height="100%" fill="url(#bgGrad)" />
              <g v-for="link in links" :key="link.id" class="link-line">
                <line 
                  :x1="nodePositions[link.source]?.x || 300" :y1="nodePositions[link.source]?.y || 300"
                  :x2="nodePositions[link.target]?.x || 300" :y2="nodePositions[link.target]?.y || 300"
                  stroke="#E8E0F0" 
                  :stroke-width="link.strength * 1.5"
                  opacity="0.6"
                />
              </g>
              
              <g v-for="agent in agents" :key="agent.id" class="node-group"
                @click="selectAgent(agent)"
                @mouseenter="hoveredAgent = agent"
                @mouseleave="hoveredAgent = null"
                :class="{ selected: selectedAgent?.id === agent.id }"
              >
                <circle 
                  :cx="nodePositions[agent.id]?.x || 300" 
                  :cy="nodePositions[agent.id]?.y || 300" 
                  r="24" 
                  fill="url(#nodeGlow)"
                  :stroke="agent.color"
                  stroke-width="3"
                  class="node-circle"
                />
                <text 
                  :x="nodePositions[agent.id]?.x || 300" 
                  :y="(nodePositions[agent.id]?.y || 300) + 5" 
                  text-anchor="middle" 
                  fill="#fff"
                  font-size="14"
                  font-weight="bold"
                >{{ agent.name[0] }}</text>
              </g>
            </svg>
            
            <transition name="tooltip-fade">
              <div class="agent-tooltip-float" v-if="hoveredAgent" :style="getTooltipStyle">
                <div class="tooltip-header">
                  <span class="tooltip-name">{{ hoveredAgent.name }}</span>
                  <el-tag size="small" :type="getLevelType(hoveredAgent.level)">{{ hoveredAgent.level }}级</el-tag>
                </div>
                <div class="tooltip-divider"></div>
                <div class="tooltip-row">
                  <span class="tooltip-label">性格</span>
                  <span class="tooltip-value">{{ hoveredAgent.personality }}</span>
                </div>
                <div class="tooltip-row">
                  <span class="tooltip-label">情绪</span>
                  <el-tag size="small" :type="getMoodType(hoveredAgent.mood)">{{ hoveredAgent.mood }}</el-tag>
                </div>
                <div class="tooltip-row">
                  <span class="tooltip-label">决策</span>
                  <span class="tooltip-value">{{ hoveredAgent.decisionStyle }}</span>
                </div>
                <div class="tooltip-row">
                  <span class="tooltip-label">社交</span>
                  <div class="tooltip-bar">
                    <div class="tooltip-bar-fill" :style="{ width: hoveredAgent.social + '%', background: hoveredAgent.color }"></div>
                    <span class="tooltip-bar-text">{{ hoveredAgent.social }}</span>
                  </div>
                </div>
                <div class="tooltip-row">
                  <span class="tooltip-label">影响力</span>
                  <span class="tooltip-stars">{{ '★'.repeat(hoveredAgent.influence) }}{{ '☆'.repeat(5 - hoveredAgent.influence) }}</span>
                </div>
              </div>
            </transition>
            
            <div class="network-particles">
              <div v-for="p in particles" :key="p.id" class="particle" :style="p.style"></div>
            </div>
          </div>
        </div>

        <transition name="slide-fade">
          <div class="agent-detail" v-if="selectedAgent">
            <div class="detail-header">
              <div class="detail-title">
                <div class="detail-avatar" :style="{ background: selectedAgent.color }">
                  {{ selectedAgent.name[0] }}
                </div>
                <div>
                  <h3>{{ selectedAgent.name }}</h3>
                  <el-tag size="small" :type="getLevelType(selectedAgent.level)">{{ selectedAgent.level }}级</el-tag>
                </div>
              </div>
              <el-button text @click="selectedAgent = null"><el-icon><Close /></el-icon></el-button>
            </div>
            <div class="detail-content">
              <div class="detail-item">
                <span class="label">性格类型</span>
                <span class="value">{{ selectedAgent.personality }}</span>
              </div>
              <div class="detail-item">
                <span class="label">影响力</span>
                <el-rate v-model="selectedAgent.influence" disabled size="small" />
              </div>
              <div class="detail-item">
                <span class="label">情绪状态</span>
                <el-tag :type="getMoodType(selectedAgent.mood)" size="small">{{ selectedAgent.mood }}</el-tag>
              </div>
              <div class="detail-item">
                <span class="label">社交倾向</span>
                <el-progress :percentage="selectedAgent.social" :stroke-width="6" :show-text="false" />
                <span class="progress-text">{{ selectedAgent.social }}%</span>
              </div>
              <div class="detail-item">
                <span class="label">决策风格</span>
                <span class="value">{{ selectedAgent.decisionStyle }}</span>
              </div>
            </div>
          </div>
        </transition>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection, Setting, User, CaretRight, ZoomIn, ZoomOut, Refresh, Close } from '@element-plus/icons-vue'
import { teacherApi } from '../../api/teacher'

interface Agent {
  id: number
  name: string
  personality: string
  level: string
  color: string
  influence: number
  mood: string
  social: number
  decisionStyle: string
}

interface Link {
  id: number
  source: number
  target: number
  strength: number
}

const classList = ref<{ id: number; name: string }[]>([])

const config = reactive({
  classId: 1,
  agentCount: 20,
  mode: 'auto'
})

const agents = ref<Agent[]>([])
const links = ref<Link[]>([])
const selectedAgent = ref<Agent | null>(null)
const networkCanvas = ref<HTMLElement | null>(null)
const hoveredAgent = ref<Agent | null>(null)
const checking = ref(false)
const generating = ref(false)
const isConnected = ref(false)

const canvasSize = 600

const clusterCount = computed(() => {
  const clusters = new Set(agents.value.map(a => a.personality))
  return clusters.size
})

// 预计算粒子位置，避免模板中 Math.random() 导致无限重渲染
const particles = Array.from({ length: 20 }, (_, i) => ({
  id: i,
  style: {
    left: Math.random() * 100 + '%',
    animationDelay: Math.random() * 5 + 's',
    animationDuration: (3 + Math.random() * 4) + 's'
  }
}))

// 预计算所有节点位置，避免模板中反复调用 getNodePos
const nodePositions = computed(() => {
  const map: Record<number, { x: number; y: number }> = {}
  const list = agents.value
  for (let idx = 0; idx < list.length; idx++) {
    const agent = list[idx]
    const angle = (idx / Math.max(list.length, 1)) * Math.PI * 2
    const r = 150 + (idx % 3) * 50
    map[agent.id] = {
      x: 300 + Math.cos(angle + idx * 0.2) * r,
      y: 300 + Math.sin(angle + idx * 0.2) * r
    }
  }
  return map
})

const colors = ['#8985cf', '#f48d45', '#f4bb6e', '#52c41a', '#1890ff', '#eb2f96']
const personalities = ['活泼型', '内向型', '领袖型', '跟随型', '创新型', '保守型']
const moods = ['积极', '平静', '焦虑', '低落', '兴奋']
const decisionStyles = ['民主型', '权威型', '回避型', '情感型', '理性型']

const getNodePos = (id: number) => {
  return nodePositions.value[id] || { x: 300, y: 300 }
}

const getLevelType = (level: string) => {
  const map: Record<string, string> = { S: 'danger', A: 'warning', B: 'success', C: 'info' }
  return map[level] || 'info'
}

const getMoodType = (mood: string) => {
  const map: Record<string, string> = { '积极': 'success', '平静': 'info', '焦虑': 'warning', '低落': 'danger', '兴奋': 'warning' }
  return map[mood] || 'info'
}

const getTooltipStyle = computed(() => {
  if (!hoveredAgent.value) return {}
  const pos = getNodePos(hoveredAgent.value.id)
  const canvas = networkCanvas.value
  if (!canvas) return { left: pos.x + 'px', top: (pos.y - 120) + 'px' }
  
  const rect = canvas.getBoundingClientRect()
  const scaleX = rect.width / canvasSize
  const scaleY = rect.height / canvasSize
  
  const tooltipWidth = 230
  let left = pos.x * scaleX - tooltipWidth / 2
  let top = pos.y * scaleY - 140
  
  // 防止超出左侧
  if (left < 10) left = 10
  // 防止超出右侧
  if (left + tooltipWidth > rect.width - 10) {
    left = rect.width - tooltipWidth - 10
  }
  // 防止超出顶部
  if (top < 10) {
    top = pos.y * scaleY + 40
  }
  
  return {
    left: left + 'px',
    top: top + 'px'
  }
})

const checkConnection = async (silent = false) => {
  checking.value = true
  try {
    const res = await fetch('/api/health')
    isConnected.value = res.ok
    if (!silent) {
      if (res.ok) ElMessage.success('MiroFish&DeBERTa API 连接成功')
      else ElMessage.warning('API 响应异常')
    }
  } catch {
    isConnected.value = false
    if (!silent) ElMessage.error('无法连接 MiroFish&DeBERTa API')
  }
  checking.value = false
}

const generateLinks = () => {
  links.value = []
  const count = Math.floor(agents.value.length * 1.2)
  
  for (let i = 0; i < count; i++) {
    const sourceIdx = Math.floor(Math.random() * agents.value.length)
    const targetIdx = Math.floor(Math.random() * agents.value.length)
    if (sourceIdx !== targetIdx) {
      links.value.push({
        id: i,
        source: agents.value[sourceIdx]!.id,
        target: agents.value[targetIdx]!.id,
        strength: Math.random() * 0.8 + 0.2
      })
    }
  }
}

const generateAgents = () => {
  generating.value = true
  
  const names = ['张小明', '李小红', '王小强', '陈小花', '刘小杰', '赵小琳', '周小华', '吴小军', '孙小勇', '郑小芳',
    '钱小明', '冯小红', '陈小军', '褚小琳', '卫小芳', '蒋小杰', '沈小勇', '韩小花', '杨小华', '朱小强',
    '周小明', '吴小红', '郑小军', '王小琳', '冯小芳', '陈小杰', '褚小勇', '卫小花', '蒋小华', '沈小强',
    '韩小明', '杨小红', '朱小军', '秦小琳', '尤小芳', '许小杰', '何小勇', '吕小花', '施小华', '张小强']
  
  agents.value = []
  for (let i = 0; i < config.agentCount; i++) {
    const levelRoll = Math.random()
    let level: string
    if (levelRoll < 0.1) level = 'S'
    else if (levelRoll < 0.3) level = 'A'
    else if (levelRoll < 0.7) level = 'B'
    else level = 'C'
    
    agents.value.push({
      id: i + 1,
      name: names[i] || `学生${i + 1}`,
      personality: personalities[Math.floor(Math.random() * personalities.length)] || '活泼开朗',
      level,
      color: colors[Math.floor(Math.random() * colors.length)] || '#8985cf',
      influence: Math.floor(Math.random() * 5) + 1,
      mood: moods[Math.floor(Math.random() * moods.length)] || '积极',
      social: Math.floor(Math.random() * 100),
      decisionStyle: decisionStyles[Math.floor(Math.random() * decisionStyles.length)] || '民主型'
    })
  }
  
  generateLinks()
  
  ElMessage.success(`已生成 ${config.agentCount} 个智能体`)
  generating.value = false
}

const selectAgent = (agent: Agent) => {
  selectedAgent.value = selectedAgent.value?.id === agent.id ? null : agent
}

const zoomIn = () => ElMessage.info('放大')
const zoomOut = () => ElMessage.info('缩小')
const resetView = () => {
  generateLinks()
  ElMessage.success('已重置视图')
}

const loadRoleNetwork = async () => {
  try {
    const data: any = await teacherApi.getRoleNetwork()
    if (data.agents) {
      agents.value = data.agents.map((a: any) => ({
        id: a.id,
        name: a.name,
        personality: a.role || a.personality || '未知',
        level: a.level || 'B',
        color: a.color || '#8985cf',
        influence: a.influence || 3,
        mood: a.mood || '平静',
        social: a.social || 50,
        decisionStyle: a.decisionStyle || '民主型'
      }))
    }
    if (data.links) {
      links.value = data.links.map((l: any, idx: number) => ({
        id: idx,
        source: l.source,
        target: l.target,
        strength: l.strength
      }))
    }
  } catch (e) {
    // 接口失败时保持页面可用，使用默认空值
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
  loadRoleNetwork()
  loadClasses()
})
</script>

<style scoped>
.agent-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.agent-header {
  background: linear-gradient(135deg, #fff 0%, #f8f7ff 100%);
  border: 1px solid #E8E0F0;
  border-radius: 16px;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(137, 133, 207, 0.1);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.fish-tank {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  background: linear-gradient(135deg, #faf8ff 0%, #f0eeff 100%);
  padding: 8px;
}

.fish-tank svg {
  display: block;
}

@keyframes swim {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(20px); }
}

.fish {
  animation: swim 3s ease-in-out infinite;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #8985cf, #acb6f3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-desc {
  font-size: 12px;
  color: #acb6f3;
  font-weight: 600;
  letter-spacing: 1px;
}

.agent-main {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
}

.config-panel {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex-shrink: 0;
}

.panel-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #E8E0F0;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(137, 133, 207, 0.08);
}

.config-card {
  background: linear-gradient(135deg, #fff 0%, #faf8ff 100%);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.panel-title .el-icon {
  color: #8985cf;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.mode-group {
  width: 100%;
}

.mode-group :deep(.el-radio-button) {
  flex: 1;
}

.mode-group :deep(.el-radio-button__inner) {
  width: 100%;
}

.btn-generate {
  width: 100%;
  height: 44px;
  background: linear-gradient(135deg, #8985cf, #acb6f3);
  border: none;
  font-size: 15px;
  font-weight: 600;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(137, 133, 207, 0.3);
  transition: all 0.3s;
}

.btn-generate:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(137, 133, 207, 0.4);
}

.stats-card {
  background: linear-gradient(135deg, #8985cf, #acb6f3);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-box {
  text-align: center;
  padding: 12px 8px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
}

.stat-num {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: rgba(255,255,255,0.8);
  margin-top: 4px;
}

.agent-list {
  max-height: 240px;
}

.agent-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 8px;
}

.agent-item:hover {
  background: linear-gradient(135deg, #f8f7ff 0%, #f0eeff 100%);
  transform: translateX(4px);
}

.agent-item.active {
  background: linear-gradient(135deg, #8985cf, #acb6f3);
}

.agent-item.active .agent-name,
.agent-item.active .agent-personality {
  color: #fff !important;
}

.agent-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.agent-personality {
  display: block;
  font-size: 11px;
  color: #999;
}

.content-area {
  flex: 1;
  display: flex;
  gap: 16px;
}

.network-container {
  flex: 1;
  height: 600px;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #E8E0F0;
  padding: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(137, 133, 207, 0.08);
}

.network-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.network-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.network-canvas {
  flex: 1;
  min-height: 400px;
  background: linear-gradient(135deg, #faf8ff 0%, #f5f3ff 100%);
  border-radius: 16px;
  overflow: visible;
  position: relative;
}

.network-svg {
  width: 100%;
  height: 100%;
}

.node-group {
  cursor: pointer;
  transition: all 0.3s;
}

.node-group:hover .node-circle {
  filter: drop-shadow(0 0 12px currentColor);
}

.node-group.selected .node-circle {
  stroke-width: 4;
  filter: drop-shadow(0 0 16px #8985cf);
}

.network-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #acb6f3;
  border-radius: 50%;
  opacity: 0.4;
  animation: float 5s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0; }
  50% { transform: translateY(-100px) rotate(180deg); opacity: 0.6; }
}

.agent-detail {
  width: 280px;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #E8E0F0;
  padding: 20px;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(137, 133, 207, 0.1);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}

.detail-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #faf8ff;
  border-radius: 10px;
}

.detail-item .label {
  font-size: 12px;
  color: #999;
}

.detail-item .value {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  color: #8985cf;
  margin-left: 8px;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: all 0.2s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  transform: translateY(8px);
  opacity: 0;
}

.agent-tooltip-float {
  position: absolute;
  min-width: 200px;
  max-width: 230px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
  border-radius: 12px;
  border: 1px solid rgba(137, 133, 207, 0.4);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 16px rgba(137, 133, 207, 0.2);
  padding: 14px 16px;
  pointer-events: none;
  z-index: 9999;
  backdrop-filter: blur(8px);
  transform: translateX(-50%);
}

.agent-tooltip-float .tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.agent-tooltip-float .tooltip-name {
  font-weight: 600;
  font-size: 14px;
  color: #fff;
}

.agent-tooltip-float .tooltip-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.12);
  margin: 8px 0;
}

.agent-tooltip-float .tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.agent-tooltip-float .tooltip-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.agent-tooltip-float .tooltip-value {
  font-size: 12px;
  color: #fff;
  font-weight: 500;
}

.agent-tooltip-float .tooltip-bar {
  position: relative;
  width: 80px;
  height: 8px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 4px;
  overflow: hidden;
}

.agent-tooltip-float .tooltip-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.agent-tooltip-float .tooltip-bar-text {
  position: absolute;
  right: 0;
  top: -16px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
}

.agent-tooltip-float .tooltip-stars {
  font-size: 12px;
  color: #f4bb6e;
  letter-spacing: 2px;
}
</style>
