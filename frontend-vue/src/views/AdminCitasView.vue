<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('admin.citas.title') }}</h1>
      <div class="header-actions">
        <button @click="openModal()" class="btn-primary">{{ $t('admin.citas.addNew') }}</button>
      </div>
    </div>

    <!-- FILTROS -->
    <div class="filters">
      <input
        v-model="search"
        type="text"
        :placeholder="$t('admin.citas.searchPlaceholder')"
        class="input-search"
        @input="debouncedLoad"
      />
      <select v-model="filterEstado" class="select-filter" @change="loadCitas">
        <option value="">{{ $t('admin.citas.filterAllStates') }}</option>
        <option value="pendiente">{{ $t('common.states.pendiente') }}</option>
        <option value="confirmada">{{ $t('common.states.confirmada') }}</option>
        <option value="completada">{{ $t('common.states.completada') }}</option>
        <option value="cancelada">{{ $t('common.states.cancelada') }}</option>
      </select>
    </div>

    <!-- LOADING / ERROR / EMPTY -->
    <div v-if="loading" class="empty-state">{{ $t('admin.citas.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <div v-else-if="filteredCitas.length === 0" class="empty-state">{{ $t('admin.citas.noResults') }}</div>

    <!-- TABLA -->
    <table v-else class="table">
      <thead>
        <tr>
          <th>{{ $t('admin.citas.table.client') }}</th>
          <th>{{ $t('admin.citas.table.stylist') }}</th>
          <th>{{ $t('admin.citas.table.service') }}</th>
          <th>{{ $t('admin.citas.table.date') }}</th>
          <th>{{ $t('admin.citas.table.startTime') }}</th>
          <th>{{ $t('admin.citas.table.endTime') }}</th>
          <th>{{ $t('admin.citas.table.status') }}</th>
          <th>{{ $t('admin.citas.table.notes') }}</th>
          <th>{{ $t('common.actions') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in filteredCitas" :key="c.id">
          <td class="strong">{{ c.cliente?.nombre_completo || '—' }}</td>
          <td>{{ c.estilista?.nombre_completo || '—' }}</td>
          <td>{{ c.servicio?.nombre || '—' }}</td>
          <td class="mono">{{ formatDate(c.fecha) || '—' }}</td>
          <td class="mono">{{ formatTime(c.hora_inicio) || '—' }}</td>
          <td class="mono">{{ formatTime(c.hora_fin) || '—' }}</td>
          <td><span :class="['badge', c.estado]">{{ formatEstado(c.estado) }}</span></td>
          <td class="obs-cell">{{ c.observaciones || '—' }}</td>
          <td class="actions-cell">
            <button class="btn-icon" :title="$t('common.edit')" @click="openModal(c)">E</button>
            <button class="btn-icon btn-danger" :title="$t('common.delete')" @click="confirmDelete(c)">X</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- PAGINACION -->
    <div v-if="totalPages > 1" class="pagination">
      <button :disabled="currentPage === 1" @click="changePage(currentPage - 1)">{{ $t('common.previous') }}</button>
      <span class="page-info">{{ $t('common.page', { current: currentPage, total: totalPages }) }}</span>
      <button :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">{{ $t('common.next') }}</button>
    </div>

    <!-- MODAL: Crear / Editar Cita -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ isEditing ? $t('admin.citas.editTitle') : $t('admin.citas.newTitle') }}</h2>
            <button class="btn-close" @click="closeModal">X</button>
          </div>

          <form @submit.prevent="handleSubmit" class="modal-form">
            <!-- Cliente -->
            <div class="field">
              <label for="f-cliente">{{ $t('admin.citas.table.client') }} *</label>
              <select id="f-cliente" v-model="form.cliente_id" required>
                <option :value="null" disabled>{{ $t('admin.citas.selectClient') }}</option>
                <option v-for="cl in clientes" :key="cl.id" :value="cl.id">
                  {{ cl.nombre_completo }}
                </option>
              </select>
            </div>

            <!-- Estilista -->
            <div class="field">
              <label for="f-estilista">{{ $t('admin.citas.table.stylist') }} *</label>
              <select id="f-estilista" v-model="form.estilista_id" required>
                <option :value="null" disabled>{{ $t('admin.citas.selectStylist') }}</option>
                <option v-for="e in estilistas" :key="e.id" :value="e.id">
                  {{ e.nombre_completo }}
                </option>
              </select>
            </div>

            <!-- Servicio -->
            <div class="field">
              <label for="f-servicio">{{ $t('admin.citas.table.service') }} *</label>
              <select id="f-servicio" v-model="form.servicio_id" required>
                <option :value="null" disabled>{{ $t('admin.citas.selectService') }}</option>
                <option v-for="s in servicios" :key="s.id" :value="s.id">
                  {{ s.nombre }} — {{ formatCurrency(s.precio) }}
                </option>
              </select>
            </div>

            <!-- Fecha -->
            <div class="field">
              <label for="f-fecha">{{ $t('admin.citas.table.date') }} *</label>
              <input id="f-fecha" v-model="form.fecha" type="date" required />
            </div>

            <!-- Hora inicio / Hora fin -->
            <div class="row-2">
              <div class="field">
                <label for="f-hora-inicio">{{ $t('admin.citas.fieldStartTime') }}</label>
                <input id="f-hora-inicio" v-model="form.hora_inicio" type="time" required />
              </div>
              <div class="field">
                <label for="f-hora-fin">{{ $t('admin.citas.fieldEndTime') }}</label>
                <input id="f-hora-fin" v-model="form.hora_fin" type="time" required />
              </div>
            </div>

            <!-- Estado -->
            <div class="field">
              <label for="f-estado">{{ $t('admin.citas.table.status') }} *</label>
              <select id="f-estado" v-model="form.estado" required>
                <option value="pendiente">{{ $t('common.states.pendiente') }}</option>
                <option value="confirmada">{{ $t('common.states.confirmada') }}</option>
                <option value="completada">{{ $t('common.states.completada') }}</option>
                <option value="cancelada">{{ $t('common.states.cancelada') }}</option>
              </select>
            </div>

            <!-- Observaciones -->
            <div class="field">
              <label for="f-observaciones">{{ $t('admin.citas.table.notes') }}</label>
              <textarea
                id="f-observaciones"
                v-model="form.observaciones"
                rows="3"
                :placeholder="$t('admin.citas.fieldNotes')"
              ></textarea>
            </div>

            <!-- Errores del servidor -->
            <div v-if="formErrors.length > 0" class="form-errors">
              <p v-for="(e, i) in formErrors" :key="i">{{ e }}</p>
            </div>

            <!-- Botones -->
            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeModal">{{ $t('common.cancel') }}</button>
              <button type="submit" class="btn-primary" :disabled="submitting">
                {{ submitting ? $t('common.saving') : (isEditing ? $t('common.updating') : $t('admin.citas.create')) }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- MODAL: Confirmar Eliminacion -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h2>{{ $t('admin.citas.deleteConfirmTitle') }}</h2>
          </div>
          <div class="modal-body">
            <p v-html="$t('admin.citas.deleteConfirmMsg', { name: deleteTarget?.cliente?.nombre_completo || '', date: formatDate(deleteTarget?.fecha) || '' })"></p>
            <p class="muted">{{ $t('admin.citas.deleteWarning') }}</p>
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showDeleteModal = false">{{ $t('common.cancel') }}</button>
            <button class="btn-danger" @click="deleteCita" :disabled="submitting">
              {{ submitting ? $t('common.deleting') : $t('common.delete') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'
import api from '@/services/api'

const { t } = useI18n()
const { formatDate, formatTime, formatCurrency } = useLocale()

// ============================================================================
// STATE
// ============================================================================
const citas = ref([])
const clientes = ref([])
const estilistas = ref([])
const servicios = ref([])
const loading = ref(false)
const submitting = ref(false)
const error = ref(null)
const search = ref('')
const filterEstado = ref('')
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 20

// Modal
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const formErrors = ref([])

const form = ref(getEmptyForm())

// Delete modal
const showDeleteModal = ref(false)
const deleteTarget = ref(null)

// ============================================================================
// COMPUTED
// ============================================================================
const filteredCitas = computed(() => {
  let list = citas.value
  if (filterEstado.value) {
    list = list.filter(c => c.estado === filterEstado.value)
  }
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(c =>
      (c.cliente?.nombre_completo || '').toLowerCase().includes(q)
    )
  }
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))

// ============================================================================
// HELPERS
// ============================================================================
function getEmptyForm() {
  return {
    cliente_id: null,
    estilista_id: null,
    servicio_id: null,
    fecha: '',
    hora_inicio: '',
    hora_fin: '',
    estado: 'pendiente',
    observaciones: '',
  }
}

function formatEstado(estado) {
  const map = {
    pendiente: t('common.states.pendiente'),
    confirmada: t('common.states.confirmada'),
    completada: t('common.states.completada'),
    cancelada: t('common.states.cancelada'),
  }
  return map[estado] || estado
}

// Debounce para la busqueda
let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { currentPage.value = 1; loadCitas() }, 300)
}

// ============================================================================
// API CALLS
// ============================================================================
async function loadCitas() {
  loading.value = true
  error.value = null
  try {
    const params = { page: currentPage.value }
    const response = await api.get('/citas/', { params })
    const data = response.data
    citas.value = Array.isArray(data) ? data : (data.results || [])
    totalCount.value = data.count || citas.value.length
  } catch (err) {
    error.value = t('admin.citas.errorLoading')
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function loadClientes() {
  try {
    const res = await api.get('/usuarios/', { params: { rol: 'cliente' } })
    const data = res.data
    clientes.value = Array.isArray(data) ? data : (data.results || [])
  } catch (err) {
    console.error(err)
  }
}

async function loadEstilistas() {
  try {
    const res = await api.get('/usuarios/', { params: { rol: 'estilista' } })
    const data = res.data
    estilistas.value = Array.isArray(data) ? data : (data.results || [])
  } catch (err) {
    console.error(err)
  }
}

async function loadServicios() {
  try {
    const res = await api.get('/servicios/')
    const data = res.data
    servicios.value = Array.isArray(data) ? data : (data.results || [])
  } catch (err) {
    console.error(err)
  }
}

// ============================================================================
// MODAL: Crear / Editar
// ============================================================================
function openModal(cita = null) {
  formErrors.value = []
  if (cita) {
    isEditing.value = true
    editingId.value = cita.id
    form.value = {
      cliente_id: cita.cliente?.id || null,
      estilista_id: cita.estilista?.id || null,
      servicio_id: cita.servicio?.id || null,
      fecha: cita.fecha || '',
      hora_inicio: cita.hora_inicio ? cita.hora_inicio.slice(0, 5) : '',
      hora_fin: cita.hora_fin ? cita.hora_fin.slice(0, 5) : '',
      estado: cita.estado || 'pendiente',
      observaciones: cita.observaciones || '',
    }
  } else {
    isEditing.value = false
    editingId.value = null
    form.value = getEmptyForm()
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  formErrors.value = []
}

async function handleSubmit() {
  formErrors.value = []
  submitting.value = true

  try {
    const payload = {
      cliente_id: form.value.cliente_id,
      estilista_id: form.value.estilista_id,
      servicio_id: form.value.servicio_id,
      fecha: form.value.fecha,
      hora_inicio: form.value.hora_inicio,
      hora_fin: form.value.hora_fin,
      estado: form.value.estado,
      observaciones: form.value.observaciones,
    }

    if (isEditing.value) {
      await api.patch(`/citas/${editingId.value}/`, payload)
    } else {
      await api.post('/citas/', payload)
    }

    closeModal()
    await loadCitas()
  } catch (err) {
    if (err.response?.data) {
      const errors = err.response.data
      formErrors.value = Object.values(errors).flat()
    } else {
      formErrors.value = [t('admin.citas.errorSaving')]
    }
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// MODAL: Eliminar
// ============================================================================
function confirmDelete(cita) {
  deleteTarget.value = cita
  showDeleteModal.value = true
}

async function deleteCita() {
  if (!deleteTarget.value) return
  submitting.value = true
  try {
    await api.delete(`/citas/${deleteTarget.value.id}/`)
    showDeleteModal.value = false
    deleteTarget.value = null
    await loadCitas()
  } catch (err) {
    alert(t('admin.citas.deleteError'))
    console.error(err)
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// PAGINACION
// ============================================================================
function changePage(page) {
  currentPage.value = page
  loadCitas()
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => {
  loadCitas()
  loadClientes()
  loadEstilistas()
  loadServicios()
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

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* ===== BUTTONS ===== */
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
  transition: opacity 0.15s;
}
.btn-primary:hover { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

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

.btn-danger {
  padding: 0.5rem 1rem;
  background: #1a1212;
  color: #c47a7a;
  border: 1px solid #2a1a1a;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-danger:hover { background: #2a1a1a; }
.btn-danger:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-icon {
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  color: #888;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.btn-icon:hover { color: #e8e8e8; border-color: #444; }
.btn-icon.btn-danger:hover { color: #c47a7a; border-color: #3a2222; }

/* ===== FILTERS ===== */
.filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.input-search {
  flex: 1;
  min-width: 200px;
  padding: 0.5rem 0.75rem;
  background: #161616;
  border: 1px solid #252525;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 0.8rem;
  font-family: inherit;
  transition: border-color 0.15s;
}
.input-search::placeholder { color: #444; }
.input-search:focus { outline: none; border-color: #555; }

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

/* ===== TABLE ===== */
.empty-state {
  padding: 3rem 1rem;
  text-align: center;
  color: #555;
  font-size: 0.85rem;
}
.error-state { color: #b05a5a; }

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
  white-space: nowrap;
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
.obs-cell {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== BADGES ===== */
.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  white-space: nowrap;
}
.badge.pendiente { background: #1a1810; color: #b8a44a; }
.badge.confirmada { background: #122218; color: #5fa868; }
.badge.completada { background: #121820; color: #5a8fbf; }
.badge.cancelada { background: #1a1212; color: #b05a5a; }

/* ===== ACTIONS CELL ===== */
.actions-cell {
  display: flex;
  gap: 0.35rem;
}

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

/* ===== MODAL ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}
.modal {
  background: #141414;
  border: 1px solid #222;
  border-radius: 12px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-sm { max-width: 400px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #1a1a1a;
}
.modal-header h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0;
}
.btn-close {
  background: none;
  border: none;
  color: #666;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.15s;
}
.btn-close:hover { color: #e8e8e8; }

.modal-form {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.modal-body {
  padding: 1.25rem 1.5rem;
}
.modal-body p {
  font-size: 0.85rem;
  color: #bbb;
  margin: 0 0 0.5rem;
}
.muted { color: #555 !important; font-size: 0.8rem !important; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #1a1a1a;
}

/* ===== FORM ELEMENTS ===== */
.field {
  margin-bottom: 1rem;
}
.field label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: #888;
  margin-bottom: 0.3rem;
}
.field input[type="text"],
.field input[type="email"],
.field input[type="tel"],
.field input[type="password"],
.field input[type="date"],
.field input[type="time"],
.field select,
.field textarea {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background: #1a1a1a;
  border: 1px solid #252525;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 0.85rem;
  font-family: inherit;
  transition: border-color 0.15s;
  box-sizing: border-box;
}
.field input::placeholder,
.field textarea::placeholder { color: #444; }
.field input:focus,
.field select:focus,
.field textarea:focus { outline: none; border-color: #555; }
.field input:disabled { opacity: 0.4; cursor: not-allowed; }
.field textarea {
  resize: vertical;
  min-height: 60px;
}

.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.form-errors {
  padding: 0.6rem 0.75rem;
  background: #1a1212;
  border: 1px solid #2a1a1a;
  border-radius: 8px;
  margin-bottom: 0.75rem;
}
.form-errors p {
  margin: 0;
  padding: 0.15rem 0;
  color: #c47a7a;
  font-size: 0.8rem;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .page { padding: 1rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .filters { flex-direction: column; }
  .row-2 { grid-template-columns: 1fr; }
  .table { font-size: 0.75rem; }
  .table thead th,
  .table tbody td { padding: 0.5rem; }
  .obs-cell { max-width: 100px; }
  .modal { max-height: 95vh; }
}

@media (max-width: 480px) {
  .table { font-size: 0.7rem; }
  .obs-cell { display: none; }
}
</style>