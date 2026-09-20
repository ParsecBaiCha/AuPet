<template>
  <div class="ai-course-library">
    <!-- 学段统计 -->
    <div class="summary-grid">
      <el-card v-for="g in GRADE_OPTIONS" :key="g.value" class="summary-card" shadow="hover">
        <div class="summary-head">
          <span class="summary-title">{{ g.label }}</span>
          <span class="summary-total">共 {{ gradeStat(g.value).total }} 门</span>
        </div>
        <div class="summary-body">
          <div class="summary-item">
            <span class="summary-value value-published">{{ gradeStat(g.value).published }}</span>
            <span class="summary-label">已上架</span>
          </div>
          <div class="summary-item">
            <span class="summary-value value-archived">{{ gradeStat(g.value).archived }}</span>
            <span class="summary-label">已下架</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 筛选条 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-bar">
        <div class="filter-group">
          <span class="filter-label">学段</span>
          <el-select v-model="filters.gradeLevel" placeholder="全部学段" style="width: 150px" @change="loadCourses">
            <el-option label="全部学段" value="" />
            <el-option v-for="g in GRADE_OPTIONS" :key="g.value" :label="g.label" :value="g.value" />
          </el-select>

          <span class="filter-label">状态</span>
          <el-select v-model="filters.status" placeholder="全部状态" style="width: 130px" @change="loadCourses">
            <el-option label="全部" value="" />
            <el-option label="已上架" value="published" />
            <el-option label="已下架" value="archived" />
          </el-select>

          <el-input
            v-model="filters.keyword"
            placeholder="搜索课程名称或简介"
            clearable
            style="width: 220px"
            @keyup.enter="loadCourses"
            @clear="loadCourses"
          />

          <el-button type="primary" @click="loadCourses">查询</el-button>
        </div>

        <el-button type="primary" @click="openCreate">新增课程</el-button>
      </div>
    </el-card>

    <!-- 课程列表 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>AI 课程库（{{ courses.length }}）</span>
          <el-button text type="primary" :loading="loading" @click="loadCourses">刷新</el-button>
        </div>
      </template>

      <el-table
        :data="courses"
        v-loading="loading"
        border
        empty-text="没有符合条件的课程"
        style="width: 100%"
      >
        <el-table-column prop="title" label="课程名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="学段" width="120">
          <template #default="{ row }">{{ gradeText(row.gradeLevel) }}</template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="110" />
        <el-table-column label="难度" width="90">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :type="DIFFICULTY_TAG[row.difficulty] || 'info'">
              {{ DIFFICULTY_TEXT[row.difficulty] || row.difficulty || '—' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sortOrder" label="排序" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'published' ? 'success' : 'info'">
              {{ row.status === 'published' ? '已上架' : '已下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="测验题" width="90">
          <template #default="{ row }">
            <span :class="row.hasQuiz ? 'text-ok' : 'text-muted'">{{ row.hasQuiz ? '已有' : '无' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="建议提问" width="100">
          <template #default="{ row }">{{ row.suggestedCount }} 条</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button
              size="small"
              :type="row.status === 'published' ? 'warning' : 'success'"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 'published' ? '下架' : '上架' }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增 / 编辑 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增课程' : '编辑课程'"
      width="560px"
      @closed="handleDialogClosed"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="课程名称" prop="title">
          <el-input v-model="form.title" maxlength="50" show-word-limit placeholder="请输入 2 至 50 字的课程名称" />
        </el-form-item>

        <el-form-item label="学段" prop="gradeLevel">
          <el-select v-model="form.gradeLevel" :disabled="dialogMode === 'edit'" placeholder="请选择学段" style="width: 100%">
            <el-option v-for="g in GRADE_OPTIONS" :key="g.value" :label="g.label" :value="g.value" />
          </el-select>
          <div v-if="dialogMode === 'edit'" class="form-tip">学段保存后不可修改</div>
        </el-form-item>

        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="c in CATEGORY_OPTIONS" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>

        <el-form-item label="难度" prop="difficulty">
          <el-select v-model="form.difficulty" placeholder="请选择难度" style="width: 100%">
            <el-option v-for="d in DIFFICULTY_OPTIONS" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="dialogMode === 'edit'" label="排序">
          <el-input-number v-model="form.sortOrder" :min="0" :max="9999" />
        </el-form-item>

        <el-form-item label="课程简介">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="简要说明课程内容（选填）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { adminApi } from '../../api/admin'

interface GradeStat {
  total: number
  published: number
  archived: number
}

interface AICourseItem {
  id: number
  title: string
  description: string
  gradeLevel: string
  category: string
  difficulty: string
  sortOrder: number
  status: string
  bookDir: string
  hasQuiz: boolean
  suggestedCount: number
}

type TagType = 'primary' | 'success' | 'info' | 'warning' | 'danger'

const GRADE_OPTIONS = [
  { value: 'lower_primary', label: '小学低年级' },
  { value: 'upper_primary', label: '小学高年级' },
  { value: 'middle_school', label: '初中' },
  { value: 'high_school', label: '高中' }
]

const CATEGORY_OPTIONS = ['AI基础', '编程入门', '算法思维', '机器学习', '伦理安全']

const DIFFICULTY_OPTIONS = [
  { value: 'easy', label: '简单' },
  { value: 'medium', label: '中等' },
  { value: 'hard', label: '困难' }
]

const DIFFICULTY_TEXT: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }
const DIFFICULTY_TAG: Record<string, TagType> = { easy: 'success', medium: 'warning', hard: 'danger' }

const filters = reactive({ gradeLevel: '', status: '', keyword: '' })
const courses = ref<AICourseItem[]>([])
const summary = ref<Record<string, GradeStat>>({})
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref<FormInstance>()

const form = reactive({
  id: 0,
  title: '',
  gradeLevel: '',
  category: '',
  difficulty: 'medium',
  description: '',
  sortOrder: 0
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '课程名称需 2 至 50 字', trigger: 'blur' }
  ],
  gradeLevel: [{ required: true, message: '请选择学段', trigger: 'change' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  difficulty: [{ required: true, message: '请选择难度', trigger: 'change' }]
}

const toNumber = (value: unknown): number => {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

const pickError = (error: any, fallback: string): string => {
  const message = error?.response?.data?.message
  return typeof message === 'string' && message ? message : fallback
}

const gradeText = (value: string): string => {
  const hit = GRADE_OPTIONS.find((item) => item.value === value)
  return hit ? hit.label : value || '—'
}

const gradeStat = (grade: string): GradeStat => {
  const hit = summary.value?.[grade]
  return hit ? { total: toNumber(hit.total), published: toNumber(hit.published), archived: toNumber(hit.archived) } : { total: 0, published: 0, archived: 0 }
}

const normalizeCourse = (raw: any): AICourseItem => ({
  id: toNumber(raw?.id),
  title: raw?.title || '',
  description: raw?.description || '',
  gradeLevel: raw?.gradeLevel || '',
  category: raw?.category || '',
  difficulty: raw?.difficulty || 'medium',
  sortOrder: toNumber(raw?.sortOrder),
  status: raw?.status || 'published',
  bookDir: raw?.bookDir || '',
  hasQuiz: Boolean(raw?.hasQuiz),
  suggestedCount: toNumber(raw?.suggestedCount)
})

const loadCourses = async () => {
  loading.value = true
  try {
    const res: any = await adminApi.getAICourses({
      gradeLevel: filters.gradeLevel,
      status: filters.status,
      keyword: filters.keyword.trim()
    })
    courses.value = Array.isArray(res?.list) ? res.list.map(normalizeCourse) : []
    summary.value = res?.summary && typeof res.summary === 'object' ? res.summary : {}
  } catch (e) {
    courses.value = []
    summary.value = {}
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  dialogMode.value = 'create'
  form.id = 0
  form.title = ''
  form.gradeLevel = ''
  form.category = ''
  form.difficulty = 'medium'
  form.description = ''
  form.sortOrder = 0
  dialogVisible.value = true
}

const openEdit = (row: AICourseItem) => {
  dialogMode.value = 'edit'
  form.id = row.id
  form.title = row.title
  form.gradeLevel = row.gradeLevel
  form.category = row.category
  form.difficulty = row.difficulty
  form.description = row.description
  form.sortOrder = row.sortOrder
  dialogVisible.value = true
}

const handleDialogClosed = () => {
  formRef.value?.clearValidate()
}

const handleSave = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (dialogMode.value === 'create') {
      const res: any = await adminApi.createAICourse({
        title: form.title.trim(),
        gradeLevel: form.gradeLevel,
        category: form.category,
        difficulty: form.difficulty,
        description: form.description.trim()
      })
      ElMessage.success(res?.message || '新增成功')
    } else {
      const res: any = await adminApi.updateAICourse(form.id, {
        title: form.title.trim(),
        description: form.description.trim(),
        category: form.category,
        difficulty: form.difficulty,
        sortOrder: form.sortOrder
      })
      ElMessage.success(res?.message || '保存成功')
    }
    dialogVisible.value = false
    await loadCourses()
  } catch (e: any) {
    ElMessage.error(pickError(e, '保存失败，请稍后重试'))
  } finally {
    saving.value = false
  }
}

const handleToggleStatus = async (row: AICourseItem) => {
  const next: 'published' | 'archived' = row.status === 'published' ? 'archived' : 'published'
  const confirmText =
    next === 'published'
      ? `确定重新上架课程「${row.title}」吗？上架后教师端与学生端立即可用。`
      : `确定下架课程「${row.title}」吗？下架后学生端选课列表不再显示。`
  try {
    await ElMessageBox.confirm(confirmText, next === 'published' ? '上架确认' : '下架确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
  } catch {
    return
  }

  try {
    const res: any = await adminApi.setAICourseStatus(row.id, next)
    ElMessage.success(res?.message || '操作成功')
    await loadCourses()
  } catch (e: any) {
    ElMessage.error(pickError(e, '操作失败，请稍后重试'))
  }
}

const handleDelete = async (row: AICourseItem) => {
  try {
    await ElMessageBox.confirm(`确定删除课程「${row.title}」吗？删除后不可恢复。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定删除',
      cancelButtonText: '取消'
    })
  } catch {
    return
  }

  try {
    const res: any = await adminApi.deleteAICourse(row.id)
    ElMessage.success(res?.message || '已删除')
    await loadCourses()
  } catch (e: any) {
    // 409：该课程已有学习 / 绘本记录，后端会给出「请改为下架」的原因
    ElMessage.error(pickError(e, '删除失败，请稍后重试'))
  }
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.ai-course-library {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.summary-card {
  border-radius: 14px;
  border: none;
}

.summary-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 14px;
}

.summary-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.summary-total {
  font-size: 12px;
  color: #909399;
}

.summary-body {
  display: flex;
  gap: 24px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.1;
}

.value-published {
  color: #52c41a;
}

.value-archived {
  color: #909399;
}

.summary-label {
  font-size: 12px;
  color: #909399;
}

.filter-card {
  border-radius: 14px;
  border: none;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: #606266;
}

.table-card {
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

.text-ok {
  color: #52c41a;
}

.text-muted {
  color: #909399;
}

.form-tip {
  font-size: 12px;
  color: #f48d45;
  line-height: 1.6;
  margin-top: 2px;
}

@media (max-width: 1200px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
