<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('admin.peluquerias.title') }}</h1>
      <div class="header-actions">
        <button @click="openModal()" class="btn-primary">+ {{ $t('admin.peluquerias.new') }}</button>
      </div>
    </div>

    <!-- BUSQUEDA -->
    <div class="filters">
      <input
        v-model="search"
        type="text"
        :placeholder="$t('admin.peluquerias.search')"
        class="input-search"
        @input="debouncedLoad"
      />
    </div>

    <!-- LOADING / ERROR / EMPTY -->
    <div v-if="loading" class="empty-state">{{ $t('admin.peluquerias.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <div v-else-if="filteredPeluquerias.length === 0" class="empty-state">{{ $t('admin.peluquerias.noResults') }}</div>

    <!-- TABLA -->
    <div v-else class="table-wrapper">
      <table class="table">
        <thead>
          <tr>
            <th>{{ $t('admin.peluquerias.table.name') }}</th>
            <th>{{ $t('admin.peluquerias.table.address') }}</th>
            <th>{{ $t('admin.peluquerias.table.phone') }}</th>
            <th>{{ $t('admin.peluquerias.table.description') }}</th>
            <th>{{ $t('admin.peluquerias.table.registeredDate') }}</th>
            <th>{{ $t('admin.peluquerias.table.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in filteredPeluquerias" :key="p.id">
            <td class="strong">{{ p.nombre }}</td>
            <td>{{ p.direccion || '—' }}</td>
            <td class="mono">{{ p.telefono || '—' }}</td>
            <td class="desc-cell" :title="p.descripcion">{{ truncate(p.descripcion, 60) || '—' }}</td>
            <td class="mono">{{ formatDate(p.fecha_registro) }}</td>
            <td class="actions-cell">
              <button class="btn-icon" :title="$t('common.edit')" @click="openModal(p)">E</button>
              <button class="btn-icon btn-danger" :title="$t('common.delete')" @click="confirmDelete(p)">X</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL: Crear / Editar Peluqueria -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ isEditing ? $t('admin.peluquerias.edit') : $t('admin.peluquerias.create') }}</h2>
            <button class="btn-close" @click="closeModal">X</button>
          </div>

          <form @submit.prevent="handleSubmit" class="modal-form">
            <!-- Nombre -->
            <div class="field">
              <label for="f-nombre">{{ $t('admin.peluquerias.form.name') }} *</label>
              <input
                id="f-nombre"
                v-model="form.nombre"
                type="text"
                :placeholder="$t('admin.peluquerias.form.namePlaceholder')"
                required
              />
            </div>

            <!-- Direccion -->
            <div class="field">
              <label for="f-direccion">{{ $t('admin.peluquerias.form.address') }} *</label>
              <input
                id="f-direccion"
                v-model="form.direccion"
                type="text"
                :placeholder="$t('admin.peluquerias.form.addressPlaceholder')"
                required
              />
            </div>

            <!-- Telefono -->
            <div class="field">
              <label for="f-telefono">{{ $t('admin.peluquerias.form.phone') }} *</label>
              <input
                id="f-telefono"
                v-model="form.telefono"
                type="tel"
                :placeholder="$t('admin.peluquerias.form.phonePlaceholder')"
                required
              />
            </div>

            <!-- Descripcion -->
            <div class="field">
              <label for="f-descripcion">{{ $t('admin.peluquerias.form.description') }}</label>
              <textarea
                id="f-descripcion"
                v-model="form.descripcion"
                :placeholder="$t('admin.peluquerias.form.descriptionPlaceholder')"
                rows="3"
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
                {{ submitting ? $t('admin.peluquerias.saving') : (isEditing ? $t('admin.peluquerias.update') : $t('admin.peluquerias.create')) }}
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
            <h2>{{ $t('admin.peluquerias.deleteConfirm.title') }}</h2>
          </div>
          <div class="modal-body">
            <p>{{ $t('admin.peluquerias.deleteConfirm.message', { name: deleteTarget?.nombre }) }}</p>
            <p class="muted">{{ $t('admin.peluquerias.deleteConfirm.warning') }}</p>
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showDeleteModal = false">{{ $t('common.cancel') }}</button>
            <button class="btn-danger" @click="deletePeluqueria" :disabled="submitting">
              {{ submitting ? $t('admin.peluquerias.deleting') : $t('admin.peluquerias.delete') }}
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
const { formatDate } = useLocale()

// ============================================================================
// STATE
// ============================================================================
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
const filteredPeluquerias = computed(() => {
  let list = peluquerias.value
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(p =>
      (p.nombre || '').toLowerCase().includes(q)
    )
  }
  return list
})

// ============================================================================
// HELPERS
// ============================================================================
function getEmptyForm() {
  return {
    nombre: '',
    direccion: '',
    telefono: '',
    descripcion: '',
  }
}

function truncate(str, len) {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '...' : str
}

// Debounce para la busqueda
let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadPeluquerias(), 300)
}

// ============================================================================
// API CALLS
// ============================================================================
async function loadPeluquerias() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/peluquerias/')
    const data = response.data
    peluquerias.value = Array.isArray(data) ? data : (data.results || [])
  } catch (err) {
    error.value = t('admin.peluquerias.loadError')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// ============================================================================
// MODAL: Crear / Editar
// ============================================================================
function openModal(peluqueria = null) {
  formErrors.value = []
  if (peluqueria) {
    isEditing.value = true
    editingId.value = peluqueria.id
    form.value = {
      nombre: peluqueria.nombre || '',
      direccion: peluqueria.direccion || '',
      telefono: peluqueria.telefono || '',
      descripcion: peluqueria.descripcion || '',
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
      direccion: form.value.direccion,
      telefono: form.value.telefono,
      descripcion: form.value.descripcion,
    }

    if (isEditing.value) {
      await api.patch(`/peluquerias/${editingId.value}/`, payload)
    } else {
      await api.post('/peluquerias/', payload)
    }

    closeModal()
    await loadPeluquerias()
  } catch (err) {
    if (err.response?.data) {
      const errors = err.response.data
      formErrors.value = Object.values(errors).flat()
    } else {
      formErrors.value = [t('admin.peluquerias.saveError')]
    }
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// MODAL: Eliminar
// ============================================================================
function confirmDelete(peluqueria) {
  deleteTarget.value = peluqueria
  showDeleteModal.value = true
}

async function deletePeluqueria() {
  if (!deleteTarget.value) return
  submitting.value = true
  try {
    await api.delete(`/peluquerias/${deleteTarget.value.id}/`)
    showDeleteModal.value = false
    deleteTarget.value = null
    await loadPeluquerias()
  } catch (err) {
    alert(t('admin.peluquerias.deleteError'))
    console.error(err)
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => {
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

/* ===== FILTERS / SEARCH ===== */
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
.mono { font-variant-numeric: tabular-nums; white-space: nowrap; }
.desc-cell {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
.field input[type="tel"],
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
  resize: vertical;
}
.field input::placeholder,
.field textarea::placeholder { color: #444; }
.field input:focus,
.field textarea:focus { outline: none; border-color: #555; }

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
  .table { font-size: 0.75rem; }
  thead th, tbody td { padding: 0.5rem 0.5rem; }
  .desc-cell { max-width: 140px; }
  .modal { max-height: 95vh; }
}
</style>
