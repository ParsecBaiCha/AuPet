<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '../../stores/user'

interface ClassPet { id: number; studentName: string; petName: string; points: number; level: string; progress: number }
const props = defineProps<{ classPets: ClassPet[] }>()
const userStore = useUserStore()
const progress = computed(() => Math.min(100, userStore.completedTasks || 0))
const today = new Intl.DateTimeFormat('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' }).format(new Date())
</script>

<template>
  <section class="senior-home">
    <div class="senior-hero">
      <div>
        <p class="eyebrow">{{ today }} · {{ userStore.grade || '高中阶段' }}</p>
        <h2>你好，{{ userStore.studentInfo.name }}</h2>
        <p class="subtitle">保持节奏，今天也向你的目标前进一点。</p>
      </div>
      <div class="goal-card">
        <span>本周学习完成度</span>
        <strong>{{ progress }}%</strong>
        <div class="track"><i :style="{ width: progress + '%' }"></i></div>
      </div>
    </div>

    <div class="stat-grid">
      <article><span>成长积分</span><strong>{{ userStore.userPoints }}</strong><small>持续积累，兑换成长权益</small></article>
      <article><span>班级排名</span><strong>#{{ userStore.rank || '--' }}</strong><small>专注自己的进步</small></article>
      <article><span>完成任务</span><strong>{{ userStore.completedTasks || 0 }}</strong><small>每个完成都值得记录</small></article>
    </div>

    <div class="content-grid">
      <article class="plan-card">
        <div class="section-title"><div><span>今日计划</span><h3>把大目标拆成现在能做的事</h3></div><router-link to="/student/tasks">查看计划 →</router-link></div>
        <div class="plan-row"><b>01</b><div><strong>完成今日学习任务</strong><p>按优先级推进，完成后及时记录。</p></div><span>进行中</span></div>
        <div class="plan-row"><b>02</b><div><strong>与 AI 学习伙伴复盘</strong><p>梳理难点，形成自己的理解。</p></div><router-link to="/student/ai-learning">开始</router-link></div>
      </article>
      <article class="companion-card">
        <p>成长伙伴</p><h3>{{ userStore.petInfo.name || '学习伙伴' }}</h3>
        <span>陪你记录每一次专注与突破</span>
        <router-link to="/student/ai-companion">去聊一聊</router-link>
      </article>
    </div>

    <section class="peers">
      <div class="section-title"><div><span>班级动态</span><h3>同伴的学习进度</h3></div></div>
      <div class="peer-grid"><article v-for="peer in props.classPets.slice(0, 4)" :key="peer.id"><strong>{{ peer.studentName }}</strong><span>{{ peer.petName }} · {{ peer.points }} 积分</span><div class="mini-track"><i :style="{ width: peer.progress + '%' }"></i></div></article></div>
    </section>
  </section>
</template>

