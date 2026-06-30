<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('admin.horarios.title') }}</h1>
      <div class="header-actions">
        <button @click="openModal()" class="btn-primary">{{ $t('admin.horarios.addNew') }}</button>
      </div>
    </div>

    <!-- FILTROS -->
    <div class="filters">
      <select v-model="filterEstilista" class="select-filter" @change="loadHorarios">
        <option value="">{{ $t('admin.horarios.filterAllStylists') }}</option>
        <option v-for="e in estilistas" :key="e.id" :value="e.id">
          {{ e.nombre_completo || [e.first_name, e.last_name].filter(Boolean).join(' ') || e.username }}
        </option>
      </select>
      <select v-model="filterDia" class="select-filter" @change="loadHorarios">
        <option value="">{{ $t('admin.horarios.filterAllDays') }}</option>
        <option v-for="d in diasSemana" :key="d.value" :value="d.value">
          {{ d.label }}
        </option>
      </select>
    </div>

    <!-- LOADING / ERROR / EMPTY -->
    <div v-if="loading" class="empty-state">{{ $t('admin.horarios.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <div v-else-if="filteredHorarios.length === 0" class="empty-state">{{ $t('admin.horarios.noResults') }}</div>

    <!-- TABLA -->
    <div v-else class="table-wrapper">
      <table class="table">
        <thead>
          <tr>
            <th>{{ $t('admin.horarios.table.stylist') }}</th>
            <th>{{ $t('admin.horarios.table.day') }}</th>
            <th>{{ $t('admin.horarios.table.startTime') }}</th>
            <th>{{ $t('admin.horarios.table.endTime') }}</th>
            <th>{{ $t('admin.horarios.table.status') }}</th>
            <th>{{ $t('admin.horarios.table.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="h in filteredHorarios" :key="h.id">
            <td class="strong">{{ h.estilista?.nombre_completo || '—' }}</td>
            <td><span class="badge-dia">{{ formatDia(h.dia_semana) }}</span></td>
            <td class="mono">{{ formatTime(h.hora_inicio) || '—' }}</td>
            <td class="mono">{{ formatTime(h.hora_fin) || '—' }}</td>
            <td>
              <button
                :class="['toggle-btn', h.activo ? 'active' : 'inactive']"
                @click="toggleActivo(h)"
                :title="h.activo ? $t('common.deactivate') : $t('common.activate')"
              >
                {{ h.activo ? $t('common.active') : $t('common.inactive') }}
              </button>
            </td>
            <td class="actions-cell">
              <button class="btn-icon" :title="$t('common.edit')" @click="openModal(h)">E</button>
              <button class="btn-icon btn-danger" :title="$t('common.delete')" @click="confirmDelete(h)">X</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL: Crear / Editar Horario -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ isEditing ? $t('admin.horarios.editTitle') : $t('admin.horarios.newTitle') }}</h2>
            <button class="btn-close" @click="closeModal">X</button>
          </div>

          <form @submit.prevent="handleSubmit" class="modal-form">
            <!-- Estilista -->
            <div class="field">
              <label for="f-estilista">{{ $t('admin.horarios.table.stylist') }} *</label>
              <select id="f-estilista" v-model="form.estilista_id" required>
                <option :value="null" disabled>{{ $t('admin.horarios.selectStylist') }}</option>
                <option v-for="e in estilistas" :key="e.id" :value="e.id">
                  {{ e.nombre_completo || [e.first_name, e.last_name].filter(Boolean).join(' ') || e.username }}
                </option>
              </select>
            </div>

            <!-- Dia de la semana -->
            <div class="field">
              <label for="f-dia">{{ $t('admin.horarios.fieldDay') }}</label>
              <select id="f-dia" v-model="form.dia_semana" required>
                <option :value="''" disabled>{{ $t('admin.horarios.selectDay') }}</option>
                <option v-for="d in diasSemana" :key="d.value" :value="d.value">
                  {{ d.label }}
                </option>
              </select>
            </div>

            <!-- Hora inicio / Hora fin -->
            <div class="row-2">
              <div class="field">
                <label for="f-inicio">{{ $t('admin.horarios.table.startTime') }} *</label>
                <input
                  id="f-inicio"
                  v-model="form.hora_inicio"
                  type="time"
                  required
                />
              </div>
              <div class="field">
                <label for="f-fin">{{ $t('admin.horarios.table.endTime') }} *</label>
                <input
                  id="f-fin"
                  v-model="form.hora_fin"
                  type="time"
                  required
                />
              </div>
            </div>

            <!-- Activo -->
            <div class="field field-inline">
              <label>
                <input type="checkbox" v-model="form.activo" />
                {{ $t('admin.horarios.activeSchedule') }}
              </label>
            </div>

            <!-- Errores del servidor -->
            <div v-if="formErrors.length > 0" class="form-errors">
              <p v-for="(e, i) in formErrors" :key="i">{{ e }}</p>
            </div>

            <!-- Botones -->
            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeModal">{{ $t('common.cancel') }}</button>
              <button type="submit" class="btn-primary" :disabled="submitting">
                {{ submitting ? $t('common.saving') : (isEditing ? $t('common.updating') : $t('admin.horarios.create')) }}
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
            <h2>{{ $t('admin.horarios.deleteConfirmTitle') }}</h2>
          </div>
          <div class="modal-body">
            <p v-html="$t('admin.horarios.deleteConfirmMsg', { name: deleteTarget?.estilista?.nombre_completo || '', day: formatDia(deleteTarget?.dia_semana) })"></p>
            <p class="muted">{{ $t('admin.horarios.deleteWarning') }}</p>
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showDeleteModal = false">{{ $t('common.cancel') }}</button>
            <button class="btn-danger" @click="deleteHorario" :disabled="submitting">
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
const { formatTime } = useLocale()

// ============================================================================
// CONSTANTS
// ============================================================================
const diasSemana = computed(() => [
  { value: 'lunes', label: t('common.days.monday') },
  { value: 'martes', label: t('common.days.tuesday') },
  { value: 'miercoles', label: t('common.days.wednesday') },
  { value: 'jueves', label: t('common.days.thursday') },
  { value: 'viernes', label: t('common.days.friday') },
  { value: 'sabado', label: t('common.days.saturday') },
  { value: 'domingo', label: t('common.days.sunday') },
])

// ============================================================================
// STATE
// ============================================================================
const horarios = ref([])
const estilistas = ref([])
const loading = ref(false)
const submitting = ref(false)
const error = ref(null)
const filterEstilista = ref('')
const filterDia = ref('')

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
const filteredHorarios = computed(() => {
  let list = horarios.value
  if (filterEstilista.value) {
    list = list.filter(h => h.estilista && h.estilista.id === filterEstilista.value)
  }
  if (filterDia.value) {
    list = list.filter(h => h.dia_semana === filterDia.value)
  }
  return list
})

// ============================================================================
// HELPERS
// ============================================================================
function getEmptyForm() {
  return {
    estilista_id: null,
    dia_semana: '',
    hora_inicio: '',
    hora_fin: '',
    activo: true,
  }
}

function formatDia(dia) {
  const found = diasSemana.value.find(d => d.value === dia)
  return found ? found.label : dia || '—'
}

// ============================================================================
// API CALLS
// ============================================================================
async function loadHorarios() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/horarios/')
    const data = response.data
    horarios.value = Array.isArray(data) ? data : (data.results || [])
  } catch (err) {
    error.value = t('admin.horarios.errorLoading')
    console.error(err)
  } finally {
    loading.value = false
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

async function toggleActivo(horario) {
  const newStatus = !horario.activo
  try {
    await api.patch(`/horarios/${horario.id}/`, { activo: newStatus })
    horario.activo = newStatus
  } catch (err) {
    alert(t('admin.horarios.errorToggleStatus'))
    console.error(err)
  }
}

// ============================================================================
// MODAL: Crear / Editar
// ============================================================================
function openModal(horario = null) {
  formErrors.value = []
  if (horario) {
    isEditing.value = true
    editingId.value = horario.id
    form.value = {
      estilista_id: horario.estilista?.id || null,
      dia_semana: horario.dia_semana || '',
      hora_inicio: formatTime(horario.hora_inicio),
      hora_fin: formatTime(horario.hora_fin),
      activo: horario.activo,
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
    // Build payload — ensure time format includes seconds for the API
    const payload = {
      estilista_id: form.value.estilista_id,
      dia_semana: form.value.dia_semana,
      hora_inicio: form.value.hora_inicio ? form.value.hora_inicio + ':00' : '',
      hora_fin: form.value.hora_fin ? form.value.hora_fin + ':00' : '',
      activo: form.value.activo,
    }

    if (isEditing.value) {
      await api.patch(`/horarios/${editingId.value}/`, payload)
    } else {
      await api.post('/horarios/', payload)
    }

    closeModal()
    await loadHorarios()
  } catch (err) {
    if (err.response?.data) {
      const errors = err.response.data
      formErrors.value = Object.values(errors).flat()
    } else {
      formErrors.value = [t('admin.horarios.errorSaving')]
    }
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// MODAL: Eliminar
// ============================================================================
function confirmDelete(horario) {
  deleteTarget.value = horario
  showDeleteModal.value = true
}

async function deleteHorario() {
  if (!deleteTarget.value) return
  submitting.value = true
  try {
    await api.delete(`/horarios/${deleteTarget.value.id}/`)
    showDeleteModal.value = false
    deleteTarget.value = null
    await loadHorarios()
  } catch (err) {
    alert(t('admin.horarios.deleteError'))
    console.error(err)
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => {
  loadHorarios()
  loadEstilistas()
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

.select-filter {
  padding: 0.5rem 0.75rem;
  background: #161616;
  border: 1px solid #252525;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 0.8rem;
  font-family: inherit;
  cursor: pointer;
  min-width: 180px;
}
.select-filter:focus { outline: none; border-color: #555; }

/* ===== TABLE ===== */
.table-wrapper {
  overflow-x: auto;
}

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

/* ===== DAY BADGE ===== */
.badge-dia {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  background: #121820;
  color: #5a8fbf;
  text-transform: capitalize;
}

/* ===== TOGGLE BUTTON ===== */
.toggle-btn {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  border: 1px solid transparent;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
}
.toggle-btn.active {
  background: #122218;
  color: #4ade80;
  border-color: #1a3020;
}
.toggle-btn.inactive {
  background: #1a1212;
  color: #f87171;
  border-color: #2a1a1a;
}

/* ===== ACTIONS CELL ===== */
.actions-cell {
  display: flex;
  gap: 0.35rem;
}

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
.field input[type="time"],
.field select {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background: #1a1a1a;
  border: 1px solid #252525;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 0.85rem;
  font-family: inherit;
  transition: border-color 0.15s;
}
.field input::placeholder { color: #444; }
.field input:focus, .field select:focus { outline: none; border-color: #555; }
.field input:disabled { opacity: 0.4; cursor: not-allowed; }

/* Ensure time picker is styled consistently in dark mode */
.field input[type="time"]::-webkit-calendar-picker-indicator {
  filter: invert(0.7);
  cursor: pointer;
}

.field-inline label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.8rem;
  color: #bbb;
}
.field-inline input[type="checkbox"] {
  accent-color: #a78bfa;
  width: 16px;
  height: 16px;
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
  .select-filter { min-width: 100%; }
  .row-2 { grid-template-columns: 1fr; }
  .table { font-size: 0.75rem; }
  .modal { max-height: 95vh; }
}
</style>