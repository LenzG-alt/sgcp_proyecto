<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('admin.estilistas.title') }}</h1>
      <div class="header-actions">
        <button @click="openModal()" class="btn-primary">{{ $t('admin.estilistas.addNew') }}</button>
      </div>
    </div>

    <!-- BUSQUEDA -->
    <div class="filters">
      <input
        v-model="search"
        type="text"
        :placeholder="$t('admin.estilistas.searchPlaceholder')"
        class="input-search"
      />
    </div>

    <!-- LOADING / ERROR / EMPTY -->
    <div v-if="loading" class="empty-state">{{ $t('admin.estilistas.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <div v-else-if="filteredEstilistas.length === 0" class="empty-state">
      {{ search.trim() ? $t('admin.estilistas.noResultsSearch') : $t('admin.estilistas.noResults') }}
    </div>

    <!-- TABLA -->
    <table v-else class="table">
      <thead>
        <tr>
          <th>{{ $t('admin.estilistas.thFullName') }}</th>
          <th>{{ $t('admin.estilistas.thEmail') }}</th>
          <th>{{ $t('admin.estilistas.thPhone') }}</th>
          <th>{{ $t('admin.estilistas.thSpecialty') }}</th>
          <th>{{ $t('admin.estilistas.thBranch') }}</th>
          <th>{{ $t('admin.estilistas.thRole') }}</th>
          <th>{{ $t('admin.estilistas.thStatus') }}</th>
          <th>{{ $t('admin.estilistas.thActions') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="e in filteredEstilistas" :key="e.id">
          <td class="strong">{{ displayName(e) }}</td>
          <td class="mono">{{ e.email || '—' }}</td>
          <td class="mono">{{ e.telefono || '—' }}</td>
          <td>{{ e.especialidad || '—' }}</td>
          <td>{{ peluqueriaNombre(e) }}</td>
          <td><span class="badge estilista">{{ $t('common.roles.estilista') }}</span></td>
          <td>
            <button
              :class="['toggle-btn', e.is_active ? 'active' : 'inactive']"
              @click="toggleActive(e)"
              :title="e.is_active ? $t('common.states.deactivate') : $t('common.states.activate')"
            >
              {{ e.is_active ? $t('common.states.active') : $t('common.states.inactive') }}
            </button>
          </td>
          <td class="actions-cell">
            <button class="btn-icon" :title="$t('common.edit')" @click="openModal(e)">E</button>
            <button class="btn-icon btn-danger" :title="$t('common.delete')" @click="confirmDelete(e)">X</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- MODAL: Crear / Editar Estilista -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ isEditing ? $t('admin.estilistas.editTitle') : $t('admin.estilistas.newTitle') }}</h2>
            <button class="btn-close" @click="closeModal">X</button>
          </div>

          <form @submit.prevent="handleSubmit" class="modal-form">
            <!-- Username -->
            <div class="field">
              <label for="f-username">{{ $t('admin.estilistas.fieldUsername') }}</label>
              <input
                id="f-username"
                v-model="form.username"
                type="text"
                placeholder="nombre_usuario"
                required
                :disabled="isEditing"
                autocomplete="username"
              />
              <span v-if="isEditing" class="field-hint">{{ $t('admin.estilistas.usernameReadonly') }}</span>
            </div>

            <!-- Nombre / Apellido -->
            <div class="row-2">
              <div class="field">
                <label for="f-first_name">{{ $t('admin.estilistas.fieldFirstName') }}</label>
                <input id="f-first_name" v-model="form.first_name" type="text" placeholder="Maria" required />
              </div>
              <div class="field">
                <label for="f-last_name">{{ $t('admin.estilistas.fieldLastName') }}</label>
                <input id="f-last_name" v-model="form.last_name" type="text" placeholder="Lopez" required />
              </div>
            </div>

            <!-- Email -->
            <div class="field">
              <label for="f-email">{{ $t('admin.estilistas.fieldEmail') }}</label>
              <input id="f-email" v-model="form.email" type="email" placeholder="correo@ejemplo.com" required />
            </div>

            <!-- Telefono -->
            <div class="field">
              <label for="f-telefono">{{ $t('admin.estilistas.fieldPhone') }}</label>
              <input id="f-telefono" v-model="form.telefono" type="tel" placeholder="+51 999 888 777" />
            </div>

            <!-- Contrasena -->
            <div class="field">
              <label for="f-password">
                {{ isEditing ? $t('admin.estilistas.newPasswordLabel') : $t('admin.estilistas.passwordLabel') }}
              </label>
              <input
                id="f-password"
                v-model="form.password"
                type="password"
                :placeholder="isEditing ? $t('admin.estilistas.newPasswordPlaceholder') : $t('admin.estilistas.passwordPlaceholder')"
                :required="!isEditing"
                :minlength="isEditing ? 0 : 6"
                autocomplete="new-password"
              />
            </div>

            <!-- Peluqueria -->
            <div class="field">
              <label for="f-peluqueria">{{ $t('admin.estilistas.fieldBranch') }}</label>
              <select id="f-peluqueria" v-model="form.peluqueria" required>
                <option :value="null" disabled>{{ $t('admin.estilistas.selectBranch') }}</option>
                <option v-for="p in peluquerias" :key="p.id" :value="p.id">
                  {{ p.nombre }}
                </option>
              </select>
            </div>

            <!-- Especialidad -->
            <div class="field">
              <label for="f-especialidad">{{ $t('admin.estilistas.fieldSpecialty') }}</label>
              <input
                id="f-especialidad"
                v-model="form.especialidad"
                type="text"
                :placeholder="$t('admin.estilistas.specialtyPlaceholder')"
              />
            </div>

            <!-- Estado -->
            <div class="field field-inline">
              <label>
                <input type="checkbox" v-model="form.is_active" />
                {{ $t('admin.estilistas.activeAccount') }}
              </label>
            </div>

            <!-- Errores del servidor -->
            <div v-if="formErrors.length > 0" class="form-errors">
              <p v-for="(err, i) in formErrors" :key="i">{{ err }}</p>
            </div>

            <!-- Botones -->
            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeModal">{{ $t('common.cancel') }}</button>
              <button type="submit" class="btn-primary" :disabled="submitting">
                {{ submitting ? $t('common.saving') : (isEditing ? $t('common.update') : $t('admin.estilistas.createStylist')) }}
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
            <p>{{ $t('admin.estilistas.deleteConfirm') }} <strong>{{ deleteTarget ? displayName(deleteTarget) : '' }}</strong>?</p>
            <p class="muted">{{ $t('admin.estilistas.deleteWarning') }}</p>
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showDeleteModal = false">{{ $t('common.cancel') }}</button>
            <button class="btn-danger" @click="deleteEstilista" :disabled="submitting">
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
import api from '@/services/api'

const { t } = useI18n()

// ============================================================================
// STATE
// ============================================================================
const estilistas = ref([])
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
const filteredEstilistas = computed(() => {
  let list = estilistas.value
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(e => {
      const nombre = [e.first_name, e.last_name].filter(Boolean).join(' ').toLowerCase()
      return nombre.includes(q) || (e.username || '').toLowerCase().includes(q)
    })
  }
  return list
})

// ============================================================================
// HELPERS
// ============================================================================
function getEmptyForm() {
  return {
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    telefono: '',
    password: '',
    rol: 'estilista',
    is_active: true,
    peluqueria: null,
    especialidad: '',
  }
}

function displayName(e) {
  return [e.first_name, e.last_name].filter(Boolean).join(' ') || e.username || '—'
}

function peluqueriaNombre(e) {
  if (e.peluqueria_data && e.peluqueria_data.nombre) return e.peluqueria_data.nombre
  return '—'
}

// ============================================================================
// API CALLS
// ============================================================================
async function loadEstilistas() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/usuarios/', { params: { rol: 'estilista' } })
    const data = response.data
    estilistas.value = Array.isArray(data) ? data : (data.results || [])
  } catch (err) {
    error.value = t('admin.estilistas.errorLoad')
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

async function toggleActive(estilista) {
  const newStatus = !estilista.is_active
  try {
    await api.patch(`/usuarios/${estilista.id}/`, { is_active: newStatus })
    estilista.is_active = newStatus
  } catch (err) {
    alert(t('admin.estilistas.errorToggleStatus'))
    console.error(err)
  }
}

// ============================================================================
// MODAL: Crear / Editar
// ============================================================================
function openModal(estilista = null) {
  formErrors.value = []
  if (estilista) {
    isEditing.value = true
    editingId.value = estilista.id
    form.value = {
      username: estilista.username,
      first_name: estilista.first_name || '',
      last_name: estilista.last_name || '',
      email: estilista.email || '',
      telefono: estilista.telefono || '',
      password: '',
      rol: 'estilista',
      is_active: estilista.is_active,
      peluqueria: estilista.peluqueria || null,
      especialidad: estilista.especialidad || '',
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
      username: form.value.username,
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      email: form.value.email,
      telefono: form.value.telefono,
      rol: 'estilista',
      is_active: form.value.is_active,
      peluqueria: form.value.peluqueria,
      especialidad: form.value.especialidad,
    }

    // On create, password is required
    if (!isEditing.value) {
      payload.password = form.value.password
    } else if (form.value.password) {
      // On edit, only send password if provided
      payload.password = form.value.password
    }

    if (isEditing.value) {
      await api.patch(`/usuarios/${editingId.value}/`, payload)
    } else {
      await api.post('/usuarios/', payload)
    }

    closeModal()
    await loadEstilistas()
  } catch (err) {
    if (err.response?.data) {
      const errors = err.response.data
      formErrors.value = Object.values(errors).flat()
    } else {
      formErrors.value = [t('admin.estilistas.errorSave')]
    }
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// MODAL: Eliminar
// ============================================================================
function confirmDelete(estilista) {
  deleteTarget.value = estilista
  showDeleteModal.value = true
}

async function deleteEstilista() {
  if (!deleteTarget.value) return
  submitting.value = true
  try {
    await api.delete(`/usuarios/${deleteTarget.value.id}/`)
    showDeleteModal.value = false
    deleteTarget.value = null
    await loadEstilistas()
  } catch (err) {
    alert(t('admin.estilistas.errorDelete'))
    console.error(err)
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => {
  loadEstilistas()
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

/* ===== BADGES ===== */
.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
}
.badge.estilista { background: #1a1812; color: #b8a44a; }

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
  color: #5fa868;
  border-color: #1a3020;
}
.toggle-btn.inactive {
  background: #1a1212;
  color: #b05a5a;
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

.field-hint {
  display: block;
  font-size: 0.7rem;
  color: #444;
  margin-top: 0.2rem;
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
  .row-2 { grid-template-columns: 1fr; }
  .table { font-size: 0.75rem; }
  .modal { max-height: 95vh; }
}
</style>