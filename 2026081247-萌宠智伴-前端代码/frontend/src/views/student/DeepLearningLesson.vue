<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { dataset, forward, metrics, network, train } from '../../utils/neuralExperiment'

const pages = [
  { title: '从一个分类问题开始', formula: '输入 (x₁, x₂) → 神经网络 → P(紫色类)', guide: 'x₁ 是横坐标，x₂ 是纵坐标；P 表示概率，取值从 0 到 1。橙色记为 0，紫色记为 1。', principle: '给模型一些带有正确类别的点，让它从位置与类别的关系中学习，再判断新点。颜色是答案标签，不是输入特征。', example: '假设新点的位置是 (−0.2, 0.3)，模型输出 0.8，就表示它给出 80% 的紫色类概率；以 50% 为界，把这个点预测为紫色类。', question: '如果把正确颜色直接作为输入，模型还需要学习位置与类别的关系吗？', answer: '不需要，那相当于提前告诉模型答案。实验只输入两个坐标。' },
  { title: '一个神经元怎样计算', formula: 'z = w₁x₁ + w₂x₂ + b', guide: 'w₁、w₂ 是权重，决定坐标怎样影响结果；b 是偏置，用来平移判断标准。z 是加权求和的结果。', principle: '先将每个输入乘以权重，再加上偏置。训练会调整这些参数，让模型逐步减少错误。权重可以是正数，也可以是负数。', example: '取 x₁ = 0.2，x₂ = 0.6，w₁ = −1，w₂ = 2，b = −0.1，则 z = −0.2 + 1.2 − 0.1 = 0.9。', question: '其他数值不变，偏置 b 增加 0.1，z 会怎样变化？', answer: 'z 也增加 0.1。偏置可以整体调整神经元的输出。' },
  { title: '从神经元到神经网络', formula: 'hⱼ = tanh(wⱼ₁x₁ + wⱼ₂x₂ + bⱼ)\np = σ(Σ vⱼhⱼ + c)，σ(z) = 1 / (1 + e⁻ᶻ)', guide: 'hⱼ 是第 j 个隐藏神经元的输出；Σ 表示求和；vⱼ 和 c 是输出层参数。tanh 将数值映射到 −1 至 1，σ 将数值映射到 0 至 1。', principle: '本实验使用 2 个输入、4 个隐藏神经元和 1 个概率输出。非线性激活函数让网络能够学习弯曲的边界。图中橙色概率为 1−p，紫色概率为 p，它们来自同一个输出。', example: '一条直线很难把圆心附近的紫色点与外围的橙色点分开。隐藏层组合多个非线性变换，可以逐步学到弯曲边界。', question: '只有一层隐藏层，也能用来理解深度学习吗？', answer: '可以。这里用小型网络理解基本机制；深度学习通常使用更多层来学习更复杂的特征。' },
  { title: '模型如何知道自己错了', formula: 'L = −(1/N) Σ [y ln(p) + (1−y) ln(1−p)]', guide: 'N 是训练样本数；y 是正确标签（0 或 1）；p 是紫色类概率；ln 是自然对数。L 称为二元交叉熵损失。先理解作用，不必手算对数。', principle: '损失衡量预测与正确答案的差距，越小通常说明训练样本上的预测越好。准确率只看类别是否判断正确，损失还会考虑模型有多大把握。', example: '一个紫色点的 y=1：预测 p=0.9 时损失约 0.105，预测 p=0.1 时损失约 2.303。很有把握却判断错误，会受到更大的惩罚。', question: '损失下降时，准确率每一轮都一定上升吗？', answer: '不一定。概率从 0.6 变成 0.8，损失可以下降，但预测类别仍然是紫色，准确率可能不变。' },
  { title: '一次训练发生了什么', formula: '参数新值 = 参数旧值 − η × 损失对该参数的梯度', guide: 'η（读作 eta）是学习率，控制每次调整的步长；梯度描述损失随参数变化的方向。这里不要求微积分推导。', principle: '先预测 → 计算损失 → 反向传播计算梯度 → 更新权重和偏置 → 再次预测。本实验每一轮使用全部训练样本，进行一次参数更新。', example: '某个权重为 0.5，梯度为 0.2，学习率为 0.3，那么新权重为 0.5−0.3×0.2=0.44。学习率过大可能造成震荡。', question: '训练样本准确率很高，能说明所有新点都会判断正确吗？', answer: '不能。训练样本用于学习；还需要用未参与训练的数据检验模型。实验会同时展示验证集准确率。' },
  { title: '准备好，开始你的第一次实验', formula: '先猜一猜 → 默认训练 → 观察变化 → 只改一个变量', guide: '任务：让网络根据点的位置区分橙色类和紫色类。先使用默认参数，不需要一次理解所有设置。', principle: '左上观察数据与分类边界；右上观察网络结构；左下控制实验；右下观察损失、准确率和固定新点的概率变化。', example: '先点击图中的一个位置并猜它的类别，再开始训练。然后重置，只改变学习率，比较相同轮数下的结果。进一步尝试圆形分布或标签噪声。', question: '三张曲线分别帮我们回答什么问题？', answer: '损失：错得多不多？准确率：判断正确的比例多高？固定点概率：模型对同一个新点的判断怎样变化？' },
]
// 每页只保留核心含义、一个例子和一句提醒，完整展示而不折叠内容。
const summaries = [
  ['x₁、x₂ 是点的横纵坐标；p 是紫色概率。橙色标签为 0，紫色为 1。', '模型根据坐标学习类别。颜色是正确答案，不作为输入。', '新点 (−0.2, 0.3) 输出 p=0.8：紫色概率为 80%，按 50% 阈值预测为紫色。', '只输入坐标，不提前告诉模型答案。'],
  ['w 是权重，b 是偏置，z 是加权求和结果。', '输入乘权重再求和，加上偏置。训练就是调整这些参数。', 'x₁=0.2，x₂=0.6，w₁=−1，w₂=2，b=−0.1：z=−0.2+1.2−0.1=0.9。', '其他量不变，b 增加 0.1，z 也增加 0.1。'],
  ['hⱼ 是隐藏输出；Σ 表示求和；vⱼ、c 是输出参数。tanh 输出 −1 至 1，σ 输出 0 至 1。', '2 个输入 → 4 个隐藏神经元 → 1 个概率输出。非线性激活帮助网络学习弯曲边界。', '圆心的紫色点与外围的橙色点难用直线分开，隐藏层可以学习弯曲边界。', '紫色概率为 p，橙色为 1−p。这里用小型网络入门，深度网络通常有更多层。'],
  ['N 是样本数；y 是正确标签；p 是紫色概率；ln 是自然对数。L 为平均损失。', '损失衡量预测偏差，也考虑把握程度；准确率只统计类别判断是否正确。', '紫色点 y=1：p=0.9 时损失约 0.105；p=0.1 时约 2.303。自信地答错，损失更大。', '概率从 0.6 变为 0.8，损失可下降，但准确率可能不变。不必手算对数。'],
  ['η 是学习率，控制调整步长；梯度描述损失随参数变化的方向。', '预测 → 算损失 → 反向传播求梯度 → 更新参数。本实验每轮用全部训练样本更新一次。', '权重 0.5，梯度 0.2，学习率 0.3：新权重=0.5−0.3×0.2=0.44。', '步长过大可能震荡。训练成绩好不等于新点都答对，还要查看验证集表现。'],
  ['任务：只根据位置，区分橙色与紫色两类点。先用默认参数训练。', '左上看数据，右上看网络，左下调设置，右下看三张训练曲线。', '选一个新点并猜类别 → 开始训练 → 重置 → 只改学习率，比较同一轮数下的结果。', '损失看偏差，准确率看答对比例，概率曲线跟踪同一个新点。'],
]
pages.forEach((item, i) => {
  const [guide, principle, example, answer] = summaries[i]
  Object.assign(item, { guide, principle, example, answer })
})
const page = ref(0), experiment = ref(false), experimentExpanded = ref(false)

