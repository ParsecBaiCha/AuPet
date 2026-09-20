<template>
  <div class="ai-board">
    <!-- 筛选条 -->
    <el-card shadow="hover" class="filter-card">
      <div class="filter-bar">
        <div class="filter-item">
          <span class="filter-label">班级</span>
          <el-select v-model="classId" placeholder="全部班级" style="width: 170px">
            <el-option label="全部班级" :value="0" />
            <el-option v-for="item in classes" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">课程</span>
          <el-select v-model="courseId" placeholder="全部课程" style="width: 190px">
            <el-option label="全部课程" :value="0" />
            <el-option v-for="item in courses" :key="item.id" :label="item.title" :value="item.id" />
          </el-select>
        </div>

        <div class="filter-item">
          <span class="filter-label">时间范围</span>
          <el-radio-group v-model="range">
            <el-radio-button value="7">近 7 天</el-radio-button>
            <el-radio-button value="30">近 30 天</el-radio-button>
            <el-radio-button value="all">本学期</el-radio-button>
          </el-radio-group>
        </div>

        <el-button type="primary" :loading="overviewLoading || studentsLoading" @click="reload">
          <el-icon><Refresh /></el-icon>
          <span>刷新</span>
        </el-button>

        <span class="filter-tip">共 {{ students.length }} 名学生有研习记录</span>
      </div>
    </el-card>

    <!-- 指标区 -->
    <div class="kpi-grid" v-loading="overviewLoading">
      <div v-for="item in metricCards" :key="item.label" class="kpi-card" :class="item.theme">
        <div class="kpi-label">{{ item.label }}</div>
        <div class="kpi-value">{{ item.value }}</div>
        <div class="kpi-desc">{{ item.desc }}</div>
      </div>
    </div>

    <!-- 学生名单 -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>学生研习名单</span>
          <span class="card-header-tip">点击行首箭头可查看该生各课程明细</span>
        </div>
      </template>

      <el-table
        :data="students"
        v-loading="studentsLoading"
        style="width: 100%"
        empty-text="本班在当前筛选条件下没有 AI 研习记录"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="sub-table-wrap">
              <div class="sub-title">{{ row.name }} 的课程研习明细</div>
              <el-table :data="row.courses || []" size="small" empty-text="该生暂无课程明细">
                <el-table-column prop="title" label="课程" min-width="180" show-overflow-tooltip />
                <el-table-column prop="visits" label="学习次数" width="100" />
                <el-table-column label="最高分" width="100">
                  <template #default="scope">{{ formatScore(scope.row.bestScore) }}</template>
                </el-table-column>
                <el-table-column prop="quizCount" label="测验次数" width="100" />
                <el-table-column label="最近学习" width="160">
                  <template #default="scope">{{ formatTime(scope.row.lastTime) }}</template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="学生" min-width="120" />
        <el-table-column label="班级" min-width="130">
          <template #default="{ row }">{{ row.className || '未分班' }}</template>
        </el-table-column>
        <el-table-column prop="visits" label="学习次数" width="110" sortable />
        <el-table-column prop="quizCount" label="测验次数" width="110" sortable />
        <el-table-column label="平均分" width="100">
          <template #default="{ row }">{{ formatScore(row.avgScore) }}</template>
        </el-table-column>
        <el-table-column label="及格率" width="100">
          <template #default="{ row }">{{ formatRate(row.passRate) }}</template>
        </el-table-column>
        <el-table-column label="最近学习时间" width="170">
          <template #default="{ row }">{{ formatTime(row.lastTime) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 在线编程练习 -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <el-icon><Monitor /></el-icon>
          <span>在线编程练习</span>
          <span class="card-header-tip">学生每次「运行代码」都会留痕，可据此判断卡点</span>
          <span class="card-header-right">共 {{ programming.length }} 人</span>
        </div>
      </template>

      <el-table
        :data="programming"
        v-loading="programmingLoading"
        style="width: 100%"
        empty-text="本班在当前筛选条件下还没有编程练习记录"
      >
        <el-table-column prop="name" label="学生" min-width="120" />
        <el-table-column label="班级" min-width="130">
          <template #default="{ row }">{{ row.className || '未分班' }}</template>
        </el-table-column>
        <el-table-column prop="doneTasks" label="已通过题目" width="120" sortable />
        <el-table-column prop="runs" label="运行次数" width="110" sortable />
        <el-table-column prop="lastCourse" label="最近课程" min-width="160" show-overflow-tooltip />
        <el-table-column label="最近练习" width="170">
          <template #default="{ row }">{{ formatTime(row.lastTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openProgramming(row)">查看代码</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编程提交明细 -->
    <el-dialog v-model="detailVisible" :title="detailTitle" width="820px" top="6vh">
      <div v-loading="detailLoading" class="code-detail">
        <el-empty v-if="!detailLoading && !detailRecords.length" description="暂无提交记录" />
        <div v-for="(item, index) in detailRecords" :key="index" class="code-item">
          <div class="code-item-head">
            <span class="code-item-title">{{ item.taskTitle || '未命名题目' }}</span>
            <el-tag size="small" :type="item.allPassed ? 'success' : 'info'">
              {{ item.allPassed ? '已通过' : `通过 ${item.passed}/${item.total}` }}
            </el-tag>
            <span class="code-item-time">{{ item.courseTitle }} · {{ item.time }}</span>
          </div>
          <pre class="code-block">{{ item.code }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { teacherApi } from '../../api/teacher'
import { Refresh, DataAnalysis, Monitor } from '@element-plus/icons-vue'

interface ClassOption {
  id: number
  name: string
}

interface CourseOption {
  id: number
  title: string
  grade_level?: string
  status?: string
}

interface AiKpis {
  visits: number
  students: number
  quizCount: number
  avgScore: number | null
  passRate: number | null
}

interface StudentCourseRow {
  courseId: number | null
  title: string
  visits: number
  bestScore: number | null
  quizCount: number
  lastTime: string
}

interface StudentRow {
  studentId: number
  name: string
  className: string
  classId: number
  visits: number
  quizCount: number
  avgScore: number | null
  passRate: number | null
  lastTime: string
  courses: StudentCourseRow[]
}

interface ProgrammingRow {
  studentId: number
  name: string
  className: string
  doneTasks: number
  runs: number
  lastCourse: string
  lastTime: string
}

interface ProgrammingRecord {
  courseTitle: string
  taskTitle: string
  code: string
  passed: number
  total: number
  allPassed: boolean
  time: string
}

const emptyKpis = (): AiKpis => ({
  visits: 0,
  students: 0,
  quizCount: 0,
  avgScore: null,
  passRate: null,
})

const classId = ref<number>(0)
const courseId = ref<number>(0)
const range = ref<string>('7')

const overviewLoading = ref(false)
const studentsLoading = ref(false)
const classes = ref<ClassOption[]>([])
const courses = ref<CourseOption[]>([])
const kpis = ref<AiKpis>(emptyKpis())
const students = ref<StudentRow[]>([])

// 在线编程练习
const programmingLoading = ref(false)
const programming = ref<ProgrammingRow[]>([])
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailTitle = ref('')
const detailRecords = ref<ProgrammingRecord[]>([])

// 避免快速切换筛选时旧请求覆盖新结果
let requestSeq = 0

const toNumber = (value: unknown, fallback = 0): number => {
  const num = Number(value)
  return Number.isFinite(num) ? num : fallback
}

const toNullableNumber = (value: unknown): number | null => {
  if (value === null || value === undefined || value === '') return null
  const num = Number(value)
  return Number.isFinite(num) ? num : null
}

const formatScore = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '—'
  const num = Number(value)
  return Number.isFinite(num) ? String(num) : '—'
}

