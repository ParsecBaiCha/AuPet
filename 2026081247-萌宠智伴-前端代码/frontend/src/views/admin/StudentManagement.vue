<template>
  <div class="student-manage">
    <div class="filter-bar">
      <div class="filter-group">
        <el-select v-model="gradeFilter" placeholder="年级">
          <el-option label="全部年级" value="" />
          <el-option v-for="g in gradeList" :key="g" :label="g" :value="g" />
        </el-select>

        <el-select v-model="classFilter" placeholder="班级">
          <el-option label="全部" value="" />
          <el-option v-for="c in classList" :key="c" :label="c" :value="c" />
        </el-select>

        <el-select v-model="petLevelFilter" placeholder="宠物等级">
          <el-option label="全部" value="" />
          <el-option label="S级" value="S级" />
          <el-option label="A级" value="A级" />
          <el-option label="B级" value="B级" />
          <el-option label="C级" value="C级" />
        </el-select>
      </div>

      <div class="filter-group">
        <el-button type="primary" @click="refreshList">确认查询</el-button>
        <el-button type="primary" @click="openDialog">添加学生</el-button>
      </div>
    </div>

    <el-table :data="filteredStudents" border max-height="calc(100vh - 240px)" style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="姓名" min-width="80" />
      <el-table-column prop="class" label="班级" min-width="120" />
      <el-table-column prop="points" label="积分" width="80" />
      <el-table-column prop="petLevel" label="宠物等级" width="90" />
      <el-table-column prop="taskCompletionRate" label="任务完成率" min-width="100">
        <template #default="{ row }">
          <el-tag type="success" v-if="row.taskCompletionRate >= 90">{{ row.taskCompletionRate }}%</el-tag>
          <el-tag type="warning" v-else>{{ row.taskCompletionRate }}%</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="moodIndex" label="心情指标" min-width="150">
        <template #default="{ row }">
          <el-progress :percentage="row.moodIndex" :color="getMoodColor(row.moodIndex)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editStudent(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteStudent(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="学生信息" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="form.class">
            <el-option v-for="c in classList" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始积分">
          <el-input-number v-model="form.points" :min="0" />
        </el-form-item>
        <el-form-item label="宠物等级">
          <el-select v-model="form.petLevel">
            <el-option label="S级" value="S级" />
            <el-option label="A级" value="A级" />
            <el-option label="B级" value="B级" />
            <el-option label="C级" value="C级" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务完成率">
          <el-input-number v-model="form.taskCompletionRate" />
        </el-form-item>
        <el-form-item label="心情指标">
          <el-slider v-model="form.moodIndex" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStudent">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../../api/admin'

interface Student {
  id: string
  name: string
  class: string
  points: number
  status: string
  petLevel: string
  taskCompletionRate: number
  moodIndex: number
}

const gradeFilter = ref('')
const classFilter = ref('')
const petLevelFilter = ref('')
const dialogVisible = ref(false)
const loading = ref(false)

const gradeList = ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级']
const classList = ['一年级1班', '一年级2班', '一年级3班', '二年级1班', '二年级2班', '二年级3班', '三年级1班', '三年级2班', '三年级3班', '四年级1班', '四年级2班', '四年级3班', '五年级1班', '五年级2班', '五年级3班', '六年级1班', '六年级2班', '六年级3班']

const students = ref<Student[]>([])

const form = ref<{ id?: string; name: string; class: string; points: number; status: string; petLevel: string; taskCompletionRate: number; moodIndex: number }>({
  name: '', class: '', points: 0, status: 'active',
  petLevel: 'B级', taskCompletionRate: 80, moodIndex: 50
})

const fetchStudents = async () => {
  loading.value = true
  try {
    const res = await adminApi.getStudents({ page: 1, size: 20 })
    if (res?.success && Array.isArray(res.data)) {
      students.value = res.data.map((s: any) => ({
        id: s.sno,
        name: s.name,
        class: s.className || '',
        points: s.points || 0,
        petLevel: s.petLevel || 'C级',
        taskCompletionRate: s.taskCompletionRate || 0,
        moodIndex: typeof s.moodIndex === 'number' && s.moodIndex <= 5 ? s.moodIndex * 20 : s.moodIndex,
        status: s.status === 1 || s.status === 'active' ? 'active' : 'inactive',
      }))
    }
  } catch (e) {
    console.error('获取学生列表失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchStudents)

const filteredStudents = computed(() => {
  return students.value.filter(s => {
    if (gradeFilter.value && !s.class.startsWith(gradeFilter.value)) return false
    if (classFilter.value && s.class !== classFilter.value) return false
    if (petLevelFilter.value && s.petLevel !== petLevelFilter.value) return false
    return true
  })
})

const getMoodColor = (index: number) => {
  if (index >= 80) return '#52c41a'
  if (index >= 60) return '#f4bb6e'
  return '#f48d45'
}

const refreshList = () => { fetchStudents() }

const openDialog = () => {
  form.value = { name: '', class: '', points: 0, status: 'active', petLevel: 'B级', taskCompletionRate: 80, moodIndex: 50 }
  dialogVisible.value = true
}

const editStudent = (row: Student) => {
  form.value = { ...row }
  dialogVisible.value = true
}

const saveStudent = async () => {
  try {
    if (form.value.id) {
      await adminApi.updateStudent(form.value.id, {
        name: form.value.name,
        className: form.value.class,
        points: form.value.points,
        moodIndex: form.value.moodIndex,
        petLevel: form.value.petLevel,
        taskCompletionRate: form.value.taskCompletionRate,
      })
      ElMessage.success('更新成功')
    } else {
      await adminApi.createStudent({
        name: form.value.name,
        className: form.value.class,
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchStudents()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const deleteStudent = async (id: string) => {
  try {
    await adminApi.deleteStudent(id)
    ElMessage.success('已删除')
    fetchStudents()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.student-manage {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: space-between;
}

.filter-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-group .el-select {
  width: 200px;
}

:deep(.filter-group .el-button) {
  background: #8985cf;
  border-color: #8985cf;
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table th) {
  background: #f5f3f0 !important;
  color: #333;
  font-weight: 600;
}

:deep(.el-button) {
  border-radius: 8px;
}
</style>
