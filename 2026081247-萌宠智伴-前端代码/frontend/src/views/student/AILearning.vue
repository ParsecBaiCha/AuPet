<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useUserStore } from '../../stores/user'
import { studentApi } from '../../api/student'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DEFAULT_STUDENT_AVATAR, setImageFallback } from '../../utils/images'
import DeepLearningLesson from './DeepLearningLesson.vue'
import OnlineProgrammingLesson from './OnlineProgrammingLesson.vue'
import xiaozhiAvatar from '../../../../../2026081247-萌宠智伴-前端素材/头像素材/xiaozhi.png'
import zhixingAvatar from '../../../../../2026081247-萌宠智伴-前端素材/头像素材/zhixing.png'

const userStore = useUserStore()
const coursePanelCollapsed = ref(false)

// ===== 年级选择 =====
const grade = ref('upper_primary')
const gradeName = ref('小学高年级')
const isSeniorTeacher = computed(() => ['middle_school', 'high_school'].includes(grade.value))
const teacherName = computed(() => isSeniorTeacher.value ? '知行老师' : '小知老师')
const teacherAvatar = computed(() => isSeniorTeacher.value ? zhixingAvatar : xiaozhiAvatar)
const teacherWelcome = computed(() => isSeniorTeacher.value
  ? '你好，我是知行老师。我们从一个问题开始，一起理解它，再动手验证。'
  : '你好呀，我是小知老师！今天我们一起发现 AI 的小秘密。')
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
    // 课程表随学段变化，旧路径作废，强制按新学段重新生成（丢弃仍在路上的旧请求）
    learningPath.value = null
    pathFetchedAt = 0
    fetchLearningPath(true)
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
  const changed = selectedCourse.value?.id !== c.id
  selectedCourse.value = c
  selectedTopic.value = c.title
  loadSuggestedQuestions(c.id, c.title)
  if (activeTab.value === 'materials') loadMaterials()
  if (activeTab.value === 'quiz') {
    quizStage.value = 'idle'
    quizGroup.value = 0
    generateQuiz()
  }
  if (activeTab.value === 'book' && grade.value !== 'high_school') {
    bookData.value = null
    generateBook()
  }
  // 切换到不同课程时，AI主动围绕该课程给出学习引导
  if (changed) loadCourseGuide(c)
}

// 切换课程时，AI主动给出该课程的学习引导语
const guideLoading = ref(false)
let guideRequest = 0
const loadCourseGuide = async (c: any) => {
  if (!c?.id) return
  const requestId = ++guideRequest
  guideLoading.value = true
  try {
    const data: any = await studentApi.getCourseGuide(c.id, c.title)
    if (requestId !== guideRequest || selectedCourse.value?.id !== c.id) return
    if (data?.reply) {
      chatMessages.value.push({
        id: Date.now() + 1,
        type: 'assistant',
        content: data.reply,
        time: data?.time ?? nowTime(),
      })
      scrollChat()
    }
  } catch (e) { /* 引导生成失败不影响使用 */ } finally {
    if (requestId === guideRequest) guideLoading.value = false
  }
}

// 进入测验/绘本/动画前确保已选课程，未选则自动选择第一门课并提示
const ensureCourseSelected = (): boolean => {
  if (selectedCourse.value) return true
  if (courses.value.length > 0) {
    selectCourse(courses.value[0])
    ElMessage.info(`已为您自动选择课程：${courses.value[0].title}`)
    return true
  }
  ElMessage.warning('请先在左侧选择一个课程')
  return false
}

