<template>
  <div class="page">
    <!-- WELCOME HEADER -->
    <div class="page-header">
      <div class="header-text">
        <h1>{{ $t('estilista.dashboard.welcome', { name: authStore.userName }) }}</h1>
        <span v-if="authStore.user?.especialidad" class="especialidad-tag">
          {{ authStore.user.especialidad }}
        </span>
      </div>
    </div>

    <!-- LOADING / ERROR -->
    <div v-if="loading" class="empty-state">{{ $t('estilista.dashboard.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>

    <template v-else>
      <!-- STATS CARDS -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-label">{{ $t('estilista.dashboard.citasHoy') }}</span>
          <span class="stat-value">{{ data.total_citas_hoy }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">{{ $t('estilista.dashboard.pendientes') }}</span>
          <span class="stat-value">{{ data.total_citas_pendientes }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">{{ $t('estilista.dashboard.proximas') }}</span>
          <span class="stat-value">{{ data.citas_proximas.length }}</span>
        </div>
      </div>

      <!-- CITAS PROXIMAS -->
      <section class="section">
        <h2 class="section-title">{{ $t('estilista.dashboard.proximasCitas') }}</h2>
        <div v-if="data.citas_proximas.length === 0" class="empty-state">
          {{ $t('estilista.dashboard.noProximas') }}
        </div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>{{ $t('estilista.dashboard.fecha') }}</th>
              <th>{{ $t('estilista.dashboard.hora') }}</th>
              <th>{{ $t('estilista.dashboard.cliente') }}</th>
              <th>{{ $t('estilista.dashboard.servicio') }}</th>
              <th>{{ $t('estilista.dashboard.estado') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cita in data.citas_proximas" :key="cita.id">
              <td class="mono">{{ formatDate(cita.fecha) }}</td>
              <td class="mono">{{ formatTime(cita.hora_inicio) }}</td>
              <td class="strong">{{ cita.cliente?.nombre_completo || '—' }}</td>
              <td>{{ cita.servicio?.nombre || '—' }}</td>
              <td>
                <span :class="['badge', 'estado-' + cita.estado]">
                  {{ formatEstado(cita.estado) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- HORARIO SEMANAL -->
      <section class="section">
        <h2 class="section-title">{{ $t('estilista.dashboard.horarioSemanal') }}</h2>
        <div v-if="data.horarios.length === 0" class="empty-state">
          {{ $t('estilista.dashboard.noHorarios') }}
        </div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>{{ $t('estilista.dashboard.dia') }}</th>
              <th>{{ $t('estilista.dashboard.entrada') }}</th>
              <th>{{ $t('estilista.dashboard.salida') }}</th>
              <th>{{ $t('estilista.dashboard.estado') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in data.horarios" :key="h.id">
              <td class="strong">{{ capitalizeDay(h.dia_semana) }}</td>
              <td class="mono">{{ formatTime(h.hora_inicio) }}</td>
              <td class="mono">{{ formatTime(h.hora_fin) }}</td>
              <td>
                <span :class="['badge', h.activo ? 'activo' : 'inactivo-badge']">
                  {{ h.activo ? t('common.states.activo') : t('common.states.inactivo') }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const { formatDate, formatTime } = useLocale()
const authStore = useAuthStore()

// ============================================================================
// STATE
// ============================================================================
const loading = ref(false)
const error = ref(null)
const data = ref({
  estilista: null,
  citas_proximas: [],
  horarios: [],
  total_citas_hoy: 0,
  total_citas_pendientes: 0,
})

// ============================================================================
// HELPERS
// ============================================================================
function formatEstado(estado) {
  const map = {
    pendiente: t('common.states.pendiente'),
    confirmada: t('common.states.confirmada'),
    completada: t('common.states.completada'),
    cancelada: t('common.states.cancelada'),
  }
  return map[estado] || estado
}

function capitalizeDay(dia) {
  if (!dia) return '—'
  return dia.charAt(0).toUpperCase() + dia.slice(1)
}

// ============================================================================
// API
// ============================================================================
async function fetchPanel() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/panel-estilista/')
    data.value = response.data
  } catch (err) {
    error.value = t('estilista.dashboard.error')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => {
  fetchPanel()
})
</script>

<style scoped>
/* ===== PAGE LAYOUT ===== */
.page {
  padding: 1.5rem;
  background: #0c0c0c;
  min-height: 100vh;
  color: #ccc;
  font-family: 'Inter', system-ui, sans-serif;
}

/* ===== HEADER ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.header-text {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.page-header h1 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0;
}

.especialidad-tag {
  padding: 0.2rem 0.55rem;
  background: #1a1812;
  border: 1px solid #2a2518;
  border-radius: 4px;
  font-size: 0.7rem;
  color: #b8a44a;
  font-weight: 500;
}

/* ===== STATS CARDS ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.75rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 1rem 1.25rem;
  background: #141414;
  border: 1px solid #222;
  border-radius: 10px;
}

.stat-label {
  font-size: 0.7rem;
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

/* ===== SECTION ===== */
.section {
  margin-bottom: 1.75rem;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0 0 0.75rem;
}

/* ===== EMPTY / ERROR ===== */
.empty-state {
  padding: 2.5rem 1rem;
  text-align: center;
  color: #555;
  font-size: 0.85rem;
}
.error-state { color: #b05a5a; }

/* ===== TABLE ===== */
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}
thead th {
  text-align: left;
  padding: 0.6rem 0.75rem;
  color: #666;
  font-weight: 500;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid #222;
}
tbody td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #181818;
  color: #bbb;
  vertical-align: middle;
}
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: #111; }

.strong { color: #e8e8e8; font-weight: 500; }
.mono { font-variant-numeric: tabular-nums; }

/* ===== BADGES ===== */
.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
}

.estado-pendiente {
  background: #1a1812;
  color: #b8a44a;
}

.estado-confirmada {
  background: #122218;
  color: #5fa868;
}

.estado-completada {
  background: #121820;
  color: #5a8fbf;
}

.estado-cancelada {
  background: #1a1212;
  color: #b05a5a;
}

.activo {
  background: #122218;
  color: #5fa868;
}

.inactivo-badge {
  background: #1a1212;
  color: #b05a5a;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .page { padding: 1rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .stats-grid { grid-template-columns: 1fr; }
  .table { font-size: 0.75rem; }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>