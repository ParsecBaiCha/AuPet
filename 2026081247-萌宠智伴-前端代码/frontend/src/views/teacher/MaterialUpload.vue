<template>
  <div class="material-upload">
    <el-card class="upload-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Upload /></el-icon>
          <span>添加学习资料</span>
          <el-tag size="small" type="info" effect="plain" class="header-tip">
            视频等大文件请用「上传文件」，外站资源用「添加网站」
          </el-tag>
        </div>
      </template>

      <el-radio-group v-model="mode" class="mode-switch">
        <el-radio-button value="link">
          <el-icon><Link /></el-icon>
          <span>添加网站</span>
        </el-radio-button>
        <el-radio-button value="file">
          <el-icon><UploadFilled /></el-icon>
          <span>上传文件</span>
        </el-radio-button>
      </el-radio-group>

      <el-form :model="form" label-width="80px" @submit.prevent="submit">
        <el-form-item label="标题">
          <el-input
            v-model="form.title"
            :placeholder="mode === 'link' ? '请输入资料标题，如：Python入门教程' : '留空则自动使用文件名作为标题'"
          />
        </el-form-item>

        <el-form-item label="类型">
          <el-select v-model="form.type" placeholder="选择资料类型" style="width: 100%">
            <el-option label="视频" value="video" />
            <el-option label="文档" value="doc" />
            <el-option label="课件" value="ppt" />
            <el-option v-if="mode === 'link'" label="链接" value="link" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="mode === 'link'" label="链接">
          <el-input v-model="form.url" placeholder="请粘贴资料链接（如B站视频链接、文档网址等）" />
        </el-form-item>

        <el-form-item v-else label="文件">
          <el-upload
            class="file-uploader"
            drag
            :auto-upload="false"
            :limit="1"
            :file-list="fileList"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :on-exceed="handleExceed"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">把文件拖到这里，或<em>点击选择文件</em></div>
            <template #tip>
              <div class="upload-tip">
                支持视频（mp4 / webm）、课件（ppt / pptx）、文档（pdf / word / 表格 / 文本），单个文件不超过 200MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="简要描述资料内容（选填）" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="uploading" @click="submit">
            <el-icon><UploadFilled /></el-icon>
            {{ mode === 'link' ? '添加网站' : '上传文件' }}
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
        <el-table-column label="存放位置" width="110">
          <template #default="{ row }">
            <el-tag size="small" :type="isLocalFile(row.url) ? 'success' : 'info'" effect="plain">
              {{ isLocalFile(row.url) ? '本站文件' : '外部链接' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="简介" min-width="180" show-overflow-tooltip />
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
import { Upload, UploadFilled, FolderOpened, Link } from '@element-plus/icons-vue'

const mode = ref<'link' | 'file'>('link')

const form = ref({
  title: '',
  type: 'link',
  url: '',
  description: '',
})
const uploading = ref(false)
const loading = ref(false)
const materials = ref<any[]>([])

// 待上传文件（未选类型时按扩展名自动判断）
const fileList = ref<any[]>([])
const selectedFile = ref<File | null>(null)

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

const extTypeMap: Record<string, string> = {
  mp4: 'video', webm: 'video', mov: 'video', m4v: 'video', ogv: 'video',
  pdf: 'doc', doc: 'doc', docx: 'doc', txt: 'doc', md: 'doc', xls: 'doc', xlsx: 'doc',
  ppt: 'ppt', pptx: 'ppt',
}

const guessType = (fileName: string): string => {
  const ext = (fileName.split('.').pop() || '').toLowerCase()
  return extTypeMap[ext] || ''
}

const isLocalFile = (url: string): boolean => !!url && url.startsWith('/uploads/')

const handleFileChange = (file: any) => {
  selectedFile.value = file?.raw || null
  fileList.value = file ? [file] : []
  const guessed = guessType(file?.name || '')
  if (guessed) form.value.type = guessed
}

const handleFileRemove = () => {
  selectedFile.value = null
  fileList.value = []
}

// 只允许一个文件：超出时用新文件替换旧的
const handleExceed = (files: File[]) => {
  const file = files?.[0]
  if (!file) return
  handleFileChange({ name: file.name, raw: file })
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

const submit = () => {
  if (mode.value === 'link') {
    handleUploadLink()
  } else {
    handleUploadFile()
  }
}

const handleUploadLink = async () => {
  if (!form.value.title.trim() || !form.value.url.trim()) {
    ElMessage.warning('标题和链接不能为空')
    return
  }
  uploading.value = true
  try {
    await teacherApi.uploadMaterial({ ...form.value })
    ElMessage.success('添加成功！')
    resetForm()
    loadMaterials()
  } catch (e) {
    ElMessage.error('添加失败，请稍后重试')
  } finally {
    uploading.value = false
  }
}

const handleUploadFile = async () => {
  const file = selectedFile.value
  if (!file) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }
  const type = form.value.type === 'link' ? (guessType(file.name) || 'doc') : form.value.type
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('title', form.value.title.trim())
    fd.append('type', type)
    fd.append('description', form.value.description)
    await teacherApi.uploadMaterialFile(fd)
    ElMessage.success('文件已上传到服务器')
    resetForm()
    loadMaterials()
  } catch (e) {
    ElMessage.error('上传失败，请稍后重试')
  } finally {
    uploading.value = false
  }
}

const handleDelete = async (row: any) => {
  const tip = isLocalFile(row.url)
    ? `确定删除「${row.title}」吗？服务器上的文件也会一起删除。`
    : `确定删除「${row.title}」吗？`
  try {
    await ElMessageBox.confirm(tip, '提示', { type: 'warning' })
    await teacherApi.deleteMaterial(row.id)
    ElMessage.success('已删除')
    loadMaterials()
  } catch (e) { /* cancelled */ }
}

const resetForm = () => {
  form.value = { title: '', type: mode.value === 'link' ? 'link' : 'doc', url: '', description: '' }
  fileList.value = []
  selectedFile.value = null
}

const openUrl = (url: string) => {
  if (!url) return
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
.header-tip {
  margin-left: auto;
  font-weight: 400;
}
.mode-switch {
  margin-bottom: 18px;
}
.mode-switch :deep(.el-radio-button__inner) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.file-uploader {
  width: 100%;
}
.file-uploader :deep(.el-upload),
.file-uploader :deep(.el-upload-dragger) {
  width: 100%;
}
.upload-icon {
  font-size: 40px;
  color: #c0c4cc;
  margin-top: 8px;
}
.upload-text {
  margin-top: 6px;
  font-size: 14px;
  color: #606266;
}
.upload-text em {
  color: #8985cf;
  font-style: normal;
  font-weight: 600;
}
.upload-tip {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
  line-height: 1.6;
}
</style>