const lesson = computed(() => pages[page.value])
// 按课程面板实际可用空间等比适配，四个模块始终同屏，不裁切内容。
const experimentViewport = ref<HTMLElement | null>(null)
const boardScale = ref(1)
const boardStyle = computed(() => ({
  transform: experimentExpanded.value
    ? `translate(-50%, -50%) scale(${boardScale.value})`
    : `translateX(-50%) scale(${boardScale.value})`
}))
let boardObserver: ResizeObserver | undefined
watch(experimentViewport, element => {
  boardObserver?.disconnect()
  if (!element) return
  const resize = () => { boardScale.value = Math.min(element.clientWidth / 1000, element.clientHeight / 600) }
  boardObserver = new ResizeObserver(resize)
  boardObserver.observe(element)
  resize()
}, { flush: 'post' })
let previousBodyOverflow = ''
function closeExpandedExperiment() { experimentExpanded.value = false }
function handleExperimentKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') closeExpandedExperiment()
}
watch(experimentExpanded, expanded => {
  if (expanded) {
    previousBodyOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', handleExperimentKeydown)
  } else {
    document.body.style.overflow = previousBodyOverflow
    window.removeEventListener('keydown', handleExperimentKeydown)
  }
}, { flush: 'post' })
onBeforeUnmount(() => {
  boardObserver?.disconnect()
  window.removeEventListener('keydown', handleExperimentKeydown)
  if (experimentExpanded.value) document.body.style.overflow = previousBodyOverflow
})
const kind = ref('linear'), noise = ref(0), rate = ref(0.3), target = ref(300), speed = ref(10)
const net = ref(network()), samples = ref(dataset('linear', 0)), validation = ref(dataset('linear', 0, 2026, 100))
const point = ref({ x: -0.2, y: 0.3 }), epoch = ref(0), running = ref(false)
type RecordPoint = { epoch: number; loss: number; accuracy: number; validation: number; probability: number }
const history = ref<RecordPoint[]>([])
let timer: ReturnType<typeof setInterval> | undefined
function pause() { if (timer !== undefined) clearInterval(timer); timer = undefined; running.value = false }
function record() { history.value.push({ epoch: epoch.value, ...metrics(net.value, samples.value), validation: metrics(net.value, validation.value).accuracy, probability: forward(net.value, point.value.x, point.value.y).p }) }
function reset() { pause(); net.value = network(); epoch.value = 0; history.value = []; record() }
watch([kind, noise], () => { samples.value = dataset(kind.value, noise.value); validation.value = dataset(kind.value, 0, 2026, 100); reset() })
watch(rate, reset)
watch(target, () => { if (epoch.value >= target.value) pause() })
function step(count = 1) {
  for (let i = 0; i < count && epoch.value < target.value; i++) { train(net.value, samples.value, rate.value); epoch.value++; record() }
  if (epoch.value >= target.value) pause()
}
function start() { if (running.value || epoch.value >= target.value) return; running.value = true; timer = setInterval(() => step(speed.value), 120) }
function leave() { closeExpandedExperiment(); pause(); experiment.value = false }
onBeforeUnmount(pause)
reset()
const current = computed(() => history.value[history.value.length - 1])
const probability = computed(() => forward(net.value, point.value.x, point.value.y).p)
const activations = computed(() => forward(net.value, point.value.x, point.value.y).h)
const cells = computed(() => Array.from({ length: 400 }, (_, i) => {
  const col = i % 20, row = Math.floor(i / 20), p = forward(net.value, (col + 0.5) / 10 - 1, 1 - (row + 0.5) / 10).p
  return { x: col * 15, y: row * 15, color: `rgb(${Math.round(255 - 79 * p)},${Math.round(222 - 62 * p)},${Math.round(177 + 37 * p)})` }
}))
function pick(event: MouseEvent) {
  if (epoch.value > 0 || running.value) return
  const rect = event.currentTarget instanceof Element ? event.currentTarget.getBoundingClientRect() : null
  if (!rect) return
  point.value = { x: Math.max(-1, Math.min(1, (event.clientX - rect.left) / rect.width * 2 - 1)), y: Math.max(-1, Math.min(1, 1 - (event.clientY - rect.top) / rect.height * 2)) }
  history.value = []; record()
}
const charts = ['损失函数', '准确率', '固定点预测概率']
const lossMax = computed(() => Math.max(1, ...history.value.map(r => r.loss)) * 1.05)
function curve(key: 'loss' | 'accuracy' | 'validation' | 'probability', inverse = false) {
  const max = key === 'loss' ? lossMax.value : 1
  const end = Math.max(target.value, epoch.value)
  return history.value.map(r => `${28 + r.epoch / end * 152},${128 - (inverse ? 1 - r[key] : r[key]) / max * 110}`).join(' ')
}
</script>

