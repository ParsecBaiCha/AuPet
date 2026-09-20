<template>
  <div class="ai-book-assets">
    <el-card class="filter-card" shadow="never">
      <div class="filter-bar">
        <div class="filter-left">
          <span class="filter-label">学段</span>
          <el-select v-model="gradeLevel" placeholder="全部学段" style="width: 170px" @change="loadAssets">
            <el-option v-for="opt in GRADE_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-button text type="primary" :loading="loading" @click="loadAssets">
            <el-icon><Refresh /></el-icon>
            <span>刷新</span>
          </el-button>
        </div>
        <div class="filter-right">
          <el-tag size="small" type="info">共 {{ assets.length }} 门课程</el-tag>
          <el-tag size="small" type="success">其中 {{ photoCourseCount }} 门已有照片</el-tag>
        </div>
      </div>
    </el-card>

    <el-alert
      v-if="rootUnavailable"
      type="error"
      show-icon
      :closable="false"
      title="后端未找到照片绘本目录"
      description="请确认前端 public/images/picture_books 目录存在，否则无法上传或删除照片，学生端也将无法阅读。"
    />

    <div class="content-layout">
      <el-card class="course-panel" shadow="hover" v-loading="loading">
        <template #header>
          <div class="card-header">
            <el-icon><Collection /></el-icon>
            <span>课程列表（{{ assets.length }}）</span>
          </div>
        </template>
        <div v-if="assets.length" class="course-list">
          <div
            v-for="item in assets"
            :key="item.courseId"
            class="course-item"
            :class="{ active: item.courseId === activeCourseId }"
            @click="selectCourse(item)"
          >
            <div class="course-item-title">{{ item.title || '未命名课程' }}</div>
            <div class="course-item-meta">
              <el-tag size="small" :type="item.count > 0 ? 'success' : 'info'">
                {{ item.count > 0 ? `已有 ${item.count} 张` : '待上传' }}
              </el-tag>
              <el-tag v-if="item.mismatched" size="small" type="warning">目录名与标题不一致</el-tag>
            </div>
            <div class="course-item-dir">目录：{{ item.bookDir || '—' }}</div>
          </div>
        </div>
        <el-empty v-else description="当前学段下暂无课程" :image-size="80" />
      </el-card>

      <el-card class="asset-panel" shadow="hover" v-loading="detailLoading">
        <template #header>
          <div class="card-header">
            <el-icon><Picture /></el-icon>
            <span>{{ activeAsset ? activeAsset.title : '照片绘本' }}</span>
            <span v-if="activeAsset" class="header-dir">/images/picture_books/{{ activeAsset.bookDir }}/</span>
          </div>
        </template>

        <template v-if="activeAsset">
          <div v-if="activeAsset.mismatched" class="warn-line">
            <el-icon><Warning /></el-icon>
            <span>该课程实际目录名为「{{ activeAsset.bookDir }}」，与课程标题不一致，请确认照片是否挂在该目录下。</span>
          </div>

          <div class="upload-zone">
            <el-upload
              v-model:file-list="fileList"
              :auto-upload="false"
              multiple
              accept="image/*"
              :disabled="!canUpload"
            >
              <el-button type="primary" plain :disabled="!canUpload">
                <el-icon><Plus /></el-icon>
                <span>选择图片</span>
              </el-button>
              <template #tip>
                <div class="upload-tip">
                  支持一次选择多张图片；文件名以 01_、02_ 开头决定页码顺序（如 01_封面.png、02_第一页.png）。
                </div>
              </template>
            </el-upload>
            <div class="upload-actions">
              <el-button
                type="primary"
                :loading="uploading"
                :disabled="!canUpload || !fileList.length"
                @click="handleUpload"
              >
                <el-icon><UploadFilled /></el-icon>
                <span>上传到本课</span>
              </el-button>
              <el-button :disabled="!fileList.length" @click="clearSelected">清空选择</el-button>
              <span class="upload-count">已选择 {{ fileList.length }} 个文件</span>
            </div>
            <div v-if="!canUpload" class="upload-disabled-tip">照片目录不可用，已禁用上传。</div>
          </div>

          <el-divider />

          <div v-if="activeAsset.files.length" class="photo-grid">
            <div v-for="file in activeAsset.files" :key="file" class="photo-item">
              <div class="photo-thumb">
                <img :src="photoUrl(file)" :alt="file" loading="lazy" />
              </div>
              <div class="photo-name" :title="file">{{ file }}</div>
              <el-button text type="danger" size="small" @click="handleDelete(file)">删除</el-button>
            </div>
          </div>
          <el-empty v-else description="本课还没有照片绘本，上传图片后学生端即可阅读" :image-size="90">
            <div class="empty-naming">命名规则：文件名以 01_、02_ 开头决定页码顺序，例如 01_封面.png、02_第一页.png。</div>
          </el-empty>
        </template>

        <el-empty v-else description="请先在左侧选择一门课程" :image-size="100" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadUserFile } from 'element-plus'
import { Collection, Picture, Plus, Refresh, UploadFilled, Warning } from '@element-plus/icons-vue'
import { teacherApi } from '../../api/teacher'

interface BookAsset {
  courseId: number
  title: string
  gradeLevel: string
  bookDir: string
  exists: boolean
  count: number
  files: string[]
  mismatched: boolean
  rootAvailable: boolean
}

