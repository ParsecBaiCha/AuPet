import api from './index'

const sGet = (url: string) => api.get(url, { _silent: true } as any)

export const studentApi = {
  requestLearningHelp: (kind: 'study' | 'mood') => api.post('/student/learning-support/help', { kind }),
  submitQuizRating: (data: { topic: string; question: string; stars: number; tags: string[] }) =>
    api.post('/student/learning-support/rating', data),
  getDashboard: () => sGet('/student/dashboard'),
  getMyPet: () => sGet('/student/mypet'),
  getShopItems: () => sGet('/student/shop'),
  buyItem: (itemId: number) => api.post('/student/shop/buy', { itemId }),
  getChatHistory: () => sGet('/student/chat'),
  sendChat: (message: string) => api.post('/student/chat', { message }, { timeout: 90000 }),
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
  generateQuiz: (data: { topic: string; count?: number; courseId?: number; group?: number }) =>
    api.post('/student/ai/quiz/generate', data, { timeout: 120000 }),
  gradeQuiz: (data: { questions: any[]; answers: number[]; topic?: string; courseId?: number }) =>
    api.post('/student/ai/quiz/grade', data),
  // 答题进度暂存：存后端，换设备也能接着做
  getQuizProgress: () => sGet('/student/ai/quiz/progress'),
  saveQuizProgress: (data: any) => api.post('/student/ai/quiz/progress', data),
  clearQuizProgress: () => api.delete('/student/ai/quiz/progress'),
  generateBook: (data: { topic: string; courseId?: number }) =>
    api.post('/student/ai/picture-book/generate', data),
  getBooks: () => sGet('/student/ai/picture-books'),
  getFavoriteBooks: () => sGet('/student/ai/picture-books?favorite=1'),
  getBook: (id: number) => sGet(`/student/ai/picture-books/${id}`),
  toggleBookFavorite: (id: number) => api.post(`/student/ai/picture-books/${id}/favorite`),
  getLearningPath: () => sGet('/student/ai/learning-path'),
  getAIChatHistory: () => sGet('/student/ai/chat/history'),
  sendAIChat: (message: string, courseId?: number, topic?: string) =>
    api.post('/student/chat', { message, courseId, topic, scene: 'learning' }, { timeout: 90000 }),
  getCourseGuide: (courseId: number, topic?: string) =>
    api.post('/student/chat/guide', { courseId, topic }, { timeout: 90000 }),
  deleteChatMessage: (msgId: number) => api.delete(`/student/chat/${msgId}?scene=learning`),
  editChatMessage: (msgId: number, content: string) => api.put(`/student/chat/${msgId}?scene=learning`, { content }),
  clearChat: () => api.post('/student/chat/clear?scene=learning'),
  rollbackChat: () => api.post('/student/chat/rollback?scene=learning'),
  getMaterials: (courseId?: number) => sGet(`/student/ai/materials${courseId ? '?courseId=' + courseId : ''}`),
  getTeacherMaterials: () => sGet('/student/ai/teacher-materials'),
  getSuggestedQuestions: (courseId?: number, topic?: string) => {
    let url = '/student/ai/suggested-questions?'
    if (courseId) url += `courseId=${courseId}&`
    if (topic) url += `topic=${encodeURIComponent(topic)}`
    return sGet(url)
  },
}
