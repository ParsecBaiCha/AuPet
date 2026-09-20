<template>
  <div class="ai-chat-monitor">
    <!-- 筛选条 -->
    <el-card shadow="hover" class="filter-card">
      <div class="filter-bar">
        <div class="filter-item">
          <span class="filter-label">标记</span>
          <el-radio-group v-model="flag">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="mood">情绪低落</el-radio-button>
            <el-radio-button value="bully">关系冲突</el-radio-button>
            <el-radio-button value="study">学业压力</el-radio-button>
            <el-radio-button value="none">未命中</el-radio-button>
          </el-radio-group>
        </div>

        <div class="filter-item">
          <span class="filter-label">仅看未处理</span>
          <el-switch v-model="onlyUnhandled" />
        </div>

        <div class="filter-item">
          <span class="filter-label">时间范围</span>
          <el-radio-group v-model="range">
            <el-radio-button value="7">近 7 天</el-radio-button>
            <el-radio-button value="30">近 30 天</el-radio-button>
          </el-radio-group>
        </div>

        <el-button type="primary" :loading="listLoading" @click="loadLogs">
          <el-icon><Refresh /></el-icon>
          <span>刷新</span>
        </el-button>

        <span class="filter-tip">当前筛选共 {{ logs.length }} 条对话</span>
      </div>
    </el-card>

    <!-- 主体左右两栏 -->
    <div class="monitor-body">
      <!-- 左：对话列表 -->
      <el-card shadow="hover" class="list-card">
        <template #header>
          <div class="card-header">
            <el-icon><ChatLineRound /></el-icon>
            <span>对话列表</span>
          </div>
        </template>

        <div v-loading="listLoading" class="chat-list">
          <el-empty
            v-if="!logs.length"
            description="当前筛选条件下没有对话记录"
            :image-size="80"
          />
          <div
            v-for="item in logs"
            :key="item.id"
            class="chat-item"
            :class="{ active: item.id === activeId }"
            @click="selectLog(item)"
          >
            <div class="chat-item-top">
              <span class="chat-name">{{ item.studentName }}</span>
              <el-tag size="small" :type="item.flagType === 'none' ? 'info' : 'warning'">
                {{ item.flagText || '常规' }}
              </el-tag>
            </div>
            <div class="chat-item-content">{{ item.content || '（无内容）' }}</div>
            <div class="chat-item-bottom">
              <span class="chat-meta">{{ item.className || '未分班' }} · {{ item.createdAt || '—' }}</span>
              <el-tag size="small" :type="item.handled ? 'success' : 'danger'">
                {{ item.handled ? '已处理' : '未处理' }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 右：详情 -->
      <el-card shadow="hover" class="detail-card">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>对话详情</span>
          </div>
        </template>

        <div v-loading="detailLoading" class="detail-body">
          <el-empty v-if="!activeId" description="请从左侧选择一条对话" :image-size="90" />
          <template v-else-if="detail">
            <div class="detail-head">
              <span class="detail-name">{{ detail.studentName }}</span>
              <span class="detail-meta">班级：{{ detail.className || '未分班' }}</span>
              <span class="detail-meta">时间：{{ detail.createdAt || '—' }}</span>
              <el-tag size="small" :type="detail.flagType === 'none' ? 'info' : 'warning'">
                {{ detail.flagText || '常规' }}
              </el-tag>
              <el-tag size="small" :type="detail.handled ? 'success' : 'danger'">
                {{ detail.handled ? '已处理' : '未处理' }}
              </el-tag>
            </div>

            <div class="bubble-list">
              <div
                v-for="msg in detail.context"
                :key="msg.id"
                class="bubble-row"
                :class="msg.role === 'user' ? 'right' : 'left'"
              >
                <div class="bubble" :class="msg.role === 'user' ? 'bubble-user' : 'bubble-ai'">
                  <div class="bubble-role">{{ msg.role === 'user' ? '学生' : 'AI 伙伴' }}</div>
                  <div class="bubble-text">{{ msg.content }}</div>
                  <div class="bubble-time">{{ msg.time || '' }}</div>
                </div>
              </div>
              <div v-if="!detail.context.length" class="bubble-empty">该对话没有可展示的上下文</div>
            </div>

            <div class="detail-actions">
              <el-button type="primary" @click="openFocusDialog">转入关注名单</el-button>
              <el-button @click="handleIgnore">忽略本次</el-button>
            </div>
          </template>
          <el-empty v-else description="对话详情加载失败，请重新选择" :image-size="90" />
        </div>
      </el-card>
    </div>

    <!-- 转入关注名单对话框 -->
    <el-dialog v-model="focusVisible" title="转入关注名单" width="440px">
      <el-form label-width="80px">
        <el-form-item label="严重程度">
          <el-radio-group v-model="focusForm.severity">
            <el-radio value="轻度">轻度</el-radio>
            <el-radio value="中度">中度</el-radio>
            <el-radio value="重度">重度</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="focusForm.remark"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="可填写观察到的表现或后续跟进计划（选填）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="focusVisible = false">取消</el-button>
        <el-button type="primary" :loading="handling" @click="confirmFocus">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { teacherApi } from '../../api/teacher'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, ChatLineRound, Document } from '@element-plus/icons-vue'