const GRADE_OPTIONS = [
  { value: '', label: '全部学段' },
  { value: 'lower_primary', label: '小学低年级' },
  { value: 'upper_primary', label: '小学高年级' },
  { value: 'middle_school', label: '初中' },
  { value: 'high_school', label: '高中' },
]

const gradeLevel = ref('')
const loading = ref(false)
const detailLoading = ref(false)
const uploading = ref(false)
const assets = ref<BookAsset[]>([])
const activeCourseId = ref(0)
const fileList = ref<UploadUserFile[]>([])

const activeAsset = computed<BookAsset | null>(() => {
  return assets.value.find(item => item.courseId === activeCourseId.value) || null
})

const photoCourseCount = computed(() => assets.value.filter(item => item.count > 0).length)

const rootUnavailable = computed(() => assets.value.some(item => item.rootAvailable === false))

const canUpload = computed(() => !!activeAsset.value && activeAsset.value.rootAvailable !== false)

const activeDir = computed(() => activeAsset.value?.bookDir || activeAsset.value?.title || '')

const photoUrl = (file: string) => {
  return `/images/picture_books/${encodeURIComponent(activeDir.value)}/${encodeURIComponent(file)}`
}

const loadAssets = async () => {
  loading.value = true
  try {
    const params = gradeLevel.value ? { gradeLevel: gradeLevel.value } : undefined
    const data: any = await teacherApi.getAIBookAssets(params)
    const list = Array.isArray(data) ? data : []
    assets.value = list.map((item: any) => ({
      courseId: Number(item?.courseId) || 0,
      title: item?.title || '',
      gradeLevel: item?.gradeLevel || '',
      bookDir: item?.bookDir || item?.title || '',
      exists: !!item?.exists,
      count: Number(item?.count) || 0,
      files: Array.isArray(item?.files) ? item.files.filter((f: unknown) => typeof f === 'string' && !!f) : [],
      mismatched: !!item?.mismatched,
      rootAvailable: item?.rootAvailable !== false,
    }))
    if (!assets.value.some(item => item.courseId === activeCourseId.value)) {
      activeCourseId.value = 0
    }
    fileList.value = []
  } catch (e) {
    assets.value = []
    activeCourseId.value = 0
    fileList.value = []
  } finally {
    loading.value = false
  }
}

const selectCourse = (item: BookAsset) => {
  if (activeCourseId.value === item.courseId) return
  activeCourseId.value = item.courseId
  fileList.value = []
}

const clearSelected = () => {
  fileList.value = []
}

const collectFiles = (): File[] => {
  const files: File[] = []
  fileList.value.forEach(item => {
    if (item.raw) files.push(item.raw)
  })
  return files
}

const handleUpload = async () => {
  const asset = activeAsset.value
  if (!asset) return
  if (asset.rootAvailable === false) {
    ElMessage.warning('照片目录不可用，暂时无法上传')
    return
  }
  const files = collectFiles()
  if (!files.length) {
    ElMessage.warning('请先选择要上传的图片')
    return
  }
  uploading.value = true
  try {
    const res: any = await teacherApi.uploadAIBookPhotos(asset.courseId, files)
    ElMessage.success(res?.message || `已上传 ${files.length} 张照片`)
    fileList.value = []
    await loadAssets()
  } catch (e) {
    // 失败提示由接口拦截器统一展示，保留已选择的文件
  } finally {
    uploading.value = false
  }
}

const handleDelete = async (file: string) => {
  const asset = activeAsset.value
  if (!asset) return
  try {
    await ElMessageBox.confirm(`确定删除照片「${file}」吗？删除后学生端将不再展示。`, '提示', { type: 'warning' })
  } catch (e) {
    return
  }
  detailLoading.value = true
  try {
    const res: any = await teacherApi.deleteAIBookPhoto(asset.courseId, file)
    ElMessage.success(res?.message || '已删除该照片')
    await loadAssets()
  } catch (e) {
    // 失败提示由接口拦截器统一展示
  } finally {
    detailLoading.value = false
  }
}

onMounted(() => {
  loadAssets()
})
</script>

<style scoped>
.ai-book-assets {
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

.filter-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-layout {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.course-panel {
  width: 320px;
  flex-shrink: 0;
}

.asset-panel {
  flex: 1;
  min-width: 0;
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

.header-dir {
  font-size: 12px;
  font-weight: 400;
  color: #909399;
  word-break: break-all;
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
  flex-wrap: wrap;
  gap: 6px;
}

.course-item-dir {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
  word-break: break-all;
}

.warn-line {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  margin-bottom: 12px;
  border-radius: 8px;
  background: #fff7ef;
  color: #f48d45;
  font-size: 13px;
}

.upload-zone {
  padding: 14px;
  border-radius: 10px;
  border: 1px dashed #d8d4ec;
  background: #fbfaff;
}

.upload-tip {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}

.upload-actions {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.upload-count {
  font-size: 12px;
  color: #909399;
}

.upload-disabled-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #f56c6c;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 14px;
}

.photo-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #ece9f6;
  background: #fff;
}

.photo-thumb {
  width: 100%;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f3f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.photo-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-name {
  width: 100%;
  font-size: 12px;
  color: #606266;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-naming {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
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
