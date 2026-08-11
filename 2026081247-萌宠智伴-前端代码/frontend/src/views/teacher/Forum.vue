<template>
  <div class="forum-container">
    <div class="filter-bar">
      <div class="filter-left">
        <el-input v-model="searchText" placeholder="搜索帖子" clearable style="width: 200px">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
      <div class="filter-right">
        <el-button type="primary" @click="showPostDialog = true" style="background: #f48d45; border-color: #f48d45">
          <el-icon><Plus /></el-icon>发布帖子
        </el-button>
      </div>
    </div>

    <div class="main-content">
      <aside class="forum-sidebar">
        <div class="sidebar-header">全部板块</div>
        <div class="forum-list">
          <div 
            class="forum-item" 
            :class="{ active: selectedForum === null }"
            @click="selectForum(null)"
          >
            <span class="forum-name">全部帖子</span>
          </div>

          <div 
            class="forum-item" 
            :class="{ active: selectedForum === 1 }"
            @click="selectForum(1)"
            style="background: #FFF7E6;"
          >
            <span class="forum-name" style="color: #f48d45;">校园公告区</span>
          </div>
          
          <div class="forum-group">
            <div class="group-header" @click="toggleGroup('subject')">
              <el-icon><Reading /></el-icon>
              <span>学科专区</span>
              <el-icon class="arrow" :class="{ expanded: expandedGroups.subject }"><CaretRight /></el-icon>
            </div>
            <div class="group-children" v-show="expandedGroups.subject">
              <div 
                v-for="forum in subjectForums" 
                :key="forum.id"
                class="forum-item child"
                :class="{ active: selectedForum === forum.id }"
                @click="selectForum(forum.id)"
              >
                <span class="forum-name">{{ forum.name }}</span>
              </div>
            </div>
          </div>

          <div class="forum-group">
            <div class="group-header" @click="toggleGroup('daily')">
              <el-icon><ChatDotSquare /></el-icon>
              <span>日常交流</span>
              <el-icon class="arrow" :class="{ expanded: expandedGroups.daily }"><CaretRight /></el-icon>
            </div>
            <div class="group-children" v-show="expandedGroups.daily">
              <div 
                v-for="forum in dailyForums" 
                :key="forum.id"
                class="forum-item child"
                :class="{ active: selectedForum === forum.id }"
                @click="selectForum(forum.id)"
              >
                <span class="forum-name">{{ forum.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div class="post-panel">
        <div class="panel-header">
          <span class="panel-title">{{ currentForumName }}</span>
          <span class="post-count">共 {{ displayedPosts.length }} 篇</span>
        </div>

        <div class="post-list">
          <div v-for="post in displayedPosts" :key="post.id" class="post-item" @click="viewPost(post)">
            <div class="post-main">
              <div class="post-avatar">
                <el-avatar :size="44" :src="post.avatar" />
              </div>
              <div class="post-content">
                <div class="post-header">
                  <span class="post-title">{{ post.title }}</span>
                  <el-tag v-if="post.top" type="warning" size="small">置顶</el-tag>
                </div>
                <div class="post-meta">
                  <span class="post-author">{{ post.author }}</span>
                  <el-tag :type="getLevelType(post.level)" size="small" style="margin: 0 6px">{{ post.level }}</el-tag>
                  <span class="post-forum">{{ post.forumName }}</span>
                  <span class="post-time">{{ post.createTime }}</span>
                </div>
              </div>
            </div>
            <div class="post-stats">
              <span class="stat-item"><el-icon><View /></el-icon>{{ post.views }}</span>
              <span class="stat-item"><el-icon><ChatLineRound /></el-icon>{{ post.replies }}</span>
              <span class="stat-item"><el-icon><Star /></el-icon>{{ post.likes }}</span>
            </div>
          </div>
        </div>

        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="20"
            :total="displayedPosts.length"
            layout="total, prev, pager, next"
            background
          />
        </div>
      </div>

      <aside class="user-sidebar">
        <div class="user-card">
          <el-avatar :size="64" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
          <div class="user-name">王小明</div>
          <div class="user-role">语文教师</div>
          <el-tag type="danger" size="small" style="margin-top: 4px">资深教师</el-tag>
        </div>
        <div class="user-stats">
          <div class="stat-item">
            <span class="stat-value">{{ userStats.posts }}</span>
            <span class="stat-label">发帖</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ userStats.replies }}</span>
            <span class="stat-label">回复</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ userStats.likes }}</span>
            <span class="stat-label">获赞</span>
          </div>
        </div>
        <el-button class="my-posts-btn" @click="showMyPosts">我的帖子</el-button>
      </aside>
    </div>

    <el-dialog v-model="showPostDialog" title="发布帖子" width="600px" class="post-dialog">
      <div class="dialog-header">
        <el-avatar :size="48" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
        <div class="dialog-user">
          <span class="user-name">王小明</span>
          <span class="user-role">语文教师</span>
        </div>
      </div>
      
      <el-form label-position="top">
        <el-form-item label="选择板块" required>
          <el-select v-model="postForm.forumId" placeholder="请选择板块" style="width: 100%">
            <el-option v-for="f in forums" :key="f.id" :label="f.name" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="帖子标题" required>
          <el-input v-model="postForm.title" placeholder="请输入标题" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="帖子内容" required>
          <el-input v-model="postForm.content" type="textarea" :rows="6" placeholder="请输入内容..." maxlength="2000" show-word-limit />
        </el-form-item>
      </el-form>
      
      <div class="dialog-tips">
        <el-icon><InfoFilled /></el-icon>
        <span>发布后，您的帖子将在所选板块显示</span>
      </div>
      
      <template #footer>
        <el-button @click="showPostDialog = false">取消</el-button>
        <el-button type="primary" @click="publishPost" style="background: #8985cf; border-color: #8985cf">发布帖子</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="帖子详情" width="700px" class="custom-dialog">
      <div v-if="selectedPost" class="post-detail">
        <div class="detail-header">
          <div class="detail-user">
            <el-avatar :size="48" :src="selectedPost.avatar" />
            <div class="user-info">
              <div class="author-row">
                <span class="author-name">{{ selectedPost.author }}</span>
                <el-tag :type="getLevelType(selectedPost.level)" size="small">{{ selectedPost.level }}</el-tag>
              </div>
              <span class="post-time">{{ selectedPost.createTime }}</span>
            </div>
          </div>
          <el-tag type="warning">{{ selectedPost.forumName }}</el-tag>
        </div>
        <h2 class="detail-title">{{ selectedPost.title }}</h2>
        <div class="detail-content">{{ selectedPost.content }}</div>
        <div class="detail-actions">
          <span class="action-item"><el-icon><Star /></el-icon>{{ selectedPost.likes }} 赞</span>
          <span class="action-item"><el-icon><ChatLineRound /></el-icon>{{ selectedPost.replies }} 回复</span>
        </div>
        <el-divider />
        <div class="reply-section">
          <h4>全部回复 ({{ selectedPost.replies }})</h4>
          <div class="reply-list">
            <div v-for="reply in postReplies" :key="reply.id" class="reply-item">
              <el-avatar :size="36" :src="reply.avatar" />
              <div class="reply-content">
                <div class="reply-header">
                  <div class="reply-author-row">
                    <span class="reply-author">{{ reply.author }}</span>
                    <el-tag :type="getLevelType(reply.level)" size="small">{{ reply.level }}</el-tag>
                  </div>
                  <span class="reply-time">{{ reply.time }}</span>
                </div>
                <div class="reply-text">{{ reply.content }}</div>
              </div>
            </div>
          </div>
          <div class="reply-input">
            <el-input v-model="replyText" placeholder="发表回复..." />
            <el-button type="primary" @click="submitReply">发表</el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showMyPostsDialog" title="我的帖子" width="700px" class="custom-dialog">
      <div class="my-posts-list" v-if="myPosts.length > 0">
        <div v-for="post in myPosts" :key="post.id" class="my-post-item" @click="viewPost(post)">
          <div class="post-info">
            <span class="post-title">{{ post.title }}</span>
            <el-tag size="small" type="warning">{{ post.forumName }}</el-tag>
          </div>
          <div class="post-meta">
            <span><el-icon><View /></el-icon>{{ post.views }}</span>
            <span><el-icon><ChatLineRound /></el-icon>{{ post.replies }}</span>
            <span><el-icon><Star /></el-icon>{{ post.likes }}</span>
            <span class="post-time">{{ post.createTime }}</span>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无帖子" :image-size="60" />
    </el-dialog>
  </div>
