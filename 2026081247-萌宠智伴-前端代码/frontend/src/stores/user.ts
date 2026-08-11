import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export const useUserStore = defineStore('user', () => {

  // 初始值为空，由各页面在 onMounted 时从后端 API 填充
  const studentInfo = reactive({
    name: '',
    avatar: '',
    class: '',
    email: '',
    phone: '',
    bio: '',
  })

  const petInfo = reactive({
    name: '',
    type: '',
    birthday: '',
    gender: '',
    bio: '',
  })

  const petExp = ref(0)
  const petMaxExp = ref(0)
  const userPoints = ref(0)
  const completedTasks = ref(0)
  const rank = ref(0)

  function spendPoints(amount: number): boolean {
    if (userPoints.value >= amount) {
      userPoints.value -= amount
      return true
    }
    return false
  }

  function addExp(exp: number) {
    petExp.value = Math.min(petExp.value + exp, petMaxExp.value)
  }

  function updateStudentInfo(data: Partial<typeof studentInfo>) {
    Object.assign(studentInfo, data)
  }

  function updatePetInfo(data: Partial<typeof petInfo>) {
    Object.assign(petInfo, data)
  }

  // 从 /student/dashboard 响应填充学生与宠物基础信息（字段名适配映射）
  function applyDashboard(data: any) {
    if (!data) return
    if (data.studentName !== undefined) studentInfo.name = data.studentName
    if (data.avatar !== undefined) studentInfo.avatar = data.avatar
    if (data.className !== undefined) studentInfo.class = data.className
    if (data.petName !== undefined) petInfo.name = data.petName
    if (data.petImage !== undefined) petInfo.type = data.petImage
    if (data.points !== undefined) userPoints.value = data.points
    if (data.rank !== undefined) rank.value = data.rank
    if (data.completedTasks !== undefined) completedTasks.value = data.completedTasks
  }

  // 从 /student/mypet 响应填充宠物档案与学生信息（字段名适配映射）
  function applyMyPet(data: any) {
    if (!data) return
    if (data.student) {
      const s = data.student
      if (s.name !== undefined) studentInfo.name = s.name
      if (s.avatar !== undefined) studentInfo.avatar = s.avatar
      if (s.className !== undefined) studentInfo.class = s.className
      if (s.points !== undefined) userPoints.value = s.points
      if (s.completedTasks !== undefined) completedTasks.value = s.completedTasks
      if (s.rank !== undefined) rank.value = s.rank
    }
    if (data.pet) {
      const p = data.pet
      if (p.name !== undefined) petInfo.name = p.name
      if (p.type !== undefined) petInfo.type = p.type
      if (p.adoptDate !== undefined) petInfo.birthday = p.adoptDate
      if (p.exp !== undefined) petExp.value = p.exp
      if (p.maxExp !== undefined) petMaxExp.value = p.maxExp
    }
  }

  return {
    studentInfo, petInfo, petExp, petMaxExp, userPoints, completedTasks, rank,
    spendPoints, addExp, updateStudentInfo, updatePetInfo, applyDashboard, applyMyPet,
  }
})
