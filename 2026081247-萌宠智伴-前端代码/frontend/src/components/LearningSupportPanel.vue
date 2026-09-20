<template>
  <section class="support-panel" v-loading="loading">
    <div class="support-heading">
      <div><h3>学习关怀提醒 <el-tag type="warning">{{ pendingCount }} 条待关注</el-tag></h3>
        <p>心情记录、学生求助或练习低于 60 分时提醒。低分代表学习可能遇到困难，不直接判断为情绪低落。</p></div>
      <el-button @click="load">刷新</el-button>
    </div>
    <el-alert v-if="failed" title="提醒加载失败，请点击刷新重试" type="error" :closable="false" />
    <el-table :data="items" empty-text="暂无学习关怀提醒" width="100%">
      <el-table-column prop="studentName" label="学生" width="95" />
      <el-table-column prop="className" label="班级" width="110" />
      <el-table-column label="提醒来源" width="105"><template #default="{ row }">{{ kindNames[row.kind] }}</template></el-table-column>
      <el-table-column prop="reason" label="关注原因" min-width="180" />
      <el-table-column prop="updated_at" label="最近提醒" width="160" />
      <el-table-column label="学生反馈" min-width="160">
        <template #default="{ row }">
          <div v-if="row.studentRating" class="rating-cell">
            <el-tag type="danger" size="small" effect="light">自评偏难</el-tag>
            <span class="rating-stars">{{ '★'.repeat(row.studentRating.stars) }}</span>
            <span class="rating-topic" :title="row.studentRating.question">{{ row.studentRating.topic }}</span>
          </div>
          <span v-else class="rating-empty">—</span>
        </template>
      </el-table-column>
      <el-table-column label="练习安排" width="100"><template #default="{ row }">{{ row.difficulty === 'easy' ? '基础练习' : '正常难度' }}</template></el-table-column>
      <el-table-column label="状态" width="90"><template #default="{ row }"><el-tag :type="row.status === 'pending' ? 'warning' : 'success'">{{ row.status === 'pending' ? '待关注' : '已跟进' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="110" fixed="right"><template #default="{ row }"><el-button type="primary" link @click="open(row)">查看与干预</el-button></template></el-table-column>
    </el-table>
    <el-dialog v-model="visible" title="学习关怀与难度调整" width="560px">
      <template v-if="selected">
        <p><strong>{{ selected.studentName }} · {{ selected.className }}</strong></p>
        <p>{{ selected.reason }}</p>
        <div v-if="selected.studentRating" class="rating-detail">
          <div class="rating-detail-title">
            <el-tag type="danger" size="small" effect="light">学生自评这题偏难</el-tag>
            <span class="rating-detail-stars">{{ '★'.repeat(selected.studentRating.stars) }} {{ selected.studentRating.stars }}星</span>
          </div>
          <p class="rating-detail-question" :title="selected.studentRating.question">题目：{{ selected.studentRating.question }}</p>
          <div v-if="selected.studentRating.tags?.length" class="rating-detail-tags">
            <el-tag v-for="tag in selected.studentRating.tags" :key="tag" size="small" type="warning" effect="plain">{{ tag }}</el-tag>
          </div>
          <p class="rating-detail-time">反馈时间：{{ selected.studentRating.time }}</p>
        </div>
        <el-form label-position="top">
          <el-form-item label="干预方式"><el-select v-model="action" style="width:100%">
            <el-option label="降低难度：安排基础练习" value="easy" />
            <el-option label="先关心了解，保持当前难度" value="observe" />
            <el-option label="恢复正常难度" value="normal" />
          </el-select></el-form-item>
          <el-alert title="难度调整仅作用于这名学生，下次生成 AI 练习时生效，持续到教师恢复正常难度。" type="info" :closable="false" />
          <el-form-item label="关怀备注" style="margin-top:16px"><el-input v-model="note" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="例如：先巩固基础，课后了解遇到的困难" /></el-form-item>
        </el-form>
        <h4>本次提醒的跟进记录</h4>
        <el-empty v-if="!selected.actions.length" description="尚无跟进记录" :image-size="45" />
        <div v-for="(record, i) in selected.actions" :key="i" class="support-record">
          <strong>{{ actionNames[record.action] }}</strong> · {{ record.teacherName }} · {{ record.created_at }}
          <p>{{ record.note || '未填写备注' }}</p>
        </div>
      </template>
      <template #footer><el-button @click="visible = false">取消</el-button><el-button type="primary" :loading="saving" @click="save">保存干预</el-button></template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { ref, onActivated, onDeactivated, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { teacherApi } from '../api/teacher'

const items = ref<any[]>([])
const pendingCount = ref(0)
const loading = ref(false)
const failed = ref(false)
const visible = ref(false)
const saving = ref(false)
const selected = ref<any>(null)
const action = ref('observe')
const note = ref('')
const kindNames: Record<string, string> = { mood: '情绪相关', study: '学习困难', score: '练习低分' }
const actionNames: Record<string, string> = { easy: '安排基础练习', normal: '恢复正常难度', observe: '关心了解' }
let timer: ReturnType<typeof setInterval> | undefined
async function load() {
  if (loading.value) return
  loading.value = true
  try {
    const data: any = await teacherApi.getLearningSupport()
    items.value = data.items
    pendingCount.value = data.pendingCount
    failed.value = false
  } catch { failed.value = true } finally { loading.value = false }
}
function open(row: any) { selected.value = row; action.value = 'observe'; note.value = ''; visible.value = true }
async function save() {
  saving.value = true
  try {
    await teacherApi.setLearningSupport(selected.value.id, { action: action.value, note: note.value })
    ElMessage.success('干预已保存')
    visible.value = false
    window.dispatchEvent(new Event('learning-support-updated'))
    await load()
  } finally { saving.value = false }
}
function stop() { if (timer) clearInterval(timer); timer = undefined }
onActivated(() => { stop(); load(); timer = setInterval(load, 30000) })
onDeactivated(stop)
onUnmounted(stop)
</script>

<style scoped>
.support-panel { background: #fff; border: 1px solid #e8e0f0; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
.support-heading { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
h3 { margin: 0 0 10px; color: #514887; }
.support-heading p { color: #777; font-size: 13px; line-height: 1.7; }
.rating-cell { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.rating-stars { color: #ffb400; font-size: 13px; letter-spacing: -1px; }
.rating-topic { color: #666; font-size: 12px; max-width: 90px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rating-empty { color: #ccc; }
.rating-detail { background: #fff5f5; border: 1px solid #ffdbdb; border-radius: 10px; padding: 12px 14px; margin: 12px 0; }
.rating-detail-title { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.rating-detail-stars { color: #ffb400; font-size: 14px; font-weight: 600; }
.rating-detail-question { color: #666; font-size: 13px; line-height: 1.6; margin: 0 0 8px; }
.rating-detail-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 6px; }
.rating-detail-time { color: #999; font-size: 12px; margin: 0; }
.support-record { border-top: 1px solid #eee; padding: 12px 0; font-size: 13px; }
</style>
