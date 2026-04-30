const DEPLOYED_API_BASE = 'https://insightcanvas-api.onrender.com/api';
const LOCAL_API_BASE = 'http://localhost:8000/api';
const isLocalHost =
  typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname);

const API_BASE = import.meta.env.VITE_API_BASE_URL || (isLocalHost ? LOCAL_API_BASE : DEPLOYED_API_BASE);

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return response.json();
  return response.blob();
}

export const api = {
  uploadFile: (file) => {
    const form = new FormData();
    form.append('file', file);
    return request('/datasets/upload', { method: 'POST', body: form });
  },
  uploadCsv: (file) => {
    const form = new FormData();
    form.append('file', file);
    return request('/datasets/upload', { method: 'POST', body: form });
  },
  loadSample: (name) => request(`/datasets/sample/${name}`, { method: 'POST' }),
  generateChart: (payload) => request('/charts/generate', { method: 'POST', body: JSON.stringify(payload) }),
  runAnalysis: (payload) => request('/analysis/run', { method: 'POST', body: JSON.stringify(payload) }),
  listSessions: () => request('/sessions'),
  getSession: (id) => request(`/sessions/${id}`),
  deleteSession: (id) => request(`/sessions/${id}`, { method: 'DELETE' }),
  getSharedSession: (shareId) => request(`/sessions/shared/${shareId}/public`),
  exportReport: (payload) => request('/reports/export', { method: 'POST', body: JSON.stringify(payload) }),
};
