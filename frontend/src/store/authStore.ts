// src/store/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number; email: string; username: string
  full_name: string; role: string; avatar_color: string
}

interface AuthState {
  accessToken:  string | null
  refreshToken: string | null
  user:         User | null
  setAuth:      (access: string, refresh: string, user: User) => void
  setTokens:    (access: string, refresh: string) => void
  logout:       () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    set => ({
      accessToken:  null,
      refreshToken: null,
      user:         null,
      setAuth: (access, refresh, user) => set({ accessToken: access, refreshToken: refresh, user }),
      setTokens: (access, refresh)     => set({ accessToken: access, refreshToken: refresh }),
      logout: () => set({ accessToken: null, refreshToken: null, user: null }),
    }),
    { name: 'stockmetry-auth', partialize: s => ({ accessToken: s.accessToken, refreshToken: s.refreshToken, user: s.user }) }
  )
)
