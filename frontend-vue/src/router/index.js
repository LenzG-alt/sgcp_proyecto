import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layouts
import AdminLayout from '@/views/AdminLayout.vue'
import EstilistaLayout from '@/views/EstilistaLayout.vue'
import RecepcionistaLayout from '@/views/RecepcionistaLayout.vue'
import ClienteLayout from '@/views/ClienteLayout.vue'

// Vistas publicas
import LandingView from '@/views/LandingView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'

// Vistas de admin
import AdminDashboardView from '@/views/AdminDashboardView.vue'
import AdminPeluqueriasView from '@/views/AdminPeluqueriasView.vue'
import AdminUsuariosView from '@/views/AdminUsuariosView.vue'
import AdminEstilistasView from '@/views/AdminEstilistasView.vue'
import AdminServiciosView from '@/views/AdminServiciosView.vue'
import AdminCitasView from '@/views/AdminCitasView.vue'
import AdminHorariosView from '@/views/AdminHorariosView.vue'

// Vistas de estilista
import EstilistaDashboardView from '@/views/EstilistaDashboardView.vue'
import EstilistaCitasView from '@/views/EstilistaCitasView.vue'
import EstilistaHistorialView from '@/views/EstilistaHistorialView.vue'
import EstilistaPerfilView from '@/views/EstilistaPerfilView.vue'
import EstilistaServiciosView from '@/views/EstilistaServiciosView.vue'
import EstilistaEstadisticasView from '@/views/EstilistaEstadisticasView.vue'

// Vistas de recepcionista
import RecepcionistaDashboardView from '@/views/RecepcionistaDashboardView.vue'
import RecepcionistaCitasView from '@/views/RecepcionistaCitasView.vue'
import RecepcionistaCrearCitaView from '@/views/RecepcionistaCrearCitaView.vue'
import RecepcionistaCalendarioView from '@/views/RecepcionistaCalendarioView.vue'
import RecepcionistaClientesView from '@/views/RecepcionistaClientesView.vue'
import RecepcionistaServiciosView from '@/views/RecepcionistaServiciosView.vue'

// Vistas de cliente
import ClientePanelView from '@/views/ClientePanelView.vue'
import ClienteMisCitasView from '@/views/ClienteMisCitasView.vue'
import ClienteReservarView from '@/views/ClienteReservarView.vue'
import ClienteServiciosView from '@/views/ClienteServiciosView.vue'
import ClienteEstilistasView from '@/views/ClienteEstilistasView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // =========================================================================
    // RUTAS PUBLICAS (sin autenticacion)
    // =========================================================================
    {
      path: '/',
      name: 'landing',
      component: LandingView,
      meta: { requiresGuest: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true }
    },
    {
      path: '/registro',
      name: 'registro',
      component: RegisterView,
      meta: { requiresGuest: true }
    },

    // =========================================================================
    // RUTAS DE ADMINISTRADOR (requiere auth + rol=admin)
    // =========================================================================
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, requiredRole: 'administrador' },
      children: [
        { path: '', name: 'admin-dashboard', component: AdminDashboardView },
        { path: 'peluquerias', name: 'admin-peluquerias', component: AdminPeluqueriasView },
        { path: 'usuarios', name: 'admin-usuarios', component: AdminUsuariosView },
        { path: 'estilistas', name: 'admin-estilistas', component: AdminEstilistasView },
        { path: 'servicios', name: 'admin-servicios', component: AdminServiciosView },
        { path: 'citas', name: 'admin-citas', component: AdminCitasView },
        { path: 'horarios', name: 'admin-horarios', component: AdminHorariosView },
      ]
    },

    // =========================================================================
    // RUTAS DE ESTILISTA (requiere auth + rol=estilista)
    // =========================================================================
    {
      path: '/estilista',
      component: EstilistaLayout,
      meta: { requiresAuth: true, requiredRole: 'estilista' },
      children: [
        { path: '', name: 'estilista-dashboard', component: EstilistaDashboardView },
        { path: 'citas', name: 'estilista-citas', component: EstilistaCitasView },
        { path: 'historial', name: 'estilista-historial', component: EstilistaHistorialView },
        { path: 'perfil', name: 'estilista-perfil', component: EstilistaPerfilView },
        { path: 'servicios', name: 'estilista-servicios', component: EstilistaServiciosView },
        { path: 'estadisticas', name: 'estilista-estadisticas', component: EstilistaEstadisticasView },
      ]
    },

    // =========================================================================
    // RUTAS DE RECEPCIONISTA (requiere auth + rol=recepcionista)
    // =========================================================================
    {
      path: '/recepcionista',
      component: RecepcionistaLayout,
      meta: { requiresAuth: true, requiredRole: 'recepcionista' },
      children: [
        { path: '', name: 'recepcionista-dashboard', component: RecepcionistaDashboardView },
        { path: 'citas', name: 'recepcionista-citas', component: RecepcionistaCitasView },
        { path: 'citas/crear', name: 'recepcionista-crear-cita', component: RecepcionistaCrearCitaView },
        { path: 'calendario', name: 'recepcionista-calendario', component: RecepcionistaCalendarioView },
        { path: 'clientes', name: 'recepcionista-clientes', component: RecepcionistaClientesView },
        { path: 'servicios', name: 'recepcionista-servicios', component: RecepcionistaServiciosView },
      ]
    },

    // =========================================================================
    // RUTAS DE CLIENTE (requiere auth + rol=cliente)
    // =========================================================================
    {
      path: '/cliente',
      component: ClienteLayout,
      meta: { requiresAuth: true, requiredRole: 'cliente' },
      children: [
        { path: '', name: 'cliente-panel', component: ClientePanelView },
        { path: 'mis-citas', name: 'cliente-mis-citas', component: ClienteMisCitasView },
        { path: 'reservar', name: 'cliente-reservar', component: ClienteReservarView },
        { path: 'servicios', name: 'cliente-servicios', component: ClienteServiciosView },
        { path: 'estilistas', name: 'cliente-estilistas', component: ClienteEstilistasView },
      ]
    },

    // =========================================================================
    // RUTA POR DEFECTO — Redirige segun rol o a landing
    // =========================================================================
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// ============================================================================
// NAVIGATION GUARD — Control de acceso por autenticacion y rol
// ============================================================================
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Si hay token pero no tenemos datos del usuario en memoria,
  // intentar obtenerlos del backend (verifica que el token sea valido)
  if (authStore.token && !authStore.user) {
    await authStore.fetchProfile()
  }

  const isAuthenticated = authStore.isAuthenticated
  const userRol = authStore.userRol

  // --- Rutas que requieren NO estar autenticado (login, registro, landing) ---
  if (to.meta.requiresGuest) {
    if (isAuthenticated) {
      // Ya esta logueado: redirigir a su panel segun rol
      return next(redirigirPorRol(userRol))
    }
    return next()
  }

  // --- Rutas que requieren autenticacion ---
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      return next('/login')
    }

    // Verificar rol requerido (si esta definido en la ruta)
    if (to.meta.requiredRole && userRol !== to.meta.requiredRole) {
      // Rol incorrecto: redirigir al panel correcto
      return next(redirigirPorRol(userRol))
    }

    return next()
  }

  next()
})

/**
 * Devuelve la ruta correcta segun el rol del usuario.
 */
function redirigirPorRol(rol) {
  switch (rol) {
    case 'administrador': return '/admin'
    case 'estilista': return '/estilista'
    case 'recepcionista': return '/recepcionista'
    case 'cliente': return '/cliente'
    default: return '/login'
  }
}

export default router