const formatRate = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '—'
  const num = Number(value)
  return Number.isFinite(num) ? `${num}%` : '—'
}

const formatTime = (value: string | null | undefined): string => {
  return value ? value : '—'
}

const rangeLabel = computed(() => {
  if (range.value === '30') return '近 30 天'
  if (range.value === 'all') return '本学期'
  return '近 7 天'
})

const metricCards = computed(() => [
  {
    label: '学习人次',
    value: String(kpis.value.visits),
    desc: `筛选范围：${rangeLabel.value}`,
    theme: 'purple',
  },
  {
    label: '参与学生',
    value: String(kpis.value.students),
    desc: `共 ${classes.value.length} 个可选班级`,
    theme: 'violet',
  },
  {
    label: '测验次数',
    value: String(kpis.value.quizCount),
    desc: `课程 ${courses.value.length} 门可选`,
    theme: 'orange',
  },
  {
    label: '测验平均分',
    value: formatScore(kpis.value.avgScore),
    desc: `及格率 ${formatRate(kpis.value.passRate)}`,
    theme: 'green',
  },
])

const normalizeKpis = (raw: any): AiKpis => {
  if (!raw || typeof raw !== 'object') return emptyKpis()
  return {
    visits: toNumber(raw.visits),
    students: toNumber(raw.students),
    quizCount: toNumber(raw.quizCount),
    avgScore: toNullableNumber(raw.avgScore),
    passRate: toNullableNumber(raw.passRate),
  }
}