<template>
  <section class="deep-lesson" :class="{ 'compact-lesson': !experiment, 'single-screen-experiment': experiment }">
    <template v-if="!experiment">
      <header><span class="eyebrow">深度学习基础 · 算法讲解</span><h3>{{ lesson.title }}</h3></header>
      <nav class="steps" aria-label="讲解章节"><button v-for="(item, i) in pages" :key="item.title" :class="{ active: page === i }" :aria-current="page === i ? 'step' : undefined" @click="page = i">{{ i + 1 }}. {{ ['分类问题', '神经元', '网络结构', '损失函数', '训练原理', '实验任务'][i] }}</button></nav>
      <div class="formula"><small>本页公式 / 核心流程</small><code>{{ lesson.formula }}</code></div>
      <div class="explanation"><article><h4>符号与含义</h4><p>{{ lesson.guide }}</p><h4>原理讲解</h4><p>{{ lesson.principle }}</p></article><article><h4>一个例子</h4><p>{{ lesson.example }}</p><h4>记住这一点</h4><p class="answer">{{ lesson.answer }}</p></article></div>
      <footer class="lesson-pagination">
        <button :disabled="page === 0" @click="page--">上一页</button>
        <div class="lesson-page-dots">
          <button v-for="(item, i) in pages" :key="item.title" :class="{ active: page === i }"
                  :aria-label="item.title" :aria-current="page === i ? 'step' : undefined" @click="page = i"></button>
        </div>
        <span aria-live="polite">{{ page + 1 }} / {{ pages.length }}</span>
        <button v-if="page < pages.length - 1" class="lesson-next" @click="page++">下一页</button>
        <button v-else class="lesson-next" @click="experiment = true">进入神经网络实验 →</button>
      </footer>
    </template>
    <template v-else>
      <Teleport to="body" :disabled="!experimentExpanded">
      <div class="experiment-shell" :class="{ 'experiment-shell--expanded': experimentExpanded }"
           :role="experimentExpanded ? 'dialog' : undefined"
           :aria-modal="experimentExpanded ? 'true' : undefined" aria-label="神经网络实验放大视图"
           @click.self="closeExpandedExperiment">
      <div ref="experimentViewport" class="experiment-viewport"><div class="experiment-board" :style="boardStyle">
      <header class="experiment-head"><div><span v-if="!experimentExpanded" class="eyebrow">深度学习基础 · 神经网络实验</span><h3>看见神经网络学会分类</h3><p>点击散点图选择一个十字新点，观察模型训练后如何根据位置预测类别。</p></div><div class="experiment-head-actions"><button @click="leave">← 返回讲解</button><button v-if="!experimentExpanded" class="experiment-expand" @click="experimentExpanded = true"><span aria-hidden="true">⛶</span> 放大实验</button><button v-else class="experiment-close" aria-label="关闭放大实验" title="关闭放大实验" @click="closeExpandedExperiment">×</button></div></header>
      <div class="lab-grid">
        <article class="module"><h4>01 / 数据可视化</h4><div class="data-layout"><svg class="scatter" viewBox="0 0 300 300" role="img" aria-label="橙色与紫色分类散点图；训练前可点击选择新点" @click="pick"><rect v-for="(cell, i) in cells" :key="i" :x="cell.x" :y="cell.y" width="15.2" height="15.2" :fill="cell.color"/><path d="M150 0V300 M0 150H300" stroke="white" stroke-dasharray="4 4"/><circle v-for="(s, i) in samples" :key="i" :cx="(s.x + 1) * 150" :cy="(1 - s.y) * 150" r="4.3" :fill="s.label ? '#805bb5' : '#e58a24'" stroke="white" stroke-width="1.5"/><path :d="`M${(point.x + 1) * 150 - 7} ${(1 - point.y) * 150}h14 M${(point.x + 1) * 150} ${(1 - point.y) * 150 - 7}v14`" stroke="#41334f" stroke-width="2.5"/></svg><div class="legend"><p><i class="orange"/>橙色类（0）</p><p><i class="purple"/>紫色类（1）</p><p>横轴 x₁ / 纵轴 x₂<br>坐标范围 −1 至 1</p><strong>P(紫色) = {{ (probability * 100).toFixed(1) }}%</strong><p>新点 ({{ point.x.toFixed(2) }}, {{ point.y.toFixed(2) }})</p></div></div></article>
        <article class="module model-module"><h4>02 / 模型结构与可视化</h4><div class="model-flow" aria-hidden="true"><span><b>① 输入坐标</b><small>新点的位置</small></span><i>乘权重 →</i><span><b>② 提取特征</b><small>4 个隐藏神经元</small></span><i>求和 + σ →</i><span><b>③ 输出概率</b><small>选择可能性更高的一类</small></span></div><svg class="network" viewBox="0 0 520 190" role="img" aria-label="新点的横纵坐标进入网络，经四个隐藏神经元提取特征，最后输出橙色和紫色的概率"><g v-for="(_, j) in net.w" :key="j"><line v-for="(_, i) in net.w[j]" :key="i" x1="82" :y1="65 + i * 70" x2="253" :y2="36 + j * 39" :stroke="net.w[j][i] >= 0 ? '#e58a24' : '#805bb5'" :stroke-width="Math.min(3.5, 0.7 + Math.abs(net.w[j][i]))" opacity="0.46"/><line x1="274" :y1="36 + j * 39" x2="370" y2="92" :stroke="net.v[j] >= 0 ? '#e58a24' : '#805bb5'" :stroke-width="Math.min(3.5, 0.7 + Math.abs(net.v[j]))" opacity="0.46"/><circle cx="264" :cy="36 + j * 39" r="16" fill="#805bb5" :fill-opacity="0.22 + (activations[j] + 1) * 0.3" stroke="#805bb5"/><text x="257" :y="40 + j * 39" class="node-name">h{{ j + 1 }}</text><text x="288" :y="40 + j * 39" class="node-value">{{ activations[j].toFixed(2) }}</text></g><circle cx="72" cy="65" r="19" fill="#ffdfb3" stroke="#e58a24"/><circle cx="72" cy="135" r="19" fill="#ffdfb3" stroke="#e58a24"/><text x="63" y="70" class="node-name">x₁</text><text x="8" y="43" class="axis-label">横坐标</text><text x="8" y="64" class="input-value">{{ point.x.toFixed(2) }}</text><text x="63" y="140" class="node-name">x₂</text><text x="8" y="113" class="axis-label">纵坐标</text><text x="8" y="134" class="input-value">{{ point.y.toFixed(2) }}</text><circle cx="376" cy="92" r="22" fill="#eee6f6" stroke="#805bb5" stroke-width="2"/><text x="369" y="97" class="node-name">p</text><text x="409" y="52" class="orange-output">橙色  {{ ((1 - probability) * 100).toFixed(1) }}%</text><rect x="409" y="61" width="94" height="9" rx="4.5" fill="#f3eadf"/><rect x="409" y="61" :width="94 * (1 - probability)" height="9" rx="4.5" fill="#e58a24"/><text x="409" y="110" class="purple-output">紫色  {{ (probability * 100).toFixed(1) }}%</text><rect x="409" y="119" width="94" height="9" rx="4.5" fill="#eee8f3"/><rect x="409" y="119" :width="94 * probability" height="9" rx="4.5" fill="#805bb5"/><text x="409" y="154" class="prediction">预测：{{ probability >= 0.5 ? '紫色类' : '橙色类' }}</text><text x="165" y="181" class="weight-guide">连线颜色表示权重方向，粗细表示影响大小</text></svg><p class="hint model-hint">读图顺序：输入新点坐标 → 隐藏层组合位置特征 → 输出两类概率；概率较高的类别就是当前预测。</p></article>
        <article class="module settings-module"><h4>03 / 实验设置</h4><div class="controls"><label>数据分布<select v-model="kind"><option value="linear">两类分区 · 入门</option><option value="circle">圆形分布 · 进阶</option></select></label><label>标签噪声<select v-model.number="noise"><option :value="0">0% · 干净数据</option><option :value="0.1">10% · 随机翻转标签</option><option :value="0.2">20% · 随机翻转标签</option></select></label><label>学习率<select v-model.number="rate"><option :value="0.03">0.03 · 小步学习</option><option :value="0.3">0.3 · 标准</option><option :value="3">3 · 大步探索</option></select></label><label>目标训练轮数<select v-model.number="target"><option :value="100">100 轮</option><option :value="300">300 轮</option><option :value="1000">1000 轮</option></select></label><label>自动播放速度<select v-model.number="speed"><option :value="1">1 轮 / 周期</option><option :value="10">10 轮 / 周期</option><option :value="30">30 轮 / 周期</option></select></label><div class="status" role="status">{{ running ? '正在训练' : epoch >= target ? '训练完成' : epoch ? '已暂停' : '准备就绪' }}<br>第 {{ epoch }} / {{ target }} 轮</div></div><div class="actions"><button v-if="running" class="primary" @click="pause">暂停训练</button><button v-else class="primary" :disabled="epoch >= target" @click="start">{{ epoch ? '继续训练' : '开始训练' }}</button><button :disabled="running || epoch >= target" @click="step()">单步训练</button><button @click="reset">重置</button></div><p class="hint">改变数据或学习率会重置训练，便于公平比较。重置保留同一新点和随机种子。先默认训练，再只改一个变量。</p></article>
        <article class="module"><h4>04 / 实验过程可视化</h4><div class="charts"><div v-for="(title, i) in charts" :key="title" class="chart"><h5>{{ title }}</h5><svg viewBox="0 0 200 160" role="img" :aria-label="title"><path v-for="y in [18, 73, 128]" :key="y" :d="`M28 ${y}H180`" stroke="#eee8f3"/><path d="M28 18V128H180" fill="none" stroke="#b8abc5"/><text x="2" y="22">{{ i === 0 ? lossMax.toFixed(1) : '1.0' }}</text><text x="10" y="131">0</text><text x="25" y="143">0</text><text x="158" y="143">{{ Math.max(target, epoch) }}</text><polyline :points="curve(i === 0 ? 'loss' : i === 1 ? 'accuracy' : 'probability')" fill="none" stroke="#805bb5" stroke-width="2"/><polyline v-if="i === 1" :points="curve('validation')" fill="none" stroke="#e58a24" stroke-width="2" stroke-dasharray="4 3"/><polyline v-if="i === 2" :points="curve('probability', true)" fill="none" stroke="#e58a24" stroke-width="2"/><text x="76" y="158">训练轮数</text></svg><p v-if="i === 0">当前 {{ current.loss.toFixed(3) }}</p><p v-else-if="i === 1"><span class="purple-text">训练 {{ (current.accuracy * 100).toFixed(0) }}%</span><br><span class="orange-text">验证 {{ (current.validation * 100).toFixed(0) }}%（虚线）</span></p><p v-else><span class="orange-text">橙色 {{ ((1 - probability) * 100).toFixed(1) }}%</span><br><span class="purple-text">紫色 {{ (probability * 100).toFixed(1) }}%</span></p></div></div><p class="hint">验证集为另外 100 个无噪声样本，不参与训练。反复据此调参后，仍需新的测试集评估泛化能力。概率高不保证正确。</p></article>
      </div>
      <p class="reflection">实验复盘：分类边界如何变化？损失下降时准确率一定上升吗？每次只改一个变量进行比较。</p>
      </div></div>
      </div>
      </Teleport>
    </template>
  </section>
