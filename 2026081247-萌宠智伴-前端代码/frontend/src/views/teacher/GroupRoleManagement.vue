<template>
  <div class="evaluate-page">
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="selectedClass" placeholder="请选择班级" @change="handleClassChange" style="width: 140px">
          <el-option v-for="cls in classList" :key="cls" :label="cls" :value="cls" />
        </el-select>
        <el-input v-model="searchText" placeholder="搜索学生姓名" clearable style="width: 160px; margin-left: 12px">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
    </div>

    <div class="content-card">
      <div class="card-header">
        <h3 class="card-title">待评价学生</h3>
        <span class="student-count">共 {{ filteredStudents.length }} 名学生</span>
      </div>

      <el-table :data="filteredStudents" stripe style="width: 100%">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column label="最近评价" width="150">
          <template #default="{ row }">
            <span v-if="row.lastEvaluation" class="last-eval" :class="getEvalClass(row.lastEvaluation)">
              {{ row.lastEvaluation }}
            </span>
            <span v-else class="no-eval">未评价</span>
          </template>
        </el-table-column>
        <el-table-column label="评价时间" width="150">
          <template #default="{ row }">
            <span class="eval-time">{{ row.lastEvalTime || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="对话分析">
          <template #default="{ row }">
            <div class="chat-info">
              <span class="chat-rate">积极性 {{ row.chatRate }}%</span>
              <div class="emotion-bar">
                <span class="emotion-tag good">积极 {{ row.positiveRate }}%</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="AI性格标签" min-width="200">
          <template #default="{ row }">
            <div class="ai-tags">
              <el-tag v-for="tag in row.aiTraits" :key="tag" size="small" type="info">{{ tag }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openEvaluate(row)">评价</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showDialog" :title="'评价 - ' + currentStudent?.name" width="600px" class="custom-dialog">
      <div v-if="currentStudent" class="evaluate-form">
        <div class="student-header">
          <el-avatar :size="48" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
          <div class="student-info">
            <span class="name">{{ currentStudent.name }}</span>
            <span class="class-name">{{ currentStudent.class }}</span>
          </div>
        </div>

        <div class="chat-analysis">
          <div class="analysis-title">
            <el-icon><ChatDotSquare /></el-icon>
            <span>对话数据分析</span>
          </div>
          <div class="analysis-grid">
            <div class="analysis-item">
              <span class="label">对话积极性</span>
              <el-progress :percentage="currentStudent.chatRate" :stroke-width="6" :show-text="false" />
              <span class="value">{{ currentStudent.chatRate }}%</span>
            </div>
            <div class="analysis-item">
              <span class="label">情感倾向</span>
              <div class="emotion-tags">
                <el-tag size="small" type="success">积极 {{ currentStudent.positiveRate }}%</el-tag>
                <el-tag size="small">中性 {{ 100 - currentStudent.positiveRate - currentStudent.negativeRate }}%</el-tag>
                <el-tag size="small" type="warning">消极 {{ currentStudent.negativeRate }}%</el-tag>
              </div>
            </div>
            <div class="analysis-item">
              <span class="label">关键词</span>
              <div class="keywords">
                <el-tag v-for="kw in currentStudent.aiTraits.slice(0, 4)" :key="kw" size="small">{{ kw }}</el-tag>
              </div>
            </div>
          </div>
        </div>

        <el-divider />

        <el-form label-position="top">
          <el-form-item label="综合评分">
            <el-rate v-model="evaluateForm.score" :max="5" show-text :texts="['很差', '较差', '一般', '良好', '优秀']" />
          </el-form-item>

          <el-form-item label="性格特征">
            <div class="trait-tags">
              <el-tag v-for="trait in currentStudent.aiTraits" :key="trait" type="info" effect="plain">{{ trait }}</el-tag>
            </div>
          </el-form-item>

          <el-form-item label="选择标签">
            <el-checkbox-group v-model="evaluateForm.tags">
              <el-checkbox label="积极主动" />
              <el-checkbox label="思维活跃" />
              <el-checkbox label="遵守纪律" />
              <el-checkbox label="乐于助人" />
              <el-checkbox label="内敛害羞" />
              <el-checkbox label="调皮捣蛋" />
              <el-checkbox label="注意力分散" />
              <el-checkbox label="缺乏自信" />
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="教师评语">
            <el-input v-model="evaluateForm.comment" type="textarea" :rows="3" placeholder="请输入评语..." />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitEvaluate">提交评价</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, ChatDotSquare } from '@element-plus/icons-vue'
import { teacherApi } from '../../api/teacher'

interface Student {
  id: number
  name: string
  class: string
  aiTraits: string[]
  chatRate: number
  positiveRate: number
  negativeRate: number
  lastEvaluation: string
  lastEvalTime: string
}

const classList = ['一年级1班', '一年级2班', '一年级3班']
const selectedClass = ref('一年级1班')
const searchText = ref('')
const showDialog = ref(false)
const currentStudent = ref<Student | null>(null)

const evaluateForm = reactive({
  score: 3,
  tags: [] as string[],
  comment: ''
})

const students = ref<Student[]>([])

const loadGroupRoles = async () => {
  try {
    const data: any = await teacherApi.getGroupRoles()
    if (Array.isArray(data)) students.value = data
  } catch (e) {
    // 接口失败时保持页面可用，使用默认空值
  }
}

const filteredStudents = computed(() => {
  return students.value.filter(s => {
    const matchClass = !selectedClass.value || s.class === selectedClass.value
    const matchName = !searchText.value || s.name.includes(searchText.value)
    return matchClass && matchName
  })
})

const getEvalClass = (eval_: string) => {
  if (eval_ === '优秀') return 'eval-excellent'
  if (eval_ === '良好') return 'eval-good'
  if (eval_ === '一般') return 'eval-normal'
  return ''
}

const handleClassChange = () => {}

const openEvaluate = (student: Student) => {
  currentStudent.value = student
  evaluateForm.score = 3
  evaluateForm.tags = []
  evaluateForm.comment = ''
  showDialog.value = true
}

const submitEvaluate = async () => {
  if (!currentStudent.value) return
  try {
    await teacherApi.evaluateStudent({
      studentId: currentStudent.value.id,
      score: evaluateForm.score,
      tags: evaluateForm.tags,
      comment: evaluateForm.comment
    })
    const student = students.value.find(s => s.id === currentStudent.value!.id)
    if (student) {
      const scoreText = evaluateForm.score >= 4 ? '优秀' : evaluateForm.score >= 3 ? '良好' : '一般'
      student.lastEvaluation = scoreText
      student.lastEvalTime = new Date().toLocaleDateString()
    }
    ElMessage.success('评价提交成功')
  } catch (e) {
    // 错误已由拦截器提示
  }
  showDialog.value = false
}

onMounted(() => {
  loadGroupRoles()
})
</script>

<style scoped>
.evaluate-page { padding: 0; }

.filter-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.filter-left { display: flex; }

.content-card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #E8E0F0;
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.student-count { font-size: 13px; color: #999; }

.last-eval { font-size: 13px; }
.eval-excellent { color: #f48d45; font-weight: 500; }
.eval-good { color: #52c41a; }
.eval-normal { color: #999; }

.no-eval { color: #ff7875; font-size: 13px; }

.eval-time { font-size: 13px; color: #999; }

.chat-info { display: flex; flex-direction: column; gap: 4px; }
.chat-rate { font-size: 13px; color: #666; }
.emotion-bar { display: flex; gap: 4px; }
.emotion-tag { font-size: 11px; }
.emotion-tag.good { background: #f6ffed; border-color: #b7eb8f; color: #52c41a; }

.ai-tags { display: flex; gap: 4px; flex-wrap: wrap; }

.student-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.student-header .name { font-size: 16px; font-weight: 500; color: #333; }
.student-header .class-name { font-size: 13px; color: #999; }

.chat-analysis {
  background: #f9f9f9;
  padding: 16px;
  border-radius: 8px;
}
.analysis-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}
.analysis-grid { display: flex; flex-direction: column; gap: 12px; }
.analysis-item { display: flex; align-items: center; gap: 12px; }
.analysis-item .label { width: 70px; font-size: 13px; color: #666; }
.analysis-item :deep(.el-progress) { flex: 1; }
.analysis-item .value { width: 40px; font-size: 13px; color: #333; text-align: right; }
.emotion-tags, .keywords { display: flex; gap: 6px; flex-wrap: wrap; }

.trait-tags { display: flex; gap: 8px; flex-wrap: wrap; }
</style>