interface ChatLogRow {
  id: number
  studentId: number
  studentName: string
  className: string
  classId: number
  flagType: string
  flagText: string
  handled: boolean
  content: string
  reply: string
  createdAt: string
}

interface ChatContextItem {
  id: number
  role: string
  content: string
  time: string
}

interface ChatDetail {
  id: number
  studentId: number
  studentName: string
  className: string
  flagType: string
  flagText: string
  handled: boolean
  createdAt: string
  context: ChatContextItem[]
}

const flag = ref<string>('all')
const onlyUnhandled = ref(false)
const range = ref<string>('7')

const listLoading = ref(false)
const detailLoading = ref(false)
const handling = ref(false)
const logs = ref<ChatLogRow[]>([])
const activeId = ref<number | null>(null)
const detail = ref<ChatDetail | null>(null)

const focusVisible = ref(false)
const focusForm = ref({ severity: '轻度', remark: '' })

let requestSeq = 0

const toNumber = (value: unknown, fallback = 0): number => {
  const num = Number(value)
  return Number.isFinite(num) ? num : fallback
}

const normalizeLog = (raw: any): ChatLogRow => ({
  id: toNumber(raw?.id),
  studentId: toNumber(raw?.studentId),
  studentName: raw?.studentName || '未知学生',
  className: raw?.className || '',
  classId: toNumber(raw?.classId),
  flagType: raw?.flagType || 'none',
  flagText: raw?.flagText || '常规',
  handled: !!raw?.handled,
  content: raw?.content || '',
  reply: raw?.reply || '',
  createdAt: raw?.createdAt || '',
})

const normalizeDetail = (raw: any): ChatDetail | null => {
  if (!raw || typeof raw !== 'object' || raw.id === undefined || raw.id === null) return null
  return {
    id: toNumber(raw.id),
    studentId: toNumber(raw.studentId),
    studentName: raw.studentName || '未知学生',
    className: raw.className || '',
    flagType: raw.flagType || 'none',
    flagText: raw.flagText || '常规',
    handled: !!raw.handled,
    createdAt: raw.createdAt || '',
    context: Array.isArray(raw.context)
      ? raw.context.map((m: any): ChatContextItem => ({
          id: toNumber(m?.id),
          role: m?.role === 'assistant' ? 'assistant' : 'user',
          content: m?.content || '',
          time: m?.time || '',
        }))
      : [],
  }
}

const loadLogs = async () => {
  const seq = ++requestSeq
  listLoading.value = true
  try {
    const res: any = await teacherApi.getAIChatLogs({
      flag: flag.value,
      handled: onlyUnhandled.value ? '0' : '',
      range: range.value,
    })
    if (seq !== requestSeq) return
    logs.value = Array.isArray(res) ? res.map(normalizeLog) : []
  } catch (e) {
    if (seq !== requestSeq) return
    logs.value = []
  } finally {
    if (seq === requestSeq) listLoading.value = false
  }
}

const loadDetail = async (id: number) => {
  detailLoading.value = true
  try {
    const res: any = await teacherApi.getAIChatLogDetail(id)
    detail.value = normalizeDetail(res)
  } catch (e) {
    detail.value = null
  } finally {
    detailLoading.value = false
  }
}

