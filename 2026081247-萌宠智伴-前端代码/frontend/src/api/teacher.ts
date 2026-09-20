import api from './index'

// GET 请求静默处理错误（页面初始加载时不应弹错误提示）
const silentGet = (url: string, config?: any) => api.get(url, { ...config, _silent: true } as any)

export const teacherApi = {
  getLearningSupport: () => api.get('/teacher/learning-support', { _silent: true } as any),
  setLearningSupport: (id: number, data: { action: string; note: string }) => api.post(`/teacher/learning-support/${id}`, data),
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
  uploadMaterialFile: (formData: FormData) =>
    api.post('/teacher/materials/upload', formData, { timeout: 300000 } as any),
  deleteMaterial: (id: number) => api.delete(`/teacher/materials/${id}`),

  // ===== AI 研习配套：学习看板 =====
  getAIOverview: (params?: any) => silentGet('/teacher/ai/overview', { params }),
  getAIStudents: (params?: any) => silentGet('/teacher/ai/students', { params }),

  // ===== AI 研习配套：在线编程练习 =====
  getAIProgramming: (params?: any) => silentGet('/teacher/ai/programming', { params }),
  getAIProgrammingDetail: (studentId: number) => silentGet(`/teacher/ai/programming/${studentId}`),

  // ===== AI 研习配套：对话查看与关注预警 =====
  getAIChatLogs: (params?: any) => silentGet('/teacher/ai/chat-logs', { params }),
  getAIChatLogDetail: (id: number) => silentGet(`/teacher/ai/chat-logs/${id}`),
  handleAIChatLog: (id: number, data: { action: 'focus' | 'ignore'; abnormalType?: string; severity?: string; remark?: string }) =>
    api.post(`/teacher/ai/chat-logs/${id}/handle`, data),

  // ===== AI 研习配套：课程内容维护 =====
  getAICourseList: (params?: any) => silentGet('/teacher/ai/courses', { params }),
  getAICourseContent: (courseId: number) => silentGet(`/teacher/ai/courses/${courseId}/content`),
  saveAICourseContent: (courseId: number, data: { suggestedQuestions?: string[]; regenerateQuiz?: boolean }) =>
    api.put(`/teacher/ai/courses/${courseId}/content`, data),
  getAICourseMaterials: (courseId: number) => silentGet(`/teacher/ai/courses/${courseId}/materials`),
  addAICourseMaterial: (courseId: number, data: { title: string; url: string; type?: string; description?: string }) =>
    api.post(`/teacher/ai/courses/${courseId}/materials`, data),
  removeAICourseMaterial: (courseId: number, materialId: number) =>
    api.delete(`/teacher/ai/courses/${courseId}/materials/${materialId}`),

  // ===== AI 研习配套：照片绘本素材 =====
  getAIBookAssets: (params?: any) => silentGet('/teacher/ai/book-assets', { params }),
  uploadAIBookPhotos: (courseId: number, files: File[], dir?: string) => {
    const fd = new FormData()
    files.forEach(f => fd.append('files', f))
    if (dir) fd.append('dir', dir)
    return api.post(`/teacher/ai/book-assets/${courseId}`, fd)
  },
  deleteAIBookPhoto: (courseId: number, file: string) =>
    api.delete(`/teacher/ai/book-assets/${courseId}`, { params: { file } }),
}
