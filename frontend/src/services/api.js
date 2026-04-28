const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const authStore = {
  get token() {
    return localStorage.getItem('autoVizToken');
  },
  set(token) {
    localStorage.setItem('autoVizToken', token);
  },
  clear() {
    localStorage.removeItem('autoVizToken');
  },
};

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  if (authStore.token) headers.set('Authorization', `Bearer ${authStore.token}`);

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    if (response.status === 401) {
      authStore.clear();
      if (window.location.pathname !== '/login') {
        window.location.assign('/login');
      }
    }
    throw new Error(error.detail || 'Request failed');
  }
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return response.json();
  return response.blob();
}

export const api = {
  signup: (payload) => request('/auth/signup', { method: 'POST', body: JSON.stringify(payload) }),
  login: (payload) => request('/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  uploadCsv: (file) => {
    const form = new FormData();
    form.append('file', file);
    return request('/datasets/upload', { method: 'POST', body: form });
  },
  loadSample: (name) => request(`/datasets/sample/${name}`, { method: 'POST' }),
  generateChart: (payload) => request('/charts/generate', { method: 'POST', body: JSON.stringify(payload) }),
  listSessions: () => request('/sessions'),
  getSession: (id) => request(`/sessions/${id}`),
  deleteSession: (id) => request(`/sessions/${id}`, { method: 'DELETE' }),
  getSharedSession: (shareId) => request(`/sessions/shared/${shareId}/public`),
  exportReport: (payload) => request('/reports/export', { method: 'POST', body: JSON.stringify(payload) }),
};
