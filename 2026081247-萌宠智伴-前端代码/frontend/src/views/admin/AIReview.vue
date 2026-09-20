<template>
  <div class="ai-review">
    <el-tabs v-model="activeTab" class="review-tabs" @tab-change="handleTabChange">
      <!-- 学生对话 -->
      <el-tab-pane name="chat">
        <template #label>
          <span class="tab-label">
            学生对话
            <el-tag size="small" class="tab-count" :type="pendingChats > 0 ? 'warning' : 'info'">{{ pendingChats }}</el-tag>
          </span>
        </template>

        <el-card class="tab-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>学生对话审核</span>
              <el-button text type="primary" :loading="loadingReviews" @click="loadReviews">刷新</el-button>
            </div>
          </template>

          <el-table
            :data="chats"
            v-loading="loadingReviews"
            border
            empty-text="暂无需要审核的学生对话"
            style="width: 100%"
          >
            <el-table-column prop="studentName" label="学生" width="100" />
            <el-table-column prop="className" label="班级" width="140" />
            <el-table-column label="命中标记" width="110">
              <template #default="{ row }">
                <el-tag size="small" type="warning">{{ row.flagText || '其他' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="对话内容" min-width="240" show-overflow-tooltip />
            <el-table-column prop="createdAt" label="时间" width="150" />
            <el-table-column label="审核状态" width="200">
              <template #default="{ row }">
                <el-tag v-if="row.reviewResult" size="small" :type="reviewTagType(row.reviewResult)">
                  {{ row.reviewText || row.reviewResult }}
                </el-tag>
                <el-tag v-else size="small" type="danger" effect="plain">待审核</el-tag>
                <div v-if="row.reviewRemark" class="review-remark">{{ row.reviewRemark }}</div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="210" fixed="right">
              <template #default="{ row }">
                <template v-if="!row.reviewResult">
                  <el-button size="small" type="success" @click="handleApprove('chat', row)">通过</el-button>
                  <el-button size="small" type="warning" @click="openReject('chat', row)">驳回</el-button>
                  <el-button size="small" type="danger" @click="handleRemove('chat', row)">下架</el-button>
                </template>
                <span v-else class="reviewed-tip">已审核</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 教师资料 -->
      <el-tab-pane name="material">
        <template #label>
          <span class="tab-label">
            教师资料
            <el-tag size="small" class="tab-count" :type="pendingMaterials > 0 ? 'warning' : 'info'">{{ pendingMaterials }}</el-tag>
          </span>
        </template>

        <el-card class="tab-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>教师资料审核</span>
              <el-button text type="primary" :loading="loadingReviews" @click="loadReviews">刷新</el-button>
            </div>
          </template>

          <el-table
            :data="materials"
            v-loading="loadingReviews"
            border
            empty-text="暂无需要审核的教师资料"
            style="width: 100%"
          >
            <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
            <el-table-column label="类型" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="MATERIAL_TYPE_TAG[row.type] || 'info'">
                  {{ MATERIAL_TYPE_TEXT[row.type] || row.type || '链接' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="teacherName" label="上传教师" width="120" />
            <el-table-column label="链接" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <el-link
                  v-if="row.url"
                  type="primary"
                  :href="row.url"
                  target="_blank"
                  rel="noopener"
                  :underline="false"
                >
                  {{ row.url }}
                </el-link>
                <span v-else class="text-muted">—</span>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="时间" width="150" />
            <el-table-column label="审核状态" width="200">
              <template #default="{ row }">
                <el-tag v-if="row.reviewResult" size="small" :type="reviewTagType(row.reviewResult)">
                  {{ row.reviewText || row.reviewResult }}
                </el-tag>
                <el-tag v-else size="small" type="danger" effect="plain">待审核</el-tag>
                <div v-if="row.reviewRemark" class="review-remark">{{ row.reviewRemark }}</div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="210" fixed="right">
              <template #default="{ row }">
                <template v-if="!row.reviewResult">
                  <el-button size="small" type="success" @click="handleApprove('material', row)">通过</el-button>
                  <el-button size="small" type="warning" @click="openReject('material', row)">驳回</el-button>
                  <el-button size="small" type="danger" @click="handleRemove('material', row)">下架</el-button>
                </template>
                <span v-else class="reviewed-tip">已审核</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 操作留痕 -->
      <el-tab-pane name="log">
        <template #label>
          <span class="tab-label">操作留痕</span>
        </template>

        <el-alert
          class="log-tip"
          type="info"
          :closable="false"
          show-icon
          title="教师查看学生对话与处置操作都会留痕"
        />

        <el-card class="tab-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>操作留痕（最近 {{ auditLogs.length }} 条）</span>
              <el-button text type="primary" :loading="loadingLogs" @click="loadAuditLogs">刷新</el-button>
            </div>
          </template>

          <el-table
            :data="auditLogs"
            v-loading="loadingLogs"
            border
            empty-text="暂无操作留痕"
            style="width: 100%"
          >
            <el-table-column prop="createdAt" label="时间" width="180" />
            <el-table-column prop="teacherName" label="教师" width="120">
              <template #default="{ row }">{{ row.teacherName || '—' }}</template>
            </el-table-column>
            <el-table-column prop="studentName" label="学生" width="120">
              <template #default="{ row }">{{ row.studentName || '—' }}</template>
            </el-table-column>
            <el-table-column prop="actionText" label="动作" width="140">
              <template #default="{ row }">{{ row.actionText || row.action || '—' }}</template>
            </el-table-column>
            <el-table-column prop="detail" label="备注" min-width="240" show-overflow-tooltip>
              <template #default="{ row }">{{ row.detail || '—' }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 驳回原因 -->
    <el-dialog v-model="rejectVisible" title="驳回原因" width="460px" @closed="handleRejectClosed">
      <el-input
        v-model="rejectRemark"
        type="textarea"
        :rows="3"
        maxlength="255"
        show-word-limit
        placeholder="请填写驳回原因（必填）"
      />
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitReject">确定驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '../../api/admin'

type ObjectType = 'chat' | 'material'
type TagType = 'primary' | 'success' | 'info' | 'warning' | 'danger'

interface ReviewChat {
  id: number
  studentId: number
  studentName: string
  className: string
  content: string
  flagType: string
  flagText: string
  handled: boolean
  createdAt: string
  reviewResult: string | null
  reviewText: string
  reviewRemark: string
}

interface ReviewMaterial {
  id: number
  title: string
  url: string
  type: string
  teacherName: string
  createdAt: string
  reviewResult: string | null
  reviewText: string
  reviewRemark: string
}

interface AuditLog {
  id: number
  teacherName: string
  studentName: string
  action: string
  actionText: string
  chatId: number | null
  detail: string
  createdAt: string
}

const MATERIAL_TYPE_TEXT: Record<string, string> = { video: '视频', doc: '文档', ppt: '课件', link: '链接' }
const MATERIAL_TYPE_TAG: Record<string, TagType> = {
  video: 'danger',
  doc: 'warning',
  ppt: 'success',
  link: 'info'
}

const activeTab = ref('chat')
const loadingReviews = ref(false)
const loadingLogs = ref(false)
const submitting = ref(false)
const logLoaded = ref(false)

const chats = ref<ReviewChat[]>([])
const materials = ref<ReviewMaterial[]>([])
const auditLogs = ref<AuditLog[]>([])
const pendingChats = ref(0)
const pendingMaterials = ref(0)

const rejectVisible = ref(false)
const rejectRemark = ref('')
const rejectTarget = ref<{ objectType: ObjectType; objectId: number; title: string } | null>(null)

const toNumber = (value: unknown): number => {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

const pickError = (error: any, fallback: string): string => {
  const message = error?.response?.data?.message
  return typeof message === 'string' && message ? message : fallback
}

const reviewTagType = (result: string): TagType => {
  if (result === 'approved') return 'success'
  if (result === 'rejected') return 'danger'
  if (result === 'removed') return 'info'
  return 'info'
}

const normalizeChat = (raw: any): ReviewChat => ({
  id: toNumber(raw?.id),
  studentId: toNumber(raw?.studentId),
  studentName: raw?.studentName || '—',
  className: raw?.className || '未分班',
  content: raw?.content || '',
  flagType: raw?.flagType || '',
  flagText: raw?.flagText || '其他',
  handled: Boolean(raw?.handled),
  createdAt: raw?.createdAt || '',
  reviewResult: raw?.reviewResult ?? null,
  reviewText: raw?.reviewText || '',
  reviewRemark: raw?.reviewRemark || ''
})

const normalizeMaterial = (raw: any): ReviewMaterial => ({
  id: toNumber(raw?.id),
  title: raw?.title || '',
  url: raw?.url || '',
  type: raw?.type || '',
  teacherName: raw?.teacherName || '',
  createdAt: raw?.createdAt || '',
  reviewResult: raw?.reviewResult ?? null,
  reviewText: raw?.reviewText || '',
  reviewRemark: raw?.reviewRemark || ''
})

const normalizeLog = (raw: any): AuditLog => ({
  id: toNumber(raw?.id),
  teacherName: raw?.teacherName || '',
  studentName: raw?.studentName || '',
  action: raw?.action || '',
  actionText: raw?.actionText || '',
  chatId: raw?.chatId === null || raw?.chatId === undefined ? null : toNumber(raw?.chatId),
  detail: raw?.detail || '',
  createdAt: raw?.createdAt || ''
})

const loadReviews = async () => {
  loadingReviews.value = true
  try {
    const res: any = await adminApi.getAIReviews({ type: '' })
    chats.value = Array.isArray(res?.chats) ? res.chats.map(normalizeChat) : []
    materials.value = Array.isArray(res?.materials) ? res.materials.map(normalizeMaterial) : []
    pendingChats.value = toNumber(res?.pendingChats)
    pendingMaterials.value = toNumber(res?.pendingMaterials)
  } catch (e) {
    chats.value = []
    materials.value = []
    pendingChats.value = 0
    pendingMaterials.value = 0
  } finally {
    loadingReviews.value = false
  }
}

const loadAuditLogs = async () => {
  loadingLogs.value = true
  try {
    const res: any = await adminApi.getAIAuditLogs({ limit: 80 })
    auditLogs.value = Array.isArray(res) ? res.map(normalizeLog) : []
    logLoaded.value = true
  } catch (e) {
    auditLogs.value = []
  } finally {
    loadingLogs.value = false
  }
}

const handleTabChange = () => {
  if (activeTab.value === 'log' && !logLoaded.value && !loadingLogs.value) {
    loadAuditLogs()
  }
}

const doReview = async (
  objectType: ObjectType,
  objectId: number,
  result: 'approved' | 'rejected' | 'removed',
  remark?: string
): Promise<boolean> => {
  submitting.value = true
  try {
    const res: any = await adminApi.reviewAIContent({ objectType, objectId, result, remark })
    ElMessage.success(res?.message || '操作成功')
    await loadReviews()
    if (logLoaded.value) await loadAuditLogs()
    return true
  } catch (e: any) {
    ElMessage.error(pickError(e, '操作失败，请稍后重试'))
    return false
  } finally {
    submitting.value = false
  }
}

const handleApprove = async (objectType: ObjectType, row: any) => {
  await doReview(objectType, toNumber(row?.id), 'approved')
}

const openReject = (objectType: ObjectType, row: any) => {
  rejectTarget.value = {
    objectType,
    objectId: toNumber(row?.id),
    title: objectType === 'material' ? row?.title || '' : `${row?.studentName || '该学生'}的对话`
  }
  rejectRemark.value = ''
  rejectVisible.value = true
}

const handleRejectClosed = () => {
  rejectRemark.value = ''
  rejectTarget.value = null
}

const submitReject = async () => {
  const target = rejectTarget.value
  if (!target) return
  const remark = rejectRemark.value.trim()
  if (!remark) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  const ok = await doReview(target.objectType, target.objectId, 'rejected', remark)
  if (ok) {
    rejectVisible.value = false
    ElMessage.info(`已驳回「${target.title}」`)
  }
}

const handleRemove = async (objectType: ObjectType, row: any) => {
  const isMaterial = objectType === 'material'
  const name = isMaterial ? `资料「${row?.title || ''}」` : `${row?.studentName || '该学生'}的这条对话`
  const confirmText = isMaterial
    ? `确定下架（移除）${name}吗？移除后教师端不再展示该资料。`
    : `确定下架${name}吗？该条对话内容将不再保留。`
  try {
    await ElMessageBox.confirm(confirmText, '下架确认', {
      type: 'warning',
      confirmButtonText: '确定下架',
      cancelButtonText: '取消'
    })
  } catch {
    return
  }
  await doReview(objectType, toNumber(row?.id), 'removed')
}

onMounted(() => {
  loadReviews()
})
</script>

<style scoped>
.ai-review {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.review-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 600;
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.tab-count {
  height: 18px;
  line-height: 18px;
  padding: 0 6px;
  font-weight: 500;
}

.tab-card {
  border-radius: 14px;
  border: none;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.review-remark {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.reviewed-tip {
  font-size: 12px;
  color: #909399;
}

.text-muted {
  color: #909399;
}

.log-tip {
  margin-bottom: 16px;
  border-radius: 12px;
}
</style>
