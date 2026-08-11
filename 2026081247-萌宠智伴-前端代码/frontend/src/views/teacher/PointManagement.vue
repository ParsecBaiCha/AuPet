<template>
  <div class="points-container">
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="selectedClass" placeholder="请选择班级" @change="handleClassChange" style="width: 140px">
          <el-option v-for="cls in classList" :key="cls" :label="cls" :value="cls" />
        </el-select>
        <el-input v-model="searchText" placeholder="搜索学生姓名" clearable style="width: 160px; margin-left: 12px">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
      <div class="filter-right">
        <el-button @click="showGroupDialog = true">管理小组</el-button>
        <el-button type="primary" @click="handlePublishTask" style="background: #f48d45; border-color: #f48d45">+ 发布任务</el-button>
      </div>
    </div>

    <div class="main-content">
      <aside class="group-sidebar">
        <div class="sidebar-header">
          <span>学习小组</span>
          <el-button link @click="showGroupDialog = true"><el-icon><Plus /></el-icon></el-button>
        </div>
        <div class="group-list">
          <div class="group-item" :class="{ active: selectedGroupId === null }" @click="selectGroup(null)">
            <span class="group-name">全部学生</span>
          </div>
          <div v-for="group in groups" :key="group.id" class="group-item" :class="{ active: selectedGroupId === group.id }" @click="selectGroup(group.id)">
            <span class="group-name">{{ group.name }}</span>
          </div>
        </div>
      </aside>

      <div class="student-panel">
        <div class="panel-header">
          <div class="panel-title">
            <span>{{ currentGroupName }}</span>
            <span class="student-count">共 {{ filteredStudents.length }} 人</span>
          </div>
          <el-button type="primary" link @click="handleGroupPoints" :disabled="!selectedGroupId">
            <el-icon><Edit /></el-icon>小组加减分
          </el-button>
        </div>

        <el-table :data="displayedStudents" border stripe style="width: 100%">
          <el-table-column type="index" label="排名" width="60" />
          <el-table-column prop="name" label="姓名" min-width="80" />
          <el-table-column prop="class" label="班级" min-width="100" />
          <el-table-column prop="points" label="积分" min-width="80">
            <template #default="{ row }">
              <span class="points-value">{{ row.points }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="petLevel" label="宠物等级" min-width="90">
            <template #default="{ row }">
              <el-tag :type="getPetLevelType(row.petLevel)" size="small">{{ row.petLevel }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="taskCompletionRate" label="任务完成率" min-width="120">
            <template #default="{ row }">
              <div class="rate-cell">
                <el-progress :percentage="row.taskCompletionRate" :stroke-width="6" :show-text="false" :color="getRateColor(row.taskCompletionRate)" />
                <span class="rate-text">{{ row.taskCompletionRate }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="moodIndex" label="心情指数" min-width="120">
            <template #default="{ row }">
              <div class="rate-cell">
                <el-progress :percentage="row.moodIndex" :stroke-width="6" :show-text="false" :color="getMoodColor(row.moodIndex)" />
                <span class="rate-text">{{ row.moodIndex }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="personality" label="性格分析" min-width="180">
            <template #default="{ row }">
              <el-button type="primary" link @click="analyzePersonality(row)">
                <el-icon><TrendCharts /></el-icon>
                {{ row.personality ? '查看' : '分析' }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="190" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleViewDetail(row)">详情</el-button>
              <el-button type="primary" link @click="handleEditPoints(row)">积分</el-button>
              <el-button type="primary" link @click="handleChangeGroup(row)">调组</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="filteredStudents.length"
            :page-sizes="[10, 20, 50]"
            layout="total, prev, pager, next"
            background
          />
        </div>
      </div>
    </div>

    <el-dialog v-model="showGroupDialog" title="管理学习小组" width="500px" class="custom-dialog">
      <div class="group-manage">
        <div class="add-group-row">
          <el-input v-model="newGroupName" placeholder="新小组名称" style="width: 180px" />
          <el-button type="primary" @click="addGroup">添加小组</el-button>
        </div>
        <el-divider />
        <div class="group-list-edit" v-if="groups.length > 0">
          <div v-for="group in groups" :key="group.id" class="group-edit-item">
            <div class="group-info">
              <el-tag size="large">{{ group.name }}</el-tag>
              <span class="group-meta">{{ group.memberCount }}人 · {{ group.totalPoints }}分</span>
            </div>
            <el-button type="danger" link @click="deleteGroup(group)">删除</el-button>
          </div>
        </div>
        <el-empty v-else description="暂无小组" :image-size="60" />
      </div>
      <template #footer>
        <el-button @click="showGroupDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showChangeGroupDialog" title="调整小组" width="420px" class="custom-dialog">
      <el-form label-position="top">
        <el-form-item label="学生">
          <el-tag size="large">{{ changeGroupForm.studentName }}</el-tag>
        </el-form-item>
        <el-form-item label="调整到">
          <el-select v-model="changeGroupForm.newGroupId" placeholder="选择小组" style="width: 100%">
            <el-option label="不分组" :value="0" />
            <el-option v-for="g in availableGroups" :key="g.id" :label="`${g.name} (${g.memberCount}人)`" :value="g.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChangeGroupDialog = false">取消</el-button>
        <el-button type="primary" @click="saveGroupChange">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showGroupPointsDialog" title="小组加减分" width="500px" class="custom-dialog">
      <div class="group-points-form">
        <div class="selected-group center">
          <el-tag type="warning" size="large">{{ currentGroupName }}</el-tag>
        </div>
        <div class="points-rules-grid">
          <div v-for="rule in groupPointRules" :key="rule.id" class="rule-card" :class="{ selected: selectedGroupRuleId === rule.id }" @click="selectGroupRule(rule)">
            <span class="rule-name">{{ rule.name }}</span>
            <span class="rule-points" :class="rule.points > 0 ? 'add' : 'sub'">{{ rule.points > 0 ? '+' : '' }}{{ rule.points }}</span>
          </div>
        </div>
        <el-form label-position="top" style="margin-top: 20px">
          <el-form-item label="积分变动">
            <el-input-number v-model="groupPointsForm.points" :min="-200" :max="200" />
            <span class="points-range">范围: -200 ~ 200</span>
          </el-form-item>
          <el-form-item label="变动原因">
            <el-input v-model="groupPointsForm.reason" placeholder="如：课堂表现优秀" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showGroupPointsDialog = false; selectedGroupRuleId = null">取消</el-button>
        <el-button type="primary" @click="submitGroupPoints">确认</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditPointsDialog" title="调整积分" width="420px" class="custom-dialog">
      <div class="add-points-header">
        <el-avatar :size="48" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
        <div class="student-info">
          <span class="name">{{ editPointsForm.name }}</span>
          <span class="current-points">当前积分: {{ editPointsForm.currentPoints }}</span>
        </div>
      </div>
      <el-form label-position="top" style="margin-top: 20px">
        <el-form-item label="积分变动">
          <div class="points-adjust">
            <el-input-number v-model="editPointsForm.points" :min="-100" :max="100" />
            <span class="points-hint">正数为加分，负数为扣分</span>
          </div>
        </el-form-item>
        <el-form-item label="变动原因">
          <el-input v-model="editPointsForm.reason" placeholder="请输入原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditPointsDialog = false">取消</el-button>
        <el-button type="primary" @click="savePoints">确认</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="学生详情" width="600px" class="custom-dialog">
      <div v-if="selectedStudent" class="student-detail">
        <div class="detail-top">
          <el-avatar :size="64" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
          <div class="detail-info">
            <h3>{{ selectedStudent.name }}</h3>
            <p>{{ selectedStudent.class }} · {{ selectedStudent.groupName || '未分组' }}</p>
          </div>
          <div class="detail-points">
            <span class="points-num">{{ selectedStudent.points }}</span>
            <span class="points-label">当前积分</span>
          </div>
        </div>
        <el-divider />
        <div class="detail-stats">
          <div class="stat-item">
            <span class="stat-label">宠物等级</span>
            <el-tag :type="getPetLevelType(selectedStudent.petLevel)" size="large">{{ selectedStudent.petLevel }}</el-tag>
          </div>
          <div class="stat-item">
            <span class="stat-label">任务完成率</span>
            <div class="stat-progress">
              <el-progress :percentage="selectedStudent.taskCompletionRate" :stroke-width="10" :color="getRateColor(selectedStudent.taskCompletionRate)" />
              <span>{{ selectedStudent.taskCompletionRate }}%</span>
            </div>
          </div>
          <div class="stat-item">
            <span class="stat-label">心情指数</span>
            <div class="stat-progress">
              <el-progress :percentage="selectedStudent.moodIndex" :stroke-width="10" :color="getMoodColor(selectedStudent.moodIndex)" />
              <span>{{ selectedStudent.moodIndex }}</span>
            </div>
          </div>
        </div>
        <el-divider />
        <div class="detail-records">
          <h4>积分记录</h4>
          <div class="records-list">
            <div v-for="(record, idx) in studentRecords" :key="idx" class="record-item">
              <span class="record-name">{{ record.name }}</span>
              <span class="record-points" :class="record.points > 0 ? 'add' : 'sub'">{{ record.points > 0 ? '+' : '' }}{{ record.points }}</span>
              <span class="record-time">{{ record.time }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showTaskDialog" title="发布积分任务" width="520px" class="task-dialog">
      <div class="dialog-header">
        <el-avatar :size="40" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
        <div class="dialog-user">
          <span class="user-name">{{ store.user?.name || '教师' }}</span>
          <span class="user-role">正在发布积分任务</span>
        </div>
      </div>
      <el-form label-position="top">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.name" placeholder="请输入任务名称，如：每日阅读打卡" maxlength="30" show-word-limit />
        </el-form-item>
        <el-form-item label="选择积分规则">
          <div class="rules-grid">
            <div v-for="rule in pointRules" :key="rule.id" class="rule-card" :class="{ selected: selectedRuleId === rule.id }" @click="selectRule(rule)">
              <div class="rule-info">
                <span class="rule-name">{{ rule.name }}</span>
                <span class="rule-points" :class="rule.points > 0 ? 'add' : 'sub'">{{ rule.points > 0 ? '+' : '' }}{{ rule.points }}</span>
              </div>
            </div>
          </div>
          <div class="rules-tip">点击选择预设规则，或手动设置积分</div>
        </el-form-item>
        <el-form-item label="奖励积分">
          <div class="points-input">
            <el-input-number v-model="taskForm.points" :min="-50" :max="50" />
            <span class="points-unit">积分</span>
          </div>
          <div class="points-tips">正值加分，负值扣分</div>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker v-model="taskForm.deadline" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" :shortcuts="dateShortcuts" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" @click="publishTask" style="background: #8985cf; border-color: #8985cf">发布任务</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEvaluateDialog" title="群体智能角色管理" width="600px" class="custom-dialog">
      <div v-if="evaluateForm.studentId" class="evaluate-form">
        <div class="evaluate-header">
          <el-avatar :size="56" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
          <div class="student-info">
            <h3>{{ evaluateForm.studentName }}</h3>
            <span>{{ evaluateForm.studentClass }}</span>
          </div>
          <el-tag type="info" style="margin-left: auto">对话分析生成</el-tag>
        </div>
        <div class="chat-analysis">
          <div class="analysis-title">
            <el-icon><ChatDotSquare /></el-icon>
            <span>对话数据分析</span>
          </div>
          <div class="analysis-items">
            <div class="analysis-item">
              <span class="item-label">对话积极性</span>
              <el-progress :percentage="evaluateForm.chatAnalysis.activeRate" :stroke-width="8" :show-text="false" />
              <span class="item-value">{{ evaluateForm.chatAnalysis.activeRate }}%</span>
            </div>
            <div class="analysis-item">
              <span class="item-label">情感倾向</span>
              <div class="emotion-tags">
                <el-tag size="small" type="success">积极 68%</el-tag>
                <el-tag size="small">中性 25%</el-tag>
                <el-tag size="small" type="warning">消极 7%</el-tag>
              </div>
            </div>
            <div class="analysis-item">
              <span class="item-label">关键词提取</span>
              <div class="keyword-tags">
                <el-tag v-for="kw in evaluateForm.chatAnalysis.keywords" :key="kw" size="small">{{ kw }}</el-tag>
              </div>
            </div>
          </div>
        </div>
        <el-divider />
        <el-form label-position="top">
          <el-form-item label="表现分数">
            <el-rate v-model="evaluateForm.score" :max="5" show-text :texts="['很差', '较差', '一般', '良好', '优秀']" />
          </el-form-item>
          <el-form-item label="性格标签（基于对话分析）">
            <div class="ai-traits">
              <el-tag v-for="trait in evaluateForm.aiTraits" :key="trait" type="info" effect="plain">{{ trait }}</el-tag>
            </div>
          </el-form-item>
          <el-form-item label="评价标签">
            <el-checkbox-group v-model="evaluateForm.tags">
              <el-checkbox label="积极主动" />
              <el-checkbox label="思维活跃" />
              <el-checkbox label="遵守纪律" />
              <el-checkbox label="乐于助人" />
              <el-checkbox label="内敛害羞" />
              <el-checkbox label="调皮捣蛋" />
              <el-checkbox label="注意力分散" />
              <el-checkbox label="缺乏自信" />
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="评语">
            <el-input v-model="evaluateForm.comment" type="textarea" :rows="3" placeholder="请输入评语..." />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showEvaluateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEvaluation">保存评价</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPersonalityDialog" title="学生性格分析" width="650px" class="custom-dialog">
      <div v-if="analyzeTarget" class="personality-analysis">
        <div class="analyze-header">
          <el-avatar :size="56" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
          <div class="student-base">
            <h3>{{ analyzeTarget.name }}</h3>
            <span>{{ analyzeTarget.class }}</span>
          </div>
        </div>
        <el-divider />
        <div class="analyze-section">
          <h4><el-icon><TrendCharts /></el-icon> 行为特征分析</h4>
          <div class="trait-list">
            <div v-for="trait in behaviorTraits" :key="trait.label" class="trait-item">
              <span class="trait-label">{{ trait.label }}</span>
              <el-progress :percentage="trait.value" :stroke-width="8" :show-text="false" :color="trait.color" />
              <span class="trait-value">{{ trait.value }}%</span>
            </div>
          </div>
        </div>
        <div class="analyze-section">
          <h4><el-icon><User /></el-icon> 性格标签</h4>
          <div class="personality-tags">
            <el-tag v-for="tag in personalityTags" :key="tag" type="warning">{{ tag }}</el-tag>
          </div>
        </div>
        <div class="analyze-section">
          <h4><el-icon><Reading /></el-icon> 学习风格</h4>
          <div class="learning-style">
            <div class="style-item">
              <span class="style-label">视觉学习</span>
              <el-progress :percentage="learningStyle.visual" :stroke-width="6" color="#acb6f3" />
            </div>
            <div class="style-item">
              <span class="style-label">听觉学习</span>
              <el-progress :percentage="learningStyle.auditory" :stroke-width="6" color="#f4bb6e" />
            </div>
            <div class="style-item">
              <span class="style-label">动手实践</span>
              <el-progress :percentage="learningStyle.practical" :stroke-width="6" color="#8985cf" />
            </div>
          </div>
        </div>
        <div class="analyze-section">
          <h4><el-icon><Connection /></el-icon> 人际关系</h4>
          <div class="relationship-info">
            <div class="rel-item">
              <span class="rel-label">社交主动性</span>
              <el-rate v-model="relationship.socialActive" disabled />
            </div>
            <div class="rel-item">
              <span class="rel-label">团队协作</span>
              <el-rate v-model="relationship.teamwork" disabled />
            </div>
            <div class="rel-item">
              <span class="rel-label">同理心</span>
              <el-rate v-model="relationship.empathy" disabled />
            </div>
          </div>
        </div>
        <div class="analyze-section summary">
          <h4><el-icon><Document /></el-icon> 综合分析</h4>
          <div class="summary-content">
            <p>{{ analyzeTarget.name }} 是一个 <strong>{{ mainPersonality }}</strong> 的学生。</p>
            <p>在学习方面，{{ learningType }}，建议采用 {{ suggestedMethod }} 的教学方式。</p>
            <p>与同学相处时，表现 {{ socialDescription }}，适合参与 {{ suitableActivity }}。</p>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showPersonalityDialog = false">关闭</el-button>
        <el-button type="primary" @click="savePersonalityAnalysis">保存分析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, Edit, TrendCharts, User, Reading, Connection, Document, ChatDotSquare } from '@element-plus/icons-vue'
import { useAppStore } from '../../stores/app'
import { teacherApi } from '../../api/teacher'

const store = useAppStore()

interface Student { id: number; name: string; class: string; groupId: number | null; groupName: string | null; points: number; status: string; petLevel: string; taskCompletionRate: number; moodIndex: number; personality: string }
interface Group { id: number; name: string; className: string; memberCount: number; totalPoints: number }

const classList = ['一年级1班', '一年级2班', '一年级3班', '二年级1班', '二年级2班', '二年级3班', '三年级1班', '三年级2班', '三年级3班', '四年级1班', '四年级2班', '四年级3班', '五年级1班', '五年级2班', '五年级3班', '六年级1班', '六年级2班', '六年级3班']

const groups = ref<Group[]>([])

const students = ref<Student[]>([])

const buildGroupsFromStudents = () => {
  const map = new Map<number, Group>()
  students.value.forEach(s => {
    if (s.groupId != null && s.groupName) {
      if (!map.has(s.groupId)) {
        map.set(s.groupId, { id: s.groupId, name: s.groupName, className: s.class, memberCount: 0, totalPoints: 0 })
      }
      const g = map.get(s.groupId)!
      g.memberCount += 1
      g.totalPoints += s.points
    }
  })
  groups.value = Array.from(map.values())
}

const loadStudents = async () => {
  try {
    const data: any = await teacherApi.getPoints()
    if (Array.isArray(data)) {
      students.value = data
      buildGroupsFromStudents()
    }
  } catch (e) {
    // 接口失败时保持页面可用，使用默认空值
  }
}

const selectedClass = ref('一年级1班')
const selectedGroupId = ref<number | null>(null)
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const getPetLevelType = (level: string) => { if (level === 'S级') return 'danger'; if (level === 'A级') return 'warning'; if (level === 'B级') return 'success'; return 'info' }
const getRateColor = (rate: number) => { if (rate >= 90) return '#f48d45'; if (rate >= 70) return '#f4bb6e'; if (rate >= 50) return '#acb6f3'; return '#8985cf' }
const getMoodColor = (mood: number) => { if (mood >= 80) return '#f48d45'; if (mood >= 60) return '#f4bb6e'; if (mood >= 40) return '#acb6f3'; return '#8985cf' }

const filteredStudents = computed(() => students.value.filter(s => {
  return (!selectedClass.value || s.class === selectedClass.value) && (selectedGroupId.value === null || s.groupId === selectedGroupId.value) && (!searchText.value || s.name.includes(searchText.value))
}).sort((a, b) => b.points - a.points))

const displayedStudents = computed(() => { const start = (currentPage.value - 1) * pageSize.value; return filteredStudents.value.slice(start, start + pageSize.value) })

const currentGroupName = computed(() => { if (selectedGroupId.value === null) return '全部学生'; const g = groups.value.find(g => g.id === selectedGroupId.value); return g?.name || '全部学生' })
const availableGroups = computed(() => { const s = students.value.find(s => s.id === changeGroupForm.studentId); return groups.value.filter(g => !s || g.className === s.class) })

const studentRecords = ref<any[]>([])

const showGroupDialog = ref(false); const showChangeGroupDialog = ref(false); const showGroupPointsDialog = ref(false)
const showEditPointsDialog = ref(false); const showDetailDialog = ref(false); const showTaskDialog = ref(false)
const showEvaluateDialog = ref(false); const showPersonalityDialog = ref(false)
const selectedStudent = ref<Student | null>(null)
const newGroupName = ref('')

const changeGroupForm = reactive({ studentId: 0, studentName: '', newGroupId: 0 })
const groupPointsForm = reactive({ points: 10, reason: '' })
const editPointsForm = reactive({ id: 0, name: '', currentPoints: 0, points: 10, reason: '' })
const taskForm = reactive({ name: '', points: 10, deadline: '' })

const pointRules = ref<any[]>([])
const groupPointRules = ref<any[]>([])

const loadPointRules = async () => {
  try {
    const data: any = await teacherApi.getPointRules()
    if (Array.isArray(data)) {
      pointRules.value = data
      groupPointRules.value = data
    }
  } catch (e) {
    // 接口失败时保持页面可用，使用默认空值
  }
}

const selectedGroupRuleId = ref<number | null>(null); const selectedRuleId = ref<number | null>(null)
const dateShortcuts = [{ text: '今天', value: new Date() }, { text: '明天', value: () => { const d = new Date(); d.setDate(d.getDate() + 1); return d } }, { text: '本周', value: () => { const d = new Date(); d.setDate(d.getDate() + (7 - d.getDay())); return d } }, { text: '下周', value: () => { const d = new Date(); d.setDate(d.getDate() + 14 - d.getDay()); return d } }]

const handleClassChange = () => { selectedGroupId.value = null }
const selectGroup = (id: number | null) => { selectedGroupId.value = id; currentPage.value = 1 }
const selectGroupRule = (rule: any) => { selectedGroupRuleId.value = rule.id; groupPointsForm.points = rule.points; groupPointsForm.reason = rule.name }
const selectRule = (rule: any) => { selectedRuleId.value = rule.id; taskForm.name = rule.name; taskForm.points = rule.points }

const addGroup = () => { if (!newGroupName.value) return; groups.value.push({ id: Date.now(), name: newGroupName.value, className: selectedClass.value || '一年级1班', memberCount: 0, totalPoints: 0 }); newGroupName.value = ''; ElMessage.success('添加成功') }
const deleteGroup = (group: Group) => { const idx = groups.value.findIndex(g => g.id === group.id); if (idx > -1) groups.value.splice(idx, 1); students.value.forEach(s => { if (s.groupId === group.id) { s.groupId = null; s.groupName = null } }); ElMessage.success('删除成功') }
const handleChangeGroup = (row: Student) => { changeGroupForm.studentId = row.id; changeGroupForm.studentName = row.name; changeGroupForm.newGroupId = row.groupId || 0; showChangeGroupDialog.value = true }
const saveGroupChange = () => { const s = students.value.find(s => s.id === changeGroupForm.studentId); if (s) { if (changeGroupForm.newGroupId === 0) { s.groupId = null; s.groupName = null } else { const g = groups.value.find(x => x.id === changeGroupForm.newGroupId); s.groupId = changeGroupForm.newGroupId; s.groupName = g?.name || null } } ElMessage.success('调整成功'); showChangeGroupDialog.value = false }
const handleGroupPoints = () => { if (!selectedGroupId.value) return; groupPointsForm.points = 10; groupPointsForm.reason = ''; selectedGroupRuleId.value = null; showGroupPointsDialog.value = true }
const submitGroupPoints = async () => {
  if (groupPointsForm.points === 0) return
  const groupStudents = students.value.filter(s => s.groupId === selectedGroupId.value)
  try {
    for (const s of groupStudents) {
      await teacherApi.awardPoints({ studentId: s.id, points: groupPointsForm.points, reason: groupPointsForm.reason })
      s.points += groupPointsForm.points
    }
    ElMessage.success('小组加分成功')
  } catch (e) {
    // 错误已由拦截器提示
  }
  showGroupPointsDialog.value = false
  selectedGroupRuleId.value = null
}
const handleEditPoints = (row: Student) => { editPointsForm.id = row.id; editPointsForm.name = row.name; editPointsForm.currentPoints = row.points; editPointsForm.points = 10; editPointsForm.reason = ''; showEditPointsDialog.value = true }
const savePoints = async () => {
  const s = students.value.find(s => s.id === editPointsForm.id)
  if (s) {
    try {
      await teacherApi.awardPoints({ studentId: editPointsForm.id, points: editPointsForm.points, reason: editPointsForm.reason })
      s.points += editPointsForm.points
      ElMessage.success(`${editPointsForm.points > 0 ? '加分' : '扣分'}成功，当前积分: ${s.points}`)
    } catch (e) {
      // 错误已由拦截器提示
    }
  }
  showEditPointsDialog.value = false
}
const handleViewDetail = async (row: Student) => {
  selectedStudent.value = row
  studentRecords.value = []
  showDetailDialog.value = true
  try {
    const data: any = await teacherApi.getPointRecords(row.id)
    if (Array.isArray(data)) studentRecords.value = data
  } catch (e) {
    // 接口失败时保持弹窗可用，记录为空
  }
}
const handlePublishTask = () => { showTaskDialog.value = true }

const evaluateForm = reactive({ studentId: 0, studentName: '', studentClass: '', score: 3, tags: [] as string[], comment: '', aiTraits: [] as string[], chatAnalysis: { activeRate: 75, keywords: ['努力', '认真', '活泼', '友爱'] } })

const analyzeTarget = ref<Student | null>(null)
const behaviorTraits = ref([{ label: '专注力', value: 85, color: '#8985cf' }, { label: '积极性', value: 72, color: '#f4bb6e' }, { label: '自律性', value: 68, color: '#acb6f3' }, { label: '创造力', value: 80, color: '#f48d45' }, { label: '合作性', value: 75, color: '#52c41a' }])
const personalityTags = ref(['积极主动', '思维活跃', '乐于助人'])
const learningStyle = reactive({ visual: 70, auditory: 55, practical: 65 })
const relationship = reactive({ socialActive: 4, teamwork: 4, empathy: 3 })
const mainPersonality = computed(() => analyzeTarget.value?.personality || '')
const learningType = computed(() => learningStyle.visual > 60 ? '偏视觉学习' : learningStyle.auditory > 60 ? '偏听觉学习' : '偏动手实践')
const suggestedMethod = computed(() => learningStyle.visual > 60 ? '图文并茂、多媒体展示' : learningStyle.auditory > 60 ? '讲授讨论、音频视频' : '实验操作、项目实践')
const socialDescription = computed(() => relationship.socialActive >= 4 ? '积极主动' : relationship.socialActive >= 3 ? '较为活跃' : '相对内向')
const suitableActivity = computed(() => relationship.teamwork >= 4 ? '小组合作项目' : relationship.teamwork >= 3 ? '团队竞赛' : '个人展示')

const analyzePersonality = (student: Student) => {
  analyzeTarget.value = student
  behaviorTraits.value = [{ label: '专注力', value: Math.floor(Math.random() * 30) + 60, color: '#8985cf' }, { label: '积极性', value: Math.floor(Math.random() * 30) + 60, color: '#f4bb6e' }, { label: '自律性', value: Math.floor(Math.random() * 30) + 60, color: '#acb6f3' }, { label: '创造力', value: Math.floor(Math.random() * 30) + 60, color: '#f48d45' }, { label: '合作性', value: Math.floor(Math.random() * 30) + 60, color: '#52c41a' }]
  const tags = ['积极主动', '思维活跃', '遵守纪律', '乐于助人', '内敛害羞', '调皮捣蛋', '注意力分散', '缺乏自信']
  personalityTags.value = tags.sort(() => Math.random() - 0.5).slice(0, 4)
  learningStyle.visual = Math.floor(Math.random() * 40) + 50; learningStyle.auditory = Math.floor(Math.random() * 40) + 40; learningStyle.practical = Math.floor(Math.random() * 40) + 50
  relationship.socialActive = Math.floor(Math.random() * 3) + 2; relationship.teamwork = Math.floor(Math.random() * 3) + 2; relationship.empathy = Math.floor(Math.random() * 3) + 2
  showPersonalityDialog.value = true
}
const savePersonalityAnalysis = () => { if (analyzeTarget.value) { analyzeTarget.value.personality = mainPersonality.value; ElMessage.success('性格分析已保存') } showPersonalityDialog.value = false }

const generateAiTraits = (student: Student) => { const t = []; if (student.moodIndex >= 80) t.push('情绪稳定'); if (student.taskCompletionRate >= 80) t.push('任务执行力强'); if (student.petLevel === 'S级' || student.petLevel === 'A级') t.push('综合表现优异'); if (student.points >= 800) t.push('积分积累快'); t.push('善于表达', '团队协作'); return t.slice(0, 4) }
const generateKeywords = (personality: string) => { const k: string[] = []; if (personality.includes('活泼')) k.push('活泼'); if (personality.includes('文静') || personality.includes('内向')) k.push('内向'); if (personality.includes('聪明')) k.push('聪慧'); if (personality.includes('乐于助人') || personality.includes('善良')) k.push('友爱'); if (k.length < 3) k.push('努力', '认真', '进取'); return k.slice(0, 5) }

const handleEvaluate = (row: Student) => {
  evaluateForm.studentId = row.id; evaluateForm.studentName = row.name; evaluateForm.studentClass = row.class
  evaluateForm.score = 3; evaluateForm.tags = []; evaluateForm.comment = ''
  evaluateForm.aiTraits = generateAiTraits(row)
  evaluateForm.chatAnalysis = { activeRate: Math.floor(Math.random() * 30) + 60, keywords: generateKeywords(row.personality) }
  showEvaluateDialog.value = true
}

const saveEvaluation = () => { const s = students.value.find(s => s.id === evaluateForm.studentId); if (s) ElMessage.success(`评价已保存: ${s.name}`); showEvaluateDialog.value = false }
const publishTask = () => { if (!taskForm.name) return; ElMessage.success('任务发布成功'); showTaskDialog.value = false; taskForm.name = ''; taskForm.points = 10; taskForm.deadline = '' }

onMounted(() => {
  loadStudents()
  loadPointRules()
})
</script>

<style scoped>
.points-container { height: 100%; display: flex; flex-direction: column; }
.filter-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #fff; border-radius: 10px; margin-bottom: 12px; border: 1px solid #E8E0F0; }
.filter-left, .filter-right { display: flex; align-items: center; }
.main-content { flex: 1; display: flex; gap: 12px; min-height: 0; }
.group-sidebar { width: 160px; background: #fff; border-radius: 10px; border: 1px solid #E8E0F0; display: flex; flex-direction: column; }
.sidebar-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 14px; border-bottom: 1px solid #E8E0F0; font-weight: 600; color: #333; font-size: 13px; }
.group-list { flex: 1; overflow-y: auto; padding: 6px; }
.group-item { display: flex; align-items: center; padding: 8px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s; margin-bottom: 2px; }
.group-item:hover { background: #F5F3FF; }
.group-item.active { background: #F5F3FF; border-left: 3px solid #f48d45; }
.group-item .group-name { flex: 1; font-size: 12px; color: #333; }
.student-panel { flex: 1; background: #fff; border-radius: 10px; border: 1px solid #E8E0F0; display: flex; flex-direction: column; min-width: 0; overflow: hidden; }
.panel-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 14px; border-bottom: 1px solid #E8E0F0; }
.panel-title { font-weight: 600; color: #333; display: flex; align-items: center; gap: 8px; }
.panel-title .student-count { font-weight: 400; color: #999; font-size: 12px; }
.pagination-wrapper { padding: 12px; display: flex; justify-content: flex-end; border-top: 1px solid #E8E0F0; }
.points-value { color: #f48d45; font-weight: 600; font-size: 14px; }
.rate-cell { display: flex; align-items: center; gap: 8px; }
.rate-text { font-size: 12px; color: #666; min-width: 35px; }
.group-manage .add-group-row { display: flex; gap: 12px; margin-bottom: 16px; }
.group-edit-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.group-edit-item .group-info { display: flex; flex-direction: column; }
.group-edit-item .group-meta { font-size: 12px; color: #999; }
.student-detail .detail-top { display: flex; align-items: center; gap: 16px; }
.student-detail .detail-info h3 { margin: 0; font-size: 18px; color: #333; }
.student-detail .detail-info p { margin: 4px 0 0; color: #999; font-size: 13px; }
.student-detail .detail-points { margin-left: auto; text-align: center; padding: 10px 16px; background: #F5F3FF; border-radius: 8px; }
.student-detail .detail-points .points-num { display: block; font-size: 22px; font-weight: 700; color: #f48d45; }
.student-detail .detail-points .points-label { font-size: 11px; color: #999; }
.student-detail .detail-stats { display: flex; justify-content: space-around; padding: 16px 0; }
.student-detail .stat-item { text-align: center; }
.student-detail .stat-label { display: block; font-size: 12px; color: #999; margin-bottom: 8px; }
.student-detail .stat-progress { display: flex; align-items: center; gap: 8px; }
.student-detail .stat-progress span { font-size: 14px; font-weight: 600; color: #f48d45; min-width: 40px; }
.student-detail .detail-records h4 { margin: 0 0 12px; font-size: 13px; color: #333; }
.student-detail .records-list .record-item { display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.student-detail .records-list .record-name { flex: 1; color: #333; font-size: 13px; }
.student-detail .records-list .record-points { width: 50px; font-weight: 600; font-size: 13px; }
.student-detail .records-list .record-points.add { color: #f48d45; }
.student-detail .records-list .record-points.sub { color: #f44d45; }
.student-detail .records-list .record-time { color: #999; font-size: 11px; width: 100px; text-align: right; }
.add-points-header { display: flex; align-items: center; gap: 16px; padding: 16px; background: #F5F3FF; border-radius: 8px; }
.add-points-header .student-info { display: flex; flex-direction: column; }
.add-points-header .name { font-size: 16px; font-weight: 600; color: #333; }
.add-points-header .current-points { font-size: 14px; color: #8985cf; font-weight: 500; }
.task-dialog .dialog-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.task-dialog .dialog-user { display: flex; flex-direction: column; }
.task-dialog .user-name { font-weight: 500; color: #333; font-size: 14px; }
.task-dialog .user-role { font-size: 12px; color: #8985cf; }
.task-dialog .points-input { display: flex; align-items: center; gap: 8px; }
.task-dialog .points-unit { color: #666; font-size: 14px; }
.task-dialog .points-tips { font-size: 12px; color: #999; margin-top: 6px; }
.task-dialog .rules-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.task-dialog .rule-card { padding: 10px; border: 1px solid #e8e0f0; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.task-dialog .rule-card:hover { border-color: #8985cf; background: #fafaff; }
.task-dialog .rule-card.selected { border-color: #8985cf; background: #f5f3ff; }
.task-dialog .rule-info { display: flex; flex-direction: column; gap: 4px; }
.task-dialog .rule-name { font-size: 13px; color: #333; }
.task-dialog .rule-points { font-size: 14px; font-weight: 600; }
.task-dialog .rule-points.add { color: #52c41a; }
.task-dialog .rule-points.sub { color: #ff4d4f; }
.task-dialog .rules-tip { font-size: 12px; color: #999; margin-top: 10px; }
.group-points-form .selected-group { display: flex; align-items: center; gap: 12px; padding: 12px; background: #F5F3FF; border-radius: 8px; }
.group-points-form .selected-group.center { justify-content: center; }
.group-points-form .points-range { font-size: 12px; color: #999; margin-left: 12px; }
.group-points-form .points-rules-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 16px; }
.group-points-form .points-rules-grid .rule-card { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 12px 8px; background: #fafafa; border: 1px solid #eee; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.group-points-form .points-rules-grid .rule-card:hover { border-color: #f48d45; background: #fffaf5; }
.group-points-form .points-rules-grid .rule-card.selected { border-color: #f48d45; background: #fff5ee; }
.group-points-form .points-rules-grid .rule-card .rule-name { font-size: 12px; color: #333; text-align: center; }
.group-points-form .points-rules-grid .rule-card .rule-points { font-size: 14px; font-weight: 700; }
.group-points-form .points-rules-grid .rule-card .rule-points.add { color: #52c41a; }
.group-points-form .points-rules-grid .rule-card .rule-points.sub { color: #ff4d4f; }
.personality-analysis .analyze-header { display: flex; align-items: center; gap: 16px; }
.personality-analysis .student-base h3 { margin: 0; font-size: 18px; color: #333; }
.personality-analysis .student-base span { font-size: 13px; color: #999; }
.personality-analysis .analyze-section { margin-bottom: 20px; }
.personality-analysis .analyze-section h4 { display: flex; align-items: center; gap: 8px; margin: 0 0 12px; font-size: 14px; color: #333; }
.personality-analysis .analyze-section h4 .el-icon { color: #8985cf; }
.personality-analysis .trait-list { display: flex; flex-direction: column; gap: 10px; }
.personality-analysis .trait-item { display: flex; align-items: center; gap: 12px; }
.personality-analysis .trait-label { width: 60px; font-size: 12px; color: #666; }
.personality-analysis .trait-item :deep(.el-progress) { flex: 1; }
.personality-analysis .trait-value { width: 40px; font-size: 12px; color: #333; text-align: right; }
.personality-analysis .personality-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.personality-analysis .learning-style { display: flex; flex-direction: column; gap: 12px; }
.personality-analysis .style-item { display: flex; align-items: center; gap: 12px; }
.personality-analysis .style-label { width: 70px; font-size: 12px; color: #666; }
.personality-analysis .style-item :deep(.el-progress) { flex: 1; }
.personality-analysis .relationship-info { display: flex; flex-direction: column; gap: 12px; }
.personality-analysis .rel-item { display: flex; align-items: center; gap: 12px; }
.personality-analysis .rel-label { width: 80px; font-size: 12px; color: #666; }
.personality-analysis .summary-content { background: #F5F3FF; padding: 16px; border-radius: 8px; }
.personality-analysis .summary-content p { margin: 0 0 8px; font-size: 13px; color: #666; line-height: 1.6; }
.personality-analysis .summary-content p:last-child { margin-bottom: 0; }
.personality-analysis .summary-content strong { color: #8985cf; }
.evaluate-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.evaluate-header .student-info h3 { margin: 0; font-size: 16px; }
.evaluate-header .student-info span { font-size: 13px; color: #999; }
.chat-analysis { background: #f9f9f9; padding: 16px; border-radius: 8px; margin-bottom: 16px; }
.chat-analysis .analysis-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; color: #333; margin-bottom: 12px; }
.chat-analysis .analysis-items { display: flex; flex-direction: column; gap: 12px; }
.chat-analysis .analysis-item { display: flex; align-items: center; gap: 12px; }
.chat-analysis .item-label { width: 80px; font-size: 13px; color: #666; }
.chat-analysis .item-value { width: 40px; font-size: 13px; color: #333; text-align: right; }
.chat-analysis :deep(.el-progress) { flex: 1; }
.chat-analysis .emotion-tags { display: flex; gap: 8px; }
.chat-analysis .keyword-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.ai-traits { display: flex; gap: 8px; flex-wrap: wrap; }
.custom-dialog .el-divider { margin: 16px 0; }
</style>