const selectLog = (item: ChatLogRow) => {
  activeId.value = item.id
  detail.value = null
  void loadDetail(item.id)
}

const openFocusDialog = () => {
  if (!activeId.value) return
  focusForm.value = { severity: '轻度', remark: '' }
  focusVisible.value = true
}

const confirmFocus = async () => {
  const id = activeId.value
  if (!id) return
  handling.value = true
  try {
    const res: any = await teacherApi.handleAIChatLog(id, {
      action: 'focus',
      severity: focusForm.value.severity,
      remark: focusForm.value.remark,
    })
    ElMessage.success(res?.message || '已转入关注名单')
    focusVisible.value = false
    await loadLogs()
    await loadDetail(id)
  } catch (e) {
    // 403 / 404 等错误已由 axios 拦截器提示，这里只做兜底
  } finally {
    handling.value = false
  }
}

const handleIgnore = async () => {
  const id = activeId.value
  if (!id) return
  try {
    await ElMessageBox.confirm('确定忽略本次对话吗？该对话将标记为已处理，不写入关注名单。', '提示', {
      type: 'warning',
      confirmButtonText: '确定忽略',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return
  }
  handling.value = true
  try {
    const res: any = await teacherApi.handleAIChatLog(id, { action: 'ignore' })
    ElMessage.success(res?.message || '已忽略本次对话')
    await loadLogs()
    await loadDetail(id)
  } catch (e) {
    // 403 / 404 等错误已由 axios 拦截器提示，这里只做兜底
  } finally {
    handling.value = false
  }
}

watch(
  [flag, onlyUnhandled, range],
  () => {
    void loadLogs()
  },
  { immediate: true }
)
</script>

<style scoped>
.ai-chat-monitor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card :deep(.el-card__body) {
  padding: 16px 20px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
}

.filter-tip {
  margin-left: auto;
  font-size: 13px;
  color: #909399;
}

.monitor-body {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.list-card {
  width: 360px;
  flex-shrink: 0;
}

.detail-card {
  flex: 1;
  min-width: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.chat-list {
  max-height: calc(100vh - 330px);
  min-height: 220px;
  overflow-y: auto;
}

.chat-item {
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #edebf7;
  border-radius: 10px;
  background: #fafaff;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-item:hover {
  border-color: #acb6f3;
}

.chat-item.active {
  border-color: #8985cf;
  background: #f0f0ff;
  box-shadow: 0 2px 10px rgba(137, 133, 207, 0.25);
}

.chat-item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.chat-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.chat-item-content {
  margin: 8px 0;
  font-size: 13px;
  line-height: 1.5;
  color: #606266;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chat-item-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.chat-meta {
  font-size: 12px;
  color: #909399;
}

.detail-body {
  min-height: 260px;
}

.detail-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #edebf7;
}

.detail-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.detail-meta {
  font-size: 13px;
  color: #606266;
}

.bubble-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 420px;
  overflow-y: auto;
  padding: 16px 4px;
}

.bubble-row {
  display: flex;
}

.bubble-row.right {
  justify-content: flex-end;
}

.bubble-row.left {
  justify-content: flex-start;
}

.bubble {
  max-width: 72%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.bubble-user {
  background: #8985cf;
  color: #fff;
  border-top-right-radius: 2px;
}

.bubble-ai {
  background: #f0f0ff;
  color: #333;
  border-top-left-radius: 2px;
}

.bubble-role {
  font-size: 11px;
  opacity: 0.85;
  margin-bottom: 4px;
}

.bubble-time {
  margin-top: 6px;
  font-size: 11px;
  opacity: 0.75;
  text-align: right;
}

.bubble-empty {
  padding: 24px 0;
  text-align: center;
  font-size: 13px;
  color: #909399;
}

.detail-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #edebf7;
}

@media (max-width: 1200px) {
  .monitor-body {
    flex-direction: column;
  }

  .list-card {
    width: 100%;
  }

  .chat-list {
    max-height: 360px;
  }
}

@media (max-width: 768px) {
  .filter-tip {
    margin-left: 0;
  }
}
</style>
