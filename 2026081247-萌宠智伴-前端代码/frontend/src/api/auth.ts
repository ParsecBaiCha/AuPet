import api from './index'

export const authApi = {
  login: (data: { username: string; password: string }) => api.post('/auth/login', data),
  register: (data: { username: string; password: string; name: string; role: string; email?: string }) =>
    api.post('/auth/register', data),
  getCurrentUser: () => api.get('/auth/me'),
}
