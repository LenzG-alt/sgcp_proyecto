<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <div class="header-left">
        <h1>{{ $t('recepcionista.dashboard.title') }}</h1>
        <span class="badge recepcionista">{{ $t('recepcionista.role') }}</span>
      </div>
      <div class="header-right">
        <div v-if="data" class="date-display">
          <span class="date-label">{{ $t('recepcionista.dashboard.today') }}</span>
          <span class="date-value">{{ localeFormatDate(data.fecha_hoy) }}</span>
          <span class="day-value">{{ capitalize(data.dia_semana) }}</span>
        </div>
      </div>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="empty-state">{{ $t('recepcionista.dashboard.loading') }}</div>

    <!-- ERROR -->
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>

    <!-- CONTENT -->
    <template v-else-if="data">
      <!-- STATS CARDS -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total-icon">C</div>
          <div class="stat-info">
            <span class="stat-value">{{ data.total_citas_hoy }}</span>
            <span class="stat-label">{{ $t('recepcionista.dashboard.citasHoy') }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pendiente-icon">P</div>
          <div class="stat-info">
            <span class="stat-value">{{ data.pendientes_hoy }}</span>
            <span class="stat-label">{{ $t('recepcionista.dashboard.pendientes') }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon confirmada-icon">OK</div>
          <div class="stat-info">
            <span class="stat-value">{{ data.confirmadas_hoy }}</span>
            <span class="stat-label">{{ $t('recepcionista.dashboard.confirmadas') }}</span>
          </div>
        </div>
      </div>

      <!-- TODAY'S APPOINTMENTS -->
      <section class="section">
        <div class="section-header">
          <h2>{{ $t('recepcionista.dashboard.todayAppointments') }}</h2>
          <span class="section-count">{{ data.citas_hoy.length }} {{ data.citas_hoy.length !== 1 ? $t('recepcionista.dashboard.citas') : $t('recepcionista.dashboard.cita') }}</span>
        </div>

        <div v-if="data.citas_hoy.length === 0" class="empty-state">
          {{ $t('recepcionista.dashboard.noAppointmentsToday') }}
        </div>

        <div v-else class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>{{ $t('recepcionista.dashboard.th.hora') }}</th>
                <th>{{ $t('recepcionista.dashboard.th.cliente') }}</th>
                <th>{{ $t('recepcionista.dashboard.th.estilista') }}</th>
                <th>{{ $t('recepcionista.dashboard.th.servicio') }}</th>
                <th>{{ $t('recepcionista.dashboard.th.estado') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cita in data.citas_hoy" :key="cita.id">
                <td class="mono strong">{{ localeFormatTime(cita.hora_inicio) }}</td>
                <td class="strong">{{ cita.cliente?.nombre_completo || '—' }}</td>
                <td>{{ cita.estilista?.nombre_completo || '—' }}</td>
                <td>{{ cita.servicio?.nombre || '—' }}</td>
                <td>
                  <span :class="['badge', 'estado-' + cita.estado]">
                    {{ t('common.states.' + cita.estado) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- AVAILABLE STYLISTS -->
      <section class="section">
        <div class="section-header">
          <h2>{{ $t('recepcionista.dashboard.availableStylists') }}</h2>
          <span class="section-count">{{ data.estilistas_disponibles.length }} {{ data.estilistas_disponibles.length !== 1 ? $t('recepcionista.dashboard.estilistas') : $t('recepcionista.dashboard.estilista') }}</span>
        </div>

        <div v-if="data.estilistas_disponibles.length === 0" class="empty-state">
          {{ $t('recepcionista.dashboard.noAvailableStylists') }}
        </div>

        <ul v-else class="stylist-list">
          <li v-for="est in data.estilistas_disponibles" :key="est.id" class="stylist-card">
            <div class="stylist-avatar">{{ getInitials(est.nombre_completo) }}</div>
            <div class="stylist-info">
              <span class="stylist-name">{{ est.nombre_completo }}</span>
              <span class="stylist-email">{{ est.email || '—' }}</span>
            </div>
            <span class="badge estilista">{{ $t('recepcionista.dashboard.stylistBadge') }}</span>
          </li>
        </ul>
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
const { formatDate: localeFormatDate, formatTime: localeFormatTime } = useLocale()
const authStore = useAuthStore()

const data = ref(null)
const loading = ref(false)
const error = ref(null)

// ============================================================================
// HELPERS
// ============================================================================
function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

function getInitials(name) {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  }
  return parts[0].substring(0, 2).toUpperCase()
}

// ============================================================================
// API
// ============================================================================
async function loadPanel() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/panel-recepcionista/')
    data.value = response.data
  } catch (err) {
    error.value = t('recepcionista.dashboard.errorLoad')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => {
  loadPanel()
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

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-header h1 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.date-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.85rem;
  background: #161616;
  border: 1px solid #252525;
  border-radius: 8px;
}

.date-label {
  font-size: 0.7rem;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.date-value {
  font-size: 0.8rem;
  color: #e8e8e8;
  font-weight: 500;
}

.day-value {
  font-size: 0.75rem;
  color: #888;
  text-transform: capitalize;
}

/* ===== BADGES ===== */
.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
}

.badge.recepcionista {
  background: #122218;
  color: #5fa868;
}

.badge.estilista {
  background: #1a1812;
  color: #b8a44a;
}

.badge.estado-pendiente {
  background: #1a1810;
  color: #b8a44a;
}

.badge.estado-confirmada {
  background: #122218;
  color: #5fa868;
}

.badge.estado-completada {
  background: #121820;
  color: #5a8fbf;
}

.badge.estado-cancelada {
  background: #1a1212;
  color: #b05a5a;
}

/* ===== STATS GRID ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.1rem 1.25rem;
  background: #141414;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  transition: border-color 0.15s;
}

.stat-card:hover {
  border-color: #2a2a2a;
}

.stat-icon {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 1.15rem;
  flex-shrink: 0;
}

.total-icon {
  background: #121820;
}

.pendiente-icon {
  background: #1a1810;
}

.confirmada-icon {
  background: #122218;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e8e8e8;
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: #666;
  font-weight: 400;
}

/* ===== SECTIONS ===== */
.section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0;
}

.section-count {
  font-size: 0.75rem;
  color: #555;
}

/* ===== EMPTY STATE ===== */
.empty-state {
  padding: 3rem 1rem;
  text-align: center;
  color: #555;
  font-size: 0.85rem;
}

.error-state {
  color: #b05a5a;
}

/* ===== TABLE ===== */
.table-wrapper {
  overflow-x: auto;
}

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

tbody tr:last-child td {
  border-bottom: none;
}

tbody tr:hover {
  background: #111;
}

.strong {
  color: #e8e8e8;
  font-weight: 500;
}

.mono {
  font-variant-numeric: tabular-nums;
}

/* ===== STYLIST LIST ===== */
.stylist-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stylist-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 1rem;
  background: #141414;
  border: 1px solid #1e1e1e;
  border-radius: 10px;
  transition: border-color 0.15s;
}

.stylist-card:hover {
  border-color: #2a2a2a;
}

.stylist-avatar {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #1a1812;
  color: #b8a44a;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.stylist-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  flex: 1;
  min-width: 0;
}

.stylist-name {
  font-size: 0.85rem;
  color: #e8e8e8;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stylist-email {
  font-size: 0.75rem;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .table {
    font-size: 0.75rem;
  }

  .date-display {
    width: 100%;
    justify-content: center;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>