<style scoped>
.senior-home { color: #5a4a6a; max-width: 1280px; margin: 0 auto; padding: 12px; }
.senior-hero { background: linear-gradient(125deg, #fff5e6 0%, #fce8d5 40%, #f0e8f5 100%); color: #5a4a6a; border-radius: 16px; padding: 32px 36px; display:flex; justify-content:space-between; align-items:center; gap:24px; position: relative; overflow: hidden; }
.senior-hero::after { content: ''; position: absolute; top: -50%; right: -10%; width: 300px; height: 300px; background: radial-gradient(circle, rgba(255,183,77,0.12), transparent 70%); border-radius: 50%; }
.eyebrow { color:#c97d3a; font-size:13px; margin-bottom:8px; letter-spacing:0.5px; }
.senior-hero h2 { font-size:28px; margin:0 0 8px; font-weight: 600; color: #4a3f5c; }
.subtitle { color:#8a7a6a; margin:0; }
.goal-card { min-width:220px; background:rgba(255,255,255,.65); border:1px solid rgba(244,187,110,.25); border-radius:12px; padding:18px; backdrop-filter: blur(4px); }
.goal-card span,.goal-card strong { display:block; }
.goal-card span { color: #8a7a6a; font-size: 12px; }
.goal-card strong { font-size:30px; margin:6px 0; color: #8985cf; font-weight: 700; }
.track,.mini-track { background:rgba(244,187,110,.2); height:5px; border-radius:5px; overflow:hidden; }
.track i,.mini-track i { display:block; height:100%; background:linear-gradient(90deg,#ffb74d,#ff9800); border-radius:inherit; }
.stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin:18px 0; }
.stat-grid article,.plan-card,.peers { background:#fff; border:1px solid rgba(244,187,110,.15); border-radius:12px; padding:22px; box-shadow:0 2px 12px rgba(137,133,207,.05); }
.stat-grid span,.stat-grid small { display:block; color:#b3a89a; font-size:13px; }
.stat-grid span { text-transform: uppercase; letter-spacing: 0.5px; font-size: 11px; }
.stat-grid strong { display:block; font-size:28px; margin:10px 0 4px; color:#5a4a6a; font-weight: 700; }
.content-grid { display:grid; grid-template-columns:2fr 1fr; gap:16px; }
.section-title { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.section-title span { font-size:11px; color:#b3a89a; text-transform: uppercase; letter-spacing:0.5px; }
.section-title h3 { margin:4px 0 0; font-size:18px; color:#4a3f5c; font-weight: 600; }
.section-title a,.plan-row>a { color:#c97d3a; text-decoration:none; font-size:13px; transition: color .2s; }
.section-title a:hover,.plan-row>a:hover { color:#ff9800; }
.plan-row { display:flex; gap:14px; align-items:center; border-top:1px solid rgba(244,187,110,.1); padding:14px 0; }
.plan-row b { color:#ffb74d; font-size: 18px; font-weight: 700; }
.plan-row div { flex:1; }
.plan-row strong { font-size:14px; color:#5a4a6a; }
.plan-row p { color:#b3a89a; font-size:13px; margin:4px 0 0; }
.plan-row>span { color:#c97d3a; background:rgba(255,183,77,.1); padding:4px 10px; border-radius:20px; font-size:12px; border: 1px solid rgba(255,183,77,.2); }
.companion-card { background:linear-gradient(150deg, #f0e8f5, #e6d5f0); border:1px solid rgba(137,133,207,.2); border-radius:12px; padding:24px; display:flex; flex-direction:column; align-items:flex-start; color:#5a4a6a; }
.companion-card p { color:#8a7a9a; margin:0; font-size:13px; }
.companion-card h3 { margin:10px 0 6px; color:#8985cf; font-size: 20px; }
.companion-card span { color:#8a7a9a; font-size:13px; line-height:1.7; }
.companion-card a { margin-top:auto; padding-top:26px; color:#8985cf; text-decoration:none; font-weight:600; transition: color .2s; }
.companion-card a:hover { color:#acb6f3; }
.peers { margin-top:16px; }
.peer-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
.peer-grid article { background:#fff9f0; padding:14px; border-radius:10px; border: 1px solid rgba(244,187,110,.12); transition: all .2s; }
.peer-grid article:hover { border-color: rgba(137,133,207,.3); box-shadow: 0 2px 8px rgba(137,133,207,.06); }
.peer-grid strong,.peer-grid span { display:block; }
.peer-grid strong { color: #5a4a6a; }
.peer-grid span { font-size:12px; color:#b3a89a; margin:5px 0 10px; }
.mini-track { background:rgba(244,187,110,.15); }
.mini-track i { background:linear-gradient(90deg,#ffb74d,#ff9800); }
@media (max-width:800px) { .senior-hero,.content-grid { grid-template-columns:1fr; display:grid; }.stat-grid,.peer-grid { grid-template-columns:1fr 1fr; } }
</style>
