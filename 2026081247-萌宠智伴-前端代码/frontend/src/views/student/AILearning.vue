<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useUserStore } from '../../stores/user'
import { studentApi } from '../../api/student'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()

// ===== 年级选择 =====
const grade = ref('upper_primary')
const gradeName = ref('小学高年级')
const gradeOptions = [
  { value: 'lower_primary', label: '小学低年级(1-3年级)' },
  { value: 'upper_primary', label: '小学高年级(4-6年级)' },
  { value: 'middle_school', label: '初中' },
  { value: 'high_school', label: '高中' },
]

const changeGrade = async (g: string) => {
  try {
    await studentApi.setGrade(g)
    grade.value = g
    gradeName.value = gradeOptions.find(o => o.value === g)?.label || '小学高年级'
    ElMessage.success(`已切换到${gradeName.value}`)
    loadCourses()
  } catch (e) { /* ignore */ }
}

// ===== 课程列表 =====
const courses = ref<any[]>([])
const selectedCourse = ref<any>(null)
const selectedTopic = ref('')

const courseCategories = computed(() => {
  const cats: Record<string, any[]> = {}
  courses.value.forEach(c => {
    const cat = c.category || '其他'
    if (!cats[cat]) cats[cat] = []
    cats[cat].push(c)
  })
  return cats
})

const selectCourse = (c: any) => {
  selectedCourse.value = c
  selectedTopic.value = c.title
  loadSuggestedQuestions(c.id, c.title)
  if (activeTab.value === 'materials') loadMaterials()
}

// ===== 标签页 =====
const activeTab = ref('chat')
const tabs = [
  { key: 'chat', label: 'AI对话', icon: 'AI' },
  { key: 'materials', label: '学习资料', icon: '料' },
  { key: 'quiz', label: '游戏化练习', icon: '练' },
  { key: 'animation', label: '动画讲解', icon: '动' },
  { key: 'book', label: '绘本生成', icon: '本' },
  { key: 'path', label: '学习路径', icon: '路' },
]

// ===== 对话功能 =====
interface ChatMessage {
  id: number
  type: 'user' | 'assistant'
  content: string
  time: string
}
const chatMessages = ref<ChatMessage[]>([])
const chatInput = ref('')
const chatSending = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

