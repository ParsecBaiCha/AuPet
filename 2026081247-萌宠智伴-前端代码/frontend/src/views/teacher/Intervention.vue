<template>
  <div class="intervention-container">
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="selectedClass" placeholder="请选择班级" style="width: 140px">
          <el-option label="全部班级" value="" />
          <el-option v-for="cls in classList" :key="cls" :label="cls" :value="cls" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="状态" style="width: 120px; margin-left: 12px">
          <el-option label="全部状态" value="" />
          <el-option label="待跟进" value="pending" />
          <el-option label="跟进中" value="ongoing" />
          <el-option label="已结案" value="closed" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" @click="openCreateDialog">+ 新建干预</el-button>
      </div>
    </div>

    <div class="content-card">
      <div class="card-header">
        <h3 class="card-title"><el-icon><WarningFilled /></el-icon> 异常学生列表</h3>
      </div>
      <el-table :data="abnormalStudents" stripe>
        <el-table-column prop="name" label="学生姓名" width="100" />
        <el-table-column prop="class" label="班级" width="120" />
        <el-table-column prop="abnormalType" label="异常类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.abnormalType)" size="small">{{ row.abnormalType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detectedDate" label="识别时间" width="120" />
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'pending'" type="warning" size="small">待跟进</el-tag>
            <el-tag v-else-if="row.status === 'ongoing'" type="primary" size="small">跟进中</el-tag>
            <el-tag v-else type="info" size="small">已结案</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="interventionCount" label="干预次数" width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openRecord(row)">添加记录</el-button>
            <el-button type="primary" link @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="16">
        <div class="content-card" style="height: 402px;">
          <div class="card-header">
            <h3 class="card-title"><el-icon><Document /></el-icon> 干预过程记录</h3>
          </div>
          <div class="record-timeline">
            <div class="timeline-item" v-for="(record, idx) in interventionRecords" :key="idx">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="timeline-title">{{ record.title }}</span>
                  <span class="timeline-date">{{ record.date }}</span>
                </div>
                <div class="timeline-desc">{{ record.description }}</div>
                <div class="timeline-tags">
                  <el-tag v-for="tag in record.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="content-card" style="height: 402px;">
          <div class="card-header">
            <h3 class="card-title"><el-icon><Collection /></el-icon> 干预方案库</h3>
          </div>
          <div class="plan-library">
            <div class="plan-item" v-for="plan in planLibrary" :key="plan.id" @click="viewPlan(plan)">
              <div class="plan-name">{{ plan.name }}</div>
              <div class="plan-desc">{{ plan.description }}</div>
              <div class="plan-tags">
                <el-tag v-for="tag in plan.tags" :key="tag" size="small">{{ tag }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="24">
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title"><el-icon><DataAnalysis /></el-icon> 干预效果反馈统计</h3>
          </div>
          <div class="effect-stats">
            <div class="stat-item">
              <div class="stat-num">12</div>
              <div class="stat-label">本学期干预人数</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">8</div>
              <div class="stat-label">好转人数</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">3</div>
              <div class="stat-label">持续跟进中</div>
            </div>
            <div class="stat-item">
              <div class="stat-num">1</div>
              <div class="stat-label">转介专业人员</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="showRecordDialog" title="添加干预记录" width="500px">
      <el-form :model="recordForm" label-position="top">
        <el-form-item label="干预主题">
          <el-input v-model="recordForm.title" placeholder="请输入干预主题" />
        </el-form-item>
        <el-form-item label="干预方式">
          <el-select v-model="recordForm.method" placeholder="请选择干预方式" style="width: 100%">
            <el-option label="个别谈话" value="个别谈话" />
            <el-option label="团体辅导" value="团体辅导" />
            <el-option label="家校沟通" value="家校沟通" />
            <el-option label="心理测评" value="心理测评" />
            <el-option label="转介咨询" value="转介咨询" />
          </el-select>
        </el-form-item>
        <el-form-item label="干预内容">
          <el-input v-model="recordForm.content" type="textarea" :rows="4" placeholder="请描述干预过程和内容" />
        </el-form-item>
        <el-form-item label="效果评估">
          <el-radio-group v-model="recordForm.effect">
            <el-radio label="positive">明显好转</el-radio>
            <el-radio label="stable">状态稳定</el-radio>
            <el-radio label="negative">需继续跟进</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRecordDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRecord">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCreateDialog" title="新建干预" width="500px">
      <el-form :model="createForm" label-position="top">
        <el-form-item label="选择学生">
          <el-select v-model="createForm.studentId" placeholder="请选择学生" style="width: 100%" filterable>
            <el-option v-for="s in abnormalStudents" :key="s.id" :label="s.name + ' - ' + s.class" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="异常类型">
          <el-select v-model="createForm.abnormalType" placeholder="请选择异常类型" style="width: 100%">
            <el-option label="情绪低落" value="情绪低落" />
            <el-option label="焦虑倾向" value="焦虑倾向" />
            <el-option label="社交退缩" value="社交退缩" />
            <el-option label="学习抗拒" value="学习抗拒" />
            <el-option label="行为问题" value="行为问题" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度">
          <el-radio-group v-model="createForm.severity">
            <el-radio label="轻度">轻度</el-radio>
            <el-radio label="中度">中度</el-radio>
            <el-radio label="重度">重度</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="干预方案">
          <el-select v-model="createForm.planId" placeholder="请选择干预方案" style="width: 100%" allow-create filterable>
            <el-option v-for="plan in planLibrary" :key="plan.id" :label="plan.name" :value="plan.id" />
            <el-option label="自定义方案" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="干预目标">
          <el-input v-model="createForm.goal" type="textarea" :rows="2" placeholder="请描述干预目标" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createIntervention">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" :title="currentStudent?.name + ' - 异常详情'" width="500px">
      <div class="student-detail" v-if="currentStudent">
        <div class="detail-row">
          <span class="label">班级</span>
          <span>{{ currentStudent.class }}</span>
        </div>
        <div class="detail-row">
          <span class="label">异常类型</span>
          <el-tag :type="getTypeTagType(currentStudent.abnormalType)" size="small">{{ currentStudent.abnormalType }}</el-tag>
        </div>
        <div class="detail-row">
          <span class="label">识别时间</span>
          <span>{{ currentStudent.detectedDate }}</span>
        </div>
        <div class="detail-row">
          <span class="label">严重程度</span>
          <el-tag :type="getSeverityType(currentStudent.severity)" size="small">{{ currentStudent.severity }}</el-tag>
        </div>
        <div class="detail-row">
          <span class="label">当前状态</span>
          <el-tag v-if="currentStudent.status === 'pending'" type="warning" size="small">待跟进</el-tag>
          <el-tag v-else-if="currentStudent.status === 'ongoing'" type="primary" size="small">跟进中</el-tag>
          <el-tag v-else type="info" size="small">已结案</el-tag>
        </div>
        <div class="detail-row">
          <span class="label">干预次数</span>
          <span>{{ currentStudent.interventionCount }} 次</span>
        </div>
        <el-divider />
        <div class="detail-section">
          <h4>异常描述</h4>
          <p>{{ getAbnormalDesc(currentStudent.abnormalType) }}</p>
        </div>
        <div class="detail-section">
          <h4>建议措施</h4>
          <ul>
            <li v-for="(s, i) in getSuggestions(currentStudent.abnormalType)" :key="i">{{ s }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="openRecord(currentStudent); showDetailDialog = false">添加记录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { WarningFilled, Document, Collection, DataAnalysis } from '@element-plus/icons-vue'
import { teacherApi } from '../../api/teacher'

const selectedClass = ref('')
const statusFilter = ref('')
const classList = ['一年级1班', '一年级2班', '一年级3班']

const abnormalStudents = reactive<any[]>([])

const loadInterventions = async () => {
  try {
    const data: any = await teacherApi.getInterventions()
    if (Array.isArray(data)) abnormalStudents.splice(0, abnormalStudents.length, ...data)
  } catch (e) {
    // 接口失败时保持页面可用，使用默认空值
  }
}

const interventionRecords = reactive([
  { title: '首次个别谈话', date: '2024-04-25', description: '与学生进行一对一谈话，了解近期生活和学习情况，鼓励表达情绪', tags: ['个别谈话', '情绪疏导'] },
  { title: '联系家长', date: '2024-04-23', description: '与家长沟通学生在家表现，建议关注学生情绪变化', tags: ['家校沟通'] },
  { title: '心理测评', date: '2024-04-20', description: '完成SCL-90测评，结果显示人际关系敏感维度偏高', tags: ['心理测评'] }
])

const planLibrary = reactive([
  { id: 1, name: '情绪管理训练', description: '帮助学生识别和调节情绪的常用方法', tags: ['情绪', '自我调节'], steps: ['引导识别情绪', '学习调节技巧', '实践应用', '反馈总结'] },
  { id: 2, name: '社交技能培训', description: '提升学生人际交往能力的方案', tags: ['社交', '人际'], steps: ['基础认知', '技能演练', '场景模拟', '实际应用'] },
  { id: 3, name: '学习动力激发', description: '针对学习兴趣低落的干预方案', tags: ['学习', '动力'], steps: ['原因分析', '目标设定', '正向强化', '成果展示'] }
])

const getTypeTagType = (type: string) => {
  const map: Record<string, string> = { '情绪低落': 'danger', '焦虑倾向': 'warning', '社交退缩': 'info', '学习抗拒': '' }
  return map[type] || ''
}

const getSeverityType = (severity: string) => {
  const map: Record<string, string> = { '轻度': 'info', '中度': 'warning', '重度': 'danger' }
  return map[severity] || ''
}

const getAbnormalDesc = (type: string) => {
  const map: Record<string, string> = {
    '情绪低落': '学生近期表现出情绪持续低落，对日常活动缺乏兴趣，课堂上注意力不集中，与同学交往减少。',
    '焦虑倾向': '学生表现出过度担忧，对考试或课堂发言感到紧张，出现失眠、食欲下降等躯体症状。',
    '社交退缩': '学生回避社交场合，不太愿意与同学交流，参与团体活动不积极，独处时间增多。',
    '学习抗拒': '学生对学习表现出明显抵触，不愿完成作业，课堂上注意力分散，成绩下滑明显。',
    '行为问题': '学生出现违规行为或情绪失控，与同学发生冲突，课堂纪律较差。'
  }
  return map[type] || '暂无描述'
}

const getSuggestions = (type: string) => {
  const map: Record<string, string[]> = {
    '情绪低落': ['安排一对一谈话，了解学生近期生活状况', '鼓励参与感兴趣的班级活动', '联系家长了解家庭情况'],
    '焦虑倾向': ['进行放松训练指导', '逐步暴露法缓解焦虑', '必要时转介专业心理咨询'],
    '社交退缩': ['安排同伴互助小组', '鼓励参与团队活动', '逐步建立社交信心'],
    '学习抗拒': ['了解学习困难原因', '设定小目标逐步达成', '正向强化学习行为'],
    '行为问题': ['明确行为边界和后果', '情绪管理训练', '必要时联系家长协同教育']
  }
  return map[type] || []
}

const showRecordDialog = ref(false)
const showPlanDialog = ref(false)
const showCreateDialog = ref(false)
const currentPlan = ref<any>(null)

const recordForm = reactive({
  title: '',
  method: '',
  content: '',
  effect: 'stable'
})

const createForm = reactive({
  studentId: '',
  abnormalType: '',
  severity: '轻度',
  planId: '',
  goal: ''
})

const openCreateDialog = () => {
  showCreateDialog.value = true
}

const createIntervention = async () => {
  try {
    await teacherApi.createIntervention({ ...createForm })
    ElMessage.success('创建干预成功')
    await loadInterventions()
  } catch (e) {
    // 错误已由拦截器提示
  }
  showCreateDialog.value = false
}

const openRecord = (row: any) => {
  showRecordDialog.value = true
}

const viewDetail = async (row: any) => {
  currentStudent.value = row
  showDetailDialog.value = true
  try {
    const data: any = await teacherApi.getAbnormalDetail(row.id)
    if (data && typeof data === 'object') {
      currentStudent.value = { ...row, ...data }
    }
  } catch (e) {
    // 接口失败时保持弹窗可用，使用列表数据
  }
}

const showDetailDialog = ref(false)
const currentStudent = ref<any>(null)

const viewPlan = (plan: any) => {
  currentPlan.value = plan
  showPlanDialog.value = true
}

const saveRecord = () => {
  showRecordDialog.value = false
}

onMounted(() => {
  loadInterventions()
})
</script>

<style scoped>
.intervention-container { padding: 0; }

.filter-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.filter-left, .filter-right { display: flex; }

.content-card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #E8E0F0;
  padding: 16px;
}

.card-header {
  margin-bottom: 16px;
}

.card-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-title .el-icon { color: #8985cf; }

.record-timeline {
  padding: 8px 0;
}

.timeline-item {
  position: relative;
  padding-left: 24px;
  padding-bottom: 20px;
  border-left: 2px solid #e8e0f0;
  margin-left: 8px;
}

.timeline-dot {
  position: absolute;
  left: -6px;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #8985cf;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.timeline-title { font-weight: 500; color: #333; }
.timeline-date { font-size: 12px; color: #999; }
.timeline-desc { font-size: 13px; color: #666; margin-bottom: 8px; }
.timeline-tags .el-tag { margin-right: 6px; }

.plan-library { display: flex; flex-direction: column; gap: 12px; }

.plan-item {
  padding: 12px;
  border: 1px solid #e8e0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.plan-item:hover { border-color: #8985cf; background: #fafaff; }

.plan-name { font-weight: 500; color: #333; margin-bottom: 4px; }
.plan-desc { font-size: 12px; color: #999; margin-bottom: 8px; }
.plan-tags .el-tag { margin-right: 4px; }

.plan-detail p { color: #666; margin-bottom: 16px; }

.plan-steps { display: flex; flex-direction: column; gap: 8px; }
.step-item { display: flex; align-items: center; gap: 8px; }
.step-num {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #8985cf;
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.step-content { font-size: 13px; color: #666; }

.student-detail { padding: 8px 0; }

.detail-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.detail-row .label { color: #999; min-width: 70px; }

.detail-section { margin-top: 16px; }

.detail-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.detail-section p { margin: 0; font-size: 13px; color: #666; line-height: 1.8; }

.detail-section ul { margin: 0; padding-left: 20px; }
.detail-section li { font-size: 13px; color: #666; line-height: 1.8; }

.effect-stats {
  display: flex;
  justify-content: space-around;
  padding: 16px 0;
}

.stat-item { text-align: center; }

.stat-num {
  font-size: 32px;
  font-weight: 700;
  color: #8985cf;
}

.stat-label { font-size: 13px; color: #999; margin-top: 4px; }
</style>
