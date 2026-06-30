<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('admin.servicios.title') }}</h1>
      <div class="header-actions">
        <button @click="openModal()" class="btn-primary">{{ $t('admin.servicios.addNew') }}</button>
      </div>
    </div>

    <!-- FILTROS -->
    <div class="filters">
      <input
        v-model="search"
        type="text"
        :placeholder="$t('admin.servicios.searchPlaceholder')"
        class="input-search"
        @input="debouncedLoad"
      />
    </div>

    <!-- LOADING / ERROR / EMPTY -->
    <div v-if="loading" class="empty-state">{{ $t('admin.servicios.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <div v-else-if="filteredServicios.length === 0" class="empty-state">{{ $t('admin.servicios.noResults') }}</div>

    <!-- TABLA -->
    <table v-else class="table">
      <thead>
        <tr>
          <th>{{ $t('admin.servicios.thName') }}</th>
          <th>{{ $t('admin.servicios.thDescription') }}</th>
          <th>{{ $t('admin.servicios.thPrice') }}</th>
          <th>{{ $t('admin.servicios.thDuration') }}</th>
          <th>{{ $t('admin.servicios.thBranch') }}</th>
          <th>{{ $t('admin.servicios.thActions') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in filteredServicios" :key="s.id">
          <td class="strong">{{ s.nombre }}</td>
          <td class="desc-cell">{{ s.descripcion || '—' }}</td>
          <td class="mono price-cell">{{ formatPrice(s.precio) }}</td>
          <td class="mono">{{ s.duracion_minutos }} {{ $t('admin.servicios.minutesShort') }}</td>
          <td>
            <span v-if="s.hair_salon" class="salon-info">
              <span class="strong">{{ s.hair_salon.nombre }}</span>
              <span class="muted">{{ s.hair_salon.direccion }}</span>
            </span>
            <span v-else class="muted">—</span>
          </td>
          <td class="actions-cell">
            <button class="btn-icon" :title="$t('common.edit')" @click="openModal(s)">E</button>
            <button class="btn-icon btn-danger" :title="$t('common.delete')" @click="confirmDelete(s)">X</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- MODAL: Crear / Editar Servicio -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ isEditing ? $t('admin.servicios.editTitle') : $t('admin.servicios.newTitle') }}</h2>
            <button class="btn-close" @click="closeModal">X</button>
          </div>

          <form @submit.prevent="handleSubmit" class="modal-form">
            <!-- Nombre -->
            <div class="field">
              <label for="f-nombre">{{ $t('admin.servicios.fieldName') }}</label>
              <input
                id="f-nombre"
                v-model="form.nombre"
                type="text"
                :placeholder="$t('admin.servicios.namePlaceholder')"
                required
              />
            </div>

            <!-- Descripcion -->
            <div class="field">
              <label for="f-descripcion">{{ $t('admin.servicios.fieldDescription') }}</label>
              <textarea
                id="f-descripcion"
                v-model="form.descripcion"
                :placeholder="$t('admin.servicios.descriptionPlaceholder')"
                rows="3"
                class="input-textarea"
              ></textarea>
            </div>

            <!-- Precio / Duracion -->
            <div class="row-2">
              <div class="field">
                <label for="f-precio">{{ $t('admin.servicios.fieldPrice', { currency: currencySymbol }) }}</label>
                <input
                  id="f-precio"
                  v-model.number="form.precio"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="25.00"
                  required
                />
              </div>
              <div class="field">
                <label for="f-duracion">{{ $t('admin.servicios.fieldDuration') }}</label>
                <input
                  id="f-duracion"
                  v-model.number="form.duracion_minutos"
                  type="number"
                  min="1"
                  placeholder="30"
                  required
                />
              </div>
            </div>

            <!-- Peluqueria -->
            <div class="field">
              <label for="f-salon">{{ $t('admin.servicios.fieldBranch') }}</label>
              <select id="f-salon" v-model="form.hair_salon" required>
                <option :value="null" disabled>{{ $t('admin.servicios.selectBranch') }}</option>
                <option v-for="p in peluquerias" :key="p.id" :value="p.id">
                  {{ p.nombre }}
                </option>
              </select>
            </div>

            <!-- Errores del servidor -->
            <div v-if="formErrors.length > 0" class="form-errors">
              <p v-for="(e, i) in formErrors" :key="i">{{ e }}</p>
            </div>

            <!-- Botones -->
            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeModal">{{ $t('common.cancel') }}</button>
              <button type="submit" class="btn-primary" :disabled="submitting">
                {{ submitting ? $t('common.saving') : (isEditing ? $t('common.update') : $t('admin.servicios.createService')) }}
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
            <h2>{{ $t('common.confirmDelete') }}</h2>
          </div>
          <div class="modal-body">
            <p>{{ $t('admin.servicios.deleteConfirm') }} <strong>{{ deleteTarget?.nombre }}</strong>?</p>
            <p class="muted">{{ $t('admin.servicios.deleteWarning') }}</p>
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showDeleteModal = false">{{ $t('common.cancel') }}</button>
            <button class="btn-danger" @click="deleteServicio" :disabled="submitting">
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
const { currencySymbol, formatCurrency } = useLocale()

// ============================================================================
// STATE
// ============================================================================
const servicios = ref([])
const peluquerias = ref([])
const loading = ref(false)
const submitting = ref(false)
const error = ref(null)
const search = ref('')

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
const filteredServicios = computed(() => {
  let list = servicios.value
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(s => (s.nombre || '').toLowerCase().includes(q))
  }
  return list
})

// ============================================================================
// HELPERS
// ============================================================================
function getEmptyForm() {
  return {
    nombre: '',
    descripcion: '',
    precio: '',
    duracion_minutos: '',
    hair_salon: null,
  }
}

function formatPrice(precio) {
  const num = parseFloat(precio)
  if (isNaN(num)) return formatCurrency(0)
  return formatCurrency(num)
}

// Debounce para la busqueda
let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadServicios(), 300)
}

