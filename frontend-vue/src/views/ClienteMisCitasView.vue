<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('cliente.misCitas.title') }}</h1>
      <router-link to="/cliente/reservar" class="btn-primary">{{ $t('cliente.misCitas.newAppointment') }}</router-link>
    </div>

    <!-- FILTROS -->
    <div class="filters">
      <select v-model="filterEstado" class="select-filter" @change="loadCitas">
        <option value="">{{ $t('cliente.misCitas.allStates') }}</option>
        <option value="pendiente">{{ t('common.states.pendiente') }}</option>
        <option value="confirmada">{{ t('common.states.confirmada') }}</option>
        <option value="completada">{{ t('common.states.completada') }}</option>
        <option value="cancelada">{{ t('common.states.cancelada') }}</option>
      </select>
      <label class="toggle-proximas">
        <input type="checkbox" v-model="soloProximas" @change="loadCitas" />
        <span>{{ $t('cliente.misCitas.upcomingOnly') }}</span>
      </label>
    </div>

    <!-- LOADING / ERROR / EMPTY -->
    <div v-if="loading" class="empty-state">{{ $t('cliente.misCitas.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <div v-else-if="citas.length === 0" class="empty-state">{{ $t('cliente.misCitas.notFound') }}</div>

    <!-- LISTA DE CITAS -->
    <div v-else class="citas-list">
      <div v-for="cita in citas" :key="cita.id" class="cita-card" @click="verDetalle(cita)">
        <div class="cita-main">
          <div class="cita-top">
            <span class="cita-fecha mono">{{ formatDate(cita.fecha) }}</span>
            <span class="cita-hora mono">{{ formatTime(cita.hora_inicio) }} — {{ formatTime(cita.hora_fin) }}</span>
            <span :class="['badge', 'estado-' + cita.estado]">{{ formatEstado(cita.estado) }}</span>
          </div>
          <div class="cita-servicio strong">{{ cita.servicio?.nombre || '—' }}</div>
          <div class="cita-meta muted">
            <span>{{ $t('cliente.misCitas.stylist') }}: {{ cita.estilista?.nombre_completo || '—' }}</span>
            <span v-if="cita.estilista?.especialidad" class="sep">·</span>
            <span v-if="cita.estilista?.especialidad">{{ cita.estilista.especialidad }}</span>
          </div>
          <div v-if="cita.peluqueria" class="cita-meta muted">
            {{ cita.peluqueria.nombre }} — {{ cita.peluqueria.direccion }}
          </div>
          <div v-if="cita.observaciones" class="cita-obs muted">{{ cita.observaciones }}</div>
        </div>
        <div class="cita-actions" @click.stop>
          <button
            v-if="cita.estado === 'pendiente' || cita.estado === 'confirmada'"
            class="btn-cancelar"
            @click="abrirCancelar(cita)"
          >
            {{ $t('cliente.misCitas.cancel') }}
          </button>
        </div>
      </div>
    </div>

    <!-- PAGINACION -->
    <div v-if="totalPages > 1" class="pagination">
      <button :disabled="currentPage === 1" @click="changePage(currentPage - 1)">{{ $t('cliente.misCitas.previous') }}</button>
      <span class="page-info">{{ $t('cliente.misCitas.page', { current: currentPage, total: totalPages }) }}</span>
      <button :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">{{ $t('cliente.misCitas.next') }}</button>
    </div>

    <!-- MODAL: Detalle de cita -->
    <Teleport to="body">
      <div v-if="showDetalle" class="modal-overlay" @click.self="showDetalle = false">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ $t('cliente.misCitas.detailTitle') }}</h2>
            <button class="btn-close" @click="showDetalle = false">X</button>
          </div>
          <div v-if="detalleCita" class="modal-body detalle-body">
            <div class="detalle-row">
              <span class="detalle-label">{{ $t('cliente.misCitas.state') }}</span>
              <span :class="['badge', 'estado-' + detalleCita.estado]">{{ formatEstado(detalleCita.estado) }}</span>
            </div>
            <div class="detalle-row">
              <span class="detalle-label">{{ $t('cliente.misCitas.date') }}</span>
              <span class="strong">{{ formatDate(detalleCita.fecha) }}</span>
            </div>
            <div class="detalle-row">
              <span class="detalle-label">{{ $t('cliente.misCitas.time') }}</span>
              <span>{{ formatTime(detalleCita.hora_inicio) }} — {{ formatTime(detalleCita.hora_fin) }}</span>
            </div>
            <div class="detalle-row">
              <span class="detalle-label">{{ $t('cliente.misCitas.service') }}</span>
              <span class="strong">{{ detalleCita.servicio?.nombre || '—' }}</span>
            </div>
            <div class="detalle-row">
              <span class="detalle-label">{{ $t('cliente.misCitas.price') }}</span>
              <span>{{ detalleCita.servicio?.precio ? formatCurrency(detalleCita.servicio.precio) : '—' }}</span>
            </div>
            <div class="detalle-row">
              <span class="detalle-label">{{ $t('cliente.misCitas.duration') }}</span>
              <span>{{ detalleCita.servicio?.duracion_minutos ? detalleCita.servicio.duracion_minutos + ' ' + $t('common.min') : '—' }}</span>
            </div>
            <div class="detalle-row">
              <span class="detalle-label">{{ $t('cliente.misCitas.stylist') }}</span>
              <span>{{ detalleCita.estilista?.nombre_completo || '—' }}</span>
            </div>
            <div v-if="detalleCita.estilista?.especialidad" class="detalle-row">
              <span class="detalle-label">{{ $t('cliente.misCitas.specialty') }}</span>
              <span>{{ detalleCita.estilista.especialidad }}</span>
            </div>
            <div v-if="detalleCita.peluqueria" class="detalle-row">
              <span class="detalle-label">{{ $t('cliente.misCitas.branch') }}</span>
              <span>{{ detalleCita.peluqueria.nombre }} — {{ detalleCita.peluqueria.direccion }}</span>
            </div>
            <div v-if="detalleCita.observaciones" class="detalle-row full">
              <span class="detalle-label">{{ $t('cliente.misCitas.observations') }}</span>
              <p class="detalle-text">{{ detalleCita.observaciones }}</p>
            </div>
          </div>
          <div v-if="detalleCita && (detalleCita.estado === 'pendiente' || detalleCita.estado === 'confirmada')" class="modal-actions">
            <button class="btn-danger" @click="showDetalle = false; abrirCancelar(detalleCita)">{{ $t('cliente.misCitas.cancelAppointment') }}</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- MODAL: Cancelar cita -->
    <Teleport to="body">
      <div v-if="showCancelar" class="modal-overlay" @click.self="showCancelar = false">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h2>{{ $t('cliente.misCitas.cancelTitle') }}</h2>
            <button class="btn-close" @click="showCancelar = false">X</button>
          </div>
          <div class="modal-body">
            <p v-html="$t('cliente.misCitas.cancelConfirm', { date: '<strong>' + formatDate(cancelTarget?.fecha) + '</strong>', time: '<strong>' + formatTime(cancelTarget?.hora_inicio) + '</strong>' })"></p>
            <p class="muted">{{ $t('cliente.misCitas.cancelWarning') }}</p>
            <div class="field" style="margin-top: 0.75rem;">
              <label>{{ $t('cliente.misCitas.cancelReason') }}</label>
              <textarea v-model="motivoCancel" rows="2" :placeholder="$t('cliente.misCitas.cancelReasonPlaceholder')"></textarea>
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showCancelar = false">{{ $t('cliente.misCitas.back') }}</button>
            <button class="btn-danger" @click="confirmarCancelar" :disabled="submitting">
              {{ submitting ? $t('cliente.misCitas.canceling') : $t('cliente.misCitas.confirmCancel') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'

const { t } = useI18n()
const { formatDate, formatTime, formatCurrency } = useLocale()

// ============================================================================
// STATE
// ============================================================================
const citas = ref([])
const loading = ref(false)
const submitting = ref(false)
const error = ref(null)
const filterEstado = ref('')
const soloProximas = ref(false)
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 20

// Modal detalle
const showDetalle = ref(false)
const detalleCita = ref(null)

// Modal cancelar
const showCancelar = ref(false)
const cancelTarget = ref(null)
const motivoCancel = ref('')

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

const totalPages = ref(1)

// ============================================================================
// API
// ============================================================================
async function loadCitas() {
  loading.value = true
  error.value = null
  try {
    const params = { page: currentPage.value, page_size: pageSize }
    if (filterEstado.value) params.estado = filterEstado.value
    if (soloProximas.value) params.proximas = 'true'

    const response = await api.get('/cliente/mis-citas/', { params })
    const data = response.data
    citas.value = data.results || []
    totalCount.value = data.count || 0
    totalPages.value = Math.max(1, Math.ceil(totalCount.value / pageSize))
  } catch (err) {
    error.value = t('cliente.misCitas.loadError')
    console.error(err)
  } finally {
    loading.value = false
  }
}

function changePage(page) {
  currentPage.value = page
  loadCitas()
}

// ============================================================================
// DETALLE
// ============================================================================
async function verDetalle(cita) {
  try {
    const response = await api.get(`/cliente/mis-citas/${cita.id}/`)
    detalleCita.value = response.data
    showDetalle.value = true
  } catch (err) {
    console.error('Error cargando detalle:', err)
  }
}

// ============================================================================
// CANCELAR
// ============================================================================
function abrirCancelar(cita) {
  cancelTarget.value = cita
  motivoCancel.value = ''
  showCancelar.value = true
}

async function confirmarCancelar() {
  if (!cancelTarget.value) return
  submitting.value = true
  try {
    const payload = {}
    if (motivoCancel.value.trim()) {
      payload.motivo = motivoCancel.value.trim()
    }
    await api.patch(`/cliente/mis-citas/${cancelTarget.value.id}/cancelar/`, payload)
    showCancelar.value = false
    await loadCitas()
  } catch (err) {
    const msg = err.response?.data?.detail || t('cliente.misCitas.cancelError')
    alert(msg)
    console.error(err)
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => { loadCitas() })
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
.page-header h1 {
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

/* ===== FILTERS ===== */
.filters {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  align-items: center;
}

.select-filter {
  padding: 0.5rem 0.75rem;
  background: #161616;
  border: 1px solid #252525;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 0.8rem;
  font-family: inherit;
  cursor: pointer;
}
.select-filter:focus { outline: none; border-color: #555; }

.toggle-proximas {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #888;
  font-size: 0.8rem;
  cursor: pointer;
}
.toggle-proximas input { accent-color: #5fa868; }

/* ===== CITAS LIST ===== */
.citas-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cita-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.15rem;
  background: #141414;
  border: 1px solid #1e1e1e;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s;
}
.cita-card:hover { border-color: #333; }

.cita-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  min-width: 0;
}

.cita-top {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}
.cita-fecha { font-size: 0.8rem; color: #888; }
.cita-hora { font-size: 0.8rem; color: #888; }
.cita-servicio { font-size: 0.88rem; }
.cita-meta { font-size: 0.78rem; display: flex; gap: 0.3rem; flex-wrap: wrap; }
.cita-obs { font-size: 0.75rem; margin-top: 0.15rem; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sep { color: #333; }

.cita-actions { flex-shrink: 0; margin-left: 1rem; }

.btn-cancelar {
  padding: 0.35rem 0.75rem;
  background: none;
  border: 1px solid #2a1a1a;
  border-radius: 6px;
  color: #c47a7a;
  font-size: 0.78rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-cancelar:hover { background: #1a1212; }

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

/* ===== PAGINATION ===== */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.25rem;
  padding: 0.75rem;
}
.pagination button {
  padding: 0.35rem 0.75rem;
  background: none;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  color: #888;
  font-size: 0.75rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.pagination button:hover:not(:disabled) { color: #e8e8e8; border-color: #444; }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }
.page-info { font-size: 0.75rem; color: #555; }

/* ===== EMPTY / ERROR ===== */
.empty-state { padding: 3rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }
.strong { color: #e8e8e8; font-weight: 500; }
.muted { color: #666; }
.mono { font-variant-numeric: tabular-nums; }

/* ===== MODAL ===== */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 1rem;
}
.modal {
  background: #141414; border: 1px solid #222; border-radius: 12px;
  width: 100%; max-width: 480px; max-height: 90vh; overflow-y: auto;
}
.modal-sm { max-width: 400px; }
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1.25rem 1.5rem; border-bottom: 1px solid #1a1a1a;
}
.modal-header h2 { font-size: 1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.btn-close { background: none; border: none; color: #666; font-size: 1.1rem; cursor: pointer; padding: 0.25rem; transition: color 0.15s; }
.btn-close:hover { color: #e8e8e8; }
.modal-body { padding: 1.25rem 1.5rem; }
.modal-body p { font-size: 0.85rem; color: #bbb; margin: 0 0 0.5rem; }
.muted { color: #555 !important; font-size: 0.8rem !important; }
.modal-actions {
  display: flex; justify-content: flex-end; gap: 0.5rem;
  padding: 1rem 1.5rem; border-top: 1px solid #1a1a1a;
}

.btn-secondary {
  padding: 0.5rem 1rem; background: none; color: #888;
  border: 1px solid #2a2a2a; border-radius: 8px;
  font-size: 0.8rem; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: all 0.15s;
}
.btn-secondary:hover { color: #ccc; border-color: #444; }

.btn-danger {
  padding: 0.5rem 1rem; background: #1a1212; color: #c47a7a;
  border: 1px solid #2a1a1a; border-radius: 8px;
  font-size: 0.8rem; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: all 0.15s;
}
.btn-danger:hover { background: #2a1a1a; }
.btn-danger:disabled { opacity: 0.4; cursor: not-allowed; }

/* ===== DETALLE BODY ===== */
.detalle-body { display: flex; flex-direction: column; gap: 0.6rem; }
.detalle-row {
  display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;
}
.detalle-row.full { flex-direction: column; gap: 0.3rem; }
.detalle-label { font-size: 0.75rem; color: #666; min-width: 100px; flex-shrink: 0; }
.detalle-text { font-size: 0.85rem; color: #bbb; margin: 0; line-height: 1.5; }

/* ===== FORM ===== */
.field { margin-bottom: 0.75rem; }
.field label { display: block; font-size: 0.75rem; font-weight: 500; color: #888; margin-bottom: 0.3rem; }
.field textarea {
  width: 100%; padding: 0.55rem 0.75rem; background: #1a1a1a;
  border: 1px solid #252525; border-radius: 8px;
  color: #e8e8e8; font-size: 0.85rem; font-family: inherit;
  box-sizing: border-box; resize: vertical; min-height: 50px;
}
.field textarea:focus { outline: none; border-color: #555; }
.field textarea::placeholder { color: #444; }

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .cita-card { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
  .cita-actions { margin-left: 0; align-self: flex-end; }
  .cita-obs { max-width: 100%; }
}
@media (max-width: 480px) {
  .cita-top { flex-direction: column; align-items: flex-start; gap: 0.2rem; }
}
</style>