</template>


<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, View, ChatLineRound, Star, InfoFilled, Reading, ChatDotSquare, CaretRight } from '@element-plus/icons-vue'
import { teacherApi } from '../../api/teacher'

interface Post {
  id: number
  title: string
  content: string
  author: string
  avatar: string
  forumId: number
  forumName: string
  createTime: string
  views: number
  replies: number
  likes: number
  top: boolean
  level: string
}

interface Forum {
  id: number
  name: string
  count: number
}

interface Reply {
  id: number
  author: string
  avatar: string
  content: string
  time: string
  level: string
}

const forums = ref<Forum[]>([])

const subjectForums = computed(() => forums.value.filter(f => f.id >= 101))
const dailyForums = computed(() => forums.value.filter(f => f.id === 3 || f.id === 4 || f.id === 5))

const expandedGroups = reactive({
  subject: true,
  daily: true
})

const toggleGroup = (group: 'subject' | 'daily') => {
  expandedGroups[group] = !expandedGroups[group]
}

const posts = ref<Post[]>([])

const myPosts = ref<Post[]>([])

const loadPosts = async () => {
  try {
    const data: any = await teacherApi.getForumPosts()
    if (Array.isArray(data)) posts.value = data
  } catch (e) {
    // 接口失败时保持页面可用，使用默认空值
  }
}

