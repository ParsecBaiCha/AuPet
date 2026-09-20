<script setup lang="ts">
import { ref, nextTick, onMounted, computed } from 'vue'
import { useUserStore } from '../../stores/user'
import { studentApi } from '../../api/student'
import { DEFAULT_PET_IMAGE, DEFAULT_STUDENT_AVATAR, setImageFallback } from '../../utils/images'

const userStore = useUserStore()

interface Message {
  id: number
  type: string
  content: string
  time: string
}

const messages = ref<Message[]>([])
const newMessage = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const showHistory = ref(false)
const sending = ref(false)
// 首次载入历史时给消息加入场错峰动画，之后新消息不再延迟
const staggerOn = ref(true)

const isSenior = computed(() => userStore.educationStage === 'senior')
const petName = computed(() => userStore.petInfo.name || 'AI 学习伙伴')
// 伙伴是 AI，没有上下线状态，因此不显示"在线/离线"，只说一句始终成立的话
const statusText = computed(() =>
  sending.value ? '正在认真想你的问题…' : (isSenior.value ? '随时都在 · 想聊什么都可以' : '随时都在 · 听你说心里话')
)

const toggleHistory = () => { showHistory.value = !showHistory.value }

const scrollToBottom = () => {
  nextTick(() => { if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight })
}

const nowTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

const msgDelay = (index: number) => (staggerOn.value ? Math.min(index, 12) * 45 + 'ms' : '0ms')

const sendMessage = async () => {
  if (!newMessage.value.trim() || sending.value) return
  const text = newMessage.value.trim()
  messages.value.push({ id: Date.now(), type: 'user', content: text, time: nowTime() })
  newMessage.value = ''
  sending.value = true
  scrollToBottom()
  try {
    const data: any = await studentApi.sendChat(text)
    const reply = data?.reply ?? '我们来聊天吧！'
    const replyTime = data?.time ?? nowTime()
    messages.value.push({ id: Date.now() + 1, type: 'pet', content: reply, time: replyTime })
  } catch (e) {
    // 失败时给出提示消息，不阻塞使用（错误提示由全局拦截器处理）
    messages.value.push({ id: Date.now() + 1, type: 'pet', content: '抱歉，我暂时无法回复，请稍后再试～', time: nowTime() })
  } finally {
    sending.value = false
    scrollToBottom()
  }
}

const primaryReplies = ['今天有什么好玩的？', '我要去做任务了！', '你饿了吗？', '今天心情不错！', '我们出去玩吧！']
const seniorReplies = ['帮我梳理下今天的难点', '这次没考好，有点沮丧', '怎么安排复习节奏？', '想找个人说说话', '给我一点动力']
const quickReplies = computed(() => (isSenior.value ? seniorReplies : primaryReplies))

const sendQuickReply = (text: string) => { newMessage.value = text; sendMessage() }

const welcomeMessage = (): Message => ({
  id: -1,
  type: 'pet',
  content: `你好呀！我是${petName.value}，很高兴见到你～\n今天想聊点什么？开心的、烦恼的，都可以说给我听。`,
  time: nowTime(),
})

onMounted(async () => {
  // 确保宠物/学生基础信息已加载（正常由 Home 页填充，此处兜底）
  if (!userStore.petInfo.name) {
    try {
      const dash: any = await studentApi.getDashboard()
      if (dash) userStore.applyDashboard(dash)
    } catch (e) { /* ignore */ }
  }
  try {
    const data: any = await studentApi.getChatHistory()
    if (Array.isArray(data) && data.length) {
      messages.value = data.map((m: any) => ({
        id: m.id,
        type: m.type === 'user' ? 'user' : 'pet',
        content: m.content ?? '',
        time: m.time ?? '',
      }))
    }
  } catch (e) {
    // API 失败时保持页面可用
  }
  // 兜底：无论接口是否可用，都保证有一句欢迎语，页面不留白
  if (!messages.value.length) messages.value = [welcomeMessage()]
  scrollToBottom()
  // 入场动画只在首次渲染时生效
  window.setTimeout(() => { staggerOn.value = false }, 900)
})
</script>