// ===== 标签页 =====
const activeTab = ref('chat')
const tabs = [
  { key: 'chat', label: 'AI对话', icon: 'AI' },
  { key: 'materials', label: '学习资料', icon: '料' },
  { key: 'quiz', label: '云笺小试', icon: '试' },
  { key: 'animation', label: '动画讲解', icon: '动' },
  { key: 'book', label: '故事绘本', icon: '本' },
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
    const data: any = await studentApi.sendAIChat(text, selectedCourse.value?.id, selectedTopic.value || undefined)
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
const editingMsgId = ref<number>(-1)
const editingText = ref('')

const startEdit = (msg: ChatMessage) => {
  editingMsgId.value = msg.id
  editingText.value = msg.content
}

const cancelEdit = () => {
  editingMsgId.value = -1
  editingText.value = ''
}

const saveEdit = async () => {
  if (!editingText.value.trim() || editingMsgId.value === -1) return
  try {
    await studentApi.editChatMessage(editingMsgId.value, editingText.value.trim())
    const msg = chatMessages.value.find(m => m.id === editingMsgId.value)
    if (msg) msg.content = editingText.value.trim()
    editingMsgId.value = -1
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
    editingMsgId.value = -1
    editingText.value = ''
    chatMessages.value = [{
            id: 0,
            type: 'assistant',
            content: teacherWelcome.value,
            time: nowTime(),
          }]
  } catch (e) { /* cancelled */ }
}

// ===== 游戏化练习 (闯关模式) =====
const quizQuestions = ref<any[]>([])
const supportMessage = ref('')
const helpSending = ref(false)

// 「卡住了」：带着当前专题跳到小知老师 / 知行老师对话（按学段自动切换）
const askTeacherForStuck = async () => {
  if (helpSending.value || chatSending.value) return
  helpSending.value = true
  try {
    // 同步一条学习支持提醒给真人老师，方便课后跟进
    await studentApi.requestLearningHelp('study')
  } catch (e) { /* 提醒老师失败不影响去找 AI 老师 */ }
  // 记下正在做的这道题：学生答完后请他评一下难度
  const cur = quizQuestions.value[quizCurrentIdx.value]
  stuckQuestion.value = (quizStage.value === 'playing' && cur)
    ? { idx: quizCurrentIdx.value, topic: selectedTopic.value || '', question: cur.question || '' }
    : null
  activeTab.value = 'chat'
  await nextTick()
  chatInput.value = selectedTopic.value
    ? `老师，我在「${selectedTopic.value}」这里卡住了，能给我一点提示吗？`
    : '老师，我在这里卡住了，能给我一点提示吗？'
  helpSending.value = false
  await sendChat()
}

// ===== 「休息一下」：先问要不要暂存进度，再安心休息 =====
const savedQuizProgress = ref<any>(null)
// 按登录学生区分暂存内容，避免多人共用设备时互相串进度
const quizProgressKey = () => {
  let who = ''
  try {
    const raw = localStorage.getItem('pet-education-storage')
    const u = raw ? JSON.parse(raw)?.user : null
    who = String(u?.id ?? u?.username ?? '')
  } catch (e) { /* ignore */ }
  return `ai-quiz-progress:${who || userStore.studentInfo.name || 'me'}`
}
const quizProgressing = computed(() =>
  quizStage.value === 'playing' && quizQuestions.value.length > 0 && quizAnsweredFlags.value.some(Boolean))
const savedProgressLabel = computed(() => {
  const s = savedQuizProgress.value
  if (!s || !Array.isArray(s.questions) || !s.questions.length) return ''
  const cur = Math.min(Number(s.currentIdx || 0) + 1, s.questions.length)
  return `第 ${cur} / ${s.questions.length} 关`
})

// 本地缓存只作离线兜底，真正的进度以后端为准
const readLocalProgress = () => {
  try {
    const raw = localStorage.getItem(quizProgressKey())
    return raw ? JSON.parse(raw) : null
  } catch (e) { return null }
}
const writeLocalProgress = (snapshot: any) => {
  try {
    if (snapshot) localStorage.setItem(quizProgressKey(), JSON.stringify(snapshot))
    else localStorage.removeItem(quizProgressKey())
  } catch (e) { /* ignore */ }
}
const isUsableProgress = (s: any) =>
  !!s && Array.isArray(s.questions) && s.questions.length > 0

// 读取暂存进度：后端优先，这样换设备/换浏览器也能接着做；请求失败才退回本地缓存
const loadSavedQuizProgress = async () => {
  try {
    const res: any = await studentApi.getQuizProgress()
    const remote = res?.progress
    if (isUsableProgress(remote)) {
      savedQuizProgress.value = remote
      writeLocalProgress(remote)
      return
    }
    // 后端没有有效进度：同步清掉本地残留，避免显示一条"已经不存在"的旧进度
    savedQuizProgress.value = null
    writeLocalProgress(null)
  } catch (e) {
    savedQuizProgress.value = readLocalProgress()
  }
}

const clearSavedQuizProgress = async () => {
  savedQuizProgress.value = null
  writeLocalProgress(null)
  try { await studentApi.clearQuizProgress() } catch (e) { /* 清不掉不影响继续答题 */ }
}

const stashQuizProgress = async () => {
  const snapshot = {
    courseId: selectedCourse.value?.id || null,
    topic: selectedTopic.value || selectedCourse.value?.title || '',
    questions: quizQuestions.value,
    answers: quizAnswers.value,
    answeredFlags: quizAnsweredFlags.value,
    currentIdx: quizCurrentIdx.value,
    correctCount: quizCorrectCount.value,
    savedAt: new Date().toLocaleString('zh-CN', { hour12: false }),
  }
  savedQuizProgress.value = snapshot
  writeLocalProgress(snapshot)
  try {
    await studentApi.saveQuizProgress(snapshot)
    return true
  } catch (e) {
    return false
  }
}

const takeRest = async () => {
  const total = quizQuestions.value.length
  const answered = quizAnsweredFlags.value.filter(Boolean).length
  const keep = quizProgressing.value
  const tip = keep
    ? `这次「${selectedTopic.value || '云笺小试'}」还有 ${Math.max(total - answered, 0)} 关没做完，休息前要不要先把进度存下来？存好后下次回来点「继续上次进度」就能接着做。`
    : '现在还没有正在进行的闯关。要不要先休息一会儿，等状态好了再来？'
  try {
    await ElMessageBox.confirm(tip, '休息一下', {
      confirmButtonText: keep ? '保存进度并休息' : '去休息',
      cancelButtonText: '继续练习',
      type: 'info',
      closeOnClickModal: false,
    })
  } catch (e) { return }
  if (keep) {
    const synced = await stashQuizProgress()
    ElMessage.success(synced
      ? '进度已保存，下次在任意设备登录都能点「继续上次进度」接着做'
      : '进度已存在本机，联网后会自动同步')
  } else {
    ElMessage.success('好呀，休息好了再来闯关')
  }
}

const resumeQuizProgress = () => {
  const s = savedQuizProgress.value
  if (!s || !Array.isArray(s.questions) || !s.questions.length) { clearSavedQuizProgress(); return }
  if (s.courseId) {
    const c = courses.value.find((x: any) => x.id === s.courseId)
    if (c) selectedCourse.value = c
  }
  selectedTopic.value = s.topic || selectedCourse.value?.title || ''
  quizQuestions.value = s.questions
  quizAnswers.value = (Array.isArray(s.answers) && s.answers.length === s.questions.length)
    ? s.answers : new Array(s.questions.length).fill(-1)
  quizAnsweredFlags.value = (Array.isArray(s.answeredFlags) && s.answeredFlags.length === s.questions.length)
    ? s.answeredFlags : new Array(s.questions.length).fill(false)
  quizCurrentIdx.value = Math.min(Math.max(Number(s.currentIdx) || 0, 0), s.questions.length - 1)
  quizCorrectCount.value = Number(s.correctCount) || 0
  quizFeedback.value = 'none'
  quizResult.value = null
  quizStage.value = 'playing'
  ElMessage.success('已恢复上次的进度，接着往下闯吧')
}

// ===== 难题反馈：请教过老师之后，学生做完这题给个难度评价 =====
const stuckQuestion = ref<{ idx: number; topic: string; question: string } | null>(null)
const ratingOpen = ref(false)
const ratingStars = ref(0)
const ratingTags = ref<string[]>([])
const ratingSource = ref<{ topic: string; question: string }>({ topic: '', question: '' })
const rateTagOptions = [
  '一下就懂了',
  '差一点，提示后想通了',
  '之前没想到这个思路',
  '确实有点难，还想再练一遍',
  '这题我还没太明白',
]
const ratingStarText = computed(() =>
  ['', '很简单', '比较简单', '一般', '有点难', '非常难'][ratingStars.value] || '')
const openRating = (q: { topic: string; question: string }) => {
  ratingSource.value = { topic: q.topic, question: q.question }
  ratingStars.value = 0
  ratingTags.value = []
  ratingOpen.value = true
}
const toggleRateTag = (t: string) => {
  const i = ratingTags.value.indexOf(t)
  if (i >= 0) ratingTags.value.splice(i, 1)
  else ratingTags.value.push(t)
}
const closeRating = () => { ratingOpen.value = false }
const ratingThanks = () => {
  const s = ratingStars.value
  if (s <= 2) return '收到啦，这题对你不算难，下次给你加点小挑战～'
  if (s === 3) return '记下了，这题难度刚刚好，保持这个节奏！'
  if (s === 4) return '谢谢你的反馈，这题确实有点挑战，慢慢来就好～'
  return '难一点也没关系，我们一起把它啃下来，你已经很努力啦！'
}
const submitRating = async () => {
  if (!ratingStars.value) { ElMessage.warning('先给这题打个难度分吧～'); return }
  // 评价直接写后端（教师干预页要读它），本地不再留副本，避免两份数据对不上
  let synced = true
  try {
    await studentApi.submitQuizRating({
      topic: ratingSource.value.topic,
      question: ratingSource.value.question,
      stars: ratingStars.value,
      tags: [...ratingTags.value],
    })
  } catch (e) {
    synced = false
  }
  ratingOpen.value = false
  if (synced) ElMessage.success(ratingThanks())
  else ElMessage.warning('网络不太顺，这条评价没交上去，过会儿再试一次吧～')
}
const quizAnswers = ref<number[]>([])
const quizResult = ref<any>(null)
const quizLoading = ref(false)
const quizStage = ref<'idle' | 'playing' | 'finished'>('idle')
const quizCurrentIdx = ref(0)
const quizCorrectCount = ref(0)
const quizAnsweredFlags = ref<boolean[]>([])
const quizFeedback = ref<'none' | 'correct' | 'wrong'>('none')
const quizGroup = ref(0) // 预生成题库组号，实现"换一组题"立即切换

const generateQuiz = async () => {
  const topic = selectedTopic.value || '人工智能基础'
  const group = quizGroup.value
  quizLoading.value = true
  quizResult.value = null
  quizStage.value = 'idle'
  quizCurrentIdx.value = 0
  quizCorrectCount.value = 0
  quizFeedback.value = 'none'
  try {
    const data: any = await studentApi.generateQuiz({ topic, count: 3, courseId: selectedCourse.value?.id, group })
    quizQuestions.value = data?.questions || []
    supportMessage.value = data?.supportMessage || ''
    quizAnswers.value = new Array(quizQuestions.value.length).fill(-1)
    quizAnsweredFlags.value = new Array(quizQuestions.value.length).fill(false)
    // 有预生成多组题库时，自动预取下一组，点"换一组题"即刻切换
    const total = data?.totalGroups || 1
    quizGroup.value = total > 1 ? (group + 1) % total : 0
    if (quizQuestions.value.length > 0) {
      quizStage.value = 'playing'
      // 重新开一关时，旧的暂存进度不再保留
      clearSavedQuizProgress()
      stuckQuestion.value = null
    } else {
      ElMessage.warning('题目生成失败，请重试')
    }
  } catch (e) {
    ElMessage.error('生成题目失败，请稍后重试')
  } finally {
    quizLoading.value = false
  }
}

const answerQuestion = (qIdx: number, aIdx: number) => {
  if (quizAnsweredFlags.value[qIdx]) return
  quizAnswers.value[qIdx] = aIdx
  quizAnsweredFlags.value[qIdx] = true
  // 请教过老师的这道题，答完后请学生评价一下难度
  const stuck = stuckQuestion.value
  if (stuck && stuck.idx === qIdx) {
    stuckQuestion.value = null
    setTimeout(() => openRating({ topic: stuck.topic, question: stuck.question }), 1500)
  }
  const isCorrect = aIdx === quizQuestions.value[qIdx].answer
  if (isCorrect) {
    quizCorrectCount.value++
    quizFeedback.value = 'correct'
  } else {
    quizFeedback.value = 'wrong'
  }
  setTimeout(() => {
    if (quizCurrentIdx.value < quizQuestions.value.length - 1) {
      quizCurrentIdx.value++
      quizFeedback.value = 'none'
    } else {
      finishQuiz()
    }
  }, 1800)
}

const finishQuiz = async () => {
  try {
    const result: any = await studentApi.gradeQuiz({
      questions: quizQuestions.value,
      answers: quizAnswers.value,
      topic: selectedTopic.value || '人工智能基础',
      courseId: selectedCourse.value?.id,
    })
    quizResult.value = result
    if (result.supportMessage) supportMessage.value = result.supportMessage
    quizStage.value = 'finished'
    // 本轮已闯关完成，暂存的进度可以清掉
    clearSavedQuizProgress()
    if (result.correct > 0) {
      ElMessage.success(`答对${result.correct}题，获得${result.correct * 3}积分奖励！`)
    }
  } catch (e) {
    quizResult.value = {
      total: quizQuestions.value.length,
      correct: quizCorrectCount.value,
      score: Math.round(quizCorrectCount.value / Math.max(quizQuestions.value.length, 1) * 100),
    }
    quizStage.value = 'finished'
  }
}

const resetQuiz = () => {
  quizStage.value = 'idle'
  quizQuestions.value = []
  quizAnswers.value = []
  quizResult.value = null
  quizCurrentIdx.value = 0
  quizCorrectCount.value = 0
  quizFeedback.value = 'none'
  quizAnsweredFlags.value = []
  quizGroup.value = 0
  stuckQuestion.value = null
  ratingOpen.value = false
}

// ===== 动画讲解（内置视频） =====
// 各课程内置B站视频，替代AI生成动画
const builtinVideos: Record<string, { bvid: string; title: string }> = {
  '什么是人工智能': { bvid: 'BV1wNL9zCEfy', title: '什么是人工智能' },
  '计算机是怎么思考的': { bvid: 'BV13r95BFEXU', title: '计算机是怎么思考的' },
  '和AI做朋友': { bvid: 'BV1hG411A7E4', title: '和AI做朋友' },
  '简单的指令': { bvid: 'BV12L4y1775u', title: '简单的指令' },
  '机器学习是什么': { bvid: 'BV1nt411r7tj', title: '机器学习是什么' },
  'Scratch编程入门': { bvid: 'BV17F411b7UQ', title: 'Scratch编程入门' },
  '排序算法': { bvid: 'BV1WP411c7hS', title: '排序算法' },
  'AI能做什么和不能做什么': { bvid: 'BV1FrX7YWEuZ', title: 'AI能做什么和不能做什么' },
  '条件判断': { bvid: 'BV1j5fbYAECo', title: '条件判断' },
  '循环结构': { bvid: 'BV1fofhY3EjB', title: '循环结构' },
}
const builtinVideo = computed(() => {
  const t = selectedCourse.value?.title
  if (!t) return null
  return builtinVideos[t] || null
})

type AlgorithmConcept = {
  title: string
  formula: string
  formulaGuide: string
  principle: string
  steps: string[]
  example: string
  note?: string
  application?: {
    question: string
    steps: string[]
    decision: string
  }
}

type AlgorithmLesson = {
  title: string
  intro: string
  foundation: string
  goals: string[]
  concepts: AlgorithmConcept[]
}

// 高中算法讲解；深度学习使用独立的翻页讲解与实验组件。
const highSchoolAlgorithmLessons: Record<string, AlgorithmLesson> = {
  '机器学习算法': {
    title: '机器学习算法：从数据中寻找规律',
    intro: '本课用线性回归、K 近邻和决策树说明模型如何从已知样本中学习，再对新数据做出预测。',
    foundation: '把每一行数据看成一个“样本”。用来描述样本的信息叫“特征”，记为 x；希望模型预测的答案叫“标签”，记为 y。预测连续数值叫回归，预测类别叫分类。',
    goals: ['分清回归任务和分类任务', '看懂权重、误差、距离和信息熵的含义', '知道模型如何利用数据得到预测结果'],
    concepts: [
      {
        title: '线性回归：用直线预测数值',
        formula: 'ŷ = w₁x₁ + w₂x₂ + … + wₘxₘ + b',
        formulaGuide: 'ŷ 读作“y 帽”，表示预测值；x₁ 到 xₘ 是特征；w₁ 到 wₘ 是每个特征的权重；b 是不受特征变化影响的偏置。',
        principle: '线性回归将每个特征乘以相应权重，再把结果相加。在其他特征不变时，xⱼ 每增加 1 个单位，预测值改变 wⱼ；不同特征的单位或尺度不同时，不能只比较权重绝对值判断谁更重要。训练就是反复调整 w 和 b，使预测更接近真实值。',
        steps: ['将已知样本整理成特征 x 和真实答案 y', '用当前的 w 和 b 计算预测值 ŷ', '比较 y 与 ŷ，计算预测误差', '根据误差调整 w 和 b，并重复这一过程'],
        example: '假设根据学习时间 x 预测成绩，学到的公式为 ŷ = 8x + 40。当 x = 5 小时时，预测成绩为 8 × 5 + 40 = 80 分。这只是用来理解计算方法的简化示例。',
        note: '线性回归适合预测连续数值，不能仅因为两个变量同时变化就认定它们存在因果关系。',
      },
      {
        title: '均方误差：衡量回归预测有多偏',
        formula: 'MSE = (1/n) Σᵢ₌₁ⁿ (yᵢ − ŷᵢ)²',
        formulaGuide: 'n 是样本数量；yᵢ 是第 i 个样本的真实值；ŷᵢ 是它的预测值；Σ 表示将所有样本的结果相加。',
        principle: '先计算每个样本的“真实值−预测值”，再平方，可以避免正负误差相互抵消，同时让较大的误差受到更明显的惩罚。MSE 越小，表示这组预测整体上越接近真实值。',
        steps: ['计算每个样本的误差 yᵢ − ŷᵢ', '将每个误差平方', '把全部平方误差相加', '用总和除以样本数 n'],
        example: '两个学生的真实成绩是 80、90，模型预测为 78、94。MSE = [(80−78)² + (90−94)²] / 2 = (4 + 16) / 2 = 10。',
        note: 'MSE 只是衡量误差的一种方法；训练集上误差小，不代表对新数据一定表现得好。',
      },
      {
        title: 'K 近邻：让附近样本投票',
        formula: 'd(x,z) = √[Σⱼ₌₁ᵐ (xⱼ − zⱼ)²]\nŷ = mode{ yᵢ | xᵢ ∈ Nₖ(x) }',
        formulaGuide: 'd(x,z) 是两个样本的欧氏距离；m 是特征数量；Nₖ(x) 是距离新样本 x 最近的 k 个样本；mode 表示取出现次数最多的类别。',
        principle: 'K 近邻不会事先学出一条固定公式。它在需要预测时，才计算新样本与所有已知样本的距离，选出最近的 k 个邻居，并让它们投票决定类别。',
        steps: ['选择邻居数量 k，分类时常选奇数以减少平票', '计算新样本与每个已知样本的距离', '按距离从小到大排序，取前 k 个样本', '统计这 k 个邻居的类别，得票最多者为预测结果'],
        example: '设 k = 3，与新样本最近的三个邻居类别分别为 A、A、B。A 得到 2 票，B 得到 1 票，因此预测类别为 A。',
        note: '如果一个特征的数值范围远大于其他特征，它会主导距离，因此 KNN 通常需要先对数值特征进行归一化或标准化。',
      },
      {
        title: '决策树：用问题逐层分类',
        formula: 'H(D) = −Σⱼ pⱼ log₂(pⱼ)\nGain = H(D) − Σᵥ |Dᵥ|/|D| · H(Dᵥ)',
        formulaGuide: 'H(D) 是数据集 D 的信息熵；pⱼ 是第 j 类样本所占比例；Dᵥ 是某个分支后的子集；Gain 是这次分支带来的信息增益。',
        principle: '数据类别越混杂，信息熵越大；数据全属于同一类时，信息熵为 0。决策树尝试不同问题，选择信息增益较大的问题，使分支后的子集更纯净。',
        steps: ['计算当前数据集的信息熵', '尝试用一个特征将数据分成多个子集', '计算各子集的加权信息熵和信息增益', '选择增益较大的分支，然后对子集继续重复'],
        example: '某数据集有 10 个样本，6 个属于 A 类，4 个属于 B 类。H(D) = −[0.6log₂(0.6) + 0.4log₂(0.4)] ≈ 0.971。如果某个问题能将它们分成两个更纯净的子集，分支后的加权熵就会下降。',
        note: '树生长得过深可能记住训练数据而产生过拟合，实际应用中常通过限制深度或剪枝进行控制。',
      },
    ],
  },
  'Python数据分析': {
    title: 'Python数据分析：用数字描述数据',
    intro: '本课聚焦 Pandas 和 NumPy 数据分析中最常用的统计思想：中心水平、波动大小、数值缩放和线性相关。',
    foundation: '数据表中，一行通常代表一个观测对象，一列代表一个变量。Python 负责快速执行计算，但正确解释结果仍需要理解公式。计算前还应检查缺失值、重复值和异常值。',
    goals: ['用平均数描述数据的中心', '用标准差比较数据的波动', '理解归一化和相关系数的用途与限制'],
    concepts: [
      {
        title: '算术平均数：找到数据的中心',
        formula: 'x̄ = (1/n) Σᵢ₌₁ⁿ xᵢ',
        formulaGuide: 'x̄ 是平均数；n 是有效数值的个数；xᵢ 是第 i 个数值；Σ 表示从第 1 个数值一直加到第 n 个。',
        principle: '平均数相当于把所有数值的总量平均分配给每个观测。它用一个数描述整组数据的一般水平，但容易受极端值影响。',
        steps: ['确认要分析的数值列', '处理缺失值，并确定有效数值数量 n', '把全部有效数值相加', '用总和除以 n；Pandas 和 NumPy 的 mean 方法可完成这一计算'],
        example: '三次测试成绩是 70、80、90，则 x̄ = (70 + 80 + 90) / 3 = 80。这表示三次成绩的平均水平为 80 分。',
        note: '如果数据为 70、80、150，极端值 150 会将平均数拉高。此时应同时观察中位数和数据分布。',
      },
      {
        title: '标准差：衡量数据的波动',
        formula: 'σ = √[(1/n) Σᵢ₌₁ⁿ (xᵢ − x̄)²]',
        formulaGuide: 'σ 是总体标准差；xᵢ − x̄ 是每个数值与平均数的偏差；平方后求平均得到方差，最后开平方恢复原来的单位。',
        principle: '两组数据可以有相同的平均数，但波动程度可能完全不同。标准差越小，数值越集中在平均数附近；标准差越大，数值越分散。',
        steps: ['先计算平均数 x̄', '用每个数值减去平均数', '将每个偏差平方并求平均，得到方差', '对方差开平方，得到标准差'],
        example: '数据 2、4、6 的平均数是 4。方差 = [(2−4)² + (4−4)² + (6−4)²] / 3 = 8/3，因此总体标准差 σ = √(8/3) ≈ 1.63。',
        note: '本页公式是总体标准差，分母为 n。NumPy 的 std 默认使用这一形式；Pandas Series.std 默认计算样本标准差，分母为 n−1。',
      },
      {
        title: '最小—最大归一化',
        formula: 'x′ = (x − xₘᵢₙ) / (xₘₐₓ − xₘᵢₙ)',
        formulaGuide: 'x 是原始数值；xₘᵢₙ 和 xₘₐₓ 分别是该列的最小值和最大值；x′ 是转换后的数值。',
        principle: '先用 x 减去最小值，将数据起点移到 0；再除以数值范围，将数据缩放到 0 至 1。它保留数值之间的相对大小，但会改变数值的单位。',
        steps: ['在需要处理的数值列中找到最小值和最大值', '用每个数值减去最小值', '再除以最大值与最小值之差', '检查结果：最小值应为 0，最大值应为 1'],
        example: '某列最小值是 50，最大值是 100。对数值 75，x′ = (75−50) / (100−50) = 25/50 = 0.5。',
        note: '如果最大值等于最小值，分母为 0，不能直接使用此公式。归一化的最小值和最大值应只由训练数据计算，避免泄漏测试数据信息。',
      },
      {
        title: '皮尔逊相关系数：观察线性关系',
        formula: 'r = Σ(xᵢ−x̄)(yᵢ−ȳ) / √[Σ(xᵢ−x̄)² Σ(yᵢ−ȳ)²]',
        formulaGuide: 'x̄ 和 ȳ 是两个变量的平均数；分子衡量它们是否同向变化；分母消除两个变量量纲和波动大小的影响。',
        principle: 'r 的取值范围为 −1 到 1。r 接近 1 表示两个变量有较强的正线性关系；r 接近 −1 表示有较强的负线性关系；r 接近 0 只表示线性关系较弱，不代表两者完全没有关系。',
        steps: ['保证 x 和 y 数据一一对应，并处理缺失值', '分别计算 x 和 y 的平均数', '按公式计算同向变化程度并进行标准化', '结合散点图观察关系形状，不只依赖一个 r 值'],
        example: '如果学习时间与测试成绩的 r = 0.85，可以说在这组数据中两者呈较强的正线性相关；不能仅凭此认定学习时间是成绩变化的唯一原因。',
        note: '相关不等于因果。极端值也可能明显改变 r，因此应先查看数据分布和散点图。',
      },
    ],
  },
  '排序算法进阶': {
    title: '排序算法进阶：分治与复杂度',
    intro: '本课从复杂度出发，详细拆解快速排序和归并排序中的“分治”思想，并比较它们的时间、空间和稳定性。',
    foundation: '排序是将一组元素按键值从小到大或从大到小排列。“分治”表示把大问题分成结构相同的小问题，解决小问题后再组合答案。分析时用 n 表示待排序元素数量。',
    goals: ['理解 O(n²) 与 O(n log n) 的增长差异', '能按照分区过程解释快速排序', '能比较快速排序和归并排序的特点'],
    concepts: [
      {
        title: '时间复杂度：关心增长趋势',
        formula: 'T(n) = O(n²)  或  T(n) = O(n log₂n)',
        formulaGuide: 'T(n) 表示处理 n 个元素所需的基本操作次数；O 记号描述 n 足够大时的增长级别，忽略常数倍和较低次项。',
        principle: '复杂度不是程序实际运行秒数，而是数据规模增大时运算量如何增长。对 O(n²)，n 变为原来的 2 倍，主要运算量约变为 4 倍；对 O(n log n)，增长要慢得多。',
        steps: ['确定输入规模 n 代表什么', '选择需要统计的核心操作，如元素比较', '分析循环或递归层数以及每层工作量', '保留增长最快的主要部分，用 O 记号表示'],
        example: '当 n = 1024 时，n² = 1,048,576，而 n log₂n = 1024 × 10 = 10,240。这个估算忽略了常数差异，但能显示两种增长速度的明显差距。',
        note: '复杂度相同的算法在实际运行中仍可能因常数、内存访问和输入特征而有差异。',
      },
      {
        title: '快速排序：选基准并分区',
        formula: 'T(n) = T(k) + T(n−k−1) + Θ(n)\n平衡时：T(n) ≈ 2T(n/2) + Θ(n) = Θ(n log n)',
        formulaGuide: 'k 是分区后左侧子序列的元素数；n−k−1 是右侧元素数；Θ(n) 是一次分区检查全部元素所需的线性工作。',
        principle: '快速排序选择一个基准值 pivot，将较小元素放到一侧，较大元素放到另一侧，然后对两个子序列重复此过程。当分区较平衡时，递归约有 log₂n 层，每层总工作量约为 n。',
        steps: ['从待排序序列中选一个基准值', '遍历其他元素，按与基准的比较结果进行分区', '基准进入最终的相对位置', '分别对左右子序列重复分区，直到子序列长度不超过 1'],
        example: '排序 [6, 3, 8, 2, 5]，选 5 为基准。一次分区可得到 [3, 2] | 5 | [6, 8]。再分别排序左右两部分，最终得到 [2, 3, 5, 6, 8]。',
        note: '快速排序的具体分区实现有多种，元素与基准相等时放在哪一侧取决于实现方式。',
      },
      {
        title: '快速排序的最坏情况',
        formula: 'T(n) = T(n−1) + Θ(n) = Θ(n²)',
        formulaGuide: '每次分区只排定一个基准，剩下 n−1 个元素继续递归；各层工作量约为 n + (n−1) + … + 1，其增长级别为 n²。',
        principle: '如果基准总是当前序列的最小值或最大值，分区会极度不平衡，递归深度从约 log n 增加到约 n，时间复杂度降为 O(n²)。',
        steps: ['观察基准选择方法', '检查输入是否使每次分区都接近 0 与 n−1', '将各层比较次数相加', '可用随机基准或三数取中等策略降低持续不平衡的概率'],
        example: '对已升序的 [1, 2, 3, 4, 5]，如果每次都选最后一个元素为基准，子问题规模依次为 4、3、2、1，不会形成平衡的两半。',
        note: '快速排序平均递归栈空间为 O(log n)，最坏情况可达 O(n)；常见原地快速排序通常不是稳定排序。',
      },
      {
        title: '归并排序',
        formula: 'T(n) = 2T(n/2) + Θ(n) = Θ(n log n)\nS(n) = Θ(n)',
        formulaGuide: '2T(n/2) 表示排序两个长度约为 n/2 的子序列；Θ(n) 是合并两个有序子序列的工作量；S(n) 表示额外空间。',
        principle: '归并排序不依靠基准，而是一直将序列平分，直到每个子序列只有一个元素。然后每次比较两个有序子序列的队首，取较小者放入新序列。',
        steps: ['把序列分成左右两半', '递归排序左半和右半', '从两个有序子序列的起点开始比较', '将较小元素依次放入临时序列，直到全部合并'],
        example: '合并已排序的 [2, 6] 和 [3, 5]：先比较 2 与 3，取 2；再比较 6 与 3，取 3；再取 5，最后取 6，得到 [2, 3, 5, 6]。',
        note: '归并排序在最好、平均和最坏情况下都是 O(n log n)，并且可以稳定；但数组版实现通常需要 O(n) 额外空间。',
      },
    ],
  },
  'AI项目实践': {
    title: 'AI项目实践：从问题到可验证的模型',
    intro: '本课以二分类项目为主线，说明如何划分数据，以及如何用准确率、精确率、召回率和 F1 分数评估模型。',
    foundation: '项目开始时要先明确输入、要预测的结果和成功标准。在二分类中，TP 表示正类被正确预测，TN 表示负类被正确预测，FP 是误报，FN 是漏报。以垃圾邮件识别为例，可把“垃圾邮件”定义为正类。',
    goals: ['知道训练集、验证集和测试集的不同用途', '能根据 TP、TN、FP、FN 计算常用分类指标', '能根据任务中误报和漏报的代价选择指标'],
    concepts: [
      {
        title: '数据划分：将训练和最终考试分开',
        formula: 'D = Dₜᵣₐᵢₙ ∪ Dᵥₐₗ ∪ Dₜₑₛₜ\nDₜᵣₐᵢₙ ∩ Dᵥₐₗ = Dₜᵣₐᵢₙ ∩ Dₜₑₛₜ = Dᵥₐₗ ∩ Dₜₑₛₜ = ∅',
        formulaGuide: '第一行读作：“全部数据 D，由训练集 D train、验证集 D val 和测试集 D test 合并而成。”符号 ∪ 读作“并集”，表示把三部分合起来能还原全部数据。第二行读作：“任意两部分的交集都等于空集。”符号 ∩ 读作“交集”，∅ 读作“空集”，意思是同一条样本不能同时出现在两组中。',
        principle: '训练集用来学习模型参数，验证集用来选择模型和调整设置，测试集只用于最后一次客观评估。三者不应重叠，否则会让模型提前看到“考试题”。',
        steps: ['明确每个样本的输入特征和标签', '在保持各类比例尽量合理的前提下随机划分数据', '只用训练集拟合数据处理参数和模型参数', '用验证集确定方案后，再用测试集评估一次'],
        example: '共有 1000 条样本时，可以作为示例划分为 700 条训练数据、150 条验证数据和 150 条测试数据。70%/15%/15% 是一种常见示例，不是所有项目都必须采用的固定比例。',
        note: '先用全部数据计算归一化参数，再划分数据，也会造成测试信息泄漏。应先划分，再只用训练集确定数据处理参数。',
        application: {
          question: '做垃圾邮件识别、图片分类等项目时，用这个公式把已有样本分成“练习、调试、最终考试”三部分，让模型的最终成绩更可信。',
          steps: ['项目开始就保留测试集，不让它参与训练或调参', '用训练集学习模型，用验证集比较算法、参数和分类阈值', '方案确定后只在测试集上评估，并记录这一次的结果'],
          decision: '如果验证集表现很好而测试集明显变差，要检查是否反复针对验证集调整，或两组数据的来源是否不同。不能把测试集重新混入训练集后，仍把原来的测试成绩当作客观结果。',
        },
      },
      {
        title: '准确率：全部样本中答对多少',
        formula: 'Accuracy = (TP + TN) / (TP + TN + FP + FN)',
        formulaGuide: '从等号右边读：先把 TP（正类预测正确）和 TN（负类预测正确）相加，得到“答对的总数”；再除以 TP、TN、FP、FN 的总和，也就是“全部样本数”。斜线 / 读作“除以”，括号里的加法要先算。结果通常在 0 到 1 之间，乘以 100% 就是百分比准确率。',
        principle: '准确率从整体上看模型的答对比例，容易理解。但当类别数量严重不平衡时，它可能掩盖问题。',
        steps: ['用混淆矩阵统计 TP、TN、FP、FN', '将 TP 和 TN 相加得到正确数', '用正确数除以全部样本数', '转换为百分比并结合类别分布解释'],
        example: '若 TP = 40、TN = 50、FP = 5、FN = 5，则 Accuracy = (40 + 50) / 100 = 0.90，即准确率为 90%。',
        note: '如果 1000 封邮件中只有 10 封垃圾邮件，模型把所有邮件都判为正常仍有 99% 准确率，但它一封垃圾邮件都没找到。',
        application: {
          question: '当两类样本数量比较接近，而且误报与漏报的影响相近时，准确率适合用来快速了解模型整体答对了多少。',
          steps: ['先在测试集上统计 TP、TN、FP、FN', '代入公式得到准确率，并与“永远猜多数类”的简单基线比较', '比较不同模型时，必须使用同一份测试集和相同的数据处理方法'],
          decision: '准确率高于基线很多，说明模型学到了一些有效规律；但如果正负样本很不平衡，还必须同时查看精确率和召回率，不能只凭准确率决定模型可用。',
        },
      },
      {
        title: '精确率与召回率：分别关注误报和漏报',
        formula: 'Precision = TP / (TP + FP)\nRecall = TP / (TP + FN)',
        formulaGuide: '第一行读作：“精确率等于 TP 除以 TP 加 FP。”分母 TP + FP 是模型判为正类的全部样本，所以它在问“模型找出来的有多少是真的”。第二行读作：“召回率等于 TP 除以 TP 加 FN。”分母 TP + FN 是现实中真正的正类总数，所以它在问“真正需要找的对象找回了多少”。FP 增多会拉低精确率，FN 增多会拉低召回率。',
        principle: '精确率回答“模型找出来的对象中，有多少是真的”，适合误报代价较高的任务。召回率回答“所有真正需要找到的对象中，模型找到了多少”，适合漏报代价较高的任务。',
        steps: ['先明确什么是项目中的正类', '根据真实标签与预测标签统计 TP、FP、FN', '如果更关心误报，重点查看 Precision', '如果更关心漏报，重点查看 Recall'],
        example: '仍使用 TP = 40、FP = 5、FN = 5：Precision = 40/(40+5) ≈ 88.9%；Recall = 40/(40+5) ≈ 88.9%。如果 FN 增加，召回率会下降。',
        note: '精确率与召回率常存在取舍。调低分类阈值通常能找到更多正类，但也可能增加误报；选择时应依据项目需求。',
        application: {
          question: '垃圾邮件拦截既不能经常误删正常邮件，也不能漏掉大量垃圾邮件。精确率衡量误报问题，召回率衡量漏报问题。',
          steps: ['先明确正类，例如把“垃圾邮件”规定为正类', '若更怕误删正常邮件，优先提高精确率；若更怕漏掉垃圾邮件，优先提高召回率', '调整分类阈值后重新计算两个指标，观察一升一降的取舍'],
          decision: '精确率低表示模型报出的结果中假警报较多；召回率低表示真正的目标漏掉较多。应根据实际代价决定侧重哪个指标，而不是认为其中一个永远更重要。',
        },
      },
      {
        title: 'F1 分数：平衡精确率与召回率',
        formula: 'F1 = 2 × Precision × Recall / (Precision + Recall)',
        formulaGuide: '读作：“F1 等于 2 乘以精确率，再乘以召回率，最后除以精确率与召回率之和。”计算时先算分子 2 × Precision × Recall，再算分母 Precision + Recall，最后做除法。F1 通常在 0 到 1 之间；只要精确率或召回率有一个很低，乘积就会变小，因此 F1 也会被拉低。',
        principle: '普通算术平均可能弱化较低值的影响，调和平均对较低值更敏感。因此，一个模型即使精确率很高，但召回率很低，F1 也不会很高。',
        steps: ['先计算 Precision 和 Recall', '计算二者的乘积并乘以 2', '用结果除以 Precision + Recall', '同时查看原始的 Precision 和 Recall，避免只看一个综合数字'],
        example: '如果 Precision = 0.80，Recall = 0.50，则 F1 = 2 × 0.80 × 0.50 / (0.80 + 0.50) ≈ 0.615，即约 61.5%。',
        note: 'F1 不使用 TN，所以它不能取代对混淆矩阵和业务代价的完整分析。',
        application: {
          question: '当正类较少，同时又希望兼顾误报与漏报时，可以用 F1 把精确率和召回率合成一个便于比较的分数。',
          steps: ['在同一测试集上计算每个候选模型的 Precision 和 Recall', '把两个指标代入 F1 公式，保证正类定义和计算方式一致', '用 F1 初步筛选模型后，再查看精确率、召回率和混淆矩阵'],
          decision: 'F1 较高表示精确率与召回率整体比较均衡，但它不会告诉你具体是哪一种错误更多。如果实际任务中误报和漏报的代价差很多，最终决定仍要回到两个原始指标。',
        },
      },
      {
        title: '泛化差距：检查是否只记住了训练数据',
        formula: 'Gap = Scoreₜᵣₐᵢₙ − Scoreₜₑₛₜ',
        formulaGuide: '读作：“泛化差距等于训练集分数减去测试集分数。”Score train 是模型在训练数据上的成绩，Score test 是模型在未参与训练的测试数据上的成绩；两边必须使用同一种指标才能相减。若分数写成百分比，98% − 75% 的结果应说成相差 23 个百分点，而不是下降 23%。',
        principle: '模型在训练集上得分很高，但在新数据上得分明显较低，通常说明它可能过度记住了训练样本的细节，而没有学到可推广的规律，这种现象叫过拟合。',
        steps: ['选定一个符合项目目标的评估指标', '分别在训练集和未见测试集上计算同一指标', '比较两者差距，同时关注测试集绝对表现', '如差距较大，检查数据量、特征、模型复杂度和正则化等因素'],
        example: '某模型的训练准确率是 98%，测试准确率是 75%，则 Gap = 98% − 75% = 23 个百分点。这是需要进一步检查过拟合的信号，但不能只凭一个固定阈值下结论。',
        note: '测试集不应被反复用来调整模型；否则模型选择也会逐渐过度适应测试集。',
        application: {
          question: '训练结束后，用泛化差距检查模型是不是只记住练习题，却没有学会在新样本上解决同类问题。',
          steps: ['选择一个项目真正关心的指标，并分别计算训练集与测试集分数', '用训练分数减测试分数，同时记录测试集分数本身', '结合学习曲线、数据量和模型复杂度继续寻找差距产生的原因'],
          decision: '差距较大且训练分数高，通常提示可能过拟合，可尝试增加数据、降低模型复杂度或加强正则化；差距很小但两边都低，则更像没有学好，不能因为 Gap 小就认为模型优秀。',
        },
      },
    ],
  },
}

type AlgorithmApplication = NonNullable<AlgorithmConcept['application']>

// 为其余已完成的高中课程补充公式应用。
const additionalAlgorithmApplications: Record<string, Record<string, AlgorithmApplication>> = {
  '机器学习算法': {
    '线性回归：用直线预测数值': {
      question: '需要根据若干已知特征预测一个连续数值时，可以使用线性回归，例如根据学习时间和练习量预测成绩。',
      steps: ['确定要预测的连续数值 y，并选择可能有关的特征 x', '用训练数据求出各特征权重 w 和偏置 b', '把新样本的特征代入公式，再用测试误差检查预测质量'],
      decision: '预测误差较小且在新数据上保持稳定，说明这条线性规律有一定用途；若误差具有明显弯曲趋势，应考虑变量关系可能不是线性的，而不是只继续调整权重。',
    },
    '均方误差：衡量回归预测有多偏': {
      question: '需要比较两个回归模型谁的数值预测更接近真实答案时，可以在同一测试集上计算均方误差。',
      steps: ['记录每个测试样本的真实值与预测值', '逐个计算误差、平方后相加，再除以样本数', '在相同数据和相同单位下比较不同模型的 MSE'],
      decision: 'MSE 越小通常表示整体预测越接近真实值；但它会放大少数特别大的误差，因此还要查看异常样本，必要时同时参考平均绝对误差。',
    },
    'K 近邻：让附近样本投票': {
      question: '当“相似样本往往属于同一类”时，可用 K 近邻分类，例如根据重量、颜色等特征判断水果类别。',
      steps: ['先把不同量纲的数值特征缩放到可比较的范围', '用验证集选择 k，再计算新样本到已知样本的距离', '取最近的 k 个邻居投票，把票数最多的类别作为结果'],
      decision: 'k 太小容易受噪声影响，k 太大可能忽略局部差异；应选择验证表现较好的 k，并检查最近邻居是否真的具有可比较的特征。',
    },
    '决策树：用问题逐层分类': {
      question: '需要一套可以逐步解释的分类规则时，可用决策树，例如根据环境数据判断植物是否需要浇水。',
      steps: ['准备带有类别标签的训练样本', '比较候选问题的信息增益，选择能让类别更纯的分支', '继续对子集分支，并用验证集决定树应生长多深'],
      decision: '每条根到叶的路径都能解释一次判断；若训练成绩很高而验证成绩下降，说明树可能过深，应限制深度或进行剪枝。',
    },
  },
  'Python数据分析': {
    '算术平均数：找到数据的中心': {
      question: '需要用一个数概括一组数据的一般水平时，可以计算平均数，例如班级平均分或一周平均气温。',
      steps: ['先处理缺失值并确认参与计算的有效数据', '将有效数值求和后除以数量 n', '需要比较不同小组时，可用 Pandas 按组计算各自平均数'],
      decision: '平均数适合描述较均匀的数据；若它与大部分数据相差很远，应检查极端值，并同时查看中位数和分布。',
    },
    '标准差：衡量数据的波动': {
      question: '两组数据平均水平相近时，可用标准差比较哪一组更稳定，例如比较两个班级成绩的波动。',
      steps: ['保证两组数据含义和单位相同', '分别计算平均数、平方偏差的平均值，再开平方', '把标准差与平均数、数据范围放在一起解释'],
      decision: '标准差较小表示数据更集中、更稳定，较大表示差异更明显；它不能说明波动好坏，仍要结合分析目标判断。',
    },
    '最小—最大归一化': {
      question: '多个特征单位和范围差别很大时，可把它们缩放到 0 至 1，避免大数值特征主导距离计算或图表。',
      steps: ['只用训练集找出每列的最小值和最大值', '按同一公式转换训练集、验证集和测试集', '检查分母是否为 0，并保存参数供新数据继续使用'],
      decision: '训练数据中的最小值会变成 0、最大值会变成 1；新数据超出原范围时可能小于 0 或大于 1，不应为此重新计算测试集参数。',
    },
    '皮尔逊相关系数：观察线性关系': {
      question: '需要判断两个数值变量是否一起线性变化时，可计算相关系数，例如观察学习时间与成绩的关系。',
      steps: ['整理一一对应的 x、y 数据并处理缺失值', '先画散点图，再计算皮尔逊相关系数 r', '检查极端值，并结合样本数量解释相关程度'],
      decision: 'r 的正负表示同向或反向，绝对值越接近 1 表示线性关系越明显；即使相关很强，也不能只凭 r 认定一个变量导致另一个变化。',
    },
  },
  '排序算法进阶': {
    '时间复杂度：关心增长趋势': {
      question: '程序需要处理越来越多的数据时，可用时间复杂度预估运算量增长，帮助选择能扩展到更大规模的算法。',
      steps: ['明确输入规模 n 和需要统计的核心操作', '找出循环次数或递归层数随 n 的增长方式', '比较候选算法的复杂度，同时记录内存等实际限制'],
      decision: '数据量较大时，O(n log n) 通常比 O(n²) 更有优势；数据很小时常数开销也重要，因此复杂度不是唯一选择依据。',
    },
    '快速排序：选基准并分区': {
      question: '需要在内存中快速整理大量无序数据，且不要求稳定排序时，快速排序通常具有较好的平均性能。',
      steps: ['选择基准值并把较小、较大的元素分到两侧', '对左右子序列重复分区，直到子序列长度不超过 1', '用随机基准等方法减少持续不平衡的机会'],
      decision: '分区越平衡，运行越接近 O(n log n)；若输入可能使分区长期失衡，或必须保留相同键值的原顺序，应考虑保护策略或其他排序算法。',
    },
    '快速排序的最坏情况': {
      question: '检查快速排序在有序、逆序或大量重复值数据上是否会明显变慢时，可以用最坏情况公式分析风险。',
      steps: ['观察每次基准是否总落在序列的一端', '估算递归深度与各层比较次数之和', '测试特殊输入，并采用随机基准、三数取中等策略'],
      decision: '若递归持续形成 0 与 n−1 的分区，时间会接近 O(n²)，递归栈也可能变深；对性能有严格保证时应采用带保护的实现或归并排序。',
    },
    '归并排序': {
      question: '需要稳定排序、保证 O(n log n) 时间，或处理可分段读取的大量数据时，可以使用归并排序。',
      steps: ['不断把序列分成较小的两半', '分别排好两半，再按从小到大的顺序合并', '相同键值合并时先取左侧元素，以保留原有先后顺序'],
      decision: '归并排序的运行时间稳定且容易保持相同元素的原顺序，但数组实现需要额外 O(n) 空间；内存紧张时要权衡这一成本。',
    },
  },
}

Object.entries(additionalAlgorithmApplications).forEach(([courseTitle, applications]) => {
  highSchoolAlgorithmLessons[courseTitle]?.concepts.forEach((concept) => {
    const application = applications[concept.title]
    if (application) concept.application = application
  })
})

const isDeepLearningLesson = computed(() => grade.value === 'high_school'
  && ['深度学习基础', '深度学习'].includes(selectedCourse.value?.title))

const algorithmLesson = computed(() => {
  if (grade.value !== 'high_school') return null
  const title = selectedCourse.value?.title
  return title ? highSchoolAlgorithmLessons[title] || null : null
})

const selectedAlgorithmConceptIndex = ref<number | null>(null)
const algorithmDetailPage = ref(0)
const selectedAlgorithmConcept = computed(() => {
  if (!algorithmLesson.value || selectedAlgorithmConceptIndex.value === null) return null
  return algorithmLesson.value.concepts[selectedAlgorithmConceptIndex.value] || null
})
const algorithmPageLabels = computed(() => selectedAlgorithmConcept.value?.application
  ? ['符号与原理', '分步理解', '例子与注意', '公式应用']
  : ['符号与原理', '分步理解', '例子与注意'])

const openAlgorithmConcept = (index: number) => {
  selectedAlgorithmConceptIndex.value = index
  algorithmDetailPage.value = 0
}

const closeAlgorithmConcept = () => {
  selectedAlgorithmConceptIndex.value = null
  algorithmDetailPage.value = 0
}

const turnAlgorithmPage = (offset: number) => {
  algorithmDetailPage.value = Math.min(
    algorithmPageLabels.value.length - 1,
    Math.max(0, algorithmDetailPage.value + offset),
  )
}

watch([grade, () => selectedCourse.value?.id], closeAlgorithmConcept)

// ===== 故事绘本 =====
const bookData = ref<any>(null)
const favBooks = ref<any[]>([])
const bookLoading = ref(false)
const bookPage = ref(0)
// 当前播放绘本对应的记录（用于收藏）
const bookRecordId = ref(0)
const bookFav = ref(false)

const generateBook = async () => {
  const topic = selectedTopic.value || '什么是人工智能'
  bookLoading.value = true
  bookData.value = null
  bookPage.value = 0
  try {
    const data: any = await studentApi.generateBook({ topic, courseId: selectedCourse.value?.id })
    if (data && data.success === false) {
      ElMessage.info(data.message || '该课程绘本暂未准备')
      return
    }
    bookData.value = data
    bookRecordId.value = data?.recordId || 0
    bookFav.value = !!data?.isFavorite
    loadFavoriteList()
  } catch (e) {
    ElMessage.error('绘本加载失败，请稍后重试')
  } finally {
    bookLoading.value = false
  }
}

const loadFavoriteList = async () => {
  try {
    const data: any = await studentApi.getFavoriteBooks()
    favBooks.value = Array.isArray(data) ? data : []
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

const viewFavoriteBook = async (b: any) => {
  try {
    const data: any = await studentApi.getBook(b.id)
    bookData.value = {
      title: data.bookTitle || data.title || b.title,
      pages: data.pages || [],
    }
    bookPage.value = 0
    bookLoading.value = false
    bookRecordId.value = b.id
    bookFav.value = !!b.isFavorite
  } catch (e) {
    ElMessage.error('加载绘本失败')
  }
}

// 收藏/取消收藏当前播放的绘本
const toggleCurrentFav = async () => {
  if (!bookRecordId.value) return
  try {
    const data: any = await studentApi.toggleBookFavorite(bookRecordId.value)
    bookFav.value = !!data?.isFavorite
    ElMessage.success(bookFav.value ? '已收藏' : '已取消收藏')
    loadFavoriteList()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// ===== 学习资料 =====
const materials = ref<any[]>([])
const materialsLoading = ref(false)
const materialsSubTab = ref('recommended')

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

// ===== 教师资料 =====
const teacherMaterials = ref<any[]>([])
const teacherMaterialsLoading = ref(false)

const loadTeacherMaterials = async () => {
  teacherMaterialsLoading.value = true
  try {
    const data: any = await studentApi.getTeacherMaterials()
    teacherMaterials.value = Array.isArray(data) ? data : []
  } catch (e) {
    teacherMaterials.value = []
  } finally {
    teacherMaterialsLoading.value = false
  }
}

// ===== 学习路径 =====
const learningPath = ref<any>(null)
const pathLoading = ref(false)
// 记录上次生成时间，用于判断要不要重新生成（避免每次切页都等大模型）
let pathFetchedAt = 0
// 同一个请求只发一次：预加载与学生切页共用，避免重复调用大模型
let pathInflight: Promise<void> | null = null
// 请求序号：切学段后旧请求可能还在路上，用它把过期结果丢掉
let pathReqSeq = 0

const fetchLearningPath = (force = false): Promise<void> => {
  if (pathInflight && !force) return pathInflight
  const seq = ++pathReqSeq
  const task = (async () => {
    try {
      const data: any = await studentApi.getLearningPath()
      // 只认最后一次请求的结果，避免切换学段时旧数据覆盖新学段
      if (seq !== pathReqSeq) return
      learningPath.value = data
      pathFetchedAt = Date.now()
    } catch (e) {
      // 静默失败：保留旧数据，下次切页会自动重试
    } finally {
      // 只有最新那次请求负责清空，被取代的旧请求不要去动新请求的状态
      if (seq === pathReqSeq) pathInflight = null
    }
  })()
  pathInflight = task
  return task
}

// 进页面就提前在后台生成，学生点「学习路径」时直接出结果
const prefetchLearningPath = () => { fetchLearningPath() }

const loadLearningPath = async () => {
  // 已有数据时静默刷新：只更新数字，不整页闪 loading
  pathLoading.value = !learningPath.value
  try {
    await fetchLearningPath()
  } catch (e) {
    if (!learningPath.value) ElMessage.error('学习路径加载失败')
  } finally {
    pathLoading.value = false
  }
}

// 学习路径的展示派生数据
const pathSummary = computed<any>(() => learningPath.value?.summary || {})
const pathNode = computed<any>(() => learningPath.value?.nextNode || null)
const recentScoresText = computed(() => {
  const list = learningPath.value?.recentScores || []
  return list.length ? list.map((s: number) => s + ' 分').join('、') : '暂无'
})
const statusText = (status: string) =>
  status === 'mastered' ? '已掌握' : status === 'learning' ? '学习中' : '未开始'
const actionText = (status: string) =>
  status === 'mastered' ? '去复习' : status === 'learning' ? '继续学' : '去学习'
const difficultyText = (difficulty: string) =>
  difficulty === 'easy' ? '入门' : difficulty === 'medium' ? '进阶' : '挑战'
const typeBarWidth = (count: number) => {
  const list = learningPath.value?.typeBreakdown || []
  const max = Math.max(...list.map((t: any) => Number(t.count) || 0), 1)
  return Math.round(((Number(count) || 0) / max) * 100) + '%'
}
// 从学习路径跳到具体课程：优先按 courseId 精准命中左侧课程列表，避免"推荐了却找不到课"
const openTopicInChat = (topic: string, courseId?: number) => {
  if (!topic) return
  const hit = courses.value.find((c: any) =>
    (courseId && c.id === courseId) || c.title === topic)
  if (hit) selectCourse(hit)
  else selectedTopic.value = topic
  activeTab.value = 'chat'
}

// ===== 切换标签时加载数据 =====
watch(activeTab, async (tab) => {
  // 学习路径已在进页面时预生成：有数据就立刻展示；
  // 只有数据缺失或超过 60 秒才在后台重新生成，学生在别处学完回来能看到最新进度
  if (tab === 'path' && (!learningPath.value || Date.now() - pathFetchedAt > 60000)) {
    loadLearningPath()
  }
  if (tab === 'book' && grade.value !== 'high_school') {
    loadFavoriteList()
    // 课程已有预生成绘本时，进入即直接播放，无需点击生成
    if (!bookData.value) {
      if (ensureCourseSelected()) generateBook()
    }
  }
  if (tab === 'materials') {
    if (materialsSubTab.value === 'recommended') loadMaterials()
    else loadTeacherMaterials()
  }
  if (tab === 'quiz' && quizStage.value === 'idle') {
    // 先取暂存进度（后端优先，换设备也能续），再让同学自己选：继续上次 / 重新开始
    await loadSavedQuizProgress()
    if (!savedQuizProgress.value && ensureCourseSelected()) generateQuiz()
  }
  })

// ===== 加载数据 =====
const loadCourses = async () => {
  try {
    const data: any = await studentApi.getAICourses(grade.value)
    // 数据库尚未同步该年级课程时，展示仓库内置课程，避免成功返回空数组后页面空白。
    courses.value = Array.isArray(data) && data.length > 0 ? data : getDefaultCourses()
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

  // 提前在后台生成学习路径，学生点「学习路径」时无需等待大模型（不阻塞下面加载）
  prefetchLearningPath()

  // 加载课程
  await loadCourses()

  // 暂存的答题进度不在这里读：进入「云笺小试」时才拉取（见 activeTab 的 watch），
  // 免得每次进页面都多发一个请求、还挡住后面的聊天记录加载。

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
  content: teacherWelcome.value,
  time: nowTime(),
  }]
    }
  } catch (e) {
    chatMessages.value = [{
  id: 0,
  type: 'assistant',
  content: teacherWelcome.value,
  time: nowTime(),
  }]
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
    <aside class="course-panel" :class="{ 'is-collapsed': coursePanelCollapsed }" aria-label="课程选择">
      <div v-show="!coursePanelCollapsed" class="course-panel-header">
        <h3 class="panel-title">AI通识课程</h3>
      </div>
      <div class="course-panel-handle">
        <button class="course-panel-toggle" type="button"
                :aria-expanded="!coursePanelCollapsed" aria-controls="ai-course-list"
                :aria-label="coursePanelCollapsed ? '展开课程列表' : '收起课程列表'"
                @click="coursePanelCollapsed = !coursePanelCollapsed">
          <span aria-hidden="true">{{ coursePanelCollapsed ? '»' : '«' }}</span>
        </button>
      </div>
      <div v-show="!coursePanelCollapsed" id="ai-course-list" class="course-list">
        <div v-for="(coursesInCat, cat) in courseCategories" :key="cat" class="course-category">
          <div class="category-name">{{ cat }}</div>
          <div v-for="c in coursesInCat" :key="c.id"
               class="course-item"
               :class="{ active: selectedCourse?.id === c.id }"
               @click="selectCourse(c)">
            <div class="course-title">
              {{ c.title }}
            </div>
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
          <span class="tab-label">{{ tab.key === 'book' && grade === 'high_school' ? '在线编程' : tab.key === 'animation' && grade === 'high_school' ? '算法讲解' : tab.label }}</span>
        </button>
      </div>

      <!-- 对话 -->
      <div v-if="activeTab === 'chat'" class="tab-content chat-tab">
        <!-- 聊天管理工具栏 -->
        <div class="teacher-intro" :class="{ senior: isSeniorTeacher }">
          <img :src="teacherAvatar" :alt="teacherName" />
          <div><h3>{{ teacherName }}</h3><p>{{ teacherWelcome }}</p></div>
        </div>
        <div class="chat-toolbar">
          <span class="chat-toolbar-info" v-if="selectedTopic">
            当前专题：{{ selectedTopic }}
          </span>
          <span class="chat-toolbar-info" v-else>
            {{ teacherName }} · AI 通识课导师
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
                 :src="teacherAvatar"
                 @error="setImageFallback($event, teacherAvatar)" />
            <div class="chat-bubble-wrap">
              <span v-if="msg.type === 'assistant'" class="teacher-speaker">{{ teacherName }}</span>
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
                 :src="userStore.studentInfo.avatar || DEFAULT_STUDENT_AVATAR"
                 @error="setImageFallback($event, DEFAULT_STUDENT_AVATAR)" />
          </div>
          <div v-if="chatSending" class="chat-msg msg-ai">
            <img class="chat-avatar" :src="teacherAvatar" @error="setImageFallback($event, teacherAvatar)" />
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
          <input v-model="chatInput" type="text" :placeholder="`向${teacherName}提问，聊聊你想了解的 AI 知识...`"
                 @keyup.enter="sendChat" :disabled="chatSending" />
          <button @click="sendChat" :disabled="chatSending || !chatInput.trim()" class="send-btn">
            {{ chatSending ? '思考中...' : '发送' }}
          </button>
        </div>
      </div>

      <!-- 学习资料 -->
      <div v-if="activeTab === 'materials'" class="tab-content materials-tab">
        <div class="materials-sub-tabs">
          <button class="sub-tab-btn" :class="{ active: materialsSubTab === 'recommended' }"
            @click="materialsSubTab = 'recommended'; loadMaterials()">推荐资料</button>
          <button class="sub-tab-btn" :class="{ active: materialsSubTab === 'teacher' }"
            @click="materialsSubTab = 'teacher'; loadTeacherMaterials()">教师资料</button>
        </div>

        <!-- 推荐资料 -->
        <template v-if="materialsSubTab === 'recommended'">
          <div class="materials-header">
            <h3>推荐资料</h3>
            <p class="materials-hint" v-if="selectedTopic">
              当前专题：{{ selectedTopic }} - 点击下方资料链接进行学习
            </p>
            <p class="materials-hint" v-else>
              请先在左侧选择一个课程专题，查看对应的学习资料
            </p>
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
        </template>

        <!-- 教师资料 -->
        <template v-else>
          <div class="materials-header">
            <h3>教师资料</h3>
            <p class="materials-hint">老师为你整理的学习资料，点击即可跳转学习</p>
            <button @click="loadTeacherMaterials" :disabled="teacherMaterialsLoading" class="action-btn">
              {{ teacherMaterialsLoading ? '加载中...' : '刷新资料' }}
            </button>
          </div>

          <div v-if="teacherMaterialsLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载教师资料...</p>
          </div>

          <div v-else-if="teacherMaterials.length > 0" class="materials-list">
            <a v-for="m in teacherMaterials" :key="m.id"
               :href="m.url" target="_blank" rel="noopener"
               class="material-card">
              <div class="material-icon">{{ materialTypeIcon[m.type] || '[资料]' }}</div>
              <div class="material-info">
                <div class="material-title">{{ m.title }}</div>
                <div class="material-desc" v-if="m.description">{{ m.description }}</div>
                <div class="material-teacher">上传老师：{{ m.teacherName }} · {{ m.createdAt }}</div>
              </div>
              <span class="material-go">查看 &gt;</span>
            </a>
          </div>

          <div v-else class="empty-state">
            <div class="empty-icon">[师]</div>
            <p>老师还没有上传资料，敬请期待~</p>
          </div>
        </template>
      </div>

      <!-- 游戏化练习 -->
      <div v-if="activeTab === 'quiz'" class="tab-content quiz-tab">
        <div class="quiz-header">
          <h3>云笺小试</h3>
          <p class="quiz-hint">答对每题奖励3积分！</p>
          <p v-if="supportMessage" class="quiz-hint" role="status">{{ supportMessage }}</p>
          <p class="quiz-hint">卡住的时候可以找{{ teacherName }}一起看看，累了就先休息，进度会帮你保存到账号里，换个设备登录也能接着做。</p>
          <div class="quiz-btns">
            <button @click="askTeacherForStuck" :disabled="helpSending" class="action-btn quiz-reset-btn">卡住了</button>
            <button @click="takeRest" class="action-btn quiz-reset-btn">休息一下</button>
            <button @click="generateQuiz" :disabled="quizLoading" class="action-btn">
              {{ quizLoading ? '生成中...' : (quizStage === 'playing' ? '换一组题' : quizStage === 'finished' ? '再来一关' : '开始闯关') }}
            </button>
            <button v-if="quizStage !== 'idle'" @click="resetQuiz" :disabled="quizLoading" class="action-btn quiz-reset-btn">
              返回
            </button>
          </div>
        </div>

        <!-- 上次暂存的闯关进度 -->
        <div v-if="savedQuizProgress && quizStage === 'idle'" class="quiz-saved-tip">
          <span class="saved-tip-text">
            上次暂存了「{{ savedQuizProgress.topic || '云笺小试' }}」的进度（{{ savedProgressLabel }}）{{ savedQuizProgress.savedAt ? '· ' + savedQuizProgress.savedAt : '' }}
          </span>
          <div class="quiz-saved-actions">
            <button class="action-btn" @click="resumeQuizProgress">继续上次进度</button>
            <button class="tool-btn" @click="clearSavedQuizProgress">不用了</button>
          </div>
        </div>

        <div v-if="quizLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>正在准备题目...</p>
        </div>

        <!-- 闯关地图 -->
        <div v-else-if="quizStage === 'playing'" class="quiz-game">
          <div class="quiz-map">
            <template v-for="(q, qi) in quizQuestions" :key="qi">
              <div class="map-node" :class="{
                completed: quizAnsweredFlags[qi] && quizAnswers[qi] === q.answer,
                failed: quizAnsweredFlags[qi] && quizAnswers[qi] !== q.answer,
                current: qi === quizCurrentIdx,
                locked: qi > quizCurrentIdx,
              }">
                <div class="node-icon">
                  <span v-if="quizAnsweredFlags[qi] && quizAnswers[qi] === q.answer" class="node-check">OK</span>
                  <span v-else-if="quizAnsweredFlags[qi]" class="node-cross">X</span>
                  <span v-else-if="qi === quizCurrentIdx" class="node-current">{{ qi + 1 }}</span>
                  <span v-else class="node-num">{{ qi + 1 }}</span>
                </div>
                <div class="node-label">第{{ qi + 1 }}关</div>
              </div>
              <div v-if="qi < quizQuestions.length - 1" class="map-connector" :class="{ active: qi < quizCurrentIdx }"></div>
            </template>
            <div class="map-connector" :class="{ active: quizCurrentIdx >= quizQuestions.length - 1 && quizAnsweredFlags[quizQuestions.length - 1] }"></div>
            <div class="map-node treasure" :class="{ reached: quizCurrentIdx === quizQuestions.length - 1 && quizAnsweredFlags[quizCurrentIdx] }">
              <div class="node-icon treasure-icon">BAG</div>
              <div class="node-label">宝箱</div>
            </div>
          </div>

          <!-- 当前题目 -->
          <div class="quiz-current">
            <div class="quiz-question">
              <span class="q-num">第{{ quizCurrentIdx + 1 }}关</span>
              <span class="q-text">{{ quizQuestions[quizCurrentIdx]?.question }}</span>
            </div>
            <div class="quiz-options">
              <label v-for="(opt, oi) in quizQuestions[quizCurrentIdx]?.options" :key="oi"
                     class="quiz-option"
                     :class="{
                       selected: quizAnswers[quizCurrentIdx] === oi,
                       correct: quizFeedback !== 'none' && oi === quizQuestions[quizCurrentIdx].answer,
                       wrong: quizFeedback === 'wrong' && quizAnswers[quizCurrentIdx] === oi && oi !== quizQuestions[quizCurrentIdx].answer,
                     }">
                <input type="radio" :name="`q${quizCurrentIdx}`" :checked="quizAnswers[quizCurrentIdx] === oi"
                       @change="answerQuestion(quizCurrentIdx, Number(oi))" :disabled="quizFeedback !== 'none'" />
                <span class="opt-letter">{{ String.fromCharCode(65 + Number(oi)) }}</span>
                <span class="opt-text">{{ opt }}</span>
              </label>
            </div>

            <!-- 答题反馈 -->
            <transition name="fade">
              <div v-if="quizFeedback === 'correct'" class="quiz-feedback correct">
                <span class="feedback-icon">OK!</span>
                <span class="feedback-text">回答正确！又掌握了一个知识点！</span>
              </div>
              <div v-else-if="quizFeedback === 'wrong'" class="quiz-feedback wrong">
                <span class="feedback-icon">X</span>
                <span class="feedback-text">答错了，正确答案是 {{ String.fromCharCode(65 + quizQuestions[quizCurrentIdx].answer) }}</span>
              </div>
            </transition>

            <!-- 解析 -->
            <div v-if="quizFeedback !== 'none'" class="quiz-explanation">
              <span class="expl-label">解析：</span>{{ quizQuestions[quizCurrentIdx]?.explanation }}
            </div>
          </div>
        </div>

        <!-- 闯关结果 -->
        <div v-else-if="quizStage === 'finished'" class="quiz-victory">
          <div class="treasure-open">
            <div class="treasure-emoji">BAG</div>
            <p class="treasure-text">宝箱已打开！</p>
          </div>
          <div class="quiz-result">
            <div class="result-score">
              <span class="score-num">{{ quizResult?.score }}</span>
              <span class="score-unit">分</span>
            </div>
            <div class="result-detail">
              答对 {{ quizResult?.correct }} / {{ quizResult?.total }} 题
            </div>
            <div v-if="quizResult?.correct === quizResult?.total" class="perfect-bonus">
              完美通关！额外奖励5积分！
            </div>
            <div class="reward-info">
              获得积分：+{{ (quizResult?.correct || 0) * 3 + (quizResult?.correct === quizResult?.total ? 5 : 0) }}
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <p v-if="!savedQuizProgress">还没有题目，点上面的「开始闯关」就会出几道小题。</p>
        </div>
      </div>

      <!-- 动画讲解（内置视频） -->
      <div v-if="activeTab === 'animation'" class="tab-content animation-tab"
           :class="{ 'algorithm-mode': !!algorithmLesson || isDeepLearningLesson, 'deep-learning-mode': isDeepLearningLesson }">
        <DeepLearningLesson v-if="isDeepLearningLesson" :key="selectedCourse?.id" />
        <div v-else-if="algorithmLesson" class="algorithm-lesson">
          <!-- 首页：在一屏内展示该课程的全部公式 -->
          <div v-if="!selectedAlgorithmConcept" class="algorithm-overview">
            <div class="algorithm-lesson-head algorithm-lesson-head--compact">
              <div>
                <span class="algorithm-view-tag">公式总览</span>
                <h3>{{ algorithmLesson.title }}</h3>
                <p>{{ algorithmLesson.intro }}</p>
              </div>
            </div>
            <div class="algorithm-overview-grid"
                 :class="{
                   'algorithm-overview-grid--five': algorithmLesson.concepts.length > 4,
                   'algorithm-overview-grid--project': selectedCourse?.title === 'AI项目实践',
                 }">
              <button v-for="(concept, index) in algorithmLesson.concepts" :key="concept.title"
                      class="algorithm-overview-card" @click="openAlgorithmConcept(index)">
                <div class="algorithm-overview-number">{{ String(index + 1).padStart(2, '0') }}</div>
                <h4>{{ concept.title }}</h4>
                <code>{{ concept.formula }}</code>
                <span class="algorithm-open-hint">点击查看详细讲解 →</span>
              </button>
            </div>
          </div>

          <!-- 详情：同一屏内按内容分页 -->
          <div v-else class="algorithm-detail">
            <div class="algorithm-detail-toolbar">
              <button class="algorithm-back-btn" @click="closeAlgorithmConcept">← 返回全部公式</button>
              <span>公式 {{ (selectedAlgorithmConceptIndex ?? 0) + 1 }} / {{ algorithmLesson.concepts.length }}</span>
            </div>

            <div class="algorithm-detail-head">
              <div>
                <span class="algorithm-view-tag">{{ algorithmPageLabels[algorithmDetailPage] }}</span>
                <h3>{{ selectedAlgorithmConcept.title }}</h3>
              </div>
              <div class="algorithm-detail-formula">
                <span>公式</span>
                <code>{{ selectedAlgorithmConcept.formula }}</code>
              </div>
            </div>

            <div class="algorithm-detail-page">
              <template v-if="algorithmDetailPage === 0">
                <section class="algorithm-page-panel algorithm-page-panel--foundation">
                  <strong>零基础先读</strong>
                  <p>{{ algorithmLesson.foundation }}</p>
                </section>
                <div class="algorithm-page-columns algorithm-page-columns--intro"
                     :class="{ 'algorithm-page-columns--long-guide': selectedCourse?.title === 'AI项目实践' }">
                  <section class="algorithm-page-panel algorithm-page-panel--formula-guide">
                    <strong>公式怎么读</strong>
                    <p>{{ selectedAlgorithmConcept.formulaGuide }}</p>
                  </section>
                  <section class="algorithm-page-panel algorithm-page-panel--principle">
                    <strong>原理拆解</strong>
                    <p>{{ selectedAlgorithmConcept.principle }}</p>
                  </section>
                </div>
              </template>

              <template v-else-if="algorithmDetailPage === 1">
                <section class="algorithm-page-panel algorithm-page-panel--steps">
                  <strong>按顺序理解这个知识点</strong>
                  <ol>
                    <li v-for="(step, index) in selectedAlgorithmConcept.steps" :key="step">
                      <span>{{ index + 1 }}</span>
                      <p>{{ step }}</p>
                    </li>
                  </ol>
                </section>
              </template>

              <template v-else-if="algorithmDetailPage === 2">
                <div class="algorithm-page-columns algorithm-page-columns--example">
                  <section class="algorithm-page-panel algorithm-page-panel--example">
                    <strong>算一个简单例子</strong>
                    <p>{{ selectedAlgorithmConcept.example }}</p>
                  </section>
                  <section v-if="selectedAlgorithmConcept.note"
                           class="algorithm-page-panel algorithm-page-panel--note">
                    <strong>容易忽略的注意点</strong>
                    <p>{{ selectedAlgorithmConcept.note }}</p>
                  </section>
                </div>
                <section class="algorithm-page-panel algorithm-page-panel--goals">
                  <strong>本课程的学习目标</strong>
                  <ul>
                    <li v-for="goal in algorithmLesson.goals" :key="goal">{{ goal }}</li>
                  </ul>
                </section>
              </template>

              <template v-else>
                <section class="algorithm-page-panel algorithm-page-panel--application-lead">
                  <strong>这个公式能解决什么问题</strong>
                  <p>{{ selectedAlgorithmConcept.application?.question }}</p>
                </section>
                <div class="algorithm-page-columns algorithm-page-columns--application">
                  <section class="algorithm-page-panel algorithm-page-panel--application-steps">
                    <strong>在项目中怎么用</strong>
                    <ol>
                      <li v-for="step in selectedAlgorithmConcept.application?.steps" :key="step">
                        {{ step }}
                      </li>
                    </ol>
                  </section>
                  <section class="algorithm-page-panel algorithm-page-panel--application-decision">
                    <strong>根据结果做什么决定</strong>
                    <p>{{ selectedAlgorithmConcept.application?.decision }}</p>
                  </section>
                </div>
              </template>
            </div>

            <div class="lesson-pagination">
              <button @click="turnAlgorithmPage(-1)" :disabled="algorithmDetailPage === 0">上一页</button>
              <div class="lesson-page-dots">
                <button v-for="(label, index) in algorithmPageLabels" :key="label"
                        :class="{ active: algorithmDetailPage === index }"
                        @click="algorithmDetailPage = index" :aria-label="label"></button>
              </div>
              <span aria-live="polite">{{ algorithmDetailPage + 1 }} / {{ algorithmPageLabels.length }}</span>
              <button class="lesson-next" @click="turnAlgorithmPage(1)"
                      :disabled="algorithmDetailPage === algorithmPageLabels.length - 1">下一页</button>
            </div>
          </div>
        </div>

        <div v-else-if="builtinVideo" class="anim-result anim-result--video">
          <h4 class="anim-title">{{ builtinVideo.title }}</h4>
          <div class="video-embed-container">
            <iframe
              :src="`https://player.bilibili.com/player.html?bvid=${builtinVideo.bvid}&autoplay=0&high_quality=1&danmaku=0`"
              scrolling="no" border="0" frameborder="no" framespacing="0"
              allowfullscreen="true"
            ></iframe>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">[视频]</div>
          <p>该课程暂未配置视频，敬请期待！</p>
        </div>
      </div>

      <!-- 故事绘本 -->
      <div v-if="activeTab === 'book' && grade === 'high_school'" class="tab-content programming-tab">
        <OnlineProgrammingLesson v-if="selectedCourse" :key="selectedCourse.id" :course-title="selectedCourse.title" />
        <div v-else class="empty-state"><p>请在左侧选择课程，开始在线编程练习。</p></div>
      </div>
      <div v-if="activeTab === 'book' && grade !== 'high_school'" class="tab-content book-tab">
        <div class="book-layout">
          <!-- 主播放区 -->
          <div class="book-main">
            <div v-if="bookLoading" class="loading-state">
              <div class="loading-spinner"></div>
              <p>正在加载绘本...</p>
            </div>

            <template v-else-if="bookData">
              <div class="book-result">
                <div class="book-head-row">
                  <h4 class="book-title">{{ bookData.title }}</h4>
                  <button class="book-fav-main" :class="{ active: bookFav }" @click="toggleCurrentFav"
                          :title="bookFav ? '取消收藏' : '收藏'" :disabled="!bookRecordId">
                    {{ bookFav ? '\u2605 已收藏' : '\u2606 收藏' }}
                  </button>
                </div>
                <div class="book-page-display">
                  <div class="book-page" v-if="bookData.pages[bookPage]">
                    <div class="book-svg" v-if="bookData.pages[bookPage].img">
                      <img class="book-photo" :src="bookData.pages[bookPage].img" :alt="bookData.pages[bookPage].text" />
                    </div>
                    <div class="book-svg" v-else v-html="bookData.pages[bookPage].svg"></div>
                    <p class="book-text" v-if="bookData.pages[bookPage].text">{{ bookData.pages[bookPage].text }}</p>
                  </div>
                  <div class="book-nav">
                    <button @click="prevBookPage" :disabled="bookPage === 0" class="nav-btn">上一页</button>
                    <span class="page-info">{{ bookPage + 1 }} / {{ bookData.pages.length }}</span>
                    <button @click="nextBookPage" :disabled="bookPage >= bookData.pages.length - 1" class="nav-btn">下一页</button>
                  </div>
                </div>
              </div>
            </template>

            <div v-else class="empty-state">
              <div class="empty-icon">[绘本]</div>
              <p>选择一个课程主题，绘本将自动播放！</p>
            </div>
          </div>

          <!-- 收藏侧边栏 -->
          <aside class="book-fav-panel">
            <h4 class="fav-panel-title">我的收藏</h4>
            <div v-if="favBooks.length > 0" class="fav-book-list">
              <div v-for="b in favBooks" :key="b.id" class="fav-book-item" @click="viewFavoriteBook(b)">
                <span class="fav-book-star">&#9733;</span>
                <div class="fav-book-info">
                  <span class="fav-book-title">{{ b.title }}</span>
                  <span class="fav-book-topic">{{ b.topic }}</span>
                </div>
              </div>
            </div>
            <div v-else class="fav-panel-empty">还没有收藏的绘本<br />播放时点击收藏即可</div>
          </aside>
        </div>
      </div>

      <!-- 学习路径 -->
      <div v-if="activeTab === 'path'" class="tab-content path-tab">
        <div class="path-header">
          <div class="path-title-wrap">
            <h3>个性化学习路径</h3>
            <p class="path-sub">
              {{ learningPath ? learningPath.gradeName + '课程 · 按顺序逐项攻克' : 'AI 正在结合你的学习记录生成建议' }}
            </p>
          </div>
        </div>

        <div v-if="pathLoading && !learningPath" class="loading-state">
          <div class="loading-spinner"></div>
          <p>AI正在分析你的学习情况...</p>
        </div>

        <div v-else-if="learningPath" class="path-content">
          <!-- 总体进度条：一眼看到离走完全程还有多远 -->
          <div class="path-overall">
            <div class="overall-row">
              <span class="overall-label">学习进度</span>
              <span class="overall-value">
                {{ pathSummary.masteredCount || 0 }} / {{ pathSummary.courseTotal || 0 }} 已掌握
                （{{ pathSummary.progressPercent || 0 }}%）
              </span>
            </div>
            <div class="overall-bar">
              <span :style="{ width: (pathSummary.progressPercent || 0) + '%' }"></span>
            </div>
            <p class="overall-hint">
              小测拿一次满分（或编程题全部通过）就能点亮一门课<template v-if="pathSummary.reviewCount">，还有 {{ pathSummary.reviewCount }} 门需要补一补</template>。
            </p>
          </div>

          <!-- 学习概览 -->
          <div class="path-info">
            <div class="info-card">
              <span class="info-label">当前年级</span>
              <span class="info-value">{{ learningPath.gradeName }}</span>
              <span class="info-extra">共 {{ pathSummary.courseTotal || 0 }} 个知识点</span>
            </div>
            <div class="info-card">
              <span class="info-label">课程进度</span>
              <span class="info-value">{{ pathSummary.masteredCount || 0 }} / {{ pathSummary.courseTotal || 0 }}</span>
              <span class="info-extra">
                学习中 {{ pathSummary.learningCount || 0 }} · 未开始 {{ pathSummary.todoCount || 0 }}
              </span>
            </div>
            <div class="info-card">
              <span class="info-label">测验平均分</span>
              <span class="info-value">{{ pathSummary.quizCount ? pathSummary.quizAvg + ' 分' : '暂无' }}</span>
              <span class="info-extra">共 {{ pathSummary.quizCount || 0 }} 次 · 最高 {{ pathSummary.quizBest || 0 }} 分</span>
            </div>
            <div class="info-card">
              <span class="info-label">学习记录</span>
              <span class="info-value">{{ pathSummary.recordCount || 0 }} 条</span>
              <span class="info-extra">覆盖 {{ pathSummary.learningCount || 0 }} 个知识点</span>
            </div>
            <div class="info-card">
              <span class="info-label">学习天数</span>
              <span class="info-value">{{ pathSummary.studyDays || 0 }} 天</span>
              <span class="info-extra">
                {{ pathSummary.streakDays > 1
                    ? '已连续 ' + pathSummary.streakDays + ' 天'
                    : (pathSummary.lastActive ? '最近学习 ' + pathSummary.lastActive : '还没有学习记录') }}
              </span>
            </div>
            <div class="info-card">
              <span class="info-label">最近成绩</span>
              <span class="info-value">{{ recentScoresText }}</span>
              <span class="info-extra">按时间倒序 · 最多 3 次</span>
            </div>
          </div>

          <!-- 建议下一步 -->
          <div v-if="pathNode" class="path-focus" @click="openTopicInChat(pathNode.title, pathNode.id)">
            <div class="focus-main">
              <span class="focus-label">建议下一步</span>
              <span class="focus-topic">
                {{ pathNode.title }}
                <span v-if="pathNode.selfRatedHard" class="node-hard-tag">你觉得偏难</span>
              </span>
              <span class="focus-meta">
                {{ pathNode.category }} · {{ difficultyText(pathNode.difficulty) }}
                <template v-if="pathNode.studyCount"> · 已学习 {{ pathNode.studyCount }} 次</template>
              </span>
              <span v-if="pathNode.reason" class="focus-reason">{{ pathNode.reason }}</span>
            </div>
            <button class="focus-btn">{{ actionText(pathNode.status) }}</button>
          </div>

          <!-- 学习路线图 -->
          <div class="path-section">
            <div class="section-head">
              <h4>学习路线图</h4>
              <span class="section-hint">按课程顺序推进，点击知识点可进入 AI 对话</span>
            </div>
            <div v-if="learningPath.roadmap?.length" class="roadmap">
              <div v-for="(n, i) in learningPath.roadmap" :key="n.id"
                   class="road-node" :class="n.status"
                   @click="openTopicInChat(n.title, n.id)">
                <div class="node-index">{{ n.status === 'mastered' ? '✓' : String(Number(i) + 1).padStart(2, '0') }}</div>
                <div class="node-body">
                  <div class="node-title-row">
                    <span class="node-title">{{ n.title }}</span>
                    <span v-if="n.selfRatedHard" class="node-hard-tag">你觉得偏难</span>
                    <span class="node-status" :class="n.status">{{ statusText(n.status) }}</span>
                  </div>
                  <div class="node-meta">
                    <span class="node-cat">{{ n.category }}</span>
                    <span class="node-diff" :class="n.difficulty">{{ difficultyText(n.difficulty) }}</span>
                    <span v-if="n.studyCount" class="node-stat">学习 {{ n.studyCount }} 次</span>
                    <span v-if="n.bestScore" class="node-stat">最好 {{ n.bestScore }} 分</span>
                    <span v-if="n.lastTime" class="node-time">最近 {{ n.lastTime }}</span>
                  </div>
                  <!-- 距离掌握还差什么：把状态机的终点讲明白 -->
                  <div class="node-progress">
                    <div class="node-bar"><span :style="{ width: (n.progress || 0) + '%' }"></span></div>
                    <span class="node-hint">{{ n.hint }}</span>
                  </div>
                </div>
                <span class="node-action">{{ actionText(n.status) }}</span>
              </div>
            </div>
            <p v-else class="path-empty-line">本学段暂未配置课程内容。</p>
          </div>

          <!-- 已掌握知识点 -->
          <div class="path-section">
            <div class="section-head">
              <h4>已掌握知识点</h4>
              <span class="section-hint">{{ learningPath.learnedTopics?.length || 0 }} 个 · 小测满分或编程全过即点亮</span>
            </div>
            <div v-if="learningPath.learnedTopics?.length" class="topic-tags">
              <span v-for="t in learningPath.learnedTopics" :key="t" class="learned-tag">{{ t }}</span>
            </div>
            <p v-else class="path-empty-line">还没有达到「已掌握」的知识点，把测验做到满分就可以点亮它。</p>
          </div>

          <!-- AI 推荐 -->
          <div v-if="learningPath.suggestions?.length" class="path-section">
            <div class="section-head">
              <h4>AI 推荐下一步学习</h4>
              <span class="section-hint">点击卡片直接进入 AI 对话</span>
            </div>
            <div class="suggestions">
              <div v-for="(s, i) in learningPath.suggestions" :key="i" class="suggestion-card"
                   @click="openTopicInChat(s.topic, s.courseId)">
                <div class="sug-header">
                  <span class="sug-num">{{ Number(i) + 1 }}</span>
                  <span class="sug-topic">{{ s.topic }}</span>
                  <span class="sug-difficulty" :class="s.difficulty">
                    {{ s.difficulty === 'easy' ? '入门' : s.difficulty === 'medium' ? '进阶' : '挑战' }}
                  </span>
                </div>
                <p class="sug-reason">{{ s.reason }}</p>
                <span class="sug-hint">
                  {{ actionText(s.status) }} &gt;&gt;
                  <template v-if="s.status === 'learning'">（已学一半）</template>
                  <template v-else-if="s.status === 'mastered'">（巩固复习）</template>
                </span>
              </div>
            </div>
          </div>

          <!-- 学习方式分布 + 需要复习 -->
          <div class="path-columns">
            <div class="path-section">
              <div class="section-head"><h4>学习方式分布</h4></div>
              <div v-if="learningPath.typeBreakdown?.length" class="type-list">
                <div v-for="t in learningPath.typeBreakdown" :key="t.key" class="type-row">
                  <span class="type-name">{{ t.label }}</span>
                  <div class="type-bar"><span :style="{ width: typeBarWidth(t.count) }"></span></div>
                  <span class="type-count">{{ t.count }} 次</span>
                </div>
              </div>
              <p v-else class="path-empty-line">还没有学习记录。</p>
              <div class="type-extra">
                <span>生成绘本 {{ pathSummary.bookMade || 0 }} 本</span>
                <span>编程通过 {{ pathSummary.programmingDone || 0 }} 题</span>
              </div>
            </div>

            <div class="path-section">
              <div class="section-head">
                <h4>需要复习</h4>
                <span class="section-hint">小测未满分 / 自评偏难</span>
              </div>
              <div v-if="learningPath.weakTopics?.length" class="weak-list">
                <div v-for="w in learningPath.weakTopics" :key="w.topic" class="weak-item">
                  <span class="weak-topic">{{ w.topic }}</span>
                  <span v-if="w.fromRating && !w.bestScore" class="weak-rated">自评偏难</span>
                  <span v-else class="weak-score">{{ w.bestScore }} 分</span>
                  <span class="weak-time">{{ w.lastTime }}</span>
                </div>
              </div>
              <p v-else class="path-empty-line">暂无需要复习的知识点。</p>
            </div>
          </div>

          <!-- 最近学习动态 -->
          <div class="path-section">
            <div class="section-head">
              <h4>最近学习动态</h4>
              <span class="section-hint">最近 8 条学习记录</span>
            </div>
            <div v-if="learningPath.activity?.length" class="activity-list">
              <div v-for="(a, i) in learningPath.activity" :key="i" class="activity-item">
                <span class="act-type" :class="a.type">{{ a.typeLabel }}</span>
                <span class="act-topic">{{ a.topic }}</span>
                <span v-if="a.type === 'quiz' && a.score" class="act-score">{{ a.score }} 分</span>
                <span class="act-time">{{ a.time }}</span>
              </div>
            </div>
            <p v-else class="path-empty-line">还没有学习记录，从上面路线图的第一个知识点开始吧。</p>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">[路径]</div>
          <p>学习路径正在生成中，稍后会自动重试。</p>
        </div>
      </div>
    </div>
  </div>

  <!-- 难题反馈弹窗：请教过老师之后，学生做完这题评价难度 -->
  <div v-if="ratingOpen" class="rate-mask">
    <div class="rate-dialog">
      <div class="rate-illustration">🌟</div>
      <h4 class="rate-title">这道题感觉怎么样？</h4>
      <p class="rate-guide">滑动星星告诉我们难度吧</p>
      <div class="rate-stars-bar">
        <span class="rate-extreme">很简单</span>
        <div class="rate-stars">
          <button v-for="n in 5" :key="n" class="star-btn" :class="{ on: n <= ratingStars }"
                  :aria-label="`${n} 星`" @click="ratingStars = n">
            {{ n <= ratingStars ? '★' : '☆' }}
          </button>
        </div>
        <span class="rate-extreme">非常难</span>
      </div>
      <p v-if="ratingStarText" class="rate-star-text">{{ ratingStarText }}</p>
      <div class="rate-tags">
        <button v-for="t in rateTagOptions" :key="t" class="rate-tag"
                :class="{ on: ratingTags.includes(t) }" @click="toggleRateTag(t)">{{ t }}</button>
      </div>
      <div class="rate-actions">
        <button class="action-btn" :disabled="!ratingStars" @click="submitRating">提交</button>
        <button class="tool-btn" @click="closeRating">先跳过</button>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.teacher-intro { display: flex; align-items: center; gap: 18px; padding: 18px 22px; background: #fff8e8; border-bottom: 1px solid #eee3c8; }
.teacher-intro.senior { background: #eef6fa; border-color: #dbe8f0; }
.teacher-intro img { width: 82px; height: 82px; border-radius: 20px; object-fit: cover; flex-shrink: 0; }
.teacher-intro h3 { margin: 0 0 8px; font-size: 19px; color: #444; }
.teacher-intro small { display: inline-block; font-size: 11px; font-weight: normal; color: #777; margin-left: 6px; }
.teacher-intro p { margin: 0; font-size: 13px; line-height: 1.7; color: #666; }
.teacher-speaker { display: block; margin-bottom: 5px; font-size: 12px; color: #786a9a; }

.ai-learning-page {
  height: 100%;
  flex: 1;
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
  flex-shrink: 0;
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
  position: relative;
  display: flex; flex-direction: column; min-height: 0;
  overflow: visible;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
}
.course-panel.is-collapsed { width: 8px; padding: 0; }
.course-panel .course-list { flex: 1; min-height: 0; overflow-y: auto; }
.course-panel-handle {
  position: absolute; right: -12px; top: 0; bottom: 0;
  width: 28px; z-index: 5; display: flex; align-items: center; justify-content: center;
}
.course-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  gap: 8px; margin-bottom: 12px;
}
.panel-title { font-size: 16px; color: #333; margin: 0; font-weight: 600; }
.course-panel-toggle {
  display: flex; align-items: center; justify-content: center;
  width: 24px; height: 52px; padding: 0; border: none;
  background: transparent; color: #97551e;
  cursor: pointer; transform: translateY(-60px);
}
.course-panel-toggle > span { font-size: 28px; line-height: 1; }
.course-panel-toggle:hover { color: #d97716; }
.course-panel-toggle:focus-visible { outline: 2px solid #b56820; outline-offset: 2px; }
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
  background: #fafafa; border-bottom: 1px solid #eee; flex-shrink: 0;
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
.tab-content { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.chat-tab { display: flex; flex-direction: column; height: 100%; overflow: hidden; }

/* 聊天管理工具栏 */
.chat-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 16px; background: #fff8e1; border-bottom: 1px solid #ffe0b2;
  flex-shrink: 0;
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
.chat-bubble-wrap { position: relative; max-width: 85%; }
.bubble-footer { display: flex; gap: 6px; justify-content: flex-end; margin-top: 4px; }
.msg-ai .bubble-footer { justify-content: flex-start; }
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
.quick-questions { display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 16px; border-top: 1px solid #eee; flex-shrink: 0; }
.quick-q-btn {
  padding: 6px 14px; background: #f5f5f5; border: none; border-radius: 16px;
  font-size: 12px; color: #666; cursor: pointer; transition: all 0.2s;
}
.quick-q-btn:hover { background: #ffb74d; color: white; }
.chat-input-area { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid #eee; background: white; flex-shrink: 0; }
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
.materials-sub-tabs {
  display: flex; gap: 8px; justify-content: center; margin-bottom: 16px;
  border-bottom: 2px solid #eee; padding-bottom: 8px;
}
.sub-tab-btn {
  padding: 6px 20px; border: none; background: none; cursor: pointer;
  font-size: 14px; color: #888; border-radius: 20px; transition: all 0.2s;
}
.sub-tab-btn:hover { color: #ff9800; background: #fff3e0; }
.sub-tab-btn.active { color: #fff; background: #ff9800; font-weight: 600; }
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
.material-teacher { font-size: 11px; color: #aaa; margin-top: 4px; }
.material-go { font-size: 13px; color: #ffb74d; font-weight: 500; flex-shrink: 0; }

/* 练习 */
.quiz-tab { padding: 20px; overflow-y: auto; }
.quiz-header { text-align: center; margin-bottom: 20px; }
.quiz-header h3 { font-size: 20px; color: #333; margin-bottom: 8px; }
.quiz-btns { display: flex; gap: 10px; justify-content: center; }
.quiz-reset-btn { background: #fff !important; color: #888 !important; border: 1px solid #ddd !important; }
.quiz-reset-btn:hover { border-color: #bbb !important; color: #555 !important; }
.quiz-hint { font-size: 13px; color: #888; margin-bottom: 12px; }
/* 上次暂存的闯关进度 */
.quiz-saved-tip {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 16px;
  max-width: 680px; margin: 0 auto 20px; padding: 32px 28px;
  background: #fff8e1; border: 1px solid #ffe0a3; border-radius: 16px;
  font-size: 15px; color: #8a6d3b;
  min-height: 100px;
}
.saved-tip-text { line-height: 1.7; font-size: 15px; }
.quiz-saved-actions { display: flex; gap: 12px; }
.quiz-saved-actions .action-btn,
.quiz-saved-actions .tool-btn { padding: 12px 24px; font-size: 14px; }

/* 难题反馈弹窗 */
.rate-mask {
  position: fixed; inset: 0; background: rgba(0, 0, 0, .45);
  display: flex; align-items: center; justify-content: center;
  z-index: 3000; padding: 20px;
}
.rate-dialog {
  width: 100%; max-width: 420px; background: #fff; border-radius: 20px;
  padding: 26px 22px 22px; text-align: center;
  box-shadow: 0 16px 48px rgba(0, 0, 0, .2);
}
.rate-illustration {
  width: 56px; height: 56px; margin: 0 auto 12px;
  background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 26px;
}
.rate-title { font-size: 19px; color: #333; margin: 0 0 6px; font-weight: 600; }
.rate-guide { font-size: 13px; color: #999; margin: 0 0 18px; }
.rate-stars-bar {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  margin-bottom: 8px;
}
.rate-extreme {
  font-size: 12px; color: #bbb; font-weight: 500; white-space: nowrap;
}
.rate-stars { display: flex; align-items: center; justify-content: center; gap: 6px; }
.star-btn {
  background: none; border: none; cursor: pointer; padding: 2px;
  font-size: 32px; line-height: 1; color: #e5e5e5; transition: transform .15s, color .15s;
}
.star-btn.on { color: #ffb400; }
.star-btn:hover { transform: scale(1.14); }
.rate-star-text { font-size: 13px; font-weight: 600; color: #ff9800; margin: 4px 0 16px; min-height: 19px; }
.rate-tags { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 20px; }
.rate-tag {
  font-size: 13px; color: #666; background: #f7f7f7; border: 1px solid #e8e8e8;
  border-radius: 999px; padding: 7px 14px; cursor: pointer; transition: all .15s;
}
.rate-tag:hover { border-color: #ffd08a; color: #e08a00; background: #fff8ef; }
.rate-tag.on { background: #fff3e0; border-color: #ffb74d; color: #e08a00; font-weight: 600; }
.rate-actions { display: flex; gap: 10px; justify-content: center; }
.rate-actions .action-btn,
.rate-actions .tool-btn { padding: 8px 22px; font-size: 14px; border-radius: 999px; }
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

/* 闯关地图 */
.quiz-game { display: flex; flex-direction: column; gap: 20px; max-width: 700px; margin: 0 auto; }
.quiz-map {
  display: flex; align-items: center; justify-content: center;
  padding: 20px 12px; background: linear-gradient(135deg, #fff8e1, #fff3e0);
  border-radius: 16px; gap: 0;
}
.map-node {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  flex-shrink: 0; position: relative; transition: all 0.3s;
}
.node-icon {
  width: 48px; height: 48px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: bold; transition: all 0.3s;
  background: #e0e0e0; color: #999; border: 3px solid #bdbdbd;
}
.map-node.current .node-icon {
  background: #ffb74d; color: white; border-color: #ff9800;
  box-shadow: 0 0 12px rgba(255, 152, 0, 0.5); animation: nodePulse 1.5s ease-in-out infinite;
}
.map-node.completed .node-icon { background: #4caf50; color: white; border-color: #388e3c; }
.map-node.failed .node-icon { background: #f44336; color: white; border-color: #c62828; }
.map-node.locked .node-icon { background: #eee; color: #ccc; border-color: #ddd; }
.map-node.treasure .node-icon {
  width: 56px; height: 56px; font-size: 14px;
  background: linear-gradient(135deg, #ffd700, #ffa500); color: #fff;
  border-color: #ff9800;
}
.map-node.treasure.reached .node-icon {
  animation: treasureBounce 0.6s ease-in-out; background: linear-gradient(135deg, #ffd700, #ff6f00);
}
.node-label { font-size: 11px; color: #888; }
.map-node.current .node-label { color: #ff9800; font-weight: 600; }
.map-node.completed .node-label { color: #4caf50; font-weight: 600; }
.map-connector {
  width: 32px; height: 4px; background: #e0e0e0; border-radius: 2px;
  transition: background 0.3s; flex-shrink: 0;
}
.map-connector.active { background: #4caf50; }
.node-check, .node-cross { font-size: 14px; }
.node-current { font-size: 18px; }

@keyframes nodePulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
@keyframes treasureBounce {
  0%, 100% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(1.2) rotate(-5deg); }
  75% { transform: scale(1.2) rotate(5deg); }
}

.quiz-current {
  background: #fafafa; border-radius: 12px; padding: 20px;
  border: 2px solid #ffe0b2;
}
.quiz-feedback {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: 10px; margin-top: 12px;
  animation: feedbackSlide 0.3s ease-out;
}
.quiz-feedback.correct { background: #e8f5e9; }
.quiz-feedback.correct .feedback-icon {
  color: #4caf50; font-size: 20px; font-weight: bold;
}
.quiz-feedback.wrong { background: #ffebee; }
.quiz-feedback.wrong .feedback-icon {
  color: #f44336; font-size: 20px; font-weight: bold;
}
.feedback-text { font-size: 14px; color: #333; }
@keyframes feedbackSlide { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }

/* 闯关结果 */
.quiz-victory {
  text-align: center; padding: 30px 20px; max-width: 500px; margin: 0 auto;
}
.treasure-open { margin-bottom: 20px; }
.treasure-emoji {
  width: 80px; height: 80px; margin: 0 auto 8px;
  background: linear-gradient(135deg, #ffd700, #ff6f00);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: bold; color: white;
  animation: treasureBounce 0.8s ease-in-out;
}
.treasure-text { font-size: 16px; color: #ff9800; font-weight: 600; }
.perfect-bonus {
  margin-top: 8px; padding: 6px 14px; display: inline-block;
  background: linear-gradient(135deg, #ffd700, #ffa500); color: white;
  border-radius: 20px; font-size: 13px; font-weight: 600;
}
.reward-info {
  margin-top: 8px; font-size: 15px; color: #4caf50; font-weight: 600;
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* 动画 */
.animation-tab { padding: 20px; overflow-y: auto; }
.anim-result { max-width: 800px; margin: 0 auto; }
.anim-result--video { max-width: 100%; width: 100%; margin: 0; }
.anim-title { font-size: 18px; color: #333; text-align: center; margin-bottom: 12px; }
.video-embed-container {
  position: relative; width: 100%;
  aspect-ratio: 16 / 9; border-radius: 12px; overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1); background: #000;
}
.video-embed-container iframe {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;
}
.animation-tab.algorithm-mode { padding: 16px; overflow: hidden; }
.animation-tab.algorithm-mode.deep-learning-mode { overflow-y: auto; }
.algorithm-lesson { width: 100%; max-width: 1180px; height: 100%; min-height: 0; margin: 0 auto; }
.algorithm-overview, .algorithm-detail {
  height: 100%; min-height: 0; display: flex; flex-direction: column;
}
.algorithm-lesson-head {
  padding: 18px 22px; border-radius: 12px;
  background: linear-gradient(135deg, #fff8e8, #fffdf8); border: 1px solid #ffe0a6;
}
.algorithm-lesson-head--compact { flex-shrink: 0; margin-bottom: 12px; }
.algorithm-lesson-head h3 { margin: 5px 0 5px; color: #7a5428; font-size: clamp(18px, 1.6vw, 22px); }
.algorithm-lesson-head p {
  margin: 0; color: #6f655b; font-size: 14px; line-height: 1.55;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.algorithm-view-tag {
  display: inline-block; padding: 3px 9px; border-radius: 10px;
  background: #ffb74d; color: #fff; font-size: 11px; font-weight: 600;
}
.algorithm-overview-grid {
  flex: 1; min-height: 0; display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr)); gap: 12px;
}
.algorithm-overview-grid--five {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr)); gap: 8px;
}
.algorithm-overview-grid--five .algorithm-overview-card { padding: 10px 12px; }
.algorithm-overview-grid--five .algorithm-overview-number { font-size: 10px; }
.algorithm-overview-grid--five .algorithm-overview-card h4 {
  margin: 2px 0 5px; font-size: 13px; line-height: 1.25;
}
.algorithm-overview-grid--five .algorithm-overview-card code {
  padding: 6px 8px; font-size: 11px; line-height: 1.3;
}
.algorithm-overview-grid--five .algorithm-open-hint { margin-top: 3px; font-size: 10px; }
.algorithm-overview-grid--project .algorithm-overview-card h4 {
  font-size: clamp(14px, 1.15vw, 15px); line-height: 1.3;
}
.algorithm-overview-grid--project .algorithm-overview-card code {
  font-size: clamp(12px, 1.02vw, 13px); line-height: 1.38;
}
.algorithm-overview-card {
  min-width: 0; min-height: 0; display: flex; flex-direction: column;
  padding: clamp(14px, 1.5vw, 21px); text-align: left; cursor: pointer;
  border: 1px solid #e9e0d7; border-radius: 12px; background: #fff;
  box-shadow: 0 3px 12px rgba(99, 72, 42, 0.06); transition: all 0.2s;
}
.algorithm-overview-card:hover {
  border-color: #ffb74d; background: #fffdf8; transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(99, 72, 42, 0.12);
}
.algorithm-overview-number { color: #c7b7a7; font-size: 12px; font-weight: 700; }
.algorithm-overview-card h4 {
  margin: 5px 0 10px; color: #4d443c; font-size: clamp(15px, 1.25vw, 18px);
  line-height: 1.35;
}
.algorithm-overview-card code {
  flex: 1; display: flex; align-items: center; width: 100%; padding: 10px 12px;
  border-radius: 8px; background: #f7f4ff; color: #44366d;
  font-family: "Cambria Math", "Times New Roman", serif;
  font-size: clamp(13px, 1.15vw, 16px); line-height: 1.55;
  white-space: pre-line; overflow-wrap: anywhere;
}
.algorithm-open-hint { margin-top: 9px; color: #d5892f; font-size: 12px; font-weight: 600; }
.algorithm-detail-toolbar {
  flex-shrink: 0; display: flex; justify-content: space-between; align-items: center;
  min-height: 30px; margin-bottom: 8px; color: #9a8f84; font-size: 12px;
}
.algorithm-back-btn {
  padding: 5px 11px; border: 1px solid #e7d7c5; border-radius: 14px;
  background: #fff; color: #a76a28; cursor: pointer; font-size: 12px;
}
.algorithm-back-btn:hover { background: #fff8e9; border-color: #ffb74d; }
.algorithm-detail-head {
  flex-shrink: 0; display: grid; grid-template-columns: minmax(230px, 0.8fr) minmax(0, 1.2fr);
  gap: 16px; align-items: center; padding: 14px 18px; margin-bottom: 10px;
  border-radius: 12px; background: linear-gradient(135deg, #fff8e8, #fffdf8);
  border: 1px solid #ffe0a6;
}
.algorithm-detail-head h3 { margin: 6px 0 0; color: #5a4632; font-size: clamp(18px, 1.5vw, 22px); }
.algorithm-detail-formula {
  min-width: 0; display: flex; align-items: center; gap: 10px;
  padding: 11px 13px; border-radius: 8px; background: #f7f4ff;
}
.algorithm-detail-formula span {
  flex-shrink: 0; padding: 2px 7px; border-radius: 4px;
  background: #8d79c5; color: #fff; font-size: 11px;
}
.algorithm-detail-formula code {
  color: #44366d; font-family: "Cambria Math", "Times New Roman", serif;
  font-size: clamp(14px, 1.25vw, 17px); line-height: 1.45;
  white-space: pre-line; overflow-wrap: anywhere;
}
.algorithm-detail-page {
  flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 10px; overflow: hidden;
}
.algorithm-page-columns {
  flex: 1; min-height: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px;
}
.algorithm-page-panel {
  min-width: 0; min-height: 0; padding: clamp(13px, 1.35vw, 18px);
  border: 1px solid #e8e4df; border-radius: 10px; background: #fff;
}
.algorithm-page-panel > strong { display: block; margin-bottom: 7px; color: #4d443c; font-size: 15px; }
.algorithm-page-panel p, .algorithm-page-panel li {
  margin: 0; color: #665f58; font-size: clamp(13px, 1.08vw, 15px); line-height: 1.65;
}
.algorithm-page-panel--foundation {
  flex-shrink: 0; padding: 11px 14px;
  background: #f4f8ff; border-color: #dce7fa;
}
.algorithm-page-panel--foundation > strong { color: #4f6f9f; }
.algorithm-page-columns--intro { flex: 1; }
.algorithm-page-columns--intro .algorithm-page-panel { padding: 11px 14px; }
.algorithm-page-columns--long-guide {
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
}
.algorithm-page-panel--formula-guide {
  background: #f7f4ff; border-color: #ded6f4;
}
.algorithm-page-panel--formula-guide > strong { color: #6651a0; }
.algorithm-page-panel--formula-guide p { line-height: 1.58; }
.algorithm-page-panel--principle { background: #fffdf8; border-color: #eadfce; }
.algorithm-page-panel--principle > strong { color: #8a6338; }
.algorithm-page-panel--steps { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.algorithm-page-panel--steps ol {
  flex: 1; min-height: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr)); gap: 10px; margin: 4px 0 0; padding: 0;
  list-style: none;
}
.algorithm-page-panel--steps li {
  display: flex; align-items: center; gap: 12px; padding: 14px;
  border-radius: 9px; background: #faf8f5;
}
.algorithm-page-panel--steps li > span {
  flex: 0 0 30px; width: 30px; height: 30px; display: flex;
  align-items: center; justify-content: center; border-radius: 50%;
  background: #ffb74d; color: #fff; font-weight: 700;
}
.algorithm-page-columns--example { flex: 1; }
.algorithm-page-panel--example { background: #fff8e9; border-color: #ffe0a7; }
.algorithm-page-panel--note { background: #fff5f5; border-color: #f3d4d4; }
.algorithm-page-panel--note > strong { color: #a14f4f; }
.algorithm-page-panel--goals { flex-shrink: 0; background: #f7fbf3; border-color: #dbead2; }
.algorithm-page-panel--goals ul {
  display: flex; flex-wrap: wrap; gap: 5px 24px; margin: 0; padding-left: 20px;
}
.algorithm-page-panel--application-lead {
  flex-shrink: 0; padding-top: 12px; padding-bottom: 12px;
  background: #f4f8ff; border-color: #dce7fa;
}
.algorithm-page-panel--application-lead > strong { color: #4f6f9f; }
.algorithm-page-columns--application { flex: 1; }
.algorithm-page-panel--application-steps { background: #fff8e9; border-color: #ffe0a7; }
.algorithm-page-panel--application-steps,
.algorithm-page-panel--application-decision { padding: 11px 14px; }
.algorithm-page-panel--application-steps ol {
  display: grid; gap: 2px; margin: 0; padding-left: 22px;
}
.algorithm-page-panel--application-steps li { padding-left: 2px; line-height: 1.55; }
.algorithm-page-panel--application-decision { background: #f7fbf3; border-color: #dbead2; }
.algorithm-page-panel--application-decision > strong { color: #5f7f4b; }
@media (max-width: 1000px) {
  .algorithm-overview-grid--five { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .algorithm-lesson-head { padding: 13px 16px; }
  .algorithm-detail-head { grid-template-columns: minmax(190px, 0.75fr) minmax(0, 1.25fr); }
  .algorithm-page-panel { padding: 12px; }
}

/* 绘本 */
.book-tab {
  padding: 14px 18px 16px; height: 100%; overflow: hidden;
  display: flex; flex-direction: column; min-height: 0;
}
.book-result {
  width: 100%; margin: 0 auto; flex: 1; min-height: 0;
  display: flex; flex-direction: column;
}
.book-title { font-size: 18px; color: #333; text-align: center; margin-bottom: 16px; }
.book-page-display {
  flex: 1; min-height: 0;
  background: #fffde7; border-radius: 16px; padding: 16px 22px 18px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  display: flex; flex-direction: column;
}
.book-page {
  flex: 1; min-height: 0; text-align: center;
  display: flex; flex-direction: column;
}
.book-svg {
  flex: 1; min-height: 0; margin-bottom: 10px;
  display: flex; justify-content: center; align-items: center;
  overflow: hidden;
}
.book-svg :deep(svg) {
  max-width: 100%; max-height: 100%; width: auto; height: auto;
  aspect-ratio: 1 / 1; flex-shrink: 1;
}
.book-svg .book-photo {
  max-width: 100%; max-height: 100%; width: auto; height: auto;
  border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.12);
  object-fit: contain; flex-shrink: 1;
}
.book-text {
  font-size: 15px; color: #333; line-height: 1.6;
  padding: 0 12px; flex-shrink: 0;
}
.book-nav {
  display: flex; align-items: center; justify-content: center;
  gap: 16px; margin-top: 12px; flex-shrink: 0;
}
.nav-btn {
  padding: 8px 20px; background: #ffb74d; color: white; border: none;
  border-radius: 16px; cursor: pointer; font-size: 14px; transition: all 0.2s;
}
.nav-btn:hover { background: #ff9800; }
.nav-btn:disabled { background: #ddd; cursor: not-allowed; }
.page-info { font-size: 14px; color: #666; font-weight: 500; }
/* 绘本左右布局 */
.book-layout {
  flex: 1; min-height: 0;
  display: flex; gap: 16px; align-items: stretch;
}
.book-main {
  flex: 1; min-width: 0; min-height: 0;
  display: flex; flex-direction: column;
}
.book-fav-panel {
  width: 230px; flex-shrink: 0; background: white; border-radius: 12px;
  padding: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  max-height: 100%; min-height: 0;
  display: flex; flex-direction: column;
}
.fav-panel-title { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0e6d2; flex-shrink: 0; }
.fav-book-list { display: flex; flex-direction: column; gap: 8px; overflow-y: auto; flex: 1; }
.fav-book-item {
  display: flex; gap: 8px; align-items: flex-start; cursor: pointer;
  padding: 9px 10px; background: #faf7ef; border-radius: 8px; transition: all 0.2s;
}
.fav-book-item:hover { background: #fff3e0; }
.fav-book-star { color: #ffb300; font-size: 13px; line-height: 1.5; }
.fav-book-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.fav-book-title { font-size: 13px; font-weight: 500; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fav-book-topic { font-size: 11px; color: #999; }
.fav-panel-empty { font-size: 12px; color: #bbb; text-align: center; padding: 24px 0; line-height: 1.8; }
.book-head-row { display: flex; align-items: center; justify-content: center; gap: 14px; margin-bottom: 14px; flex-shrink: 0; }
.book-head-row .book-title { margin-bottom: 0; }
.book-fav-main {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 6px 16px; border: 1.5px solid #ffb300; background: white; color: #ff8f00;
  border-radius: 16px; font-size: 13px; cursor: pointer; transition: all 0.2s; flex-shrink: 0;
}
.book-fav-main:hover { background: #fff8e1; }
.book-fav-main:disabled { opacity: 0.5; cursor: not-allowed; }
.book-fav-main.active { background: #ffb300; color: white; border-color: #ffb300; }

/* 学习路径 */
.path-tab { padding: 20px; overflow-y: auto; }
.path-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.path-header h3 { font-size: 20px; color: #333; }
.path-sub { margin: 6px 0 0; font-size: 12px; color: #999; }
.path-content { max-width: 980px; margin: 0 auto; }
.path-info {
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px; margin-bottom: 16px;
}
.info-card {
  display: flex; flex-direction: column; gap: 4px;
  padding: 14px; background: #f5f5f5; border-radius: 10px; text-align: center;
}
.info-label { font-size: 12px; color: #888; }
.info-value { font-size: 16px; font-weight: 600; color: #333; }
.info-extra { font-size: 11px; color: #aaa; line-height: 1.5; }

/* 总体进度条 */
.path-overall {
  padding: 14px 18px; margin-bottom: 14px;
  background: linear-gradient(135deg, #fff9ec, #fff4de);
  border: 1px solid #ffe6bb; border-radius: 12px;
}
.overall-row {
  display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
}
.overall-label { font-size: 13px; font-weight: 600; color: #b8860b; }
.overall-value { font-size: 13px; font-weight: 600; color: #333; }
.overall-bar {
  height: 10px; margin: 10px 0 8px; border-radius: 10px;
  background: #ffeccb; overflow: hidden;
}
.overall-bar span {
  display: block; height: 100%; border-radius: 10px; transition: width .4s ease;
  background: linear-gradient(90deg, #ffd08a, #ffa726);
}
.overall-hint { margin: 0; font-size: 11px; color: #b3924f; line-height: 1.6; }

/* 建议下一步 */
.path-focus {
  display: flex; align-items: center; justify-content: space-between; gap: 14px;
  padding: 14px 18px; margin-bottom: 16px; cursor: pointer; transition: all 0.2s;
  background: #fff8e1; border: 1px solid #ffe0a3; border-radius: 12px;
}
.path-focus:hover { border-color: #ffb74d; background: #fff3d2; }
.focus-main { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.focus-label { font-size: 11px; font-weight: 600; color: #c58f19; }
.focus-topic { font-size: 16px; font-weight: 600; color: #333; }
.focus-meta { font-size: 12px; color: #999; }
.focus-reason {
  margin-top: 2px; font-size: 12px; color: #c58f19; line-height: 1.6;
}
.focus-btn {
  flex-shrink: 0; padding: 8px 18px; border: none; border-radius: 16px;
  background: #ffb74d; color: #fff; font-size: 13px; cursor: pointer;
}
.focus-btn:hover { background: #ffa726; }

/* 分区容器 */
.path-section {
  padding: 16px 18px; margin-bottom: 16px;
  background: #fff; border: 1px solid #f0f0f0; border-radius: 12px;
}
.section-head {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 12px; margin-bottom: 14px;
}
.section-head h4 { font-size: 15px; color: #333; margin: 0; }
.section-hint { font-size: 11px; color: #aaa; }
.path-empty-line { margin: 0; font-size: 12px; color: #aaa; }
.path-columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }

/* 学习路线图 */
.roadmap { display: flex; flex-direction: column; gap: 10px; }
.road-node {
  display: flex; align-items: flex-start; gap: 12px; padding: 12px 14px; cursor: pointer;
  border: 1px solid #eee; border-radius: 10px; transition: all 0.2s;
}
.road-node:hover { border-color: #ffb74d; background: #fffdf7; }
.road-node.mastered { background: #f2faf3; border-color: #d7ecd9; }
.road-node.learning { background: #fff8ec; border-color: #ffe3b8; }
.road-node.todo { background: #fafafa; }
.node-index {
  width: 30px; height: 30px; flex-shrink: 0; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600; background: #eee; color: #999;
}
.road-node.mastered .node-index { background: #4caf50; color: #fff; }
.road-node.learning .node-index { background: #ffb74d; color: #fff; }
.node-body { flex: 1; min-width: 0; }
.node-title-row { display: flex; align-items: center; gap: 10px; }
.node-title { font-size: 14px; font-weight: 600; color: #333; }
.node-status { font-size: 11px; padding: 2px 8px; border-radius: 8px; flex-shrink: 0; }
.node-status.mastered { background: #e8f5e9; color: #4caf50; }
.node-status.learning { background: #fff3e0; color: #ff9800; }
.node-status.todo { background: #f0f0f0; color: #999; }
.node-meta {
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
  margin-top: 6px; font-size: 11px; color: #999;
}
.node-cat { color: #7e8ba3; }
.node-diff { padding: 1px 7px; border-radius: 7px; }
.node-diff.easy { background: #e8f5e9; color: #4caf50; }
.node-diff.medium { background: #fff3e0; color: #ff9800; }
.node-diff.hard { background: #ffebee; color: #f44336; }
.node-time { margin-left: auto; color: #bbb; }

/* 自评偏难标记 */
.node-hard-tag {
  flex-shrink: 0; padding: 2px 8px; border-radius: 8px; font-size: 11px;
  background: #ffebee; color: #e57373; font-weight: 600;
}
/* 单课进度条 + 掌握提示 */
.node-progress {
  display: flex; align-items: center; gap: 10px; margin-top: 8px;
}
.node-bar {
  width: 90px; height: 6px; flex-shrink: 0; border-radius: 6px;
  background: #f0f0f0; overflow: hidden;
}
.node-bar span {
  display: block; height: 100%; border-radius: 6px; transition: width .4s ease;
  background: linear-gradient(90deg, #ffd08a, #ffb74d);
}
.road-node.mastered .node-bar span { background: linear-gradient(90deg, #a5d6a7, #4caf50); }
.node-hint { font-size: 11px; color: #aaa; line-height: 1.5; }
.node-action {
  flex-shrink: 0; align-self: center; padding: 5px 12px; border-radius: 14px;
  font-size: 12px; color: #e08a00; background: #fff3e0; border: 1px solid #ffe0b2;
}
.road-node:hover .node-action { background: #ffe0b2; }

/* 学习方式分布 */
.type-list { display: flex; flex-direction: column; gap: 10px; }
.type-row { display: flex; align-items: center; gap: 10px; font-size: 12px; color: #666; }
.type-name { width: 68px; flex-shrink: 0; }
.type-bar { flex: 1; height: 8px; background: #f0f0f0; border-radius: 8px; overflow: hidden; }
.type-bar span {
  display: block; height: 100%; border-radius: 8px;
  background: linear-gradient(90deg, #ffd08a, #ffb74d);
}
.type-count { width: 48px; flex-shrink: 0; text-align: right; color: #999; }
.type-extra { display: flex; gap: 16px; margin-top: 12px; font-size: 11px; color: #aaa; }

/* 需要复习 */
.weak-list { display: flex; flex-direction: column; }
.weak-item {
  display: flex; align-items: center; gap: 10px; padding: 9px 0;
  border-bottom: 1px dashed #f0f0f0; font-size: 12px; color: #666;
}
.weak-item:last-child { border-bottom: none; }
.weak-topic { flex: 1; min-width: 0; color: #333; }
.weak-score { font-weight: 600; color: #ff9800; }
.weak-rated {
  flex-shrink: 0; padding: 1px 8px; border-radius: 8px;
  font-size: 11px; font-weight: 600; background: #ffebee; color: #e57373;
}
.weak-time { flex-shrink: 0; font-size: 11px; color: #bbb; }

/* 最近学习动态 */
.activity-list { display: flex; flex-direction: column; }
.activity-item {
  display: flex; align-items: center; gap: 10px; padding: 9px 0;
  border-bottom: 1px dashed #f0f0f0; font-size: 12px; color: #666;
}
.activity-item:last-child { border-bottom: none; }
.act-type {
  flex-shrink: 0; padding: 2px 8px; border-radius: 8px;
  font-size: 11px; background: #f0f4ff; color: #6b7fd0;
}
.act-type.quiz { background: #fff3e0; color: #ff9800; }
.act-type.book { background: #e8f5e9; color: #4caf50; }
.act-type.animation { background: #e9f4fb; color: #4aa3d0; }
.act-type.programming { background: #f3e9ff; color: #8e6fd0; }
.act-topic { flex: 1; min-width: 0; color: #333; }
.act-score { font-weight: 600; color: #ff9800; }
.act-time { flex-shrink: 0; font-size: 11px; color: #bbb; }

/* 已掌握知识点 */
.topic-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.learned-tag {
  padding: 6px 14px; background: #e8f5e9; color: #4caf50;
  border-radius: 16px; font-size: 13px; font-weight: 500;
}

/* AI 推荐卡片 */
.suggestion-card {
  padding: 16px; background: #f5f5f5; border-radius: 12px;
  margin-bottom: 12px; cursor: pointer; transition: all 0.2s;
  border: 2px solid transparent;
}
.suggestion-card:last-child { margin-bottom: 0; }
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

@media (max-width: 900px) {
  .path-info { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .path-columns { grid-template-columns: 1fr; }
  .section-head { flex-direction: column; gap: 4px; }
}

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

<style scoped src="../../styles/lesson-pagination.css"></style>

<style scoped>
/* Clear formula hierarchy and compact reading panels. */
.animation-tab.algorithm-mode { padding: 14px 18px; }
.algorithm-lesson { max-width: 1440px; }
.algorithm-lesson-head--compact { padding: 12px 16px; margin-bottom: 12px; }
.algorithm-lesson-head h3 { margin: 4px 0 0; font-size: 22px; color: #39414b; }
.algorithm-lesson-head p { white-space: normal; font-size: 14px; line-height: 1.5; margin: 6px 0 0; color: #68615a; }
.algorithm-view-tag { background: #fff0cf; color: #8a5d20; font-size: 12px; }
.algorithm-overview-grid { gap: 12px; }
.algorithm-overview-card { padding: 16px 20px; box-shadow: none; }
.algorithm-overview-number { color: #957a54; font-size: 13px; }
.algorithm-overview-card h4,
.algorithm-overview-grid--five .algorithm-overview-card h4,
.algorithm-overview-grid--project .algorithm-overview-card h4 { font-size: 18px; line-height: 1.4; margin: 6px 0 12px; color: #343d48; }
.algorithm-overview-card code,
.algorithm-overview-grid--five .algorithm-overview-card code,
.algorithm-overview-grid--project .algorithm-overview-card code {
  font-size: clamp(17px, 1.35vw, 23px); line-height: 1.65;
  padding: 14px; background: #f7f5fb; color: #493d65;
}
.algorithm-open-hint { font-size: 13px; color: #926523; margin-top: 10px; }
.algorithm-detail-toolbar { margin-bottom: 10px; font-size: 13px; color: #746859; }
.algorithm-back-btn { border-radius: 8px; padding: 7px 12px; font-size: 14px; }
.algorithm-detail-head { padding: 12px 16px; gap: 16px; }
.algorithm-detail-head h3 { font-size: 22px; line-height: 1.35; color: #343d48; }
.algorithm-detail-formula code { font-size: clamp(18px, 1.4vw, 23px); line-height: 1.5; }
.algorithm-detail-formula span { background: transparent; color: #75668e; padding: 0; font-size: 12px; }
.algorithm-detail-page { gap: 10px; }
.algorithm-page-panel { padding: 14px 16px; }
.algorithm-page-panel > strong { font-size: 17px; margin-bottom: 8px; }
.algorithm-page-panel p, .algorithm-page-panel li { font-size: 16px; line-height: 1.65; color: #4f535a; }
.algorithm-page-panel--steps li { padding: 12px; gap: 10px; }
.algorithm-page-panel--steps li > span { color: #694515; background: #ffce73; }
.algorithm-page-panel--goals { padding: 10px 14px; }
@media (max-height: 800px) {
  .algorithm-lesson-head p { display: none; }
  .algorithm-detail-head h3 { font-size: 20px; }
  .algorithm-page-panel { padding: 10px 12px; }
  .algorithm-page-panel p, .algorithm-page-panel li { font-size: 15px; line-height: 1.5; }
  .algorithm-overview-card { padding: 12px 14px; }
}
@media (max-width: 900px) {
  .algorithm-detail-head { grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr); }
  .algorithm-overview-grid--five { grid-template-columns: repeat(2, minmax(0, 1fr)); grid-template-rows: repeat(3, minmax(0, 1fr)); }
  .algorithm-overview-card h4 { font-size: 16px; }
}
</style>
