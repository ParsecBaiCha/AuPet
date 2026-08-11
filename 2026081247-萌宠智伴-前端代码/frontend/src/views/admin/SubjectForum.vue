<template>
  <div class="forum-subject">
    <div class="filter-bar">
      <div class="filter-group">
        <el-select v-model="subjectFilter" placeholder="筛选学科">
          <el-option label="全部" value="" />
          <el-option label="语文" value="语文" />
          <el-option label="数学" value="数学" />
          <el-option label="英语" value="英语" />
          <el-option label="科学" value="科学" />
          <el-option label="体育" value="体育" />
          <el-option label="美术" value="美术" />
        </el-select>

        <el-select v-model="statusFilter" placeholder="筛选审核状态">
          <el-option label="全部" value="" />
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
      </div>

      <div class="filter-group">
        <el-button type="primary" @click="refreshList">确认查询</el-button>
        <el-button type="primary" @click="openDialog">发布帖子</el-button>
      </div>
    </div>

    <el-table :data="filterPosts" border max-height="calc(100vh - 240px)">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column prop="author" label="作者" width="90" />
      <el-table-column prop="createTime" label="发布时间" width="160" />
      <el-table-column prop="status" label="审核状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'">
            {{ row.status === 'approved' ? '已通过' : row.status === 'rejected' ? '已驳回' : '待审核' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="置顶" width="80">
        <template #default="{ row }">
          <el-switch :model-value="row.isTop" @change="handleToggleTop(row.id)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editPost(row)">编辑</el-button>
          <el-button size="small" type="success" @click="auditPost(row.id, 'approved')">通过</el-button>
          <el-button size="small" type="danger" @click="auditPost(row.id, 'rejected')">驳回</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="帖子信息" width="550px">
      <el-form :model="form">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" rows="5" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="form.author" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePost">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../../api/admin'

interface Post {
  id: number
  title: string
  content: string
  author: string
  type: string
  subject?: string
  status: string
  isTop: boolean
  createTime: string
}

const dialogVisible = ref(false)
const statusFilter = ref('')
const subjectFilter = ref('')
const loading = ref(false)

const form = ref<{ id?: number; title: string; content: string; author: string; type: string; subject?: string; status: string; isTop: boolean }>({
  title: '', content: '', author: '',
  type: 'subject', status: 'pending', isTop: false
})

const posts = ref<Post[]>([])

const fetchPosts = async () => {
  loading.value = true
  try {
    const res = await adminApi.getSubjectForumPosts()
    if (res?.success && Array.isArray(res.data)) {
      posts.value = res.data.map((p: any) => ({
        id: p.id,
        title: p.title,
        content: p.content,
        author: p.authorName,
        type: 'subject',
        subject: p.subject || '',
        status: p.status || 'approved',
        isTop: p.isTop === 1 || p.isTop === true,
        createTime: p.createTime ? p.createTime.replace('T', ' ').slice(0, 16) : '',
      }))
    }
  } catch (e) {
    console.error('获取学科帖子列表失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchPosts)

const filterPosts = computed(() => {
  let result = posts.value.filter(p => p.type === 'subject')
  if (subjectFilter.value) {
    result = result.filter(p => p.subject === subjectFilter.value)
  }
  if (statusFilter.value) {
    result = result.filter(p => p.status === statusFilter.value)
  }
  return result.sort((a, b) => (b.isTop ? 1 : 0) - (a.isTop ? 1 : 0))
})

const refreshList = () => { fetchPosts() }

const openDialog = () => {
  form.value = { title: '', content: '', author: '', type: 'subject', status: 'pending', isTop: false }
  dialogVisible.value = true
}

const editPost = (row: Post) => {
  form.value = { ...row }
  dialogVisible.value = true
}

const savePost = async () => {
  try {
    if (form.value.id) {
      const idx = posts.value.findIndex(p => p.id === form.value.id)
      if (idx >= 0) posts.value[idx] = { ...posts.value[idx], ...form.value }
      ElMessage.success('保存成功')
    } else {
      await adminApi.createAnnouncement({
        title: form.value.title,
        content: form.value.content,
        authorName: form.value.author,
        type: 'subject',
        subject: form.value.subject || '',
      })
      ElMessage.success('发布成功')
      fetchPosts()
    }
    dialogVisible.value = false
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const deletePost = async (id: number) => {
  try {
    await adminApi.deletePost(id)
    ElMessage.success('已删除')
    fetchPosts()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const handleToggleTop = async (id: number) => {
  try {
    await adminApi.toggleTop(id)
    const post = posts.value.find(p => p.id === id)
    if (post) post.isTop = !post.isTop
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const auditPost = async (id: number, status: 'approved' | 'rejected') => {
  try {
    await adminApi.reviewPost(id, { status })
    const post = posts.value.find(p => p.id === id)
    if (post) post.status = status
    ElMessage.success(status === 'approved' ? '已通过' : '已驳回')
  } catch (e) {
    ElMessage.error('审核失败')
  }
}
</script>

<style scoped>
.forum-subject {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
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
</style>