const loadBoards = async () => {
  try {
    const data: any = await teacherApi.getForumBoards()
    if (Array.isArray(data)) forums.value = data
  } catch (e) {
    // 接口失败时保持页面可用，使用默认空值
  }
}

const selectedForum = ref<number | null>(null)
const searchText = ref('')
const currentPage = ref(1)
const showPostDialog = ref(false)
const showDetailDialog = ref(false)
const showMyPostsDialog = ref(false)
const selectedPost = ref<Post | null>(null)
const replyText = ref('')

const postForm = ref({ forumId: 1, title: '', content: '' })

const userStats = ref({ posts: 12, replies: 45, likes: 128 })

const getLevelType = (level: string) => {
  const map: Record<string, string> = { '资深教师': 'danger', '任课教师': 'primary', '实习教师': 'info' }
  return map[level] || ''
}

const postReplies = ref<Reply[]>([
  { id: 1, author: '李老师', avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png', content: '写得很好，受益匪浅！', time: '2026-04-22 11:00', level: '资深教师' },
  { id: 2, author: '王老师', avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png', content: '很实用的方法，收藏了', time: '2026-04-22 14:30', level: '任课教师' }
])

const totalPosts = computed(() => posts.value.length)

const currentForumName = computed(() => {
  if (selectedForum.value === null) return '全部帖子'
  const forum = forums.value.find(f => f.id === selectedForum.value)
  return forum?.name || '全部帖子'
})

const displayedPosts = computed(() => {
  let result = selectedForum.value === null 
    ? posts.value 
    : posts.value.filter(p => p.forumId === selectedForum.value)
  
  if (searchText.value) {
    result = result.filter(p => p.title.includes(searchText.value) || p.content.includes(searchText.value))
  }
  
  return result.sort((a, b) => (b.top ? 1 : 0) - (a.top ? 1 : 0))
})

const selectForum = (id: number | null) => { selectedForum.value = id; currentPage.value = 1 }

const viewPost = (post: Post) => {
  selectedPost.value = post
  showDetailDialog.value = true
}

const publishPost = async () => {
  if (!postForm.value.forumId || !postForm.value.title) {
    ElMessage.warning('请选择板块并填写标题')
    return
  }
  const forum = forums.value.find(f => f.id === postForm.value.forumId)
  try {
    await teacherApi.createForumPost({
      forumId: postForm.value.forumId,
      title: postForm.value.title,
      content: postForm.value.content
    })
    ElMessage.success('发布成功')
    await loadPosts()
  } catch (e) {
    // 错误已由拦截器提示
  }
  showPostDialog.value = false
  postForm.value = { forumId: 1, title: '', content: '' }
}

const submitReply = () => {
  if (!replyText.value) return
  ElMessage.success('回复成功')
  replyText.value = ''
}

const showMyPosts = async () => {
  showMyPostsDialog.value = true
  try {
    const data: any = await teacherApi.getMyPosts()
    if (Array.isArray(data)) myPosts.value = data
  } catch (e) {
    // 接口失败时保持弹窗可用，列表为空
  }
}

onMounted(() => {
  loadPosts()
  loadBoards()
})
</script>

<style scoped>
.forum-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid #E8E0F0;
}

.main-content {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
}

.forum-sidebar {
  width: 180px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #E8E0F0;
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 14px 16px;
  border-bottom: 1px solid #E8E0F0;
  font-weight: 600;
  color: #333;
  font-size: 14px;
  flex-shrink: 0;
}

.forum-list {
  padding: 8px;
  overflow-y: auto;
  flex: 1;
}

.forum-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 2px;
}