const nowTime = () => {
  const d = new Date()
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const scrollChat = () => {
  nextTick(() => {
    if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  })
}

const sendChat = async () => {
  if (!chatInput.value.trim() || chatSending.value) return
  const text = chatInput.value.trim()
  // 先用一个临时ID，发送成功后替换为数据库真实ID
  const tempUserId = Date.now()
  chatMessages.value.push({ id: tempUserId, type: 'user', content: text, time: nowTime() })
  chatInput.value = ''
  scrollChat()
  chatSending.value = true
  try {
    const data: any = await studentApi.sendAIChat(text)
    // 用数据库真实ID替换临时ID
    const userIdx = chatMessages.value.findIndex(m => m.id === tempUserId)
    if (userIdx >= 0 && data?.userMsgId) {
      chatMessages.value[userIdx].id = data.userMsgId
    }
    chatMessages.value.push({
      id: data?.aiMsgId || Date.now() + 1,
      type: 'assistant',
      content: data?.reply ?? '我来帮你解答~',
      time: data?.time ?? nowTime(),
    })
    scrollChat()
  } catch (e) {
    chatMessages.value.push({
      id: Date.now() + 1,
      type: 'assistant',
      content: '抱歉，我暂时无法回复，请稍后再试~',
      time: nowTime(),
    })
    scrollChat()
  } finally {
    chatSending.value = false
  }
}

const quickQuestions = ref<string[]>([
  '什么是人工智能？',
  '机器学习和人类学习有什么区别？',
  '能用简单的例子解释一下算法吗？',
  '编程入门需要学什么？',
  'AI能帮我们做什么？',
])

const loadSuggestedQuestions = async (courseId?: number, topic?: string) => {
  try {
    const data: any = await studentApi.getSuggestedQuestions(courseId, topic)
    if (data?.questions && Array.isArray(data.questions) && data.questions.length > 0) {
      quickQuestions.value = data.questions
    }
  } catch (e) { /* keep defaults */ }
}

const sendQuickQuestion = (q: string) => {
  chatInput.value = q
  sendChat()
}

// ===== 聊天记录管理 =====
const editingMsgId = ref<number>(0)
const editingText = ref('')

const startEdit = (msg: ChatMessage) => {
  editingMsgId.value = msg.id
  editingText.value = msg.content
}

const cancelEdit = () => {
  editingMsgId.value = 0
  editingText.value = ''
}

const saveEdit = async () => {
  if (!editingText.value.trim() || editingMsgId.value === 0) return
  try {
    await studentApi.editChatMessage(editingMsgId.value, editingText.value.trim())
    const msg = chatMessages.value.find(m => m.id === editingMsgId.value)
    if (msg) msg.content = editingText.value.trim()
    editingMsgId.value = 0
    editingText.value = ''
  } catch (e) { /* silently fail */ }
}

const deleteMessage = async (msg: ChatMessage) => {
  if (msg.id === 0) return // 欢迎消息不能删
  try {
    await ElMessageBox.confirm('确定删除这条消息吗？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '不确定' })
    await studentApi.deleteChatMessage(msg.id)
    chatMessages.value = chatMessages.value.filter(m => m.id !== msg.id)
  } catch (e) { /* cancelled */ }
}

const rollbackMessage = async (msg: ChatMessage) => {
  if (msg.id === 0 || msg.type !== 'user') return
  try {
    // 找到这条用户消息的位置
    const idx = chatMessages.value.findIndex(m => m.id === msg.id)
    if (idx < 0) return
    // 找到下一条AI回复
    const nextMsg = chatMessages.value[idx + 1]
    const hasAiReply = nextMsg && nextMsg.type === 'assistant' && nextMsg.id !== 0

    // 删除用户消息
    await studentApi.deleteChatMessage(msg.id)
    // 删除AI回复
    if (hasAiReply) {
      await studentApi.deleteChatMessage(nextMsg.id)
    }
    // 从前端移除
    if (hasAiReply) {
      chatMessages.value = chatMessages.value.filter(m => m.id !== msg.id && m.id !== nextMsg.id)
    } else {
      chatMessages.value = chatMessages.value.filter(m => m.id !== msg.id)
    }
  } catch (e) { /* silently fail */ }
}

const clearChat = async () => {
  try {
    await ElMessageBox.confirm('确定清空当前聊天记录吗？此操作不可恢复。', '清空聊天', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '不确定' })
    await studentApi.clearChat()
    chatMessages.value = [{
      id: 0,
      type: 'assistant',
      content: '你好呀！我是你的AI学习伙伴！\n想了解什么知识呢？可以问我任何问题哦~',
      time: nowTime(),
    }]
  } catch (e) { /* cancelled */ }
}

// ===== 游戏化练习 =====
const quizQuestions = ref<any[]>([])
const quizAnswers = ref<number[]>([])
const quizResult = ref<any>(null)
const quizLoading = ref(false)
const quizSubmitted = ref(false)

const generateQuiz = async () => {
  const topic = selectedTopic.value || '人工智能基础'
  quizLoading.value = true
  quizResult.value = null
  quizSubmitted.value = false
  try {
    const data: any = await studentApi.generateQuiz({ topic, count: 3, courseId: selectedCourse.value?.id })
    quizQuestions.value = data?.questions || []
    quizAnswers.value = new Array(quizQuestions.value.length).fill(-1)
    if (quizQuestions.value.length === 0) {
      ElMessage.warning('题目生成失败，请重试')
    }
  } catch (e) {
    ElMessage.error('生成题目失败，请稍后重试')
  } finally {
    quizLoading.value = false
  }
}

const selectAnswer = (qIdx: number, aIdx: number) => {
  if (quizSubmitted.value) return
  quizAnswers.value[qIdx] = aIdx
}

const submitQuiz = async () => {
  if (quizAnswers.value.some(a => a < 0)) {
    ElMessage.warning('请完成所有题目后再提交')
    return
  }
  quizLoading.value = true
  try {
    const result: any = await studentApi.gradeQuiz({
      questions: quizQuestions.value,
      answers: quizAnswers.value,
      topic: selectedTopic.value || '人工智能基础',
      courseId: selectedCourse.value?.id,
    })
    quizResult.value = result
    quizSubmitted.value = true
    if (result.correct > 0) {
      ElMessage.success(`答对${result.correct}题，获得${result.correct * 3}积分奖励！`)
    }
  } catch (e) {
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    quizLoading.value = false
  }
}

// ===== 动画讲解 =====
const animationData = ref<any>(null)
const animLoading = ref(false)

const generateAnimation = async () => {
  const topic = selectedTopic.value || '冒泡排序'
  animLoading.value = true
  animationData.value = null
  try {
    const data: any = await studentApi.generateAnimation({ topic, courseId: selectedCourse.value?.id })
    animationData.value = data
  } catch (e) {
    ElMessage.error('动画生成失败，请稍后重试')
  } finally {
    animLoading.value = false
  }
}

// ===== 绘本生成 =====
const bookData = ref<any>(null)
const bookList = ref<any[]>([])
const bookLoading = ref(false)
const bookPage = ref(0)

const generateBook = async () => {
  const topic = selectedTopic.value || '什么是人工智能'
  bookLoading.value = true
  bookData.value = null
  bookPage.value = 0
  try {
    const data: any = await studentApi.generateBook({ topic, courseId: selectedCourse.value?.id })
    bookData.value = data
    loadBookList()
  } catch (e) {
    ElMessage.error('绘本生成失败，请稍后重试')
  } finally {
    bookLoading.value = false
  }
}

const loadBookList = async () => {
  try {
    const data: any = await studentApi.getBooks()
    bookList.value = Array.isArray(data) ? data : []
  } catch (e) { /* ignore */ }
}

const nextBookPage = () => {
  if (bookData.value && bookPage.value < bookData.value.pages.length - 1) {
    bookPage.value++
  }
}
const prevBookPage = () => {
  if (bookPage.value > 0) bookPage.value--
}

// ===== 学习资料 =====
const materials = ref<any[]>([])
const materialsLoading = ref(false)

const materialTypeIcon: Record<string, string> = {
  video: '[视频]',
  doc: '[文档]',
  ppt: '[课件]',
  link: '[链接]',
}

const loadMaterials = async () => {
  materialsLoading.value = true
  try {
    const data: any = await studentApi.getMaterials(selectedCourse.value?.id)
    materials.value = Array.isArray(data) ? data : []
  } catch (e) {
    materials.value = []
  } finally {
    materialsLoading.value = false
  }
}

// ===== 学习路径 =====
const learningPath = ref<any>(null)
const pathLoading = ref(false)

const loadLearningPath = async () => {
  pathLoading.value = true
  try {
    const data: any = await studentApi.getLearningPath()
    learningPath.value = data
  } catch (e) {
    ElMessage.error('学习路径加载失败')
  } finally {
    pathLoading.value = false
  }
}

// ===== 切换标签时加载数据 =====
watch(activeTab, (tab) => {
  if (tab === 'path' && !learningPath.value) loadLearningPath()
  if (tab === 'book' && bookList.value.length === 0) loadBookList()
  if (tab === 'materials') loadMaterials()
})

// ===== 加载数据 =====
const loadCourses = async () => {
  try {
    const data: any = await studentApi.getAICourses(grade.value)
    courses.value = Array.isArray(data) ? data : []
  } catch (e) {
    // 如果数据库没有课程数据，使用默认课程
    courses.value = getDefaultCourses()
  }
}

const getDefaultCourses = () => {
  const defaults: Record<string, any[]> = {
    lower_primary: [
      { id: 1, title: '什么是人工智能', description: '认识AI小伙伴', category: '基础概念', difficulty: 'easy' },
      { id: 2, title: 'AI能做什么', description: '了解AI的神奇能力', category: '基础概念', difficulty: 'easy' },
      { id: 3, title: '和AI交朋友', description: '学会和AI对话', category: '互动体验', difficulty: 'easy' },
    ],
    upper_primary: [
      { id: 10, title: '人工智能简介', description: '了解AI发展历程', category: '基础概念', difficulty: 'easy' },
      { id: 11, title: '机器学习入门', description: '机器如何学习知识', category: '机器学习', difficulty: 'medium' },
      { id: 12, title: '编程基础', description: '用Python写第一个程序', category: '编程实践', difficulty: 'medium' },
      { id: 13, title: '算法思维', description: '排序算法初探', category: '算法思维', difficulty: 'medium' },
      { id: 14, title: 'AI与生活', description: 'AI在身边的应用', category: '应用探索', difficulty: 'easy' },
    ],
    middle_school: [
      { id: 20, title: '机器学习原理', description: '监督与无监督学习', category: '机器学习', difficulty: 'medium' },
      { id: 21, title: 'Python编程', description: '变量、循环、函数', category: '编程实践', difficulty: 'medium' },
      { id: 22, title: '排序算法', description: '冒泡、选择、插入排序', category: '算法思维', difficulty: 'hard' },
      { id: 23, title: '神经网络基础', description: '认识神经元和层', category: '深度学习', difficulty: 'hard' },
    ],
    high_school: [
      { id: 30, title: '深度学习', description: 'CNN与RNN原理', category: '深度学习', difficulty: 'hard' },
      { id: 31, title: '数据科学', description: '数据处理与可视化', category: '数据科学', difficulty: 'medium' },
      { id: 32, title: 'AI伦理', description: '人工智能的边界与责任', category: 'AI伦理', difficulty: 'medium' },
      { id: 33, title: '项目实战', description: '构建简单AI应用', category: '项目实践', difficulty: 'hard' },
    ],
  }
  return defaults[grade.value] || defaults.upper_primary
}

onMounted(async () => {
  // 加载年级
  try {
    const gradeData: any = await studentApi.getGrade()
    if (gradeData?.grade) {
      grade.value = gradeData.grade
      gradeName.value = gradeData.gradeName || gradeOptions.find(o => o.value === gradeData.grade)?.label || '小学高年级'
    }
  } catch (e) { /* ignore */ }

  // 加载课程
  await loadCourses()

  // 加载聊天历史
  try {
    const data: any = await studentApi.getAIChatHistory()
    if (Array.isArray(data) && data.length > 0) {
      chatMessages.value = data.map((m: any) => ({
        id: m.id,
        type: m.type === 'user' ? 'user' : 'assistant',
        content: m.content,
        time: m.time || nowTime(),
      }))
      scrollChat()
    } else {
      chatMessages.value = [{
        id: 0,
        type: 'assistant',
        content: '你好呀！我是你的AI学习伙伴！\n想了解人工智能的什么知识呢？可以问我任何问题哦~',
        time: nowTime(),
      }]
    }
  } catch (e) {
    chatMessages.value = [{
      id: 0,
      type: 'assistant',
      content: '你好呀！我是你的AI学习伙伴！\n想了解人工智能的什么知识呢？',
      time: nowTime(),
    }]
  }

  // 确保宠物信息
  if (!userStore.petInfo.name) {
    try {
      const dash: any = await studentApi.getDashboard()
      if (dash) userStore.applyDashboard(dash)
    } catch (e) { /* ignore */ }
  }
})
</script>

<template>
<div class="ai-learning-page">
  <!-- 顶部栏：年级选择 + 当前主题 -->
  <div class="top-bar">
    <div class="grade-selector">
      <span class="grade-label">当前年级：</span>
      <select v-model="grade" @change="changeGrade(grade)" class="grade-select">
        <option v-for="opt in gradeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
    </div>
    <div v-if="selectedTopic" class="current-topic">
      <span class="topic-tag">当前主题</span>
      <span class="topic-name">{{ selectedTopic }}</span>
    </div>
  </div>

  <div class="main-layout">
    <!-- 左侧：课程列表 -->
    <aside class="course-panel">
      <h3 class="panel-title">AI通识课程</h3>
      <div class="course-list">
        <div v-for="(coursesInCat, cat) in courseCategories" :key="cat" class="course-category">
          <div class="category-name">{{ cat }}</div>
          <div v-for="c in coursesInCat" :key="c.id"
               class="course-item"
               :class="{ active: selectedCourse?.id === c.id }"
               @click="selectCourse(c)">
            <div class="course-title">{{ c.title }}</div>
            <div class="course-desc">{{ c.description }}</div>
            <span class="difficulty-badge" :class="c.difficulty">
              {{ c.difficulty === 'easy' ? '入门' : c.difficulty === 'medium' ? '进阶' : '挑战' }}
            </span>
          </div>
        </div>
      </div>
    </aside>

    <!-- 右侧：功能区域 -->
    <div class="content-area">
      <!-- 标签页 -->
      <div class="tab-bar">
        <button v-for="tab in tabs" :key="tab.key"
                class="tab-btn"
                :class="{ active: activeTab === tab.key }"
                @click="activeTab = tab.key">
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <!-- 对话 -->
      <div v-if="activeTab === 'chat'" class="tab-content chat-tab">
        <!-- 聊天管理工具栏 -->
        <div class="chat-toolbar">
          <span class="chat-toolbar-info" v-if="selectedTopic">
            当前专题：{{ selectedTopic }}
          </span>
          <span class="chat-toolbar-info" v-else>
            AI学习伙伴 - 随时为你解答
          </span>
          <div class="chat-toolbar-actions">
            <button class="tool-btn clear-btn" @click="clearChat" title="清空当前聊天记录">
              清空当前聊天记录
            </button>
          </div>
        </div>
        <div class="chat-messages" ref="chatContainer">
          <div v-for="msg in chatMessages" :key="msg.id"
               class="chat-msg"
               :class="msg.type === 'user' ? 'msg-user' : 'msg-ai'">
            <img v-if="msg.type === 'assistant'" class="chat-avatar"
                 :src="userStore.petInfo.type || '/images/pets/default.jpg'"
                 @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
            <div class="chat-bubble-wrap">
              <!-- 正常显示 -->
              <div v-if="editingMsgId !== msg.id" class="chat-bubble">
                <div class="bubble-content">{{ msg.content }}</div>
                <div class="bubble-time">{{ msg.time }}</div>
              </div>
              <!-- 编辑模式 -->
              <div v-else class="chat-edit-area">
                <textarea v-model="editingText" class="edit-textarea" rows="3"
                          @keyup.ctrl.enter="saveEdit"></textarea>
                <div class="edit-actions">
                  <button class="msg-action-btn save-btn" @click="saveEdit">保存</button>
                  <button class="msg-action-btn cancel-btn" @click="cancelEdit">取消</button>
                </div>
              </div>
              <!-- 操作按钮：在气泡右下角 -->
              <div v-if="msg.id !== 0 && editingMsgId !== msg.id" class="bubble-footer">
                <button v-if="msg.type === 'user'" class="msg-action-btn" @click="startEdit(msg)" title="修改此条消息">
                  修改
                </button>
                <button v-if="msg.type === 'user'" class="msg-action-btn" @click="rollbackMessage(msg)" title="撤回此条消息及AI回复">
                  撤回
                </button>
                <button class="msg-action-btn delete-action" @click="deleteMessage(msg)" title="删除此条消息">
                  删除
                </button>
              </div>
            </div>
            <img v-if="msg.type === 'user'" class="chat-avatar"
                 :src="userStore.studentInfo.avatar || '/images/pets/default.jpg'"
                 @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
          </div>
          <div v-if="chatSending" class="chat-msg msg-ai">
            <img class="chat-avatar" :src="userStore.petInfo.type || '/images/pets/default.jpg'" />
            <div class="chat-bubble typing">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>
        <div class="quick-questions">
          <button v-for="q in quickQuestions" :key="q" class="quick-q-btn" @click="sendQuickQuestion(q)">
            {{ q }}
          </button>
        </div>
        <div class="chat-input-area">
          <input v-model="chatInput" type="text" placeholder="问我任何关于AI的问题..."
                 @keyup.enter="sendChat" :disabled="chatSending" />
          <button @click="sendChat" :disabled="chatSending || !chatInput.trim()" class="send-btn">
            {{ chatSending ? '思考中...' : '发送' }}
          </button>
        </div>
      </div>

      <!-- 学习资料 -->
      <div v-if="activeTab === 'materials'" class="tab-content materials-tab">
        <div class="materials-header">
          <h3>学习资料</h3>
          <p class="materials-hint" v-if="selectedTopic">
            当前专题：{{ selectedTopic }} - 点击下方资料链接进行学习
          </p>
          <p class="materials-hint" v-else>
            请先在左侧选择一个课程专题，查看对应的学习资料
          </p>
          <button @click="loadMaterials" :disabled="materialsLoading" class="action-btn" v-if="selectedCourse">
            {{ materialsLoading ? '加载中...' : '刷新资料' }}
          </button>
        </div>

        <div v-if="materialsLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>正在加载学习资料...</p>
        </div>

        <div v-else-if="materials.length > 0" class="materials-list">
          <a v-for="m in materials" :key="m.id"
             :href="m.url" target="_blank" rel="noopener"
             class="material-card">
            <div class="material-icon">{{ materialTypeIcon[m.type] || '[资料]' }}</div>
            <div class="material-info">
              <div class="material-title">{{ m.title }}</div>
              <div class="material-desc" v-if="m.description">{{ m.description }}</div>
            </div>
            <span class="material-go">查看 &gt;</span>
          </a>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">[资料]</div>
          <p v-if="selectedCourse">暂无学习资料，请稍后再试</p>
          <p v-else>请先在左侧选择一个课程专题</p>
        </div>
      </div>

      <!-- 游戏化练习 -->
      <div v-if="activeTab === 'quiz'" class="tab-content quiz-tab">
        <div class="quiz-header">
          <h3>游戏化练习</h3>
          <p class="quiz-hint">选择左侧课程或直接生成练习题，答对每题奖励3积分！</p>
          <button @click="generateQuiz" :disabled="quizLoading" class="action-btn">
            {{ quizLoading ? '生成中...' : (quizSubmitted ? '再来一组' : '生成练习题') }}
          </button>
        </div>

        <div v-if="quizLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>AI正在为你出题...</p>
        </div>

        <div v-else-if="quizQuestions.length > 0" class="quiz-list">
          <div v-for="(q, qi) in quizQuestions" :key="qi" class="quiz-item">
            <div class="quiz-question">
              <span class="q-num">第{{ qi + 1 }}题</span>
              <span class="q-text">{{ q.question }}</span>
            </div>
            <div class="quiz-options">
              <label v-for="(opt, oi) in q.options" :key="oi"
                     class="quiz-option"
                     :class="{
                       selected: quizAnswers[qi] === oi,
                       correct: quizSubmitted && oi === q.answer,
                       wrong: quizSubmitted && quizAnswers[qi] === oi && oi !== q.answer,
                     }">
                <input type="radio" :name="`q${qi}`" :checked="quizAnswers[qi] === oi"
                       @change="selectAnswer(qi, oi)" :disabled="quizSubmitted" />
                <span class="opt-letter">{{ String.fromCharCode(65 + oi) }}</span>
                <span class="opt-text">{{ opt }}</span>
              </label>
            </div>
            <div v-if="quizSubmitted" class="quiz-explanation">
              <span class="expl-label">解析：</span>{{ q.explanation }}
            </div>
          </div>

          <div v-if="!quizSubmitted" class="quiz-submit-area">
            <button @click="submitQuiz" :disabled="quizLoading" class="action-btn primary">
              提交答案
            </button>
          </div>

          <div v-if="quizResult" class="quiz-result">
            <div class="result-score">
              <span class="score-num">{{ quizResult.score }}</span>
              <span class="score-unit">分</span>
            </div>
            <div class="result-detail">
              答对 {{ quizResult.correct }} / {{ quizResult.total }} 题
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">[练习]</div>
          <p>点击上方按钮开始练习！</p>
        </div>
      </div>

      <!-- 动画讲解 -->
      <div v-if="activeTab === 'animation'" class="tab-content animation-tab">
        <div class="anim-header">
          <h3>动画讲解</h3>
          <p class="anim-hint">AI会生成动画来直观讲解抽象概念</p>
          <button @click="generateAnimation" :disabled="animLoading" class="action-btn">
            {{ animLoading ? '生成中...' : (animationData ? '重新生成' : '生成动画') }}
          </button>
        </div>

        <div v-if="animLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>AI正在创作动画...</p>
        </div>

        <div v-else-if="animationData" class="anim-result">
          <h4 class="anim-title">{{ animationData.title }}</h4>
          <p class="anim-desc">{{ animationData.description }}</p>
          <div class="anim-svg-container" v-html="animationData.svg"></div>
          <div class="anim-explanation">
            <span class="expl-label">详细解释：</span>
            <p>{{ animationData.explanation }}</p>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">[动画]</div>
          <p>选择一个课程主题，点击按钮生成动画讲解！</p>
        </div>
      </div>

      <!-- 绘本生成 -->
      <div v-if="activeTab === 'book'" class="tab-content book-tab">
        <div class="book-header">
          <h3>绘本生成</h3>
          <p class="book-hint">AI会创作互动绘本，用故事和图画讲解知识</p>
          <button @click="generateBook" :disabled="bookLoading" class="action-btn">
            {{ bookLoading ? '生成中...' : (bookData ? '重新生成' : '生成绘本') }}
          </button>
        </div>

        <div v-if="bookLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>AI正在创作绘本...</p>
        </div>

        <div v-else-if="bookData" class="book-result">
          <h4 class="book-title">{{ bookData.title }}</h4>
          <div class="book-page-display">
            <div class="book-page" v-if="bookData.pages[bookPage]">
              <div class="book-svg" v-html="bookData.pages[bookPage].svg"></div>
              <p class="book-text">{{ bookData.pages[bookPage].text }}</p>
            </div>
            <div class="book-nav">
              <button @click="prevBookPage" :disabled="bookPage === 0" class="nav-btn">上一页</button>
              <span class="page-info">{{ bookPage + 1 }} / {{ bookData.pages.length }}</span>
              <button @click="nextBookPage" :disabled="bookPage >= bookData.pages.length - 1" class="nav-btn">下一页</button>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">[绘本]</div>
          <p>选择一个课程主题，点击按钮生成绘本！</p>
        </div>

        <!-- 历史绘本 -->
        <div v-if="bookList.length > 0" class="book-history">
          <h4 class="history-title">我的绘本收藏</h4>
          <div class="book-list">
            <div v-for="b in bookList" :key="b.id" class="book-card">
              <span class="book-card-title">{{ b.title }}</span>
              <span class="book-card-topic">{{ b.topic }}</span>
              <span class="book-card-date">{{ b.createdAt }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 学习路径 -->
      <div v-if="activeTab === 'path'" class="tab-content path-tab">
        <div class="path-header">
          <h3>个性化学习路径</h3>
          <button @click="loadLearningPath" :disabled="pathLoading" class="action-btn">
            {{ pathLoading ? '加载中...' : '刷新建议' }}
          </button>
        </div>

        <div v-if="pathLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>AI正在分析你的学习情况...</p>
        </div>

        <div v-else-if="learningPath" class="path-content">
          <div class="path-info">
            <div class="info-card">
              <span class="info-label">当前年级</span>
              <span class="info-value">{{ learningPath.gradeName }}</span>
            </div>
            <div class="info-card">
              <span class="info-label">已学知识点</span>
              <span class="info-value">{{ learningPath.learnedTopics?.length || 0 }} 个</span>
            </div>
            <div class="info-card">
              <span class="info-label">最近成绩</span>
              <span class="info-value">
                {{ learningPath.recentScores?.length > 0
                    ? learningPath.recentScores.map((s: number) => s + '分').join('、')
                    : '暂无' }}
              </span>
            </div>
          </div>

          <div v-if="learningPath.learnedTopics?.length > 0" class="learned-topics">
            <h4>已学知识点</h4>
            <div class="topic-tags">
              <span v-for="t in learningPath.learnedTopics" :key="t" class="learned-tag">{{ t }}</span>
            </div>
          </div>

          <div v-if="learningPath.suggestions?.length > 0" class="suggestions">
            <h4>AI推荐下一步学习</h4>
            <div v-for="(s, i) in learningPath.suggestions" :key="i" class="suggestion-card"
                 @click="selectedTopic = s.topic; activeTab = 'chat'">
              <div class="sug-header">
                <span class="sug-num">{{ i + 1 }}</span>
                <span class="sug-topic">{{ s.topic }}</span>
                <span class="sug-difficulty" :class="s.difficulty">
                  {{ s.difficulty === 'easy' ? '入门' : s.difficulty === 'medium' ? '进阶' : '挑战' }}
                </span>
              </div>
              <p class="sug-reason">{{ s.reason }}</p>
              <span class="sug-hint">点击开始学习 &gt;&gt;</span>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">[路径]</div>
          <p>点击刷新按钮获取个性化学习建议！</p>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.ai-learning-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 顶部栏 */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.grade-selector { display: flex; align-items: center; gap: 8px; }
.grade-label { font-size: 14px; color: #666; font-weight: 500; }
.grade-select {
  padding: 6px 16px; border: 2px solid #ffb74d; border-radius: 20px;
  font-size: 14px; color: #333; outline: none; cursor: pointer; background: white;
}
.current-topic { display: flex; align-items: center; gap: 8px; }
.topic-tag {
  font-size: 12px; color: #fff; background: #ffb74d; padding: 4px 10px;
  border-radius: 12px;
}
.topic-name { font-size: 15px; font-weight: 600; color: #f48d45; }

/* 主布局 */
.main-layout {
  flex: 1;
  display: flex;
  gap: 12px;
  min-height: 0;
}

/* 课程面板 */
.course-panel {
  width: 260px;
  background: white;
  border-radius: 12px;
  padding: 16px;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
}
.panel-title {
  font-size: 16px; color: #333; margin-bottom: 12px; font-weight: 600;
}
.course-list { display: flex; flex-direction: column; gap: 12px; }
.category-name {
  font-size: 12px; color: #999; font-weight: 600;
  padding: 4px 0; border-bottom: 1px solid #f0f0f0;
}
.course-item {
  padding: 10px 12px; border-radius: 8px; cursor: pointer;
  transition: all 0.2s; border: 2px solid transparent; position: relative;
}
.course-item:hover { background: #fff8e1; }
.course-item.active { background: #fff3e0; border-color: #ffb74d; }
.course-title { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 4px; }
.course-desc { font-size: 12px; color: #888; }
.difficulty-badge {
  position: absolute; top: 8px; right: 8px;
  font-size: 10px; padding: 2px 6px; border-radius: 8px; font-weight: 500;
}
.difficulty-badge.easy { background: #e8f5e9; color: #4caf50; }
.difficulty-badge.medium { background: #fff3e0; color: #ff9800; }
.difficulty-badge.hard { background: #ffebee; color: #f44336; }

/* 内容区域 */
.content-area {
  flex: 1; display: flex; flex-direction: column;
  background: white; border-radius: 12px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); min-width: 0;
}

/* 标签栏 */
.tab-bar {
  display: flex; gap: 4px; padding: 8px 12px;
  background: #fafafa; border-bottom: 1px solid #eee;
}
.tab-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px; border: none; background: transparent;
  border-radius: 8px; cursor: pointer; font-size: 14px; color: #666;
  transition: all 0.2s;
}
.tab-btn:hover { background: #fff3e0; }
.tab-btn.active { background: #ffb74d; color: white; }
.tab-icon {
  font-size: 14px; font-weight: 600; min-width: 20px; text-align: center;
  background: rgba(255,183,77,0.15); border-radius: 4px; padding: 2px 6px;
}
.tab-btn.active .tab-icon { background: rgba(255,255,255,0.25); }

/* 通用样式 */
.action-btn {
  padding: 10px 24px; background: #ffb74d; color: white; border: none;
  border-radius: 20px; font-size: 14px; cursor: pointer; transition: all 0.3s;
}
.action-btn:hover { background: #ff9800; transform: scale(1.03); }
.action-btn:disabled { background: #ccc; cursor: not-allowed; transform: none; }
.action-btn.primary { background: #4caf50; }
.action-btn.primary:hover { background: #43a047; }

.loading-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 60px; gap: 12px; color: #999;
}
.loading-spinner {
  width: 40px; height: 40px; border: 4px solid #fff3e0;
  border-top-color: #ffb74d; border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 60px; gap: 8px; color: #bbb;
}
.empty-icon { font-size: 32px; color: #ffb74d; font-weight: 600; }

/* 对话 */
.chat-tab { display: flex; flex-direction: column; height: 100%; }

/* 聊天管理工具栏 */
.chat-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 16px; background: #fff8e1; border-bottom: 1px solid #ffe0b2;
}
.chat-toolbar-info { font-size: 13px; color: #e65100; font-weight: 500; }
.chat-toolbar-actions { display: flex; gap: 8px; }
.tool-btn {
  padding: 4px 14px; border: 1px solid #ffb74d; background: white;
  color: #ff9800; border-radius: 14px; font-size: 12px; cursor: pointer;
  transition: all 0.2s;
}
.tool-btn:hover { background: #ffb74d; color: white; }
.clear-btn { border-color: #ef5350; color: #ef5350; }
.clear-btn:hover { background: #ef5350; color: white; }

.chat-messages {
  flex: 1; overflow-y: auto; padding: 16px; display: flex;
  flex-direction: column; gap: 12px; background: #f5f7fa;
}
.chat-msg { display: flex; gap: 8px; align-items: flex-start; }
.chat-msg.msg-user { flex-direction: row-reverse; }
.chat-avatar {
  width: 40px; height: 40px; border-radius: 50%; object-fit: cover;
  flex-shrink: 0; border: 2px solid #ffb74d;
}
.chat-bubble-wrap { position: relative; max-width: 70%; }
.bubble-footer { display: flex; gap: 6px; justify-content: flex-end; margin-top: 4px; }
.msg-action-btn {
  padding: 2px 10px; border: 1px solid #ddd; background: white;
  color: #999; border-radius: 10px; font-size: 11px; cursor: pointer;
  transition: all 0.2s;
}
.msg-action-btn:hover { border-color: #ffb74d; color: #ff9800; background: #fff8e1; }
.msg-action-btn.delete-action { border-color: #ffcdd2; color: #ef5350; }
.msg-action-btn.delete-action:hover { border-color: #ef5350; color: white; background: #ef5350; }
.msg-action-btn.save-btn { border-color: #c8e6c9; color: #4caf50; }
.msg-action-btn.save-btn:hover { border-color: #4caf50; color: white; background: #4caf50; }
.msg-action-btn.cancel-btn { border-color: #ddd; color: #999; }
.msg-action-btn.cancel-btn:hover { border-color: #999; color: white; background: #999; }

/* 编辑区域 */
.chat-edit-area { padding: 8px; background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.edit-textarea {
  width: 100%; min-height: 60px; padding: 8px 10px; border: 2px solid #ffb74d;
  border-radius: 10px; font-size: 14px; line-height: 1.5; resize: vertical;
  outline: none; font-family: inherit; box-sizing: border-box;
}
.edit-actions { display: flex; gap: 6px; justify-content: flex-end; margin-top: 6px; }
.chat-bubble {
  padding: 10px 16px; border-radius: 16px;
  font-size: 14px; line-height: 1.6; word-break: break-word;
}
.msg-ai .chat-bubble { background: white; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.msg-user .chat-bubble { background: #ffb74d; color: white; border-bottom-right-radius: 4px; }
.bubble-content { white-space: pre-wrap; }
.bubble-time { font-size: 10px; opacity: 0.6; margin-top: 4px; }
.typing { display: flex; gap: 4px; align-items: center; padding: 14px 20px; }
.typing .dot {
  width: 8px; height: 8px; background: #ffb74d; border-radius: 50%;
  animation: bounce 1.4s infinite;
}
.typing .dot:nth-child(2) { animation-delay: 0.2s; }
.typing .dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}
.quick-questions { display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 16px; border-top: 1px solid #eee; }
.quick-q-btn {
  padding: 6px 14px; background: #f5f5f5; border: none; border-radius: 16px;
  font-size: 12px; color: #666; cursor: pointer; transition: all 0.2s;
}
.quick-q-btn:hover { background: #ffb74d; color: white; }
.chat-input-area { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid #eee; background: white; }
.chat-input-area input {
  flex: 1; padding: 10px 16px; border: 2px solid #e0e0e0;
  border-radius: 20px; font-size: 14px; outline: none; transition: border-color 0.2s;
}
.chat-input-area input:focus { border-color: #ffb74d; }
.send-btn {
  padding: 10px 24px; background: #ffb74d; color: white; border: none;
  border-radius: 20px; font-size: 14px; cursor: pointer; transition: all 0.2s;
}
.send-btn:hover { background: #ff9800; }
.send-btn:disabled { background: #ccc; cursor: not-allowed; }

/* 学习资料 */
.materials-tab { padding: 20px; overflow-y: auto; }
.materials-header { text-align: center; margin-bottom: 20px; }
.materials-header h3 { font-size: 20px; color: #333; margin-bottom: 8px; }
.materials-hint { font-size: 13px; color: #888; margin-bottom: 12px; }
.materials-list { display: flex; flex-direction: column; gap: 12px; max-width: 700px; margin: 0 auto; }
.material-card {
  display: flex; align-items: center; gap: 14px; padding: 14px 18px;
  background: #f9f9f9; border-radius: 12px; border: 2px solid #eee;
  text-decoration: none; transition: all 0.2s; cursor: pointer;
}
.material-card:hover { border-color: #ffb74d; background: #fff8e1; transform: translateX(4px); }
.material-icon {
  font-size: 14px; font-weight: 600; color: #ff9800;
  background: #fff3e0; padding: 8px 10px; border-radius: 8px;
  flex-shrink: 0; min-width: 60px; text-align: center;
}
.material-info { flex: 1; min-width: 0; }
.material-title { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 4px; }
.material-desc { font-size: 13px; color: #888; line-height: 1.4; }
.material-go { font-size: 13px; color: #ffb74d; font-weight: 500; flex-shrink: 0; }

/* 练习 */
.quiz-tab { padding: 20px; overflow-y: auto; }
.quiz-header { text-align: center; margin-bottom: 20px; }
.quiz-header h3 { font-size: 20px; color: #333; margin-bottom: 8px; }
.quiz-hint { font-size: 13px; color: #888; margin-bottom: 12px; }
.quiz-list { display: flex; flex-direction: column; gap: 16px; max-width: 700px; margin: 0 auto; }
.quiz-item {
  background: #fafafa; border-radius: 12px; padding: 16px;
  border: 2px solid #eee;
}
.quiz-question { display: flex; gap: 8px; margin-bottom: 12px; }
.q-num {
  background: #ffb74d; color: white; padding: 2px 10px;
  border-radius: 10px; font-size: 12px; font-weight: 600; flex-shrink: 0;
}
.q-text { font-size: 15px; color: #333; line-height: 1.5; }
.quiz-options { display: flex; flex-direction: column; gap: 8px; }
.quiz-option {
  display: flex; align-items: center; gap: 10px; padding: 10px 14px;
  border: 2px solid #eee; border-radius: 10px; cursor: pointer; transition: all 0.2s;
}
.quiz-option:hover { border-color: #ffb74d; background: #fff8e1; }
.quiz-option.selected { border-color: #ffb74d; background: #fff3e0; }
.quiz-option.correct { border-color: #4caf50; background: #e8f5e9; }
.quiz-option.wrong { border-color: #f44336; background: #ffebee; }
.quiz-option input { display: none; }
.opt-letter {
  width: 24px; height: 24px; border-radius: 50%; background: #e0e0e0;
  color: #666; display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600; flex-shrink: 0;
}
.quiz-option.selected .opt-letter { background: #ffb74d; color: white; }
.quiz-option.correct .opt-letter { background: #4caf50; color: white; }
.quiz-option.wrong .opt-letter { background: #f44336; color: white; }
.opt-text { font-size: 14px; color: #333; }
.quiz-explanation {
  margin-top: 10px; padding: 10px 14px; background: #e3f2fd;
  border-radius: 8px; font-size: 13px; color: #1565c0; line-height: 1.5;
}
.expl-label { font-weight: 600; }
.quiz-submit-area { text-align: center; padding: 12px; }
.quiz-result {
  text-align: center; padding: 20px; background: #fff3e0;
  border-radius: 12px; border: 2px solid #ffb74d;
}
.result-score { display: flex; align-items: baseline; justify-content: center; gap: 4px; }
.score-num { font-size: 36px; font-weight: bold; color: #ff9800; }
.score-unit { font-size: 16px; color: #ff9800; }
.result-detail { font-size: 14px; color: #666; margin-top: 4px; }

/* 动画 */
.animation-tab { padding: 20px; overflow-y: auto; }
.anim-header { text-align: center; margin-bottom: 20px; }
.anim-header h3 { font-size: 20px; color: #333; margin-bottom: 8px; }
.anim-hint { font-size: 13px; color: #888; margin-bottom: 12px; }
.anim-result { max-width: 800px; margin: 0 auto; }
.anim-title { font-size: 18px; color: #333; text-align: center; margin-bottom: 8px; }
.anim-desc { font-size: 14px; color: #888; text-align: center; margin-bottom: 16px; }
.anim-svg-container {
  background: white; border: 2px solid #eee; border-radius: 12px;
  padding: 16px; text-align: center; overflow-x: auto;
}
.anim-svg-container :deep(svg) { max-width: 100%; height: auto; }
.anim-explanation {
  margin-top: 16px; padding: 14px; background: #f5f5f5;
  border-radius: 10px; font-size: 14px; color: #333; line-height: 1.6;
}

/* 绘本 */
.book-tab { padding: 20px; overflow-y: auto; }
.book-header { text-align: center; margin-bottom: 20px; }
.book-header h3 { font-size: 20px; color: #333; margin-bottom: 8px; }
.book-hint { font-size: 13px; color: #888; margin-bottom: 12px; }
.book-result { max-width: 600px; margin: 0 auto; }
.book-title { font-size: 18px; color: #333; text-align: center; margin-bottom: 16px; }
.book-page-display {
  background: #fffde7; border-radius: 16px; padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.book-page { text-align: center; }
.book-svg {
  display: flex; justify-content: center; margin-bottom: 16px;
}
.book-svg :deep(svg) { max-width: 200px; height: auto; }
.book-text {
  font-size: 16px; color: #333; line-height: 1.8;
  padding: 0 20px;
}
.book-nav {
  display: flex; align-items: center; justify-content: center;
  gap: 16px; margin-top: 20px;
}
.nav-btn {
  padding: 8px 20px; background: #ffb74d; color: white; border: none;
  border-radius: 16px; cursor: pointer; font-size: 14px; transition: all 0.2s;
}
.nav-btn:hover { background: #ff9800; }
.nav-btn:disabled { background: #ddd; cursor: not-allowed; }
.page-info { font-size: 14px; color: #666; font-weight: 500; }
.book-history { margin-top: 24px; }
.history-title { font-size: 16px; color: #333; margin-bottom: 12px; }
.book-list { display: flex; flex-wrap: wrap; gap: 10px; }
.book-card {
  display: flex; flex-direction: column; gap: 4px;
  padding: 10px 14px; background: #f5f5f5; border-radius: 10px;
  min-width: 150px;
}
.book-card-title { font-size: 14px; font-weight: 600; color: #333; }
.book-card-topic { font-size: 12px; color: #888; }
.book-card-date { font-size: 11px; color: #bbb; }

/* 学习路径 */
.path-tab { padding: 20px; overflow-y: auto; }
.path-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.path-header h3 { font-size: 20px; color: #333; }
.path-content { max-width: 700px; margin: 0 auto; }
.path-info {
  display: flex; gap: 12px; margin-bottom: 20px;
}
.info-card {
  flex: 1; display: flex; flex-direction: column; gap: 4px;
  padding: 14px; background: #f5f5f5; border-radius: 10px; text-align: center;
}
.info-label { font-size: 12px; color: #888; }
.info-value { font-size: 16px; font-weight: 600; color: #333; }
.learned-topics { margin-bottom: 20px; }
.learned-topics h4 { font-size: 16px; color: #333; margin-bottom: 10px; }
.topic-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.learned-tag {
  padding: 6px 14px; background: #e8f5e9; color: #4caf50;
  border-radius: 16px; font-size: 13px; font-weight: 500;
}
.suggestions h4 { font-size: 16px; color: #333; margin-bottom: 12px; }
.suggestion-card {
  padding: 16px; background: #f5f5f5; border-radius: 12px;
  margin-bottom: 12px; cursor: pointer; transition: all 0.2s;
  border: 2px solid transparent;
}
.suggestion-card:hover { border-color: #ffb74d; background: #fff8e1; }
.sug-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.sug-num {
  width: 24px; height: 24px; border-radius: 50%; background: #ffb74d;
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600;
}
.sug-topic { font-size: 15px; font-weight: 600; color: #333; flex: 1; }
.sug-difficulty {
  font-size: 11px; padding: 2px 8px; border-radius: 8px; font-weight: 500;
}
.sug-difficulty.easy { background: #e8f5e9; color: #4caf50; }
.sug-difficulty.medium { background: #fff3e0; color: #ff9800; }
.sug-difficulty.hard { background: #ffebee; color: #f44336; }
.sug-reason { font-size: 13px; color: #666; line-height: 1.5; }
.sug-hint { font-size: 12px; color: #ffb74d; font-weight: 500; }

/* 滚动条 */
.course-list::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar,
.quiz-tab::-webkit-scrollbar,
.animation-tab::-webkit-scrollbar,
.book-tab::-webkit-scrollbar,
.materials-tab::-webkit-scrollbar,
.path-tab::-webkit-scrollbar { width: 6px; }
.course-list::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb,
.quiz-tab::-webkit-scrollbar-thumb,
.animation-tab::-webkit-scrollbar-thumb,
.book-tab::-webkit-scrollbar-thumb,
.materials-tab::-webkit-scrollbar-thumb,
.path-tab::-webkit-scrollbar-thumb { background: #ddd; border-radius: 3px; }
</style>
