import api from './index'

// GET 请求静默处理错误（页面初始加载时不应弹错误提示）
const silentGet = (url: string, config?: any) => api.get(url, { ...config, _silent: true } as any)

export const teacherApi = {
  getDashboard: () => silentGet('/teacher/dashboard'),
  getRoleNetwork: () => silentGet('/teacher/role-network'),
  getPredictions: () => silentGet('/teacher/predictions'),
  createPrediction: (data: any) => api.post('/teacher/predictions', data),
  getPredictionDetail: (id: number) => silentGet(`/teacher/predictions/${id}`),
  getPoints: () => silentGet('/teacher/points'),
  getPointRecords: (studentId?: number) => silentGet('/teacher/points/records', { params: { studentId } }),
  awardPoints: (data: any) => api.post('/teacher/points/award', data),
  getPointRules: () => silentGet('/teacher/points/rules'),
  createPointRule: (data: any) => api.post('/teacher/points/rules', data),
  getClasses: () => silentGet('/teacher/classes'),
  createClass: (data: any) => api.post('/teacher/classes', data),
  importClass: (data: any) => api.post('/teacher/classes/import', data),
  getClassStudents: (classId: number) => silentGet(`/teacher/classes/${classId}/students`),
  getStudentDetail: (studentId: number) => silentGet(`/teacher/students/${studentId}`),
  getInterventions: () => silentGet('/teacher/interventions'),
  getAbnormalDetail: (id: number) => silentGet(`/teacher/interventions/${id}`),
  createIntervention: (data: any) => api.post('/teacher/interventions', data),
  getGroupRoles: () => silentGet('/teacher/group-roles'),
  evaluateStudent: (data: any) => api.post('/teacher/evaluations', data),
  getForumPosts: () => silentGet('/teacher/forum'),
  createForumPost: (data: any) => api.post('/teacher/forum', data),
  getMyPosts: () => silentGet('/teacher/forum/mine'),
  getForumBoards: () => silentGet('/teacher/forum/boards'),
  getMaterials: () => silentGet('/teacher/materials'),
  uploadMaterial: (data: { title: string; url: string; description?: string; type?: string; courseId?: number }) =>
    api.post('/teacher/materials', data),
  deleteMaterial: (id: number) => api.delete(`/teacher/materials/${id}`),
}
