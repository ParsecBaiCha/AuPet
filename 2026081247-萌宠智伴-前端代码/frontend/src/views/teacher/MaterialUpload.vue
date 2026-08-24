<template>
  <div class="material-upload">
    <el-card class="upload-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Upload /></el-icon>
          <span>上传学习资料</span>
        </div>
      </template>
      <el-form :model="form" label-width="80px" @submit.prevent="handleUpload">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入资料标题，如：Python入门教程" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" placeholder="选择资料类型">
            <el-option label="视频" value="video" />
            <el-option label="文档" value="doc" />
            <el-option label="课件" value="ppt" />
            <el-option label="链接" value="link" />
          </el-select>
        </el-form-item>
        <el-form-item label="链接">
          <el-input v-model="form.url" placeholder="请粘贴资料链接（如B站视频链接、文档网址等）" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="简要描述资料内容（选填）" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="uploading" @click="handleUpload">
            <el-icon><UploadFilled /></el-icon> 上传资料
          </el-button>
          <el-button @click="resetForm">清空</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="list-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><FolderOpened /></el-icon>
          <span>已上传资料 ({{ materials.length }})</span>
          <el-button text type="primary" :loading="loading" @click="loadMaterials" style="margin-left: auto;">
            刷新
          </el-button>
        </div>
      </template>
      <el-table :data="materials" v-loading="loading" style="width: 100%" empty-text="暂无上传资料">
        <el-table-column prop="title" label="标题" min-width="160" />
        <el-table-column prop="type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="typeTagMap[row.type] || 'info'">
              {{ typeLabelMap[row.type] || '链接' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="简介" min-width="200" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="上传日期" width="110" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button text type="primary" @click="openUrl(row.url)">访问</el-button>
            <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { teacherApi } from '../../api/teacher'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, UploadFilled, FolderOpened } from '@element-plus/icons-vue'

const form = ref({
  title: '',
  type: 'link',
  url: '',
  description: '',
})
const uploading = ref(false)
const loading = ref(false)
const materials = ref<any[]>([])

const typeLabelMap: Record<string, string> = {
  video: '视频',
  doc: '文档',
  ppt: '课件',
  link: '链接',
}
const typeTagMap: Record<string, string> = {
  video: 'danger',
  doc: 'warning',
  ppt: 'success',
  link: 'info',
}

const loadMaterials = async () => {
  loading.value = true
  try {
    const data: any = await teacherApi.getMaterials()
    materials.value = Array.isArray(data) ? data : []
  } catch (e) {
    materials.value = []
  } finally {
    loading.value = false
  }
}

const handleUpload = async () => {
  if (!form.value.title.trim() || !form.value.url.trim()) {
    ElMessage.warning('标题和链接不能为空')
    return
  }
  uploading.value = true
  try {
    await teacherApi.uploadMaterial({ ...form.value })
    ElMessage.success('上传成功！')
    resetForm()
    loadMaterials()
  } catch (e) {
    ElMessage.error('上传失败，请稍后重试')
  } finally {
    uploading.value = false
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除「${row.title}」吗？`, '提示', { type: 'warning' })
    await teacherApi.deleteMaterial(row.id)
    ElMessage.success('已删除')
    loadMaterials()
  } catch (e) { /* cancelled */ }
}

const resetForm = () => {
  form.value = { title: '', type: 'link', url: '', description: '' }
}

const openUrl = (url: string) => {
  window.open(url, '_blank')
}

onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.material-upload {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.upload-card {
  max-width: 700px;
}
.list-card {
  width: 100%;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}
</style>