const normalizeStudent = (raw: any): StudentRow => ({
  studentId: toNumber(raw?.studentId),
  name: raw?.name || '未知学生',
  className: raw?.className || '',
  classId: toNumber(raw?.classId),
  visits: toNumber(raw?.visits),
  quizCount: toNumber(raw?.quizCount),
  avgScore: toNullableNumber(raw?.avgScore),
  passRate: toNullableNumber(raw?.passRate),
  lastTime: raw?.lastTime || '',
  courses: Array.isArray(raw?.courses)
    ? raw.courses.map((c: any): StudentCourseRow => ({
        courseId: c?.courseId === null || c?.courseId === undefined ? null : toNumber(c.courseId),
        title: c?.title || '未关联课程',
        visits: toNumber(c?.visits),
        bestScore: toNullableNumber(c?.bestScore),
        quizCount: toNumber(c?.quizCount),
        lastTime: c?.lastTime || '',
      }))
    : [],
})

const loadOverview = async (seq: number) => {
  overviewLoading.value = true
  try {
    const res: any = await teacherApi.getAIOverview({
      classId: classId.value,
      courseId: courseId.value,
      range: range.value,
    })
    if (seq !== requestSeq) return
    kpis.value = normalizeKpis(res?.kpis)
    classes.value = Array.isArray(res?.classes)
      ? res.classes.map((c: any): ClassOption => ({ id: toNumber(c?.id), name: c?.name || '未命名班级' }))
      : []
    courses.value = Array.isArray(res?.courses)
      ? res.courses.map((c: any): CourseOption => ({
          id: toNumber(c?.id),
          title: c?.title || '未命名课程',
          grade_level: c?.grade_level || '',
          status: c?.status || '',
        }))
      : []
  } catch (e) {
    if (seq !== requestSeq) return
    kpis.value = emptyKpis()
    classes.value = []
    courses.value = []
  } finally {
    if (seq === requestSeq) overviewLoading.value = false
  }
}

const loadStudents = async (seq: number) => {
  studentsLoading.value = true
  try {
    const res: any = await teacherApi.getAIStudents({
      classId: classId.value,
      courseId: courseId.value,
      range: range.value,
    })
    if (seq !== requestSeq) return
    students.value = Array.isArray(res) ? res.map(normalizeStudent) : []
  } catch (e) {
    if (seq !== requestSeq) return
    students.value = []
  } finally {
    if (seq === requestSeq) studentsLoading.value = false
  }
}

