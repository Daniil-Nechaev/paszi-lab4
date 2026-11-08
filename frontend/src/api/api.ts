import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const setUserIdHeader = (userId: number | null) => {
  if (userId) {
    api.defaults.headers.common['X-User-Id'] = userId.toString();
  } else {
    delete api.defaults.headers.common['X-User-Id'];
  }
};

export const authApi = {
  register: (login: string, password: string) =>
    api.post('/api/register', { login, password }),
  login: (login: string, password: string) =>
    api.post('/api/login', { login, password }),
};

export const resourceApi = {
  getResources: () => api.get('/api/resources'),
  createResource: (data: { name: string; description: string }) =>
    api.post('/api/resources', data),
  updateResource: (id: number, data: { name?: string; description?: string }) =>
    api.put(`/api/resources/${id}`, data),
  deleteResource: (id: number) => api.delete(`/api/resources/${id}`),
  setPermissions: (resourceId: number, targetUserId: number, permissions: { can_read: boolean; can_update: boolean; can_delete: boolean }) =>
    api.post(`/api/resources/${resourceId}/permissions`, { target_user_id: targetUserId, ...permissions }),
};
