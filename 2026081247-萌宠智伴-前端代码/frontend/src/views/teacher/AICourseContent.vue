<template>
  <div class="ai-course-content">
    <el-card class="filter-card" shadow="never">
      <div class="filter-bar">
        <div class="filter-left">
          <span class="filter-label">学段</span>
          <el-select v-model="gradeLevel" placeholder="全部学段" style="width: 170px" @change="loadCourses">
            <el-option v-for="opt in GRADE_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-button text type="primary" :loading="courseLoading" @click="loadCourses">
            <el-icon><Refresh /></el-icon>
            <span>刷新</span>
          </el-button>
        </div>
        <div class="filter-right">
          <span class="filter-tip">建议提问、测验题与课程素材由教师维护，学生端实时生效</span>
        </div>
      </div>
    </el-card>

    <div class="content-layout">
      <el-card class="course-panel" shadow="hover" v-loading="courseLoading">
        <template #header>
          <div class="card-header">
            <el-icon><Collection /></el-icon>
            <span>课程列表（{{ courses.length }}）</span>
          </div>
        </template>
        <div v-if="courses.length" class="course-list">
          <div
            v-for="course in courses"
            :key="course.id"
            class="course-item"
            :class="{ active: course.id === activeCourseId }"
            @click="selectCourse(course)"
          >
            <div class="course-item-title">{{ course.title || '未命名课程' }}</div>
            <div class="course-item-meta">
              <el-tag size="small" type="info">{{ course.category || '未分类' }}</el-tag>
              <span class="meta-dot">·</span>
              <span class="meta-text">{{ difficultyLabel(course.difficulty) }}</span>
            </div>
          </div>
        </div>
        <el-empty v-else description="当前学段下暂无可维护的课程" :image-size="80" />
      </el-card>

      <div class="detail-panel" v-loading="contentLoading">
        <template v-if="content">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>课程信息（只读）</span>
              </div>
            </template>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">课程名称</span>
                <span class="info-value">{{ content.title || '—' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">学段</span>
                <span class="info-value">{{ gradeLabel(content.gradeLevel) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">分类</span>
                <span class="info-value">{{ content.category || '—' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">难度</span>
                <span class="info-value">{{ difficultyLabel(content.difficulty) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">状态</span>
                <el-tag size="small" :type="content.status === 'archived' ? 'info' : 'success'">
                  {{ content.status === 'archived' ? '已下架' : '已上架' }}
                </el-tag>
              </div>
            </div>
            <div class="info-desc" v-if="content.description">{{ content.description }}</div>
            <div class="info-tip">
              <el-icon><InfoFilled /></el-icon>
              <span>课程信息由管理员在 AI 课程库维护</span>
            </div>
          </el-card>

          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><ChatDotRound /></el-icon>
                <span>建议提问</span>
                <span class="header-count">{{ questionDraft.length }} / 6</span>
              </div>
            </template>
            <div v-if="questionDraft.length" class="question-list">
              <div v-for="(item, index) in questionDraft" :key="index" class="question-row">
                <span class="question-index">{{ index + 1 }}</span>
                <el-input
                  v-model="questionDraft[index]"
                  maxlength="40"
                  show-word-limit
                  placeholder="请输入建议提问（不超过 40 字）"
                  class="question-input"
                />
                <el-button text :disabled="index === 0" @click="moveQuestion(index, -1)">
                  <el-icon><Top /></el-icon>
                </el-button>
                <el-button text :disabled="index === questionDraft.length - 1" @click="moveQuestion(index, 1)">
                  <el-icon><Bottom /></el-icon>
                </el-button>
                <el-button text type="danger" @click="removeQuestion(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <el-empty v-else description="暂时没有建议提问，点击下方按钮添加" :image-size="70" />
            <div class="block-actions">
              <el-button :disabled="questionDraft.length >= 6" @click="addQuestion">
                <el-icon><Plus /></el-icon>
                <span>添加一条</span>
              </el-button>
              <el-button type="primary" :loading="saving" @click="saveQuestions">保存建议提问</el-button>
            </div>
            <div class="block-hint">最多 6 条，每条不超过 40 字；留空则使用系统默认问题（清空全部内容后保存即恢复默认）。</div>
          </el-card>

          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><EditPen /></el-icon>
                <span>测验题预览</span>
                <span class="header-count">共 {{ content.quizCount }} 道题</span>
                <el-button
                  class="header-action"
                  type="primary"
                  plain
                  size="small"
                  :loading="regenerating"
                  @click="regenerateQuiz"
                >
                  <el-icon><Refresh /></el-icon>
                  <span>重新生成</span>
                </el-button>
              </div>
            </template>
            <div v-if="content.quiz.length" class="quiz-list">
              <div v-for="(quiz, qi) in content.quiz" :key="qi" class="quiz-item">
                <div class="quiz-title">{{ qi + 1 }}. {{ quiz.question || '（题干为空）' }}</div>
                <div v-if="quiz.options.length" class="quiz-options">
                  <div
                    v-for="(opt, oi) in quiz.options"
                    :key="oi"
                    class="quiz-option"
                    :class="{ correct: oi === quiz.answer }"
                  >
                    <span class="option-index">{{ optionLabel(oi) }}</span>
                    <span class="option-text">{{ opt }}</span>
                    <el-tag v-if="oi === quiz.answer" size="small" type="success">正确项</el-tag>
                  </div>
                </div>
                <div v-else class="quiz-empty-option">该题暂无选项</div>
                <div class="quiz-explanation-toggle" @click="toggleExplain(qi)">
                  <el-icon><ArrowRight /></el-icon>
                  <span>{{ isExplainOpen(qi) ? '收起解析' : '查看解析' }}</span>
                </div>
                <div v-show="isExplainOpen(qi)" class="quiz-explanation">
                  {{ quiz.explanation || '暂无解析' }}
                </div>
              </div>
            </div>
            <el-empty v-else description="本课还没有题目，可点击重新生成" :image-size="80" />
          </el-card>

          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><FolderOpened /></el-icon>
                <span>课程素材（{{ content.materials.length }}）</span>
                <el-button
                  class="header-action"
                  text
                  type="primary"
                  size="small"
                  :loading="materialLoading"
                  @click="refreshMaterials"
                >
                  <el-icon><Refresh /></el-icon>
                  <span>刷新</span>
                </el-button>
              </div>
            </template>
            <el-table :data="content.materials" size="small" empty-text="本课还没有挂载素材">
              <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
              <el-table-column label="类型" width="90">
                <template #default="{ row }">
                  <el-tag size="small" :type="materialTagType(row.type)">{{ materialLabel(row.type) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="链接" min-width="220">
                <template #default="{ row }">
                  <a class="material-link" :href="row.url" target="_blank" rel="noopener">{{ row.url }}</a>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="90">
                <template #default="{ row }">
                  <el-button text type="danger" @click="removeMaterial(row)">移除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="mount-section">
              <div class="mount-title">从我的资料挂载</div>
              <div v-if="content.myMaterials.length" class="mount-list">
                <div v-for="material in content.myMaterials" :key="material.id" class="mount-item">
                  <div class="mount-main">
                    <div class="mount-name">{{ material.title || '未命名资料' }}</div>
                    <div class="mount-url">{{ material.url }}</div>
                  </div>
                  <el-button
                    size="small"
                    type="primary"
                    plain
                    :loading="mountingId === material.id"
                    :disabled="isMounted(material.title)"
                    @click="mountMaterial(material)"
                  >
                    {{ isMounted(material.title) ? '已挂载' : '挂载到本课' }}
                  </el-button>
                </div>
              </div>
              <el-empty v-else description="资料库还没有资料，可先到「学习资料」页面上传" :image-size="70" />
            </div>
          </el-card>
        </template>

        <el-card v-else shadow="hover">
          <el-empty description="请先在左侧选择一门课程" :image-size="100" />
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowRight,
  Bottom,
  ChatDotRound,
  Collection,
  Delete,
  Document,
  EditPen,
  FolderOpened,
  InfoFilled,
  Plus,
  Refresh,
  Top,
} from '@element-plus/icons-vue'
import { teacherApi } from '../../api/teacher'

type TagType = 'primary' | 'success' | 'info' | 'warning' | 'danger'

interface AiCourseItem {
  id: number
  title: string
  gradeLevel: string
  category: string
  difficulty: string
}

interface QuizItem {
  question: string
  options: string[]
  answer: number | null
  explanation: string
}

interface MaterialItem {
  id: number
  title: string
  url: string
  type: string
  description: string
  sortOrder: number
}

interface MyMaterialItem {
  id: number
  title: string
  url: string
  type: string
}

interface CourseContent {
  courseId: number
  title: string
  description: string
  gradeLevel: string
  category: string
  difficulty: string
  status: string
  bookDir: string
  suggestedQuestions: string[]
  quizCount: number
  quiz: QuizItem[]
  materials: MaterialItem[]
  myMaterials: MyMaterialItem[]
}

const GRADE_OPTIONS = [
  { value: '', label: '全部学段' },
  { value: 'lower_primary', label: '小学低年级' },
  { value: 'upper_primary', label: '小学高年级' },
  { value: 'middle_school', label: '初中' },
  { value: 'high_school', label: '高中' },
]

const GRADE_LABEL: Record<string, string> = {
  lower_primary: '小学低年级',
  upper_primary: '小学高年级',
  middle_school: '初中',
  high_school: '高中',
}

const DIFFICULTY_LABEL: Record<string, string> = {
  easy: '简单',
  medium: '中等',
  hard: '困难',
}

const MATERIAL_TYPE_LABEL: Record<string, string> = {
  video: '视频',
  doc: '文档',
  ppt: '课件',
  link: '链接',
  image: '图片',
  audio: '音频',
}

const MATERIAL_TYPE_TAG: Record<string, TagType> = {
  video: 'danger',
  doc: 'warning',
  ppt: 'success',
  link: 'info',
  image: 'primary',
  audio: 'success',
}

const MAX_QUESTION_COUNT = 6
const MAX_QUESTION_LENGTH = 40

const gradeLevel = ref('')
const courseLoading = ref(false)
const courses = ref<AiCourseItem[]>([])
const activeCourseId = ref(0)
const contentLoading = ref(false)
const content = ref<CourseContent | null>(null)
const questionDraft = ref<string[]>([])
const saving = ref(false)
const regenerating = ref(false)
const materialLoading = ref(false)
const mountingId = ref(0)
const openExplain = ref<number[]>([])

const difficultyLabel = (value: string) => DIFFICULTY_LABEL[value] || value || '—'
const gradeLabel = (value: string) => GRADE_LABEL[value] || value || '—'
const materialLabel = (value: string) => MATERIAL_TYPE_LABEL[value] || '链接'
const materialTagType = (value: string): TagType => MATERIAL_TYPE_TAG[value] || 'info'
const optionLabel = (index: number) => String.fromCharCode(65 + index)
const isExplainOpen = (index: number) => openExplain.value.includes(index)
const toggleExplain = (index: number) => {
  openExplain.value = isExplainOpen(index)
    ? openExplain.value.filter(item => item !== index)
    : [...openExplain.value, index]
}

const loadCourses = async () => {
  courseLoading.value = true
  try {
    const params = gradeLevel.value ? { gradeLevel: gradeLevel.value } : undefined
    const data: any = await teacherApi.getAICourseList(params)
    const list = Array.isArray(data) ? data : []
    courses.value = list.map((item: any) => ({
      id: Number(item.id) || 0,
      title: item.title || '',
      gradeLevel: item.gradeLevel || '',
      category: item.category || '',
      difficulty: item.difficulty || '',
    }))
    if (!courses.value.some(item => item.id === activeCourseId.value)) {
      activeCourseId.value = 0
      content.value = null
      questionDraft.value = []
      openExplain.value = []
    }
  } catch (e) {
    courses.value = []
    activeCourseId.value = 0
    content.value = null
    questionDraft.value = []
  } finally {
    courseLoading.value = false
  }
}

const loadContent = async () => {
  if (!activeCourseId.value) {
    content.value = null
    questionDraft.value = []
    openExplain.value = []
    return
  }
  contentLoading.value = true
  try {
    const data: any = await teacherApi.getAICourseContent(activeCourseId.value)
    if (!data || typeof data !== 'object') {
      content.value = null
      questionDraft.value = []
      return
    }
    const questions = Array.isArray(data.suggestedQuestions)
      ? data.suggestedQuestions.filter((item: unknown) => typeof item === 'string' && !!item)
      : []
    content.value = {
      courseId: Number(data.courseId) || activeCourseId.value,
      title: data.title || '',
      description: data.description || '',
      gradeLevel: data.gradeLevel || '',
      category: data.category || '',
      difficulty: data.difficulty || '',
      status: data.status || 'published',
      bookDir: data.bookDir || '',
      suggestedQuestions: questions,
      quizCount: Number(data.quizCount) || 0,
      quiz: Array.isArray(data.quiz)
        ? data.quiz.map((item: any) => ({
            question: item?.question || '',
            options: Array.isArray(item?.options) ? item.options.map((o: any) => String(o ?? '')) : [],
            answer: typeof item?.answer === 'number' ? item.answer : null,
            explanation: item?.explanation || '',
          }))
        : [],
      materials: Array.isArray(data.materials)
        ? data.materials.map((item: any) => ({
            id: Number(item?.id) || 0,
            title: item?.title || '',
            url: item?.url || '',
            type: item?.type || 'link',
            description: item?.description || '',
            sortOrder: Number(item?.sortOrder) || 0,
          }))
        : [],
      myMaterials: Array.isArray(data.myMaterials)
        ? data.myMaterials.map((item: any) => ({
            id: Number(item?.id) || 0,
            title: item?.title || '',
            url: item?.url || '',
            type: item?.type || 'link',
          }))
        : [],
    }
    questionDraft.value = questions.length ? [...questions] : ['']
    openExplain.value = []
  } catch (e) {
    content.value = null
    questionDraft.value = []
  } finally {
    contentLoading.value = false
  }
}

const selectCourse = (course: AiCourseItem) => {
  if (activeCourseId.value === course.id) return
  activeCourseId.value = course.id
  content.value = null
  loadContent()
}

const addQuestion = () => {
  if (questionDraft.value.length >= MAX_QUESTION_COUNT) {
    ElMessage.warning(`建议提问最多 ${MAX_QUESTION_COUNT} 条`)
    return
  }
  questionDraft.value.push('')
}

const removeQuestion = (index: number) => {
  questionDraft.value.splice(index, 1)
}

const moveQuestion = (index: number, offset: number) => {
  const target = index + offset
  if (target < 0 || target >= questionDraft.value.length) return
  const list = [...questionDraft.value]
  const current = list[index]
  list[index] = list[target]
  list[target] = current
  questionDraft.value = list
}

const saveQuestions = async () => {
  if (!content.value) return
  const items = questionDraft.value.map(item => (item || '').trim()).filter(Boolean)
  if (items.length > MAX_QUESTION_COUNT) {
    ElMessage.warning(`建议提问最多 ${MAX_QUESTION_COUNT} 条`)
    return
  }
  if (items.some(item => item.length > MAX_QUESTION_LENGTH)) {
    ElMessage.warning(`每条建议提问不超过 ${MAX_QUESTION_LENGTH} 字`)
    return
  }
  saving.value = true
  try {
    const res: any = await teacherApi.saveAICourseContent(content.value.courseId, { suggestedQuestions: items })
    ElMessage.success(res?.message || '建议提问已保存')
    await loadContent()
  } catch (e) {
    // 失败提示由接口拦截器统一展示
  } finally {
    saving.value = false
  }
}

const regenerateQuiz = async () => {
  if (!content.value) return
  try {
    await ElMessageBox.confirm('重新生成会覆盖本课现有测验题目，确定继续吗？', '重新生成测验题', {
      type: 'warning',
      confirmButtonText: '重新生成',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return
  }
  regenerating.value = true
  try {
    const res: any = await teacherApi.saveAICourseContent(content.value.courseId, { regenerateQuiz: true })
    ElMessage.success(res?.message || '已重新生成测验题')
    await loadContent()
  } catch (e) {
    // 失败提示由接口拦截器统一展示
  } finally {
    regenerating.value = false
  }
}

const refreshMaterials = async () => {
  if (!content.value) return
  materialLoading.value = true
  try {
    const data: any = await teacherApi.getAICourseMaterials(content.value.courseId)
    if (content.value && Array.isArray(data)) {
      content.value.materials = data.map((item: any) => ({
        id: Number(item?.id) || 0,
        title: item?.title || '',
        url: item?.url || '',
        type: item?.type || 'link',
        description: item?.description || '',
        sortOrder: Number(item?.sortOrder) || 0,
      }))
    }
  } catch (e) {
    // 失败提示由接口拦截器统一展示，保留原有列表
  } finally {
    materialLoading.value = false
  }
}

const removeMaterial = async (row: MaterialItem) => {
  if (!content.value) return
  try {
    await ElMessageBox.confirm(`确定从本课移除素材「${row.title}」吗？`, '提示', { type: 'warning' })
  } catch (e) {
    return
  }
  try {
    await teacherApi.removeAICourseMaterial(content.value.courseId, row.id)
    ElMessage.success('已移除该素材')
    await loadContent()
  } catch (e) {
    // 失败提示由接口拦截器统一展示
  }
}

const isMounted = (title: string) => {
  if (!content.value) return false
  return content.value.materials.some(item => item.title === title)
}

const mountMaterial = async (material: MyMaterialItem) => {
  if (!content.value) return
  mountingId.value = material.id
  try {
    const res: any = await teacherApi.addAICourseMaterial(content.value.courseId, {
      title: material.title,
      url: material.url,
      type: material.type || 'link',
    })
    ElMessage.success(res?.message || '素材已挂载到该课程')
    await loadContent()
  } catch (e) {
    // 失败提示由接口拦截器统一展示
  } finally {
    mountingId.value = 0
  }
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.ai-course-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card {
  border: 1px solid #ece9f6;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
}

.filter-tip {
  font-size: 13px;
  color: #909399;
}

.content-layout {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.course-panel {
  width: 300px;
  flex-shrink: 0;
}

.detail-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-header .el-icon {
  color: #8985cf;
}

.header-count {
  font-size: 13px;
  font-weight: 400;
  color: #909399;
}

.header-action {
  margin-left: auto;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 620px;
  overflow-y: auto;
}

.course-item {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #ece9f6;
  background: #fafaff;
  cursor: pointer;
  transition: all 0.2s;
}

.course-item:hover {
  border-color: #8985cf;
}

.course-item.active {
  border-color: #8985cf;
  background: #f0eefb;
  box-shadow: 0 2px 10px rgba(137, 133, 207, 0.2);
}

.course-item-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  word-break: break-all;
}

.course-item-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.meta-dot {
  color: #c0c4cc;
}

.info-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 32px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.info-label {
  color: #909399;
}

.info-value {
  color: #333;
  font-weight: 500;
}

.info-desc {
  margin-top: 12px;
  font-size: 13px;
  color: #606266;
  line-height: 1.7;
}

.info-tip {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #f48d45;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.question-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.question-index {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  border-radius: 50%;
  background: #8985cf;
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.question-input {
  flex: 1;
}

.block-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
}

.block-hint {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.quiz-item {
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #ece9f6;
  background: #fbfaff;
}

.quiz-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  line-height: 1.6;
}

.quiz-options {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quiz-option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
  padding: 6px 10px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #f0eefb;
}

.quiz-option.correct {
  border-color: #52c41a;
  background: #f4fdf0;
  color: #333;
}

.option-index {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  border-radius: 50%;
  background: #f0eefb;
  color: #8985cf;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-text {
  flex: 1;
}

.quiz-empty-option {
  margin-top: 8px;
  font-size: 13px;
  color: #c0c4cc;
}

.quiz-explanation-toggle {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #8985cf;
  cursor: pointer;
}

.quiz-explanation {
  margin-top: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #f5f3f0;
  font-size: 13px;
  color: #606266;
  line-height: 1.7;
}

.material-link {
  color: #8985cf;
  font-size: 13px;
  word-break: break-all;
  text-decoration: none;
}

.material-link:hover {
  text-decoration: underline;
}

.mount-section {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px dashed #ece9f6;
}

.mount-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.mount-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 260px;
  overflow-y: auto;
}

.mount-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f5f3f0;
}

.mount-main {
  min-width: 0;
}

.mount-name {
  font-size: 13px;
  color: #333;
}

.mount-url {
  font-size: 12px;
  color: #909399;
  word-break: break-all;
}

@media (max-width: 1100px) {
  .content-layout {
    flex-direction: column;
  }

  .course-panel {
    width: 100%;
  }
}
</style>
