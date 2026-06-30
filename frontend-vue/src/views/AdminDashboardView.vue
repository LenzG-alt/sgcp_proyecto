<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <div class="header-left">
        <h1>{{ $t('admin.dashboard.title') }}</h1>
        <p class="page-subtitle">{{ $t('admin.dashboard.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <button class="btn-refresh" @click="loadAll" :disabled="loading">
          {{ loading ? $t('admin.dashboard.refreshing') : $t('admin.dashboard.refresh') }}
        </button>
      </div>
    </div>

    <!-- LOADING -->
    <div v-if="loading && !initialized" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('admin.dashboard.loading') }}</p>
    </div>

    <!-- ERROR -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="btn-secondary" @click="loadAll">{{ $t('admin.dashboard.retry') }}</button>
    </div>

    <!-- DASHBOARD CONTENT -->
    <template v-else>
      <!-- STATS GRID -->
      <div class="stats-grid">
        <div class="stat-card stat-card--purple">
          <div class="stat-icon">U</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.totalUsuarios }}</span>
            <span class="stat-label">{{ $t('admin.dashboard.totalUsers') }}</span>
          </div>
        </div>

        <div class="stat-card stat-card--yellow">
          <div class="stat-icon">E</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.totalEstilistas }}</span>
            <span class="stat-label">{{ $t('admin.dashboard.stylists') }}</span>
          </div>
        </div>

        <div class="stat-card stat-card--blue">
          <div class="stat-icon">C</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.totalCitas }}</span>
            <span class="stat-label">{{ $t('admin.dashboard.totalAppointments') }}</span>
          </div>
        </div>

        <div class="stat-card stat-card--green">
          <div class="stat-icon">H</div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.citasHoy }}</span>
            <span class="stat-label">{{ $t('admin.dashboard.todayAppointments') }}</span>
          </div>
        </div>
      </div>

      <!-- TWO COLUMN LAYOUT -->
      <div class="dashboard-grid">
        <!-- RECENT APPOINTMENTS -->
        <div class="section-card section-card--wide">
          <div class="section-header">
            <h2>{{ $t('admin.dashboard.recentAppointments') }}</h2>
            <router-link :to="{ name: 'admin-citas' }" class="section-link">
              {{ $t('admin.dashboard.viewAll') }} →
            </router-link>
          </div>

          <div v-if="loadingCitas" class="section-loading">{{ $t('admin.dashboard.loadingAppointments') }}</div>
          <div v-else-if="recentCitas.length === 0" class="section-empty">
            {{ $t('admin.dashboard.noAppointments') }}
          </div>
          <div v-else class="citas-list">
            <div
              v-for="cita in recentCitas"
              :key="cita.id"
              class="cita-item"
            >
              <div class="cita-left">
                <span class="cita-date">{{ formatDate(cita.fecha) }}</span>
                <span class="cita-time">{{ formatTime(cita.hora_inicio) }} - {{ formatTime(cita.hora_fin) }}</span>
              </div>
              <div class="cita-center">
                <span class="cita-cliente">{{ cita.cliente?.nombre_completo || '—' }}</span>
                <span class="cita-servicio">{{ cita.servicio?.nombre || '—' }}</span>
              </div>
              <div class="cita-right">
                <span class="cita-estilista">{{ cita.estilista?.nombre_completo || '—' }}</span>
                <span :class="['cita-estado', estadoClass(cita.estado)]">{{ formatEstado(cita.estado) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- QUICK LINKS -->
        <div class="section-card">
          <div class="section-header">
            <h2>{{ $t('admin.dashboard.quickAccess') }}</h2>
          </div>
          <div class="quick-links">
            <router-link :to="{ name: 'admin-usuarios' }" class="quick-link">
              <span class="quick-link-icon" style="color: #a78bfa;">U</span>
              <div class="quick-link-info">
                <span class="quick-link-title">{{ $t('admin.nav.usuarios') }}</span>
                <span class="quick-link-desc">{{ $t('admin.dashboard.quickAccessItems.usuarios') }}</span>
              </div>
              <span class="quick-link-arrow">→</span>
            </router-link>

            <router-link :to="{ name: 'admin-estilistas' }" class="quick-link">
              <span class="quick-link-icon" style="color: #b8a44a;">E</span>
              <div class="quick-link-info">
                <span class="quick-link-title">{{ $t('admin.nav.estilistas') }}</span>
                <span class="quick-link-desc">{{ $t('admin.dashboard.quickAccessItems.estilistas') }}</span>
              </div>
              <span class="quick-link-arrow">→</span>
            </router-link>

            <router-link :to="{ name: 'admin-citas' }" class="quick-link">
              <span class="quick-link-icon" style="color: #5a8fbf;">C</span>
              <div class="quick-link-info">
                <span class="quick-link-title">{{ $t('admin.nav.citas') }}</span>
                <span class="quick-link-desc">{{ $t('admin.dashboard.quickAccessItems.citas') }}</span>
              </div>
              <span class="quick-link-arrow">→</span>
            </router-link>

            <router-link :to="{ name: 'admin-servicios' }" class="quick-link">
              <span class="quick-link-icon" style="color: #5fa868;">S</span>
              <div class="quick-link-info">
                <span class="quick-link-title">{{ $t('admin.nav.servicios') }}</span>
                <span class="quick-link-desc">{{ $t('admin.dashboard.quickAccessItems.servicios') }}</span>
              </div>
              <span class="quick-link-arrow">→</span>
            </router-link>

            <router-link :to="{ name: 'admin-peluquerias' }" class="quick-link">
              <span class="quick-link-icon" style="color: #b05a5a;">🏪</span>
              <div class="quick-link-info">
                <span class="quick-link-title">{{ $t('admin.nav.peluquerias') }}</span>
                <span class="quick-link-desc">{{ $t('admin.dashboard.quickAccessItems.peluquerias') }}</span>
              </div>
              <span class="quick-link-arrow">→</span>
            </router-link>

            <router-link :to="{ name: 'admin-horarios' }" class="quick-link">
              <span class="quick-link-icon" style="color: #ccc;">R</span>
              <div class="quick-link-info">
                <span class="quick-link-title">{{ $t('admin.nav.horarios') }}</span>
                <span class="quick-link-desc">{{ $t('admin.dashboard.quickAccessItems.horarios') }}</span>
              </div>
              <span class="quick-link-arrow">→</span>
            </router-link>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'
import api from '@/services/api'

const { t } = useI18n()
const { formatDate } = useLocale()

// ============================================================================
// STATE
// ============================================================================
const loading = ref(false)
const loadingCitas = ref(false)
const initialized = ref(false)
const error = ref(null)
const recentCitas = ref([])

const stats = reactive({
  totalUsuarios: 0,
  totalEstilistas: 0,
  totalCitas: 0,
  citasHoy: 0,
})

// ============================================================================
// HELPERS
// ============================================================================
function todayStr() {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

function formatTime(timeStr) {
  if (!timeStr) return '—'
  // Return HH:MM from HH:MM:SS
  return timeStr.substring(0, 5)
}

function formatEstado(estado) {
  const map = {
    pendiente: t('common.states.pendiente'),
    confirmada: t('common.states.confirmada'),
    completada: t('common.states.completada'),
    cancelada: t('common.states.cancelada'),
    'no asistio': t('common.states.noAsistio'),
  }
  return map[estado] || estado
}

function estadoClass(estado) {
  const map = {
    pendiente: 'estado-pendiente',
    confirmada: 'estado-confirmada',
    completada: 'estado-completada',
    cancelada: 'estado-cancelada',
    'no asistio': 'estado-no-asistio',
  }
  return map[estado] || ''
}

function extractResults(data) {
  if (Array.isArray(data)) return data
  return data.results || []
}

function extractCount(data) {
  if (Array.isArray(data)) return data.length
  return data.count || 0
}

// ============================================================================
// API CALLS
// ============================================================================
async function loadStats() {
  // Fetch total users
  try {
    const resUsers = await api.get('/usuarios/')
    stats.totalUsuarios = extractCount(resUsers.data)
  } catch (err) {
    console.error('Error cargando usuarios:', err)
  }

  // Fetch total estilistas
  try {
    const resEst = await api.get('/usuarios/', { params: { rol: 'estilista' } })
    stats.totalEstilistas = extractCount(resEst.data)
  } catch (err) {
    console.error('Error cargando estilistas:', err)
  }

  // Fetch citas (total + recent)
  try {
    const resCitas = await api.get('/citas/', { params: { page_size: 8 } })
    const citasData = resCitas.data
    const allCitas = extractResults(citasData)

    stats.totalCitas = extractCount(citasData)
    stats.citasHoy = allCitas.filter(c => c.fecha === todayStr()).length

    // Store recent citas (last 8, already ordered from API or we reverse)
    recentCitas.value = allCitas.slice(0, 8)
  } catch (err) {
    console.error('Error cargando citas:', err)
  }
}

async function loadAll() {
  loading.value = true
  error.value = null
  try {
    await Promise.all([loadStats()])
    initialized.value = true
  } catch (err) {
    error.value = t('admin.dashboard.loadError')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => {
  loadAll()
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
  align-items: flex-start;
  margin-bottom: 1.75rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.page-header h1 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0;
}

.page-subtitle {
  font-size: 0.8rem;
  color: #555;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* ===== BUTTONS ===== */
.btn-refresh {
  padding: 0.5rem 1rem;
  background: #1a1a1a;
  color: #ccc;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-refresh:hover { color: #e8e8e8; border-color: #444; }
.btn-refresh:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-secondary {
  padding: 0.5rem 1rem;
  background: none;
  color: #888;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-secondary:hover { color: #ccc; border-color: #444; }

/* ===== LOADING / ERROR STATES ===== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  gap: 1rem;
  color: #555;
  font-size: 0.85rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #222;
  border-top-color: #a78bfa;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  gap: 1rem;
  color: #b05a5a;
  font-size: 0.85rem;
}

/* ===== STATS GRID ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: #111;
  border: 1px solid #1a1a1a;
  border-radius: 12px;
  transition: border-color 0.2s;
}
.stat-card:hover {
  border-color: #2a2a2a;
}

.stat-icon {
  font-size: 1.5rem;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  flex-shrink: 0;
}

.stat-card--purple .stat-icon { background: rgba(167, 139, 250, 0.1); }
.stat-card--yellow .stat-icon { background: rgba(184, 164, 74, 0.1); }
.stat-card--blue .stat-icon { background: rgba(90, 143, 191, 0.1); }
.stat-card--green .stat-icon { background: rgba(95, 168, 104, 0.1); }

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e8e8e8;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.stat-card--purple .stat-value { color: #a78bfa; }
.stat-card--yellow .stat-value { color: #b8a44a; }
.stat-card--blue .stat-value { color: #5a8fbf; }
.stat-card--green .stat-value { color: #5fa868; }

.stat-label {
  font-size: 0.75rem;
  color: #666;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ===== DASHBOARD GRID ===== */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 1rem;
  align-items: start;
}

/* ===== SECTION CARDS ===== */
.section-card {
  background: #111;
  border: 1px solid #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #1a1a1a;
}

.section-header h2 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0;
}

.section-link {
  font-size: 0.75rem;
  color: #a78bfa;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.15s;
}
.section-link:hover { opacity: 0.75; }

.section-loading,
.section-empty {
  padding: 2rem 1rem;
  text-align: center;
  color: #444;
  font-size: 0.8rem;
}

/* ===== CITAS LIST ===== */
.citas-list {
  display: flex;
  flex-direction: column;
}

.cita-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  align-items: center;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid #151515;
  transition: background 0.15s;
}
.cita-item:last-child { border-bottom: none; }
.cita-item:hover { background: #0e0e0e; }

.cita-left {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 90px;
}

.cita-date {
  font-size: 0.8rem;
  color: #e8e8e8;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.cita-time {
  font-size: 0.7rem;
  color: #555;
  font-variant-numeric: tabular-nums;
}

.cita-center {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.cita-cliente {
  font-size: 0.8rem;
  color: #e8e8e8;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cita-servicio {
  font-size: 0.7rem;
  color: #666;
}

.cita-right {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  align-items: flex-end;
  min-width: 110px;
}

.cita-estilista {
  font-size: 0.75rem;
  color: #aaa;
  white-space: nowrap;
}

.cita-estado {
  display: inline-block;
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.estado-pendiente { background: rgba(184, 164, 74, 0.12); color: #b8a44a; }
.estado-confirmada { background: rgba(90, 143, 191, 0.12); color: #5a8fbf; }
.estado-completada { background: rgba(95, 168, 104, 0.12); color: #5fa868; }
.estado-cancelada { background: rgba(176, 90, 90, 0.12); color: #b05a5a; }
.estado-no-asistio { background: rgba(176, 90, 90, 0.08); color: #8a5555; }

/* ===== QUICK LINKS ===== */
.quick-links {
  display: flex;
  flex-direction: column;
}

.quick-link {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 1.25rem;
  text-decoration: none;
  color: inherit;
  border-bottom: 1px solid #151515;
  transition: background 0.15s;
}
.quick-link:last-child { border-bottom: none; }
.quick-link:hover { background: #0e0e0e; }

.quick-link-icon {
  font-size: 1.15rem;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  flex-shrink: 0;
}

.quick-link-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
  flex: 1;
}

.quick-link-title {
  font-size: 0.8rem;
  font-weight: 500;
  color: #e8e8e8;
}

.quick-link-desc {
  font-size: 0.7rem;
  color: #555;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quick-link-arrow {
  font-size: 0.85rem;
  color: #333;
  flex-shrink: 0;
  transition: color 0.15s;
}
.quick-link:hover .quick-link-arrow { color: #666; }

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .section-card--wide {
    order: 1;
  }
}

@media (max-width: 768px) {
  .page { padding: 1rem; }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .cita-item {
    grid-template-columns: 1fr;
    gap: 0.35rem;
  }

  .cita-left {
    flex-direction: row;
    gap: 0.5rem;
    min-width: unset;
  }

  .cita-right {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    min-width: unset;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-value {
    font-size: 1.25rem;
  }
}
</style>