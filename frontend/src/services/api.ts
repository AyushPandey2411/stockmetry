// src/services/api.ts — Axios client with auto-refresh
import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const BASE = import.meta.env.VITE_API_URL || ''

export const api = axios.create({ baseURL: `${BASE}/api/v1` })

// Attach access token to every request
api.interceptors.request.use(cfg => {
  const token = useAuthStore.getState().accessToken
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Auto-refresh on 401
api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = useAuthStore.getState().refreshToken
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE}/api/v1/auth/refresh`, { refresh_token: refresh })
          useAuthStore.getState().setTokens(data.access_token, data.refresh_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        } catch {
          useAuthStore.getState().logout()
        }
      } else {
        useAuthStore.getState().logout()
      }
    }
    return Promise.reject(err)
  }
)