<template>
<div class="chat-page" :class="{ senior: isSenior }">
  <div class="chat-container">
    <!-- 伙伴信息条：头像 + 名称 + 陪伴状态 + 记录入口 -->
    <header class="chat-header">
      <span class="header-glow" aria-hidden="true"></span>
      <div class="pet-badge">
        <img class="pet-avatar" :src="userStore.petInfo.type" :alt="petName" @error="setImageFallback($event, DEFAULT_PET_IMAGE)" />
      </div>
      <div class="meta">
        <h3 class="pet-name">{{ petName }}</h3>
        <p class="status"><svg class="heart" viewBox="0 0 24 24" width="12" height="12" fill="currentColor" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" /></svg>{{ statusText }}</p>
      </div>
      <button class="history-btn" type="button" @click="toggleHistory">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M3 12a9 9 0 1 0 3-6.7L3 8" /><path d="M3 3v5h5" /><path d="M12 7v5l3 2" />
        </svg>
        <span>聊天记录</span>
        <span class="count">{{ messages.length }}</span>
      </button>
    </header>

    <!-- 聊天记录弹层 -->
    <div v-if="showHistory" class="history-modal" @click.self="toggleHistory">
      <div class="history-dialog">
        <div class="history-header">
          <h3>聊天记录</h3>
          <button class="close-btn" type="button" aria-label="关闭" @click="toggleHistory">✕</button>
        </div>
        <div class="history-list">
          <div v-for="msg in messages" :key="msg.id" class="history-item" :class="msg.type === 'user' ? 'user-msg' : 'pet-msg'">
            <span class="history-time">{{ msg.time }}</span>
            <span class="history-sender">{{ msg.type === 'user' ? '我' : petName }}</span>
            <span class="history-content">{{ msg.content }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="messages-container" ref="chatContainer" role="log" aria-live="polite">
      <div
        v-for="(msg, index) in messages"
        :key="msg.id"
        class="message"
        :class="msg.type === 'user' ? 'user-message' : 'pet-message'"
        :style="{ animationDelay: msgDelay(index) }"
      >
        <img v-if="msg.type !== 'user'" class="avatar" :src="userStore.petInfo.type" :alt="petName" @error="setImageFallback($event, DEFAULT_PET_IMAGE)" />
        <div class="message-content">
          <div class="bubble">{{ msg.content }}</div>
          <div class="time">{{ msg.time }}</div>
        </div>
        <img v-if="msg.type === 'user'" class="avatar" :src="userStore.studentInfo.avatar" alt="user" @error="setImageFallback($event, DEFAULT_STUDENT_AVATAR)" />
      </div>

      <!-- 正在输入 -->
      <div v-if="sending" class="message pet-message typing-row">
        <img class="avatar" :src="userStore.petInfo.type" :alt="petName" @error="setImageFallback($event, DEFAULT_PET_IMAGE)" />
        <div class="message-content">
          <div class="bubble typing"><i></i><i></i><i></i></div>
        </div>
      </div>
    </div>

    <!-- 快捷话题 + 输入区 -->
    <div class="dock">
      <div class="quick-bar">
        <span class="quick-label">
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">
            <path d="M12 3v3.2M12 17.8V21M3 12h3.2M17.8 12H21M5.6 5.6l2.3 2.3M16.1 16.1l2.3 2.3M18.4 5.6l-2.3 2.3M7.9 16.1l-2.3 2.3" />
          </svg>
          试试这样说
        </span>
        <button
          v-for="(reply, index) in quickReplies"
          :key="index"
          class="quick-btn"
          type="button"
          :style="{ animationDelay: (index * 55 + 90) + 'ms' }"
          @click="sendQuickReply(reply)"
        >{{ reply }}</button>
      </div>
      <div class="composer">
        <input v-model="newMessage" type="text" :placeholder="`和${petName}说点什么…`" @keyup.enter="sendMessage" />
        <button class="send-btn" type="button" :disabled="!newMessage.trim() || sending" aria-label="发送" @click="sendMessage">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="m22 2-7 20-4-9-9-4Z" /><path d="M22 2 11 13" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
/* ===== 主题变量：小学端暖橙，高中端改紫 ===== */
.chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  --brand: #f48d45;
  --brand-2: #ffb74d;
  --brand-3: #ffc266;
  --brand-deep: #e07b2f;
  --paper: #fffdf7;
  --paper-2: #fff8dc;
  --ink: #3c3229;
  --ink-soft: #9a8878;
  --line: rgba(244, 141, 69, 0.16);
  --line-2: rgba(244, 141, 69, 0.28);
  --tint: rgba(255, 183, 77, 0.16);
  --glow: rgba(224, 123, 47, 0.3);
  --dot: rgba(224, 123, 47, 0.1);
}
.chat-page.senior {
  --brand: #8985cf;
  --brand-2: #acb6f3;
  --brand-3: #c3c8f7;
  --brand-deep: #6f6ab8;
  --paper: #fdfcff;
  --paper-2: #f1eff8;
  --ink: #4a3f5c;
  --ink-soft: #9b93b0;
  --line: rgba(137, 133, 207, 0.16);
  --line-2: rgba(137, 133, 207, 0.3);
  --tint: rgba(137, 133, 207, 0.12);
  --glow: rgba(111, 106, 184, 0.28);
  --dot: rgba(137, 133, 207, 0.16);
}

