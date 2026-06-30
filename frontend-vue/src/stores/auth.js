import { defineStore } from 'pinia'
import api from '@/services/api'
import i18n from '@/i18n'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('auth_token') || null,
    refreshToken: localStorage.getItem('auth_refresh') || null,
    user: JSON.parse(localStorage.getItem('auth_user')) || null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userName: (state) => {
      if (!state.user) return ''
      return state.user.nombre_completo || state.user.username || ''
    },
    userRol: (state) => state.user?.rol || null,
    isAdmin: (state) => state.user?.rol === 'administrador',
    isEstilista: (state) => state.user?.rol === 'estilista',
    isRecepcionista: (state) => state.user?.rol === 'recepcionista',
    isCliente: (state) => state.user?.rol === 'cliente',
  },

  actions: {
    /**
     * Login con username y password.
     * El backend devuelve: { access, refresh, user: { id, rol, nombre_completo, ... } }
     */
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/token/', { username, password })
        const { access, refresh, user } = response.data

        this.token = access
        this.refreshToken = refresh
        this.user = user
        localStorage.setItem('auth_token', access)
        localStorage.setItem('auth_refresh', refresh)
        localStorage.setItem('auth_user', JSON.stringify(user))

        return true
      } catch (err) {
        const msg = err.response?.data?.detail || err.response?.data?.non_field_errors?.[0]
        this.error = msg || i18n.global.t('common.auth.invalidCredentials')
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * Registro de nuevo usuario (rol='cliente').
     * El backend devuelve tokens + datos del usuario creado.
     */
    async register(data) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/registro/', data)
        const { access, refresh, user } = response.data

        this.token = access
        this.refreshToken = refresh
        this.user = user
        localStorage.setItem('auth_token', access)
        localStorage.setItem('auth_refresh', refresh)
        localStorage.setItem('auth_user', JSON.stringify(user))

        return true
      } catch (err) {
        if (err.response?.data) {
          const errors = err.response.data
          const firstError = Object.values(errors)[0]
          this.error = Array.isArray(firstError) ? firstError[0] : firstError
        } else {
          this.error = i18n.global.t('common.auth.errorCreatingAccount')
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * Intenta refrescar el access token usando el refresh token.
     * Retorna true si el refresh fue exitoso, false si no.
     */
    async refreshAccessToken() {
      if (!this.refreshToken) return false

      try {
        const response = await api.post('/token/refresh/', {
          refresh: this.refreshToken
        })
        const { access } = response.data

        this.token = access
        localStorage.setItem('auth_token', access)

        return true
      } catch (err) {
        // Refresh token tambien expiro o es invalido: cerrar sesion
        this.logout()
        return false
      }
    },

    /**
     * Refresca los datos del usuario desde el backend.
     * Se usa al cargar la app para verificar que el token sigue valido.
     * Si el access token expiro, intenta refrescarlo antes.
     */
    async fetchProfile() {
      if (!this.token) return
      try {
        const response = await api.get('/perfil/')
        this.user = response.data
        localStorage.setItem('auth_user', JSON.stringify(response.data))
      } catch (err) {
        if (err.response?.status === 401) {
          // Access token expiro, intentar refrescar
          const refreshed = await this.refreshAccessToken()
          if (refreshed) {
            // Reintentar con el nuevo token
            try {
              const response = await api.get('/perfil/')
              this.user = response.data
              localStorage.setItem('auth_user', JSON.stringify(response.data))
              return
            } catch (retryErr) {
              // El refresh funciono pero el perfil fallo de todos modos
            }
          }
        }
        // Token invalido y no se pudo refrescar: limpiar todo
        this.logout()
      }
    },

    /**
     * Cierra la sesion: limpia estado y localStorage.
     */
    logout() {
      this.token = null
      this.refreshToken = null
      this.user = null
      this.error = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_refresh')
      localStorage.removeItem('auth_user')
    }
  }
})