const normalizeProgramming = (raw: any): ProgrammingRow => ({
  studentId: toNumber(raw?.studentId),
  name: raw?.name || '未知学生',
  className: raw?.className || '',
  doneTasks: toNumber(raw?.doneTasks),
  runs: toNumber(raw?.runs),
  lastCourse: raw?.lastCourse || '',
  lastTime: raw?.lastTime || '',
})

const loadProgramming = async (seq: number) => {
  programmingLoading.value = true
  try {
    const res: any = await teacherApi.getAIProgramming({
      classId: classId.value,
      range: range.value,
    })
    if (seq !== requestSeq) return
    programming.value = Array.isArray(res) ? res.map(normalizeProgramming) : []
  } catch {
    if (seq !== requestSeq) return
    programming.value = []
  } finally {
    if (seq === requestSeq) programmingLoading.value = false
  }
}

const openProgramming = async (row: ProgrammingRow) => {
  detailTitle.value = `${row.name} 的编程练习记录`
  detailVisible.value = true
  detailLoading.value = true
  detailRecords.value = []
  try {
    const res: any = await teacherApi.getAIProgrammingDetail(row.studentId)
    detailRecords.value = Array.isArray(res?.records)
      ? res.records.map((r: any): ProgrammingRecord => ({
          courseTitle: r?.courseTitle || '',
          taskTitle: r?.taskTitle || '',
          code: r?.code || '',
          passed: toNumber(r?.passed),
          total: toNumber(r?.total),
          allPassed: !!r?.allPassed,
          time: r?.time || '',
        }))
      : []
  } catch {
    detailRecords.value = []
  } finally {
    detailLoading.value = false
  }
}

const reload = async () => {
  const seq = ++requestSeq
  await Promise.all([loadOverview(seq), loadStudents(seq), loadProgramming(seq)])
}

watch(
  [classId, courseId, range],
  () => {
    void reload()
  },
  { immediate: true }
)
</script>

<style scoped>
.ai-board {
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.kpi-card {
  min-height: 108px;
  padding: 18px 20px;
  border-radius: 14px;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: all 0.3s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.kpi-label {
  font-size: 14px;
  opacity: 0.92;
}

.kpi-value {
  margin-top: 8px;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.kpi-desc {
  margin-top: 6px;
  font-size: 13px;
  opacity: 0.9;
}

.purple {
  background: linear-gradient(135deg, #8985cf 0%, #7370bb 100%);
}

.violet {
  background: linear-gradient(135deg, #acb6f3 0%, #8985cf 100%);
}

.orange {
  background: linear-gradient(135deg, #f9b27a 0%, #f48d45 100%);
}

.green {
  background: linear-gradient(135deg, #8fd66b 0%, #52c41a 100%);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.card-header-tip {
  font-size: 12px;
  font-weight: 400;
  color: #909399;
}

.sub-table-wrap {
  padding: 8px 16px 12px;
  background: #fafaff;
}

.sub-title {
  margin-bottom: 8px;
  font-size: 13px;
  color: #8985cf;
  font-weight: 600;
}

.card-header-right {
  margin-left: auto;
  font-size: 13px;
  font-weight: 400;
  color: #909399;
}

.code-detail {
  max-height: 62vh;
  overflow-y: auto;
}

.code-item {
  margin-bottom: 14px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  overflow: hidden;
}

.code-item-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #fafaff;
  font-size: 13px;
}

.code-item-title {
  font-weight: 600;
  color: #303133;
}

.code-item-time {
  margin-left: auto;
  color: #909399;
  font-size: 12px;
}

.code-block {
  margin: 0;
  padding: 12px;
  max-height: 260px;
  overflow: auto;
  background: #1f2430;
  color: #e6e9f0;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 12.5px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .filter-tip {
    margin-left: 0;
  }
}
</style>