.chat-container {
  background: var(--paper);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 10px 34px rgba(120, 70, 20, 0.13);
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  width: 100%;
}

/* ===== 顶部伙伴条 ===== */
.chat-header {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 22px;
  color: #fff;
  background: linear-gradient(115deg, var(--brand-3) 0%, var(--brand) 52%, var(--brand-deep) 100%);
  overflow: hidden;
  flex-shrink: 0;
}
.header-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 92% -30%, rgba(255, 255, 255, 0.5), transparent 60%),
    radial-gradient(circle at -8% 140%, rgba(255, 255, 255, 0.28), transparent 55%);
}
.pet-badge { position: relative; flex-shrink: 0; z-index: 1; }
.pet-avatar {
  display: block;
  width: 58px;
  height: 58px;
  object-fit: contain;
  border-radius: 50%;
  background: #fff;
  border: 2px solid rgba(255, 255, 255, 0.85);
  box-shadow: 0 6px 18px rgba(120, 60, 0, 0.26);
}

.meta { flex: 1; min-width: 0; position: relative; z-index: 1; }
.pet-name {
  margin: 0;
  font-size: 19px;
  font-weight: 700;
  letter-spacing: 0.4px;
  text-shadow: 0 1px 3px rgba(120, 60, 0, 0.22);
}
.status {
  display: flex;
  align-items: center;
  gap: 7px;
  margin: 5px 0 0;
  font-size: 12.5px;
  color: rgba(255, 255, 255, 0.94);
}
.status .heart {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.9);
  animation: beat 2.2s ease-in-out infinite;
}

.history-btn {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 15px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.55);
  background: rgba(255, 255, 255, 0.22);
  color: #fff;
  font-size: 13.5px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  backdrop-filter: blur(6px);
  transition: background 0.22s, color 0.22s, transform 0.22s, border-color 0.22s;
}
.history-btn:hover { background: #fff; border-color: #fff; color: var(--brand-deep); transform: translateY(-1px); }
.history-btn .count {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--brand-deep);
  font-size: 11px;
  font-weight: 700;
  display: grid;
  place-items: center;
}
.history-btn:hover .count { background: var(--tint); }

/* ===== 消息区：暖色纸感底纹 ===== */
.messages-container {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 22px 22px 10px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: var(--paper-2);
  background-image: radial-gradient(circle, var(--dot) 1.2px, transparent 1.2px);
  background-size: 19px 19px;
}
.messages-container::-webkit-scrollbar { width: 8px; }
.messages-container::-webkit-scrollbar-track { background: transparent; }
.messages-container::-webkit-scrollbar-thumb { background: var(--line-2); border-radius: 99px; }

.message {
  display: flex;
  gap: 11px;
  align-items: flex-end;
  animation: rise 0.45s cubic-bezier(0.22, 0.9, 0.31, 1) both;
}
.message.user-message { flex-direction: row-reverse; }

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  background: #fff;
  box-shadow: 0 4px 12px rgba(120, 70, 20, 0.16);
}
.pet-message .avatar {
  object-fit: contain;
  border: 1.5px solid var(--line-2);
}
.user-message .avatar { border: 1.5px solid rgba(255, 255, 255, 0.9); }

.message-content { max-width: 72%; min-width: 0; }
.bubble {
  padding: 12px 17px;
  font-size: 14.5px;
  line-height: 1.62;
  word-break: break-word;
  white-space: pre-wrap;
}
.pet-message .bubble {
  background: #fff;
  color: var(--ink);
  border: 1px solid var(--line);
  border-radius: 18px 18px 18px 6px;
  box-shadow: 0 6px 16px rgba(120, 70, 20, 0.1);
}
.user-message .bubble {
  background: linear-gradient(135deg, var(--brand-2) 0%, var(--brand) 68%, var(--brand-deep) 100%);
  color: #fff;
  border-radius: 18px 18px 6px 18px;
  box-shadow: 0 8px 18px var(--glow);
}
.time { margin-top: 6px; font-size: 11px; color: var(--ink-soft); opacity: 0.85; }
.user-message .time { text-align: right; }

/* 正在输入的三点动画 */
.typing { display: inline-flex; align-items: center; gap: 5px; padding: 15px 18px; }
.typing i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--brand-2);
  animation: bounceDot 1.15s ease-in-out infinite;
}
.typing i:nth-child(2) { animation-delay: 0.16s; }
.typing i:nth-child(3) { animation-delay: 0.32s; }

