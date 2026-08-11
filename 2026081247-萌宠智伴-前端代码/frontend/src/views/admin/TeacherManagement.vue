<template>
  <div class="teacher-manage">
    <div class="filter-bar">
      <div class="filter-group">
        <el-select v-model="qualificationFilter" placeholder="教师资历">
          <el-option label="全部" value="" />
          <el-option label="资深教师" value="资深教师" />
          <el-option label="任课教师" value="任课教师" />
          <el-option label="实习教师" value="实习教师" />
        </el-select>

        <el-select v-model="subjectFilter" placeholder="所属科研组">
          <el-option label="全部" value="" />
          <el-option label="数学科研组" value="数学科研组" />
          <el-option label="语文科研组" value="语文科研组" />
          <el-option label="英语科研组" value="英语科研组" />
          <el-option label="体育科研组" value="体育科研组" />
          <el-option label="科学科研组" value="科学科研组" />
        </el-select>
      </div>

      <div class="filter-group">
        <el-button type="primary" @click="refreshList">确认查询</el-button>
        <el-button type="primary" @click="openDialog">添加教师</el-button>
      </div>
    </div>

    <el-table :data="filteredTeachers" border max-height="calc(100vh - 240px)" style="width: 100%">
      <el-table-column prop="id" label="教师ID" width="80">
        <template #default="{ row }">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="姓名" min-width="70" />
      <el-table-column prop="subject" label="所属科研组" min-width="100" />
      <el-table-column prop="teachingClass" label="所教班级" min-width="120" />
      <el-table-column prop="qualification" label="教师资历" min-width="110">
        <template #default="{ row }">
          <el-tag :type="getQualificationTagType(row.qualification)">{{ row.qualification }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="simulationCount" label="模拟次数" width="90" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editTeacher(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteTeacher(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="教师信息" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="所属科研组">
          <el-select v-model="form.subject">
            <el-option label="数学科研组" value="数学科研组" />
            <el-option label="语文科研组" value="语文科研组" />
            <el-option label="英语科研组" value="英语科研组" />
            <el-option label="体育科研组" value="体育科研组" />
            <el-option label="科学科研组" value="科学科研组" />
          </el-select>
        </el-form-item>
        <el-form-item label="所教班级"><el-input v-model="form.teachingClass" placeholder="如: 一年级1班,一年级2班" /></el-form-item>
        <el-form-item label="教师资历">
          <el-select v-model="form.qualification">
            <el-option label="资深教师" value="资深教师" />
            <el-option label="任课教师" value="任课教师" />
            <el-option label="实习教师" value="实习教师" />
          </el-select>
        </el-form-item>
        <el-form-item label="模拟次数"><el-input-number v-model="form.simulationCount" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTeacher">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../../api/admin'

interface Teacher {
  id: string
  name: string
  subject: string
  teachingClass: string
  qualification: string
  status: string
  simulationCount: number
}

const qualificationFilter = ref('')
const subjectFilter = ref('')
const dialogVisible = ref(false)
const loading = ref(false)

const teachers = ref<Teacher[]>([])

const form = ref<{ id?: string; name: string; subject: string; teachingClass: string; qualification: string; status: string; simulationCount: number }>({
  name: '', subject: '', status: 'active',
  qualification: '任课教师', simulationCount: 0, teachingClass: ''
})

const fetchTeachers = async () => {
  loading.value = true
  try {
    const res = await adminApi.getTeachers()
    if (res?.success && Array.isArray(res.data)) {
      teachers.value = res.data.map((t: any) => ({
        id: t.tno,
        name: t.name,
        subject: t.subject || '',
        teachingClass: t.teachingClass || '',
        qualification: t.qualification || '',
        status: t.status === 1 || t.status === 'active' ? 'active' : 'inactive',
        simulationCount: t.simulationCount || 0,
      }))
    }
  } catch (e) {
    console.error('获取教师列表失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchTeachers)

const filteredTeachers = computed(() => {
  return teachers.value.filter(t => {
    if (qualificationFilter.value && t.qualification !== qualificationFilter.value) return false
    if (subjectFilter.value && t.subject !== subjectFilter.value) return false
    return true
  })
})

const getQualificationTagType = (type: string | undefined) => {
  switch (type) {
    case '资深教师': return 'success'
    case '任课教师': return 'info'
    case '实习教师': return 'warning'
    default: return 'default'
  }
}

const refreshList = () => { fetchTeachers() }

const openDialog = () => {
  form.value = { name: '', subject: '', status: 'active', qualification: '任课教师', simulationCount: 0, teachingClass: '' }
  dialogVisible.value = true
}

const editTeacher = (row: Teacher) => {
  form.value = { ...row }
  dialogVisible.value = true
}

const saveTeacher = async () => {
  try {
    if (form.value.id) {
      await adminApi.updateTeacher(form.value.id, {
        name: form.value.name,
        subject: form.value.subject,
        teachingClass: form.value.teachingClass,
        qualification: form.value.qualification,
        simulationCount: form.value.simulationCount,
      })
      ElMessage.success('更新成功')
    } else {
      await adminApi.createTeacher({
        name: form.value.name,
        subject: form.value.subject,
        teachingClass: form.value.teachingClass,
        qualification: form.value.qualification,
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchTeachers()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const deleteTeacher = async (id: string) => {
  try {
    await adminApi.deleteTeacher(id)
    ElMessage.success('已删除')
    fetchTeachers()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.teacher-manage {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  gap: 8px;
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
