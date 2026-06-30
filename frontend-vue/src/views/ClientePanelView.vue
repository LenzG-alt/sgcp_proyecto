<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <div class="header-text">
        <h1>{{ $t('cliente.panel.greeting', { name: authStore.userName }) }}</h1>
      </div>
      <router-link to="/cliente/reservar" class="btn-primary">{{ $t('cliente.panel.bookAppointment') }}</router-link>
    </div>

    <!-- LOADING / ERROR -->
    <div v-if="loading" class="empty-state">{{ $t('cliente.panel.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>

    <template v-else>
      <!-- PROXIMA CITA DESTACADA -->
      <div v-if="panel.estadisticas.proxima_cita" class="proxima-card">
        <div class="proxima-label">{{ $t('cliente.panel.nextAppointment') }}</div>
        <div class="proxima-body">
          <div class="proxima-info">
            <span class="proxima-fecha">{{ formatDate(panel.estadisticas.proxima_cita.fecha) }}</span>
            <span class="proxima-hora">{{ formatTime(panel.estadisticas.proxima_cita.hora_inicio) }} — {{ formatTime(panel.estadisticas.proxima_cita.hora_fin) }}</span>
          </div>
          <div class="proxima-detalle">
            <span class="strong">{{ panel.estadisticas.proxima_cita.servicio }}</span>
            <span class="muted">{{ $t('cliente.panel.with') }} {{ panel.estadisticas.proxima_cita.estilista }}</span>
          </div>
          <span :class="['badge', 'estado-' + panel.estadisticas.proxima_cita.estado]">
            {{ formatEstado(panel.estadisticas.proxima_cita.estado) }}
          </span>
        </div>
      </div>
      <div v-else class="proxima-card vacia">
        <div class="proxima-label">{{ $t('cliente.panel.noNextAppointments') }}</div>
        <router-link to="/cliente/reservar" class="link-action">{{ $t('cliente.panel.bookNow') }}</router-link>
      </div>

      <!-- STATS -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-label">{{ $t('cliente.panel.stats.total') }}</span>
          <span class="stat-value">{{ panel.estadisticas.total_citas }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">{{ $t('cliente.panel.stats.pending') }}</span>
          <span class="stat-value stat-pendiente">{{ panel.estadisticas.pendientes }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">{{ $t('cliente.panel.stats.confirmed') }}</span>
          <span class="stat-value stat-confirmada">{{ panel.estadisticas.confirmadas }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">{{ $t('cliente.panel.stats.completed') }}</span>
          <span class="stat-value stat-completada">{{ panel.estadisticas.completadas }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">{{ $t('cliente.panel.stats.cancelled') }}</span>
          <span class="stat-value stat-cancelada">{{ panel.estadisticas.canceladas }}</span>
        </div>
      </div>

      <!-- CITAS PROXIMAS -->
      <section class="section">
        <div class="section-header">
          <h2 class="section-title">{{ $t('cliente.panel.upcomingTitle') }}</h2>
          <router-link to="/cliente/mis-citas" class="link-action">{{ $t('cliente.panel.viewAll') }}</router-link>
        </div>
        <div v-if="panel.citas_proximas.length === 0" class="empty-state">
          {{ $t('cliente.panel.noUpcoming') }}
        </div>
        <div v-else class="citas-list">
          <div v-for="cita in panel.citas_proximas" :key="cita.id" class="cita-card">
            <div class="cita-left">
              <div class="cita-date">
                <span class="cita-fecha">{{ formatDate(cita.fecha) }}</span>
                <span class="cita-hora">{{ formatTime(cita.hora_inicio) }} — {{ formatTime(cita.hora_fin) }}</span>
              </div>
              <div class="cita-servicio strong">{{ cita.servicio?.nombre || '—' }}</div>
              <div class="cita-estilista muted">{{ cita.estilista?.nombre_completo || '—' }}</div>
            </div>
            <div class="cita-right">
              <span :class="['badge', 'estado-' + cita.estado]">
                {{ formatEstado(cita.estado) }}
              </span>
              <div v-if="cita.peluqueria" class="cita-lugar muted">
                {{ cita.peluqueria.nombre }}
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'

const { t } = useI18n()
const { formatDate, formatTime } = useLocale()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref(null)
const panel = ref({
  perfil: null,
  estadisticas: { total_citas: 0, pendientes: 0, confirmadas: 0, completadas: 0, canceladas: 0, proxima_cita: null },
  citas_proximas: [],
})

function formatEstado(estado) {
  const map = {
    pendiente: t('common.states.pendiente'),
    confirmada: t('common.states.confirmada'),
    completada: t('common.states.completada'),
    cancelada: t('common.states.cancelada'),
  }
  return map[estado] || estado
}

async function fetchPanel() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/cliente/panel/')
    panel.value = response.data
  } catch (err) {
    error.value = t('cliente.panel.loadError')
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchPanel() })
</script>

<style scoped>
.page {
  background: #0c0c0c;
  min-height: 100vh;
  color: #ccc;
  font-family: 'Inter', system-ui, sans-serif;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.header-text h1 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: #e8e8e8;
  color: #0c0c0c;
  border: none;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  text-decoration: none;
  transition: opacity 0.15s;
}
.btn-primary:hover { opacity: 0.85; }

/* ===== PROXIMA CITA ===== */
.proxima-card {
  padding: 1.25rem;
  background: #141414;
  border: 1px solid #222;
  border-radius: 10px;
  margin-bottom: 1.5rem;
}
.proxima-card.vacia {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.proxima-label {
  font-size: 0.7rem;
  font-weight: 500;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.6rem;
}
.proxima-card.vacia .proxima-label { margin-bottom: 0; }

.proxima-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.proxima-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.proxima-fecha { font-size: 1rem; font-weight: 600; color: #e8e8e8; }
.proxima-hora { font-size: 0.85rem; color: #888; }

.proxima-detalle {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.15rem;
}

.link-action {
  color: #5fa868;
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 500;
  transition: opacity 0.15s;
}
.link-action:hover { opacity: 0.8; }

/* ===== STATS ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.75rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 1rem;
  background: #141414;
  border: 1px solid #222;
  border-radius: 10px;
}

.stat-label {
  font-size: 0.65rem;
  font-weight: 500;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e8e8e8;
  line-height: 1;
}
.stat-pendiente { color: #b8a44a; }
.stat-confirmada { color: #5fa868; }
.stat-completada { color: #5a8fbf; }
.stat-cancelada { color: #b05a5a; }

/* ===== SECTION ===== */
.section { margin-bottom: 1.75rem; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0;
}

/* ===== CITAS LIST (CARDS) ===== */
.citas-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cita-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.9rem 1rem;
  background: #141414;
  border: 1px solid #1e1e1e;
  border-radius: 8px;
  transition: border-color 0.15s;
}
.cita-card:hover { border-color: #333; }

.cita-left {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.cita-date { display: flex; gap: 0.5rem; font-size: 0.8rem; color: #888; }
.cita-servicio { font-size: 0.85rem; }
.cita-estilista { font-size: 0.78rem; }

.cita-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.3rem;
}
.cita-lugar { font-size: 0.72rem; }

/* ===== BADGES ===== */
.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  white-space: nowrap;
}
.estado-pendiente { background: #1a1812; color: #b8a44a; }
.estado-confirmada { background: #122218; color: #5fa868; }
.estado-completada { background: #121820; color: #5a8fbf; }
.estado-cancelada { background: #1a1212; color: #b05a5a; }

/* ===== EMPTY / ERROR ===== */
.empty-state {
  padding: 2.5rem 1rem;
  text-align: center;
  color: #555;
  font-size: 0.85rem;
}
.error-state { color: #b05a5a; }

.strong { color: #e8e8e8; font-weight: 500; }
.muted { color: #666; }
.mono { font-variant-numeric: tabular-nums; }

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
  .cita-card { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
  .cita-right { align-items: flex-start; }
}

@media (max-width: 480px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .proxima-body { flex-direction: column; align-items: flex-start; }
  .proxima-detalle { align-items: flex-start; }
}
</style>