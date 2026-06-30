import axios from 'axios'
import i18n from '@/i18n'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api' || 'https://sgcpbackend.vercel.app/api',
  headers: {
    'Content-Type': 'application/json',
  }
})

// ============================================================================
// Flag para evitar loops de refresh
// ============================================================================
let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// ============================================================================
// INTERCEPTOR DE PETICION — Agrega el token JWT + Accept-Language header
// ============================================================================
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Add Accept-Language header for i18n
    const acceptLang = localStorage.getItem('api_accept_language') || 'es'
    // Add X-Locale-Region and X-Timezone headers for timezone-aware responses
    const localeRegion = localStorage.getItem('locale_region') || 'es-PE'
    const timezoneMap = {
      'es-PE': 'America/Lima',
      'en-US': 'America/New_York',
      'pt-BR': 'America/Sao_Paulo',
    }
    if (config.headers) {
      config.headers['Accept-Language'] = acceptLang
      config.headers['X-Locale-Region'] = localeRegion
      config.headers['X-Timezone'] = timezoneMap[localeRegion] || 'America/Lima'
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// ============================================================================
// INTERCEPTOR DE RESPUESTA — Maneja errores globales + auto-refresh
// ============================================================================
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response) {
      const { status } = error.response

      // --- 401: Token expirado o invalido ---
      if (status === 401 && !originalRequest._retry) {
        // No intentar refrescar endpoints publicos o de auth
        const isAuthEndpoint = originalRequest.url?.includes('/token/') ||
                               originalRequest.url?.includes('/registro/')
        if (isAuthEndpoint) {
          return Promise.reject(error)
        }

        if (isRefreshing) {
          // Ya se esta refrescando: encolar esta peticion
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject })
          }).then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          }).catch(err => {
            return Promise.reject(err)
          })
        }

        originalRequest._retry = true
        isRefreshing = true

        const refreshToken = localStorage.getItem('auth_refresh')

        if (!refreshToken) {
          // No hay refresh token: limpiar y redirigir a login
          isRefreshing = false
          clearAuthAndRedirect()
          return Promise.reject(error)
        }

        try {
          const response = await axios.post(
            `${api.defaults.baseURL}/token/refresh/`,
            { refresh: refreshToken }
          )

          const { access } = response.data
          localStorage.setItem('auth_token', access)

          // Actualizar el header de la peticion original y reintentar
          originalRequest.headers.Authorization = `Bearer ${access}`

          // Procesar la cola de peticiones pendientes
          processQueue(null, access)

          return api(originalRequest)
        } catch (refreshError) {
          // Refresh token tambien es invalido: cerrar sesion
          processQueue(refreshError, null)
          clearAuthAndRedirect()
          return Promise.reject(error)
        } finally {
          isRefreshing = false
        }
      }

      // --- 403: Sin permisos (rol incorrecto) ---
      if (status === 403) {
        console.warn(i18n.global.t('common.auth.forbidden'))
      }
    }

    return Promise.reject(error)
  }
)

/**
 * Limpia la autenticacion y redirige a login.
 * Se usa cuando el refresh token tambien ha expirado.
 */
function clearAuthAndRedirect() {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('auth_refresh')
  localStorage.removeItem('auth_user')

  const currentPath = window.location.pathname
  const isPublicPath = currentPath === '/login' || currentPath === '/' || currentPath === '/registro'

  if (!isPublicPath) {
    window.location.href = '/login'
  }
}

export default api