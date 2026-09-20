import api from './index'

type ApiResult = Promise<any>

export const adminApi = {
  getDashboard: (): ApiResult => api.get('/admin/dashboard'),
  getStudents: (params?: any): ApiResult => api.get('/admin/students', { params }),
  createStudent: (data: any): ApiResult => api.post('/admin/students', data),
  updateStudent: (id: string | number, data: any): ApiResult => api.put(`/admin/students/${id}`, data),
  deleteStudent: (id: string | number): ApiResult => api.delete(`/admin/students/${id}`),
  getStudentDetail: (id: string | number): ApiResult => api.get(`/admin/students/${id}`),
  getTeachers: (params?: any): ApiResult => api.get('/admin/teachers', { params }),
  createTeacher: (data: any): ApiResult => api.post('/admin/teachers', data),
  updateTeacher: (id: string | number, data: any): ApiResult => api.put(`/admin/teachers/${id}`, data),
  deleteTeacher: (id: string | number): ApiResult => api.delete(`/admin/teachers/${id}`),
  getTeacherDetail: (id: string | number): ApiResult => api.get(`/admin/teachers/${id}`),
  getDailyForumPosts: (params?: any): ApiResult => api.get('/admin/forum/daily', { params }),
  getSubjectForumPosts: (params?: any): ApiResult => api.get('/admin/forum/subject', { params }),
  reviewPost: (id: number, data: any): ApiResult => api.put(`/admin/forum/posts/${id}/review`, data),
  toggleTop: (id: number): ApiResult => api.put(`/admin/forum/posts/${id}/top`),
  deletePost: (id: number): ApiResult => api.delete(`/admin/forum/posts/${id}`),
  createAnnouncement: (data: any): ApiResult => api.post('/admin/forum/announcement', data),
  getForumBoards: (): ApiResult => api.get('/admin/forum/boards'),
  createForumBoard: (data: any): ApiResult => api.post('/admin/forum/boards', data),
  updateForumBoard: (id: number, data: any): ApiResult => api.put(`/admin/forum/boards/${id}`, data),
  getPointOverview: (): ApiResult => api.get('/admin/points/overview'),
  getPointRankings: (params?: any): ApiResult => api.get('/admin/points/rankings', { params }),
  getPointTrend: (): ApiResult => api.get('/admin/points/trend'),

  // ===== AI 研习配套：课程库 =====
  getAICourses: (params?: any): ApiResult => api.get('/admin/ai/courses', { params }),
  createAICourse: (data: any): ApiResult => api.post('/admin/ai/courses', data),
  updateAICourse: (id: number, data: any): ApiResult => api.put(`/admin/ai/courses/${id}`, data),
  setAICourseStatus: (id: number, status: 'published' | 'archived'): ApiResult =>
    api.post(`/admin/ai/courses/${id}/status`, { status }),
  deleteAICourse: (id: number): ApiResult => api.delete(`/admin/ai/courses/${id}`),

  // ===== AI 研习配套：使用总览与内容审核 =====
  getAIOverview: (params?: any): ApiResult => api.get('/admin/ai/overview', { params }),
  getAIReviews: (params?: any): ApiResult => api.get('/admin/ai/reviews', { params }),
  reviewAIContent: (data: { objectType: 'chat' | 'material'; objectId: number; result: string; remark?: string }): ApiResult =>
    api.post('/admin/ai/reviews', data),
  getAIAuditLogs: (params?: any): ApiResult => api.get('/admin/ai/audit-logs', { params }),
}
