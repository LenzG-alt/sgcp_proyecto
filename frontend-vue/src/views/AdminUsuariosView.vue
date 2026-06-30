<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('admin.usuarios.title') }}</h1>
      <div class="header-actions">
        <button @click="openModal()" class="btn-primary">{{ $t('admin.usuarios.addNew') }}</button>
      </div>
    </div>

    <!-- FILTROS -->
    <div class="filters">
      <input
        v-model="search"
        type="text"
        :placeholder="$t('admin.usuarios.searchPlaceholder')"
        class="input-search"
        @input="debouncedLoad"
      />
      <select v-model="filterRol" class="select-filter" @change="loadUsuarios">
        <option value="">{{ $t('admin.usuarios.allRoles') }}</option>
        <option value="cliente">{{ $t('admin.usuarios.roleClientes') }}</option>
        <option value="estilista">{{ $t('admin.usuarios.roleEstilistas') }}</option>
        <option value="recepcionista">{{ $t('admin.usuarios.roleRecepcionistas') }}</option>
        <option value="administrador">{{ $t('admin.usuarios.roleAdministradores') }}</option>
      </select>
      <select v-model="filterEstado" class="select-filter" @change="loadUsuarios">
        <option value="">{{ $t('admin.usuarios.allStates') }}</option>
        <option value="activo">{{ $t('admin.usuarios.activeFilter') }}</option>
        <option value="inactivo">{{ $t('admin.usuarios.inactiveFilter') }}</option>
      </select>
    </div>

    <!-- LOADING / ERROR / EMPTY -->
    <div v-if="loading" class="empty-state">{{ $t('admin.usuarios.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <div v-else-if="filteredUsuarios.length === 0" class="empty-state">{{ $t('admin.usuarios.noResults') }}</div>

    <!-- TABLA -->
    <table v-else class="table">
      <thead>
        <tr>
          <th>{{ $t('admin.usuarios.thUsername') }}</th>
          <th>{{ $t('admin.usuarios.thFullName') }}</th>
          <th>{{ $t('admin.usuarios.thEmail') }}</th>
          <th>{{ $t('admin.usuarios.thPhone') }}</th>
          <th>{{ $t('admin.usuarios.thRole') }}</th>
          <th>{{ $t('admin.usuarios.thStatus') }}</th>
          <th>{{ $t('admin.usuarios.thActions') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in filteredUsuarios" :key="u.id">
          <td class="mono">{{ u.username }}</td>
          <td class="strong">{{ displayName(u) }}</td>
          <td class="mono">{{ u.email }}</td>
          <td class="mono">{{ u.telefono || '—' }}</td>
          <td><span :class="['badge', u.rol]">{{ formatRol(u.rol) }}</span></td>
          <td>
            <button
              :class="['toggle-btn', u.is_active ? 'active' : 'inactive']"
              @click="toggleActive(u)"
              :title="u.is_active ? $t('admin.usuarios.deactivate') : $t('admin.usuarios.activate')"
            >
              {{ u.is_active ? $t('admin.usuarios.active') : $t('admin.usuarios.inactive') }}
            </button>
          </td>
          <td class="actions-cell">
            <button class="btn-icon" :title="$t('common.edit')" @click="openModal(u)">E</button>
            <button class="btn-icon btn-danger" :title="$t('common.delete')" @click="confirmDelete(u)">X</button>
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

    <!-- MODAL: Crear / Editar Usuario -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ isEditing ? $t('admin.usuarios.editTitle') : $t('admin.usuarios.newTitle') }}</h2>
            <button class="btn-close" @click="closeModal">X</button>
          </div>

          <form @submit.prevent="handleSubmit" class="modal-form">
            <!-- Username -->
            <div class="field">
              <label for="f-username">{{ $t('admin.usuarios.fieldUsername') }}</label>
              <input
                id="f-username"
                v-model="form.username"
                type="text"
                placeholder="nombre_usuario"
                required
                :disabled="isEditing"
                autocomplete="username"
              />
              <span v-if="isEditing" class="field-hint">{{ $t('admin.usuarios.usernameReadonly') }}</span>
            </div>

            <!-- Nombre / Apellido -->
            <div class="row-2">
              <div class="field">
                <label for="f-first_name">{{ $t('admin.usuarios.fieldFirstName') }}</label>
                <input id="f-first_name" v-model="form.first_name" type="text" placeholder="Juan" required />
              </div>
              <div class="field">
                <label for="f-last_name">{{ $t('admin.usuarios.fieldLastName') }}</label>
                <input id="f-last_name" v-model="form.last_name" type="text" placeholder="Garcia" required />
              </div>
            </div>

            <!-- Email -->
            <div class="field">
              <label for="f-email">{{ $t('admin.usuarios.fieldEmail') }}</label>
              <input id="f-email" v-model="form.email" type="email" placeholder="correo@ejemplo.com" required />
            </div>

            <!-- Telefono -->
            <div class="field">
              <label for="f-telefono">{{ $t('admin.usuarios.fieldPhone') }}</label>
              <input id="f-telefono" v-model="form.telefono" type="tel" placeholder="+51 999 888 777" />
            </div>

            <!-- Contrasena (solo al crear, o para resetear) -->
            <div class="field">
              <label for="f-password">
                {{ isEditing ? $t('admin.usuarios.newPasswordLabel') : $t('admin.usuarios.passwordLabel') }}
              </label>
              <input
                id="f-password"
                v-model="form.password"
                type="password"
                :placeholder="isEditing ? $t('admin.usuarios.newPasswordPlaceholder') : $t('admin.usuarios.passwordPlaceholder')"
                :required="!isEditing"
                :minlength="isEditing ? 0 : 6"
                autocomplete="new-password"
              />
            </div>

            <!-- Rol -->
            <div class="field">
              <label for="f-rol">{{ $t('admin.usuarios.fieldRole') }}</label>
              <select id="f-rol" v-model="form.rol" required>
                <option value="cliente">{{ $t('common.roles.cliente') }}</option>
                <option value="estilista">{{ $t('common.roles.estilista') }}</option>
                <option value="recepcionista">{{ $t('common.roles.recepcionista') }}</option>
                <option value="administrador">{{ $t('common.roles.administrador') }}</option>
              </select>
            </div>

            <!-- Estado -->
            <div class="field field-inline">
              <label>
                <input type="checkbox" v-model="form.is_active" />
                {{ $t('admin.usuarios.activeAccount') }}
              </label>
            </div>

            <!-- Campos especificos de ESTILISTA -->
            <template v-if="form.rol === 'estilista'">
              <div class="field">
                <label for="f-peluqueria">{{ $t('admin.usuarios.fieldBranch') }}</label>
                <select id="f-peluqueria" v-model="form.peluqueria" required>
                  <option :value="null" disabled>{{ $t('admin.usuarios.selectBranch') }}</option>
                  <option v-for="p in peluquerias" :key="p.id" :value="p.id">
                    {{ p.nombre }}
                  </option>
                </select>
              </div>
              <div class="field">
                <label for="f-especialidad">{{ $t('admin.usuarios.fieldSpecialty') }}</label>
                <input id="f-especialidad" v-model="form.especialidad" type="text" :placeholder="$t('admin.usuarios.specialtyPlaceholder')" />
              </div>
            </template>

            <!-- Errores del servidor -->
            <div v-if="formErrors.length > 0" class="form-errors">
              <p v-for="(e, i) in formErrors" :key="i">{{ e }}</p>
            </div>

            <!-- Botones -->
            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeModal">{{ $t('common.cancel') }}</button>
              <button type="submit" class="btn-primary" :disabled="submitting">
                {{ submitting ? $t('common.saving') : (isEditing ? $t('common.update') : $t('admin.usuarios.createUser')) }}
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
            <p>{{ $t('admin.usuarios.deleteConfirm') }} <strong>{{ deleteTarget?.username }}</strong>?</p>
            <p class="muted">{{ $t('admin.usuarios.deleteWarning') }}</p>
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showDeleteModal = false">{{ $t('common.cancel') }}</button>
            <button class="btn-danger" @click="deleteUsuario" :disabled="submitting">
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
const usuarios = ref([])
const peluquerias = ref([])
const loading = ref(false)
const submitting = ref(false)
const error = ref(null)
const search = ref('')
const filterRol = ref('')
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
const filteredUsuarios = computed(() => {
  let list = usuarios.value
  if (filterEstado.value === 'activo') list = list.filter(u => u.is_active)
  if (filterEstado.value === 'inactivo') list = list.filter(u => !u.is_active)
  if (filterRol.value) list = list.filter(u => u.rol === filterRol.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(u =>
      (u.username || '').toLowerCase().includes(q) ||
      (u.email || '').toLowerCase().includes(q) ||
      (u.first_name || '').toLowerCase().includes(q) ||
      (u.last_name || '').toLowerCase().includes(q)
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
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    telefono: '',
    password: '',
    rol: 'cliente',
    is_active: true,
    peluqueria: null,
    especialidad: '',
  }
}

function displayName(u) {
  return [u.first_name, u.last_name].filter(Boolean).join(' ') || u.username || '—'
}

function formatRol(rol) {
  const map = {
    cliente: t('common.roles.cliente'),
    estilista: t('common.roles.estilista'),
    administrador: t('common.roles.administrador'),
    recepcionista: t('common.roles.recepcionista'),
  }
  return map[rol] || rol
}

// Debounce para la busqueda
let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { currentPage.value = 1; loadUsuarios() }, 300)
}

// ============================================================================
// API CALLS
// ============================================================================
async function loadUsuarios() {
  loading.value = true
  error.value = null
  try {
    const params = { page: currentPage.value }
    if (filterRol.value) params.rol = filterRol.value
    const response = await api.get('/usuarios/', { params })
    const data = response.data
    usuarios.value = Array.isArray(data) ? data : (data.results || [])
    totalCount.value = data.count || usuarios.value.length
  } catch (err) {
    error.value = t('admin.usuarios.errorLoad')
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

async function toggleActive(user) {
  const newStatus = !user.is_active
  try {
    await api.patch(`/usuarios/${user.id}/`, { is_active: newStatus })
    user.is_active = newStatus
  } catch (err) {
    alert(t('admin.usuarios.errorToggleStatus'))
    console.error(err)
  }
}

// ============================================================================
// MODAL: Crear / Editar
// ============================================================================
function openModal(user = null) {
  formErrors.value = []
  if (user) {
    isEditing.value = true
    editingId.value = user.id
    form.value = {
      username: user.username,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      email: user.email || '',
      telefono: user.telefono || '',
      password: '',
      rol: user.rol,
      is_active: user.is_active,
      peluqueria: user.peluqueria || null,
      especialidad: user.especialidad || '',
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
    const payload = { ...form.value }

    // Limpiar campos que no aplican segun el rol
    if (payload.rol !== 'estilista') {
      delete payload.peluqueria
      delete payload.especialidad
    }

    // Si editando y contrasena vacia, eliminarla del payload
    if (isEditing.value && !payload.password) {
      delete payload.password
    }

    if (isEditing.value) {
      await api.patch(`/usuarios/${editingId.value}/`, payload)
    } else {
      await api.post('/usuarios/', payload)
    }

    closeModal()
    await loadUsuarios()
  } catch (err) {
    if (err.response?.data) {
      const errors = err.response.data
      formErrors.value = Object.values(errors).flat()
    } else {
      formErrors.value = [t('admin.usuarios.errorSave')]
    }
  } finally {
    submitting.value = false
  }
}

// ============================================================================
// MODAL: Eliminar
// ============================================================================
function confirmDelete(user) {
  deleteTarget.value = user
  showDeleteModal.value = true
}

async function deleteUsuario() {
  if (!deleteTarget.value) return
  submitting.value = true
  try {
    await api.delete(`/usuarios/${deleteTarget.value.id}/`)
    showDeleteModal.value = false
    deleteTarget.value = null
    await loadUsuarios()
  } catch (err) {
    alert(t('admin.usuarios.errorDelete'))
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
  loadUsuarios()
}

// ============================================================================
// INIT
// ============================================================================
onMounted(() => {
  loadUsuarios()
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
.badge.cliente { background: #121820; color: #5a8fbf; }
.badge.estilista { background: #1a1812; color: #b8a44a; }
.badge.administrador { background: #1a1212; color: #b05a5a; }
.badge.recepcionista { background: #122218; color: #5fa868; }

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