import axios from 'axios'

let csrfToken = null

export function setCsrfToken(token) {
  csrfToken = token
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const method = (config.method || 'get').toLowerCase()

  if (
    csrfToken &&
    !['get', 'head', 'options'].includes(method)
  ) {
    config.headers['X-CSRF-Token'] = csrfToken
  }

  return config
})

export default api