.forum-item:hover { background: #F5F3FF; }
.forum-item.active { background: #F5F3FF; border-left: 3px solid #f48d45; }

.forum-item .forum-name { font-size: 13px; color: #333; }
.forum-item .forum-count { font-size: 12px; color: #999; }

.forum-group {
  margin-bottom: 4px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.2s;
}

.group-header:hover { background: #f5f5f5; }

.group-header .arrow {
  margin-left: auto;
  transition: transform 0.2s;
}

.group-header .arrow.expanded {
  transform: rotate(90deg);
}

.group-children {
  padding-left: 8px;
}

.forum-item.child {
  padding: 8px 12px;
  font-size: 13px;
}

.post-panel {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #E8E0F0;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #E8E0F0;
}

.panel-title { font-weight: 600; color: #333; font-size: 15px; }
.post-count { color: #999; font-size: 13px; }

.post-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.post-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
  background: #fafafa;
}

.post-item:hover { background: #F5F3FF; }

.post-main { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }

.post-header { display: flex; align-items: center; gap: 8px; }
.post-title { font-size: 15px; font-weight: 500; color: #333; }

.post-meta { display: flex; align-items: center; gap: 12px; margin-top: 6px; font-size: 12px; color: #999; }
.post-meta .post-author { color: #666; }

.post-stats { display: flex; gap: 16px; }
.post-stats .stat-item { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #999; }

.pagination-wrapper {
  padding: 16px;
  display: flex;
  justify-content: center;
  border-top: 1px solid #E8E0F0;
}

.user-sidebar {
  width: 200px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #E8E0F0;
  flex-shrink: 0;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.user-card { text-align: center; }
.user-name { margin-top: 12px; font-size: 16px; font-weight: 600; color: #333; }
.user-role { color: #999; font-size: 13px; margin-top: 4px; }

.user-stats {
  display: flex;
  justify-content: space-around;
  width: 100%;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #E8E0F0;
}

.user-stats .stat-item { text-align: center; }
.user-stats .stat-value { display: block; font-size: 18px; font-weight: 600; color: #f48d45; }
.user-stats .stat-label { font-size: 12px; color: #999; }

.my-posts-btn { margin-top: 20px; width: 100%; }

.post-detail .detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.post-detail .detail-user { display: flex; align-items: center; gap: 12px; }
.post-detail .user-info { display: flex; flex-direction: column; gap: 4px; }
.post-detail .author-row { display: flex; align-items: center; gap: 8px; }
.post-detail .author-name { font-weight: 500; color: #333; }
.post-detail .post-time { font-size: 12px; color: #999; }
.post-detail .detail-title { margin: 0 0 16px; font-size: 20px; color: #333; }
.post-detail .detail-content { color: #555; line-height: 1.8; padding: 16px; background: #f9f9f9; border-radius: 8px; }
.post-detail .detail-actions { display: flex; gap: 20px; margin-top: 16px; }
.post-detail .action-item { display: flex; align-items: center; gap: 4px; color: #999; }

.reply-section h4 { margin: 0 0 16px; font-size: 14px; color: #333; }
.reply-item { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
.reply-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.reply-author { font-weight: 500; color: #333; font-size: 13px; }
.reply-time { color: #999; font-size: 12px; }
.reply-text { color: #555; font-size: 14px; }
.reply-input { display: flex; gap: 12px; margin-top: 16px; }
.reply-author-row { display: flex; align-items: center; gap: 6px; }

.my-posts-list .my-post-item { padding: 14px; border-bottom: 1px solid #f0f0f0; cursor: pointer; }
.my-posts-list .my-post-item:hover { background: #F5F3FF; }
.my-posts-list .post-info { display: flex; justify-content: space-between; margin-bottom: 8px; }
.my-posts-list .post-title { font-weight: 500; color: #333; }
.my-posts-list .post-forum { font-size: 12px; color: #8985cf; }
.my-posts-list .post-meta { display: flex; gap: 16px; font-size: 12px; color: #999; }
.my-posts-list .post-time { margin-left: auto; }

.post-dialog .dialog-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.post-dialog .dialog-user { display: flex; flex-direction: column; }
.post-dialog .user-name { font-weight: 500; color: #333; font-size: 15px; }
.post-dialog .user-role { font-size: 12px; color: #8985cf; }
.post-dialog :deep(.el-form-item__label) { color: #666; font-weight: 500; }
.post-dialog .dialog-tips { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #999; background: #F5F3FF; padding: 8px 12px; border-radius: 6px; margin-top: 12px; }
.post-dialog .dialog-tips .el-icon { color: #8985cf; }
</style>
