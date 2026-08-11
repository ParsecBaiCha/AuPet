<template>
  <div class="class-manage">
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="gradeFilter" placeholder="按年级筛选" clearable style="width: 120px">
          <el-option label="一年级" value="一年级" />
          <el-option label="二年级" value="二年级" />
          <el-option label="三年级" value="三年级" />
          <el-option label="四年级" value="四年级" />
          <el-option label="五年级" value="五年级" />
          <el-option label="六年级" value="六年级" />
        </el-select>
        <el-input v-model="searchText" placeholder="搜索班级" clearable style="width: 160px; margin-left: 12px">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
      <div class="filter-right">
        <el-button @click="handleExport">导出</el-button>
        <el-button type="primary" @click="handleImport" style="background: #f48d45; border-color: #f48d45">+ 导入班级</el-button>
      </div>
    </div>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #8985cf 0%, #acb6f3 100%)">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ filteredClasses.length }}</div>
            <div class="stat-label">班级数量</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f48d45 0%, #f4bb6e 100%)">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ totalStudents }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #52c41a 0%, #95de64 100%)">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ normalClassCount }}</div>
            <div class="stat-label">正常班级</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%)">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ warningClassCount }}</div>
            <div class="stat-label">关注班级</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <div class="content-card" style="margin-top: 16px">
      <el-table :data="filteredClasses" border stripe style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="班级名称" min-width="120" />
        <el-table-column prop="grade" label="年级" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.grade }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="teacher" label="班主任" width="100" />
        <el-table-column prop="studentCount" label="人数" width="80">
          <template #default="{ row }">{{ row.studentCount }}人</template>
        </el-table-column>
        <el-table-column prop="room" label="教室" width="80" />
        <el-table-column label="心理状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getPsychologyType(row.psychologyStatus)" size="small">
              {{ row.psychologyStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="班级状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'normal'" type="success" size="small">正常</el-tag>
            <el-tag v-else-if="row.status === 'warning'" type="warning" size="small">关注</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewStudents(row)">查看学生</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="450px" class="custom-dialog" @close="handleDialogClose">
      <el-form ref="formRef" :model="classForm" :rules="rules" label-position="top">
        <el-form-item label="班级编号" prop="id">
          <el-input v-model.number="classForm.id" :disabled="isEdit" placeholder="请输入班级编号" />
        </el-form-item>
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="classForm.name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-input v-model="classForm.grade" placeholder="请输入年级" />
        </el-form-item>
        <el-form-item label="班主任" prop="teacher">
          <el-input v-model="classForm.teacher" placeholder="请输入班主任姓名" />
        </el-form-item>
        <el-form-item label="教室" prop="room">
          <el-input v-model="classForm.room" placeholder="请输入教室号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" title="导入班级" width="520px">
      <div class="import-header">
        <span class="import-tip">请选择要导入的班级</span>
        <el-select v-model="importGradeFilter" placeholder="按年级筛选" clearable size="small" style="width: 100px">
          <el-option label="一年级" value="一年级" />
          <el-option label="二年级" value="二年级" />
          <el-option label="三年级" value="三年级" />
          <el-option label="四年级" value="四年级" />
          <el-option label="五年级" value="五年级" />
          <el-option label="六年级" value="六年级" />
        </el-select>
      </div>
      <div class="class-grid">
        <div 
          v-for="cls in filteredAvailableClasses" 
          :key="cls.id" 
          class="class-card"
          :class="{ 
            'is-selected': selectedClasses.includes(cls.id),
            'is-disabled': classes.some(c => c.id === cls.id)
          }"
          @click="toggleClass(cls)"
        >
          <div class="card-checkbox">
            <el-icon v-if="selectedClasses.includes(cls.id)"><Check /></el-icon>
          </div>
          <div class="card-content">
            <div class="class-name">{{ cls.name }}</div>
            <div class="class-info">
              <span class="grade-tag">{{ cls.grade }}</span>
              <span class="teacher-name">{{ cls.teacher }}</span>
            </div>
          </div>
          <div v-if="classes.some(c => c.id === cls.id)" class="added-badge">已导入</div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <span class="selected-count">已选择 {{ selectedClasses.length }} 个班级</span>
          <div class="footer-btns">
            <el-button @click="importDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmImport" :disabled="selectedClasses.length === 0">确认导入</el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="studentDialogVisible" :title="currentClass?.name + ' - 学生列表'" width="750px">
      <div class="student-stats">
        <div class="stat-item">
          <span class="stat-num">{{ classStudents.length }}</span>
          <span class="stat-label">学生总数</span>
        </div>
        <div class="stat-item">
          <span class="stat-num good">{{ goodCount }}</span>
          <span class="stat-label">状态良好</span>
        </div>
        <div class="stat-item">
          <span class="stat-num warning">{{ warningCount }}</span>
          <span class="stat-label">需要关注</span>
        </div>
      </div>
      <el-table :data="classStudents" stripe style="margin-top: 16px">
        <el-table-column prop="name" label="姓名" width="80" />
        <el-table-column label="性别" width="60">
          <template #default="{ row }">{{ row.gender === 'male' ? '男' : '女' }}</template>
        </el-table-column>
        <el-table-column label="积分" width="80">
          <template #default="{ row }">
            <span :class="row.points >= 0 ? 'text-good' : 'text-warning'">{{ row.points }}</span>
          </template>
        </el-table-column>
        <el-table-column label="宠物等级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPetType(row.petLevel)" size="small">{{ row.petLevel }}级</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="任务完成率" width="110">
          <template #default="{ row }">
            <el-progress :percentage="row.taskRate" :stroke-width="6" :show-text="false" size="small" />
            <span style="font-size: 12px">{{ row.taskRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="情绪指数" width="100">
          <template #default="{ row }">
            <el-rate v-model="row.moodIndex" disabled size="small" />
          </template>
        </el-table-column>
        <el-table-column label="心理状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getMoodType(row.moodStatus)" size="small">{{ row.moodStatus }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewStudentDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="showStudentDetailDialog" :title="currentStudent?.name + ' - 学生详情'" width="600px">
      <div class="student-detail-content" v-if="currentStudent">
        <div class="detail-header">
          <el-avatar :size="60" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
          <div class="header-info">
            <div class="student-name">{{ currentStudent.name }}</div>
            <div class="student-meta">
              <el-tag size="small">{{ currentStudent.gender === 'male' ? '男' : '女' }}</el-tag>
              <el-tag size="small" type="warning">{{ currentStudent.petLevel }}级</el-tag>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">积分</span>
              <span class="value" :class="currentStudent.points >= 0 ? 'text-good' : 'text-warning'">{{ currentStudent.points }}</span>
            </div>
            <div class="info-item">
              <span class="label">任务完成率</span>
              <span class="value">{{ currentStudent.taskRate }}%</span>
            </div>
            <div class="info-item">
              <span class="label">情绪指数</span>
              <span class="value"><el-rate v-model="currentStudent.moodIndex" disabled size="small" /></span>
            </div>
            <div class="info-item">
              <span class="label">心理状态</span>
              <span class="value">
                <el-tag :type="getMoodType(currentStudent.moodStatus)" size="small">{{ currentStudent.moodStatus }}</el-tag>
              </span>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-section">
          <h4>性格分析</h4>
          <p>该学生性格活泼开朗，乐于助人，在班级中表现出良好的人际交往能力。学习态度认真，能够独立完成各项任务，需要适度关注情绪波动情况。</p>
        </div>

        <el-divider />

        <div class="detail-section">
          <h4>最近表现</h4>
          <div class="behavior-list">
            <div class="behavior-item">
              <el-icon><Check /></el-icon>
              <span>本周上课积极发言</span>
            </div>
            <div class="behavior-item">
              <el-icon><Check /></el-icon>
              <span>按时完成作业</span>
            </div>
            <div class="behavior-item warning">
              <el-icon><Warning /></el-icon>
              <span>与同学发生小摩擦</span>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-section">
          <h4>教师备注</h4>
          <el-input type="textarea" :rows="2" placeholder="添加备注..." />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, OfficeBuilding, User, CircleCheck, Warning, Check } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { teacherApi } from '../../api/teacher'

interface Class {
  id: number
  name: string
  grade: string
  teacher: string
  studentCount: number
  room: string
  totalPoints: number
  avgPoints: number
  psychologyStatus: string
  status: string
}

const gradeFilter = ref('')
const searchText = ref('')

const classes = ref<Class[]>([])

const loadClasses = async () => {
  try {
    const data: any = await teacherApi.getClasses()
    if (Array.isArray(data)) classes.value = data
  } catch (e) {
    // 接口失败时保持页面可用，使用默认空值
  }
}

const filteredClasses = computed(() => {
  return classes.value.filter(c => {
    const matchGrade = !gradeFilter.value || c.grade === gradeFilter.value
    const matchSearch = !searchText.value || c.name.includes(searchText.value) || c.teacher.includes(searchText.value)
    return matchGrade && matchSearch
  })
})

const totalStudents = computed(() => filteredClasses.value.reduce((sum, c) => sum + c.studentCount, 0))
const normalClassCount = computed(() => filteredClasses.value.filter(c => c.status === 'normal').length)
const warningClassCount = computed(() => filteredClasses.value.filter(c => c.status === 'warning').length)

const getPsychologyType = (status: string) => {
  const map: Record<string, string> = { '良好': 'success', '关注': 'warning', '异常': 'danger' }
  return map[status] || ''
}

const handleViewStudents = (row: Class) => {
  currentClass.value = row
  fetchClassStudents(row.id)
  studentDialogVisible.value = true
}

const studentDialogVisible = ref(false)
const currentClass = ref<Class | null>(null)
const classStudents = ref<any[]>([])

const fetchClassStudents = async (classId: number) => {
  classStudents.value = []
  try {
    const data: any = await teacherApi.getClassStudents(classId)
    if (Array.isArray(data)) classStudents.value = data
  } catch (e) {
    // 接口失败时保持弹窗可用，列表为空
  }
}

const goodCount = computed(() => classStudents.value.filter(s => s.moodStatus === '良好').length)
const warningCount = computed(() => classStudents.value.filter(s => s.moodStatus !== '良好').length)

const getPetType = (level: string) => {
  const map: Record<string, string> = { 'S': 'danger', 'A': 'warning', 'B': 'primary', 'C': 'info' }
  return map[level] || ''
}

const getMoodType = (status: string) => {
  const map: Record<string, string> = { '良好': 'success', '一般': 'warning', '低落': 'danger' }
  return map[status] || ''
}

const viewStudentDetail = (row: any) => {
  currentStudent.value = row
  showStudentDetailDialog.value = true
}

const showStudentDetailDialog = ref(false)
const currentStudent = ref<any>(null)

const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = computed(() => isEdit.value ? '编辑班级' : '新增班级')

const classForm = reactive({ id: 0, name: '', grade: '', teacher: '', studentCount: 0, room: '', psychologyStatus: '', status: '' })
const formRef = ref<FormInstance>()

const rules: FormRules = {
  id: [{ required: true, message: '请输入班级编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  grade: [{ required: true, message: '请输入年级', trigger: 'blur' }]
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(classForm, { id: 0, name: '', grade: '', teacher: '', studentCount: 0, room: '', psychologyStatus: '', status: '' })
  dialogVisible.value = true
}

const handleEdit = (row: Class) => {
  isEdit.value = true
  Object.assign(classForm, row)
  dialogVisible.value = true
}

const handleDelete = async (row: Class) => {
  try {
    await ElMessageBox.confirm('确定要删除该班级吗？', '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    classes.value = classes.value.filter(c => c.id !== row.id)
    ElMessage.success('删除成功')
  } catch {}
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (isEdit.value) {
        const index = classes.value.findIndex(c => c.id === classForm.id)
        if (index > -1) classes.value[index] = { ...classForm, totalPoints: 0, avgPoints: 0 }
        ElMessage.success('编辑成功')
      } else {
        try {
          await teacherApi.createClass({ ...classForm })
          ElMessage.success('新增成功')
          await loadClasses()
        } catch (e) {
          // 错误已由拦截器提示
        }
      }
      dialogVisible.value = false
    }
  })
}

const handleDialogClose = () => { formRef.value?.resetFields() }

const importGradeFilter = ref('')
const importDialogVisible = ref(false)
const selectedClasses = ref<number[]>([])

const filteredAvailableClasses = computed(() => {
  if (!importGradeFilter.value) return availableClasses.value
  return availableClasses.value.filter(c => c.grade === importGradeFilter.value)
})

const toggleClass = (cls: any) => {
  const idx = selectedClasses.value.indexOf(cls.id)
  if (idx > -1) {
    selectedClasses.value.splice(idx, 1)
  } else {
    selectedClasses.value.push(cls.id)
  }
}

const availableClasses = ref([
  { id: 1, name: '一年级一班', grade: '一年级', teacher: '张老师', studentCount: 35, room: '101', psychologyStatus: '良好', status: 'normal' },
  { id: 2, name: '一年级二班', grade: '一年级', teacher: '刘老师', studentCount: 36, room: '102', psychologyStatus: '一般', status: 'normal' },
  { id: 3, name: '一年级三班', grade: '一年级', teacher: '陈老师', studentCount: 34, room: '103', psychologyStatus: '良好', status: 'normal' },
  { id: 4, name: '二年级一班', grade: '二年级', teacher: '赵老师', studentCount: 38, room: '201', psychologyStatus: '优秀', status: 'normal' },
  { id: 5, name: '二年级二班', grade: '二年级', teacher: '孙老师', studentCount: 37, room: '202', psychologyStatus: '良好', status: 'normal' },
  { id: 6, name: '二年级三班', grade: '二年级', teacher: '周老师', studentCount: 39, room: '203', psychologyStatus: '一般', status: 'normal' },
  { id: 7, name: '三年级一班', grade: '三年级', teacher: '李老师', studentCount: 40, room: '301', psychologyStatus: '良好', status: 'normal' },
  { id: 8, name: '三年级二班', grade: '三年级', teacher: '王老师', studentCount: 38, room: '302', psychologyStatus: '一般', status: 'normal' },
  { id: 9, name: '三年级三班', grade: '三年级', teacher: '张老师', studentCount: 42, room: '303', psychologyStatus: '优秀', status: 'normal' },
  { id: 10, name: '四年级一班', grade: '四年级', teacher: '钱老师', studentCount: 36, room: '401', psychologyStatus: '良好', status: 'normal' },
  { id: 11, name: '四年级二班', grade: '四年级', teacher: '郑老师', studentCount: 35, room: '402', psychologyStatus: '一般', status: 'normal' },
  { id: 12, name: '四年级三班', grade: '四年级', teacher: '冯老师', studentCount: 37, room: '403', psychologyStatus: '良好', status: 'normal' },
  { id: 13, name: '五年级一班', grade: '五年级', teacher: '曹老师', studentCount: 34, room: '501', psychologyStatus: '良好', status: 'normal' },
  { id: 14, name: '五年级二班', grade: '五年级', teacher: '卫老师', studentCount: 33, room: '502', psychologyStatus: '一般', status: 'normal' },
  { id: 15, name: '五年级三班', grade: '五年级', teacher: '蒋老师', studentCount: 35, room: '503', psychologyStatus: '优秀', status: 'normal' },
  { id: 16, name: '六年级一班', grade: '六年级', teacher: '沈老师', studentCount: 32, room: '601', psychologyStatus: '良好', status: 'normal' },
  { id: 17, name: '六年级二班', grade: '六年级', teacher: '韩老师', studentCount: 31, room: '602', psychologyStatus: '一般', status: 'normal' },
  { id: 18, name: '六年级三班', grade: '六年级', teacher: '杨老师', studentCount: 33, room: '603', psychologyStatus: '良好', status: 'normal' }
])

const handleExport = () => {
  ElMessage.success('导出成功')
}

const handleImport = () => {
  selectedClasses.value = []
  importDialogVisible.value = true
}

const confirmImport = async () => {
  const newClasses = availableClasses.value.filter(c => selectedClasses.value.includes(c.id))
  try {
    await teacherApi.importClass({ classIds: selectedClasses.value })
    ElMessage.success(`成功导入 ${newClasses.length} 个班级`)
    await loadClasses()
  } catch (e) {
    // 错误已由拦截器提示
  }
  importDialogVisible.value = false
}

onMounted(() => {
  loadClasses()
})
</script>

<style scoped>
.class-manage { padding: 0; }

.filter-bar {
  display: flex;
  justify-content: space-between;
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid #E8E0F0;
}

.filter-left, .filter-right { display: flex; }

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid #E8E0F0;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: 700; color: #333; }
.stat-label { font-size: 12px; color: #999; margin-top: 2px; }

.content-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid #E8E0F0;
  margin-top: 16px;
}

.content-card :deep(.el-table) {
  width: 100% !important;
}

.import-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.import-tip {
  color: #666;
  font-size: 14px;
}

.class-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  max-height: 340px;
  overflow-y: auto;
  padding: 4px;
}

.class-card {
  position: relative;
  background: #fafafa;
  border: 1px solid #e8e0f0;
  border-radius: 10px;
  padding: 14px 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.class-card:hover:not(.is-disabled) {
  border-color: #8985cf;
  background: #f5f3ff;
}

.class-card.is-selected {
  border-color: #8985cf;
  background: #f5f3ff;
}

.class-card.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.card-checkbox {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #d0c8e8;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #fff;
  background: #fff;
  transition: all 0.2s;
}

.class-card.is-selected .card-checkbox {
  border-color: #8985cf;
  background: #8985cf;
}

.card-content {
  text-align: center;
}

.class-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.class-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.grade-tag {
  font-size: 12px;
  color: #666;
}

.teacher-name {
  font-size: 11px;
  color: #999;
}

.added-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  background: #52c41a;
  color: #fff;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.selected-count {
  color: #8985cf;
  font-size: 13px;
}

.student-stats {
  display: flex;
  justify-content: center;
  gap: 60px;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.student-stats .stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.student-stats .stat-num {
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.student-stats .stat-num.good { color: #52c41a; }
.student-stats .stat-num.warning { color: #ff7875; }

.student-stats .stat-label {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
}

.text-good { color: #52c41a; }
.text-warning { color: #ff7875; }

:deep(.el-table .cell) {
  text-align: center;
}
:deep(.el-table .el-table__header-wrapper th) {
  text-align: center;
}
:deep(.el-dialog__body) {
  padding: 16px 20px 20px;
}
:deep(.el-table) {
  width: 100% !important;
}

.student-detail-content {
  padding: 8px 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.student-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.student-meta {
  display: flex;
  gap: 8px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 12px;
  color: #999;
}

.info-item .value {
  font-size: 15px;
  color: #333;
}

.detail-section p {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.8;
}

.behavior-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.behavior-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #52c41a;
}

.behavior-item.warning {
  color: #ff7875;
}
</style>
