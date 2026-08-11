<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'
import { studentApi } from '../../api/student'

const userStore = useUserStore()

interface Message {
  id: number
  type: 'user' | 'pet'
  content: string
  time: string
}

const messages = ref<Message[]>([])
const newMessage = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const showHistory = ref(false)
const sending = ref(false)

const toggleHistory = () => { showHistory.value = !showHistory.value }

const scrollToBottom = () => {
  nextTick(() => { if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight })
}

const nowTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || sending.value) return
  const text = newMessage.value
  messages.value.push({ id: Date.now(), type: 'user', content: text, time: nowTime() })
  newMessage.value = ''
  scrollToBottom()
  sending.value = true
  try {
    const data: any = await studentApi.sendChat(text)
    const reply = data?.reply ?? '我们来聊天吧！'
    const replyTime = data?.time ?? nowTime()
    messages.value.push({ id: Date.now() + 1, type: 'pet', content: reply, time: replyTime })
    scrollToBottom()
  } catch (e) {
    // 失败时给出提示消息，不阻塞使用（错误提示由全局拦截器处理）
    messages.value.push({ id: Date.now() + 1, type: 'pet', content: '抱歉，我暂时无法回复，请稍后再试～', time: nowTime() })
    scrollToBottom()
  } finally {
    sending.value = false
  }
}

const quickReplies = ['今天有什么好玩的？', '我要去做任务了！', '你饿了吗？', '今天心情不错！', '我们出去玩吧！']

const sendQuickReply = (text: string) => { newMessage.value = text; sendMessage() }

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
    if (Array.isArray(data)) {
      messages.value = data
    }
  } catch (e) {
    // API 失败时保持页面可用
  }
  scrollToBottom()
})
</script>

<template>
<div class="chat-page">
  <!-- Chat header bar removed, using the chat-container header instead -->
  <div class="chat-container">
    <div class="chat-header">
      <img class="pet-avatar" :src="userStore.petInfo.type" alt="pet" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
      <div class="pet-info">
        <div class="pet-name-status">
          <h3>{{ userStore.petInfo.name }}</h3>
          <span class="status">在线</span>
        </div>
      </div>
      <button class="history-btn" @click="toggleHistory">
        聊天记录
      </button>
    </div>

    <!-- History Modal -->
    <div v-if="showHistory" class="history-modal" @click.self="toggleHistory">
      <div class="history-dialog">
        <div class="history-header">
          <h3>聊天记录</h3>
          <button class="close-btn" @click="toggleHistory">✕</button>
        </div>
        <div class="history-list">
          <div v-for="msg in messages" :key="msg.id" class="history-item" :class="{ 'user-msg': msg.type === 'user', 'pet-msg': msg.type === 'pet' }">
            <span class="history-time">{{ msg.time }}</span>
            <span class="history-sender">{{ msg.type === 'user' ? '我' : userStore.petInfo.name }}</span>
            <span class="history-content">{{ msg.content }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="messages-container" ref="chatContainer">
      <div v-for="msg in messages" :key="msg.id" class="message" :class="{ 'user-message': msg.type === 'user', 'pet-message': msg.type === 'pet' }">
        <img v-if="msg.type === 'pet'" class="avatar" :src="userStore.petInfo.type" alt="pet" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
        <div class="message-content">
          <div class="bubble">{{ msg.content }}</div>
          <div class="time">{{ msg.time }}</div>
        </div>
        <img v-if="msg.type === 'user'" class="avatar" :src="userStore.studentInfo.avatar" alt="user" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
      </div>
    </div>

    <div class="quick-replies">
      <button v-for="(reply, index) in quickReplies" :key="index" @click="sendQuickReply(reply)" class="quick-btn">{{ reply }}</button>
    </div>

    <div class="input-area">
      <input v-model="newMessage" type="text" placeholder="输入消息..." @keyup.enter="sendMessage" />
      <button @click="sendMessage" class="send-btn">发送</button>
    </div>
  </div>
</div>
</template>

<style scoped>
.chat-page { height: 100%; display: flex; flex-direction: column; }
.chat-container { background: rgba(255, 250, 235, 0.98); border-radius: 5px; overflow: hidden; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); display: flex; flex-direction: column; flex: 1; min-height: 0; }
.chat-header { background: #ffb74d; color: white; padding: 20px; display: flex; align-items: center; justify-content: space-between; }
.history-btn { background: white; color: #ffb74d; border: none; padding: 8px 15px; border-radius: 20px; cursor: pointer; font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 5px; }
.history-btn:hover { background: #f0f0f0; }
.history-modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.history-dialog { background: white; border-radius: 15px; width: 80%; max-width: 500px; max-height: 70vh; overflow: hidden; display: flex; flex-direction: column; }
.history-header { background: #ffb74d; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
.close-btn { background: none; border: none; color: white; font-size: 20px; cursor: pointer; }
.history-list { padding: 15px; overflow-y: auto; flex: 1; }
.history-item { padding: 10px; margin-bottom: 10px; border-radius: 10px; display: flex; flex-direction: column; gap: 5px; }
.history-item.user-msg { background: #e8f5e9; }
.history-item.pet-msg { background: #f0f0f0; }
.history-time { font-size: 11px; color: #999; }
.history-sender { font-weight: bold; font-size: 13px; color: #ffb74d; }
.history-content { font-size: 14px; color: #333; }
.pet-avatar { width: 50px; height: 50px; object-fit: contain; border-radius: 50%; border: 3px solid #F57C00; }
.pet-info { flex: 1; margin-left: 15px; }
.pet-name-status { display: flex; align-items: center; gap: 10px; }
.pet-name-status h3 { margin: 0; font-size: 18px; }
.status { font-size: 12px; opacity: 0.8; }
.messages-container { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; background: #f5f7fa; }
.message { display: flex; gap: 10px; align-items: flex-end; }
.message.user-message { flex-direction: row-reverse; }
.avatar { width: 45px; height: 45px; object-fit: cover; border-radius: 50%; flex-shrink: 0; border: 2px solid #F57C00; }
.message-content { max-width: 70%; }
.bubble { padding: 12px 18px; border-radius: 18px; font-size: 14px; line-height: 1.5; word-break: break-word; }
.pet-message .bubble { background: white; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12); }
.user-message .bubble { background: #ffb74d; color: white; border-bottom-right-radius: 4px; }
.time { font-size: 11px; color: #999; margin-top: 5px; }
.message.user-message .time { text-align: right; }
.quick-replies { padding: 15px 20px; display: flex; flex-wrap: wrap; gap: 10px; border-top: 1px solid #eee; background: white; }
.quick-btn { padding: 8px 15px; background: #f0f0f0; border: none; border-radius: 20px; font-size: 13px; color: #666; cursor: pointer; transition: all 0.3s ease; }
.quick-btn:hover { background: #ffb74d; color: white; }
.input-area { padding: 20px; display: flex; gap: 10px; background: white; border-top: 1px solid #eee; }
.input-area input { flex: 1; padding: 12px 20px; border: 2px solid #e0e0e0; border-radius: 25px; font-size: 14px; outline: none; transition: border-color 0.3s ease; }
.input-area input:focus { border-color: #ffb74d; }
.send-btn { padding: 12px 30px; background: #ffb74d; color: white; border: none; border-radius: 25px; font-size: 14px; cursor: pointer; transition: all 0.3s ease; }
.send-btn:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }
</style>