// ============================================================================
// API CALLS
// ============================================================================
async function loadServicios() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/servicios/')
    const data = response.data
    servicios.value = Array.isArray(data) ? data : (data.results || [])
  } catch (err) {
    error.value = t('admin.servicios.errorLoad')
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function loadPeluquerias() {
  try {
    const res = await api.get('/peluquerias/')
    peluquerias.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (err) {
    console.error(err)
  }
}

// ============================================================================
// MODAL: Crear / Editar
// ============================================================================
function openModal(servicio = null) {
  formErrors.value = []
  if (servicio) {
    isEditing.value = true
    editingId.value = servicio.id
    form.value = {
      nombre: servicio.nombre || '',
      descripcion: servicio.descripcion || '',
      precio: parseFloat(servicio.precio) || '',
      duracion_minutos: servicio.duracion_minutos || '',
      hair_salon: servicio.hair_salon?.id || null,
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
      nombre: form.value.nombre,
      descripcion: form.value.descripcion || '',
      precio: form.value.precio,
      duracion_minutos: form.value.duracion_minutos,
      hair_salon: form.value.hair_salon,
    }

    if (isEditing.value) {
      await api.patch(`/servicios/${editingId.value}/`, payload)
    } else {
      await api.post('/servicios/', payload)
    }

    closeModal()
    await loadServicios()
  } catch (err) {
    if (err.response?.data) {
      const errors = err.response.data
      formErrors.value = Object.values(errors).flat()
    } else {
      formErrors.value = [t('admin.servicios.errorSave')]
    }
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// MODAL: Eliminar
// ============================================================================
function confirmDelete(servicio) {
  deleteTarget.value = servicio
  showDeleteModal.value = true
}

async function deleteServicio() {
  if (!deleteTarget.value) return
  submitting.value = true
  try {
    await api.delete(`/servicios/${deleteTarget.value.id}/`)
    showDeleteModal.value = false
    deleteTarget.value = null
    await loadServicios()
  } catch (err) {
    alert(t('admin.servicios.errorDelete'))
    console.error(err)
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => {
  loadServicios()
  loadPeluquerias()
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
.muted { color: #555; font-size: 0.75rem; }

.desc-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price-cell {
  color: #a8c79a;
  font-weight: 500;
}

.salon-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
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
.field input[type="number"],
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

.input-textarea {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background: #1a1a1a;
  border: 1px solid #252525;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 0.85rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.15s;
}
.input-textarea::placeholder { color: #444; }
.input-textarea:focus { outline: none; border-color: #555; }

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
  .desc-cell { max-width: 120px; }
  .modal { max-height: 95vh; }
}

@media (max-width: 480px) {
  .salon-info .muted { display: none; }
}
</style>