/* ===== 底部：快捷话题 + 输入 ===== */
.dock {
  flex-shrink: 0;
  background: var(--paper);
  border-top: 1px solid var(--line);
  box-shadow: 0 -6px 18px rgba(120, 70, 20, 0.05);
}
.quick-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 9px;
  padding: 14px 20px 0;
}
.quick-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-right: 2px;
  font-size: 12px;
  color: var(--ink-soft);
  flex-shrink: 0;
}
.quick-btn {
  padding: 8px 15px;
  border-radius: 999px;
  border: 1.5px solid var(--line-2);
  background: #fff;
  color: #8a6a4a;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  animation: chipIn 0.42s ease both;
  transition: background 0.2s, color 0.2s, transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.chat-page.senior .quick-btn { color: #7c75a8; }
.quick-btn:hover {
  background: linear-gradient(135deg, var(--brand-2), var(--brand));
  color: #fff;
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px var(--glow);
}
.composer { display: flex; align-items: center; gap: 12px; padding: 14px 20px 18px; }
.composer input {
  flex: 1;
  min-width: 0;
  padding: 14px 20px;
  border-radius: 999px;
  border: 2px solid var(--line);
  background: #fff;
  font-size: 14.5px;
  font-family: inherit;
  color: var(--ink);
  outline: none;
  box-shadow: inset 0 2px 6px rgba(120, 70, 20, 0.05);
  transition: border-color 0.22s, box-shadow 0.22s;
}
.composer input::placeholder { color: #c8b7a4; }
.chat-page.senior .composer input::placeholder { color: #b6afc9; }
.composer input:focus { border-color: var(--brand-2); box-shadow: 0 0 0 4px var(--tint); }
.send-btn {
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  border: none;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  cursor: pointer;
  background: linear-gradient(135deg, var(--brand-3) 0%, var(--brand) 62%, var(--brand-deep) 100%);
  box-shadow: 0 8px 18px var(--glow);
  transition: transform 0.22s, box-shadow 0.22s, opacity 0.22s;
}
.send-btn svg { transition: transform 0.25s; }
.send-btn:hover:not(:disabled) { transform: translateY(-2px) scale(1.04); box-shadow: 0 12px 24px var(--glow); }
.send-btn:hover:not(:disabled) svg { transform: translateX(2px) rotate(-8deg); }
.send-btn:disabled { opacity: 0.42; cursor: not-allowed; box-shadow: none; }

/* ===== 聊天记录弹层 ===== */
.history-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  padding: 20px;
  display: grid;
  place-items: center;
  background: rgba(58, 38, 18, 0.44);
  backdrop-filter: blur(3px);
  animation: fadeIn 0.2s ease both;
}
.history-dialog {
  width: min(560px, 92vw);
  max-height: 78vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 22px;
  background: var(--paper);
  box-shadow: 0 30px 70px rgba(58, 35, 10, 0.36);
  animation: popIn 0.3s cubic-bezier(0.22, 1.05, 0.4, 1) both;
}
.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 17px 22px;
  color: #fff;
  background: linear-gradient(115deg, var(--brand-3) 0%, var(--brand) 55%, var(--brand-deep) 100%);
}
.history-header h3 { margin: 0; font-size: 17px; letter-spacing: 0.3px; }
.close-btn {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.22);
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.close-btn:hover { background: #fff; color: var(--brand-deep); }
.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: var(--paper-2);
}
.history-list::-webkit-scrollbar { width: 8px; }
.history-list::-webkit-scrollbar-thumb { background: var(--line-2); border-radius: 99px; }
.history-item {
  display: grid;
  grid-template-columns: auto auto 1fr;
  align-items: center;
  gap: 9px;
  padding: 11px 14px;
  border-radius: 14px;
  font-size: 13.5px;
  border: 1px solid transparent;
}
.history-item.user-msg { background: #fff; border-color: var(--line); }
.history-item.pet-msg { background: var(--tint); border-color: var(--line-2); }
.history-time { font-size: 11px; color: var(--ink-soft); }
.history-sender { font-size: 12.5px; font-weight: 700; color: var(--brand-deep); white-space: nowrap; }
.history-content {
  color: var(--ink);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* ===== 动画 ===== */
@keyframes rise {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes chipIn {
  from { opacity: 0; transform: translateY(8px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes popIn {
  from { opacity: 0; transform: translateY(18px) scale(0.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes bounceDot {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.55; }
  30% { transform: translateY(-5px); opacity: 1; }
}
@keyframes beat {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.18); opacity: 1; }
}

@media (max-width: 700px) {
  .chat-header { padding: 14px 16px; gap: 12px; }
  .pet-avatar { width: 48px; height: 48px; }
  .pet-name { font-size: 17px; }
  .history-btn span:first-of-type { display: none; }
  .messages-container { padding: 16px 14px 8px; }
  .message-content { max-width: 82%; }
  .quick-bar { padding: 12px 14px 0; }
  .composer { padding: 12px 14px 16px; }
}
</style>
