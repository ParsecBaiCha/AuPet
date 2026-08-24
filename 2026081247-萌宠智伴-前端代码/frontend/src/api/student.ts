import api from './index'

const sGet = (url: string) => api.get(url, { _silent: true } as any)

export const studentApi = {
  getDashboard: () => sGet('/student/dashboard'),
  getMyPet: () => sGet('/student/mypet'),
  getShopItems: () => sGet('/student/shop'),
  buyItem: (itemId: number) => api.post('/student/shop/buy', { itemId }),
  getChatHistory: () => sGet('/student/chat'),
  sendChat: (message: string) => api.post('/student/chat', { message }),
  getDiaries: () => sGet('/student/diaries'),
  createDiary: (data: any) => api.post('/student/diaries', data),
  getEmotions: () => sGet('/student/emotions'),
  recordEmotion: (data: any) => api.post('/student/emotions', data),
  getTasks: () => sGet('/student/tasks'),
  updateTask: (id: number, data: any) => api.put(`/student/tasks/${id}`, data),
  getClassMates: () => sGet('/student/classmates'),
  getClassStats: () => sGet('/student/class-stats'),
  getPetShop: () => sGet('/student/pet-shop'),
  buyPet: (petId: number) => api.post('/student/pet-shop/buy', { petId }),
  getPoints: () => sGet('/student/points'),

  // ===== AI通识课教学助手 =====
  getAICourses: (grade: string) => sGet(`/student/ai/courses?grade=${grade}`),
  getGrade: () => sGet('/student/ai/grade'),
  setGrade: (grade: string) => api.post('/student/ai/grade', { grade }),
  generateQuiz: (data: { topic: string; count?: number; courseId?: number }) =>
    api.post('/student/ai/quiz/generate', data),
  gradeQuiz: (data: { questions: any[]; answers: number[]; topic?: string; courseId?: number }) =>
    api.post('/student/ai/quiz/grade', data),
  generateBook: (data: { topic: string; courseId?: number }) =>
    api.post('/student/ai/picture-book/generate', data),
  getBooks: () => sGet('/student/ai/picture-books'),
  getBook: (id: number) => sGet(`/student/ai/picture-books/${id}`),
  toggleBookFavorite: (id: number) => api.post(`/student/ai/picture-books/${id}/favorite`),
  generateAnimation: (data: { topic: string; courseId?: number }) =>
    api.post('/student/ai/animation/generate', data),
  getLearningPath: () => sGet('/student/ai/learning-path'),
  getAIChatHistory: () => sGet('/student/ai/chat/history'),
  sendAIChat: (message: string) => api.post('/student/chat', { message }),
  deleteChatMessage: (msgId: number) => api.delete(`/student/chat/${msgId}`),
  editChatMessage: (msgId: number, content: string) => api.put(`/student/chat/${msgId}`, { content }),
  clearChat: () => api.post('/student/chat/clear'),
  rollbackChat: () => api.post('/student/chat/rollback'),
  getMaterials: (courseId?: number) => sGet(`/student/ai/materials${courseId ? '?courseId=' + courseId : ''}`),
  getTeacherMaterials: () => sGet('/student/ai/teacher-materials'),
  getSuggestedQuestions: (courseId?: number, topic?: string) => {
    let url = '/student/ai/suggested-questions?'
    if (courseId) url += `courseId=${courseId}&`
    if (topic) url += `topic=${encodeURIComponent(topic)}`
    return sGet(url)
  },
}