</template>

<style scoped>
.deep-lesson{color:#60516e;padding:8px;width:100%;box-sizing:border-box}.deep-lesson *{box-sizing:border-box}header h3{font-size:26px;margin:10px 0}header p,.hint{color:#8b7d97;line-height:1.65}.eyebrow{font-size:12px;color:#947aad}button,select{font:inherit;color:inherit;border:1px solid #e5ddef;border-radius:9px;background:white;padding:10px 15px}button{cursor:pointer}button:hover:not(:disabled){border-color:#967bb2;background:#f8f4fc}button:disabled{opacity:.45;cursor:not-allowed}button:focus-visible,select:focus-visible{outline:2px solid #805bb5;outline-offset:3px}.primary{background:#9276af;color:white;border-color:#9276af}.primary:hover:not(:disabled){background:#805bb5;color:white}.steps{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0}.steps button{font-size:13px}.steps .active{background:#eee6f6;border-color:#9276af;color:#69458d}.formula{background:#f7f3fb;border:1px solid #e5ddef;border-radius:14px;padding:24px}.formula small{color:#8b7d97}.formula code{display:block;white-space:pre-wrap;font-size:21px;line-height:1.8;margin-top:12px;overflow-wrap:anywhere}.explanation{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin:20px 0;min-height:290px}.explanation article,.module{border:1px solid #e5ddef;border-radius:14px;padding:20px;background:#fff}.explanation h4{margin:0 0 10px}.explanation p{line-height:1.9;margin:0 0 20px}.text-btn{padding:6px 12px;color:#805bb5}.answer{background:#faf6ee;border-radius:8px;padding:12px;margin-top:10px!important}footer{display:flex;align-items:center;justify-content:space-between;border-top:1px solid #eee8f3;padding-top:18px}.experiment-head{display:flex;justify-content:space-between;align-items:center;gap:16px}.experiment-head button{flex-shrink:0}.lab-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;margin-top:22px}.module{min-width:0;padding:18px}.module h4{font-size:17px;margin:0 0 16px}.data-layout{display:flex;align-items:center;gap:14px}.scatter{width:65%;max-height:300px;aspect-ratio:1;border-radius:12px;cursor:crosshair}.legend{flex:1;font-size:12px;line-height:1.7}.legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}.orange{background:#e58a24}.purple{background:#805bb5}.network{width:100%;height:285px}.network text{font-size:13px;fill:#60516e}.hint{font-size:12px;margin:12px 0 0}.controls{display:grid;grid-template-columns:1fr 1fr;gap:14px}.controls label{font-size:13px;display:flex;flex-direction:column;gap:6px}.controls select{width:100%;padding:9px 7px}.status{font-size:13px;line-height:1.8;align-self:center;color:#805bb5}.actions{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}.charts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.chart{border:1px solid #e5ddef;border-radius:10px;padding:10px 3px;text-align:center;min-width:0}.chart h5{margin:3px 0 12px;font-size:13px}.chart svg{width:100%;margin-top:8px}.chart text{font-size:10px;fill:#8b7d97}.chart p{font-size:11px;line-height:1.8}.orange-text{color:#b76711}.purple-text{color:#805bb5}.reflection{margin-top:16px;background:#faf7fd;padding:14px;border-radius:10px;font-size:13px;line-height:1.8}.reflection summary{cursor:pointer}@media(max-width:1100px){.data-layout{flex-direction:column}.scatter{width:100%;max-width:260px}.legend{width:100%;display:flex;flex-wrap:wrap;gap:8px;align-items:center}.legend p{margin:0}.network{height:310px}}@media(max-width:760px){.lab-grid,.explanation{grid-template-columns:1fr}.experiment-head{align-items:flex-start;flex-direction:column}header h3{font-size:22px}.formula code{font-size:17px}.deep-lesson{padding:0}.network{height:auto}footer{gap:8px;font-size:13px}.charts{gap:4px}}
/* 讲解页随面板宽高排版：公式、双栏正文和底部分页共同铺满一屏。 */
.compact-lesson{padding:0;max-width:none;margin:0;height:100%;min-height:0;flex:1;container-type:size;display:flex;flex-direction:column;gap:clamp(8px,1.8cqh,18px)}
.compact-lesson header{flex:none}
.compact-lesson .eyebrow{font-size:clamp(12px,1.9cqh,16px)}
.compact-lesson header h3{font-size:clamp(21px,min(3.8cqh,3cqw),34px);line-height:1.25;margin:5px 0 0}
.compact-lesson .steps{flex:none;gap:8px;margin:0}
.compact-lesson .steps button{font-size:clamp(12px,1.9cqh,16px);padding:clamp(6px,1.2cqh,11px) 12px}
.compact-lesson .formula{flex:0 0 24%;display:flex;flex-direction:column;justify-content:center;padding:clamp(12px,2.5cqh,24px);border-radius:12px;min-height:0}
.compact-lesson .formula small{font-size:clamp(12px,1.9cqh,16px)}
.compact-lesson .formula code{font-size:clamp(17px,min(3.7cqh,2.5cqw),32px);line-height:1.5;margin-top:clamp(6px,1.5cqh,14px)}
.compact-lesson .explanation{flex:1;gap:clamp(12px,2cqw,24px);margin:0;min-height:0;grid-template-columns:1fr 1fr}
.compact-lesson .explanation article{min-height:0;padding:clamp(12px,2.5cqh,26px);border-radius:12px;display:grid;grid-template-rows:auto 1fr auto 1fr;gap:clamp(6px,1.2cqh,12px);align-content:stretch}
.compact-lesson .explanation h4{font-size:clamp(15px,min(2.7cqh,2cqw),23px);line-height:1.3;margin:0}
.compact-lesson .explanation p{font-size:clamp(14px,min(2.5cqh,1.8cqw),22px);line-height:1.65;margin:0;overflow-wrap:anywhere}
.compact-lesson .answer{padding:8px 12px;margin:0!important;align-self:start}


.single-screen-experiment{height:100%;min-height:0;flex:1;padding:0;color:#202124}
.experiment-shell,.experiment-shell *{box-sizing:border-box}
.experiment-shell{width:100%;height:100%;min-height:0}
.experiment-shell--expanded{position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;padding:24px;background:rgba(24,18,29,.74);backdrop-filter:blur(3px)}
.experiment-shell--expanded .experiment-viewport{width:min(1500px,calc(100vw - 48px));height:min(900px,calc(100vh - 48px));flex:none;overflow:hidden;border:1px solid #cdbbd9;border-radius:18px;background:#fff;box-shadow:0 24px 70px rgba(0,0,0,.36)}
.experiment-shell--expanded .experiment-board{top:50%;transform-origin:center center}
.experiment-viewport{position:relative;width:100%;height:100%;min-height:0}
.experiment-board{position:absolute;left:50%;top:0;width:1000px;height:600px;transform-origin:top center;display:flex;flex-direction:column;gap:10px}
.experiment-board .experiment-head{height:70px;flex:none;flex-direction:row;align-items:center}
.experiment-board .experiment-head-actions{display:flex;align-items:center;gap:12px;flex:none}
.experiment-board .experiment-expand{background:#f5a623;border-color:#f5a623;color:#fff}
.experiment-board .experiment-expand:hover:not(:disabled){background:#e89016;border-color:#e89016;color:#fff}
.experiment-board .experiment-close{display:grid;place-items:center;width:34px;min-width:34px;height:34px;padding:0;border-radius:50%;background:#fff7eb;border-color:#e7a348;color:#8b5616;font-size:22px;line-height:1}
.experiment-board .experiment-close:hover:not(:disabled){background:#f5a623;border-color:#f5a623;color:#fff}
.experiment-board header h3{font-size:21px;margin:3px 0}
.experiment-board .eyebrow{color:#444}
.experiment-board header h3{color:#181818}
.experiment-board header p{font-size:12px;margin:0;color:#444}
.experiment-board button{font-size:12px;padding:7px 12px}
.experiment-board .experiment-head-actions>button:not(.experiment-close){min-height:40px;padding:9px 17px;border-radius:11px;font-size:14px;font-weight:600}
.experiment-board .lab-grid{flex:1;min-height:0;margin:0;gap:10px;grid-template-columns:repeat(12,minmax(0,1fr));grid-template-rows:1fr 1fr}
.experiment-board .module:nth-child(1){grid-column:span 4}
.experiment-board .module:nth-child(2){grid-column:span 8}
.experiment-board .module:nth-child(3){grid-column:span 4}
.experiment-board .module:nth-child(4){grid-column:span 8}
.experiment-board .module{padding:12px;min-height:0;display:flex;flex-direction:column;border-color:#cdbbd9}
.experiment-board .module h4{font-size:15px;margin:0 0 6px;flex:none;color:#202124}
.experiment-board .data-layout{flex:1;min-height:0;flex-direction:row;gap:12px}
.experiment-board .scatter{width:168px;height:168px;max-width:none;max-height:none;flex:none}
.experiment-board .legend{display:block;width:auto;font-size:12px;line-height:1.5;color:#202124}
.experiment-board .legend p{margin:5px 0}
.experiment-board .model-module{display:grid;grid-template-columns:118px minmax(0,1fr);grid-template-rows:auto minmax(0,1fr) auto;column-gap:8px}
.experiment-board .model-module>h4{grid-column:1/-1;grid-row:1}
.experiment-board .model-module>.network{grid-column:2;grid-row:2;width:100%;height:100%;min-height:0;transform:translateX(-8px) scale(1.05);transform-origin:center}
.experiment-board .model-module>.model-hint{grid-column:1/-1;grid-row:3}
.experiment-board .model-flow{grid-column:1;grid-row:2;display:grid;grid-template-columns:1fr;grid-template-rows:auto auto auto auto auto;align-content:center;gap:6px;min-width:0;margin:0}
.experiment-board .model-flow span{padding:5px 7px;border-radius:7px;background:#f8f4fb;text-align:center;line-height:1.2}
.experiment-board .model-flow b{display:block;font-size:11px;color:#202124}
.experiment-board .model-flow small{display:block;margin-top:2px;font-size:9px;color:#4f4f4f}
.experiment-board .model-flow i{font-size:0;color:#555;font-style:normal;text-align:center;white-space:nowrap}
.experiment-board .model-flow i::after{font-size:9px}
.experiment-board .model-flow i:nth-of-type(1)::after{content:'乘权重 ↓'}
.experiment-board .model-flow i:nth-of-type(2)::after{content:'求和 + σ ↓'}
.experiment-board .network .node-name{font-size:12px;font-weight:700;fill:#202124}
.experiment-board .network .node-value{font-size:10px;fill:#333}
.experiment-board .network .axis-label{font-size:9px;fill:#444}
.experiment-board .network .input-value{font-size:11px;font-weight:700;fill:#b76711}
.experiment-board .network .orange-output{font-size:11px;font-weight:700;fill:#b76711}
.experiment-board .network .purple-output{font-size:11px;font-weight:700;fill:#805bb5}
.experiment-board .network .prediction{font-size:12px;font-weight:700;fill:#202124}
.experiment-board .network .weight-guide{font-size:9px;fill:#444}
.experiment-board .network line{stroke-linecap:round;opacity:.58}
.experiment-board .model-hint{padding:4px 7px;border-radius:6px;background:#faf7fd;color:#252525}
.experiment-board .hint{font-size:11px;line-height:1.4;margin:6px 0 0;flex:none;color:#333}
.experiment-board .settings-module{padding:10px}
.experiment-board .settings-module .controls{gap:4px 7px;grid-template-columns:repeat(2,minmax(0,1fr));flex:none}
.experiment-board .settings-module .controls label{font-size:10px;gap:2px;color:#202124}
.experiment-board .settings-module .controls select{padding:3px 5px;font-size:11px;color:#202124}
.experiment-board .status{font-size:12px;line-height:1.4}
.experiment-board .settings-module .status{font-size:10px;line-height:1.35;color:#202124}
.experiment-board .settings-module .actions{gap:5px;margin-top:6px;flex-wrap:nowrap;flex:none}
.experiment-board .settings-module .actions button{padding:5px 7px;font-size:10px}
.experiment-board .settings-module>.hint{margin-top:auto;padding-top:5px;font-size:9px;line-height:1.35}
.experiment-board .charts{flex:1;min-height:0;gap:8px}
.experiment-board .chart{display:flex;flex-direction:column;padding:6px 3px;min-height:0}
.experiment-board .module:nth-child(4) .chart{padding:7px 5px}
.experiment-board .chart h5{font-size:13px;margin:0 0 3px;color:#202124}
.experiment-board .chart svg{flex:1;min-height:0;height:0;margin:0;width:100%}
.experiment-board .chart text{fill:#3f3f3f}
.experiment-board .chart p{font-size:11px;line-height:1.3;margin:3px 0 0}
.experiment-board .reflection{flex:none;font-size:11px;line-height:1.5;margin:0;padding:5px 10px;color:#202124}
</style>

<style scoped src="../../styles/lesson-pagination.css"></style>
