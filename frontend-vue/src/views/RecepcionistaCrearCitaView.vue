<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('recepcionista.crearCita.title') }}</h1>
    </div>

    <div v-if="loadingData" class="empty-state">{{ $t('recepcionista.crearCita.loadingData') }}</div>
    <template v-else>
      <form @submit.prevent="crearCita" class="form">
        <!-- CLIENTE -->
        <div class="field">
          <label>{{ $t('recepcionista.crearCita.cliente') }}</label>
          <input v-model="busquedaCliente" :placeholder="$t('recepcionista.crearCita.searchCliente')" @input="searchClientes" list="clientes-list" required />
          <datalist id="clientes-list">
            <option v-for="c in clientesFiltrados" :key="c.id" :value="c.nombre_completo + ' (' + c.email + ')'" />
          </datalist>
          <span v-if="selectedCliente" class="field-hint">{{ $t('recepcionista.crearCita.selected') }}: {{ selectedCliente.nombre_completo }}</span>
        </div>

        <!-- PELUQUERIA -->
        <div class="field">
          <label>{{ $t('recepcionista.crearCita.peluqueria') }}</label>
          <select v-model="form.peluqueria_id" @change="onPeluqueriaChange" required>
            <option value="">{{ $t('recepcionista.crearCita.seleccionar') }}</option>
            <option v-for="p in peluquerias" :key="p.id" :value="p.id">{{ p.nombre }}</option>
          </select>
        </div>

        <!-- SERVICIO -->
        <div class="field">
          <label>{{ $t('recepcionista.crearCita.servicio') }}</label>
          <select v-model="form.servicio_id" @change="onServicioChange" :disabled="!form.peluqueria_id" required>
            <option value="">{{ $t('recepcionista.crearCita.seleccionar') }}</option>
            <option v-for="s in serviciosFiltrados" :key="s.id" :value="s.id">{{ s.nombre }} - {{ formatCurrency(s.precio) }} ({{ s.duracion_minutos }}{{ $t('recepcionista.crearCita.min') }})</option>
          </select>
        </div>

        <!-- ESTILISTA -->
        <div class="field">
          <label>{{ $t('recepcionista.crearCita.estilista') }}</label>
          <select v-model="form.estilista_id" :disabled="!form.peluqueria_id" required>
            <option value="">{{ $t('recepcionista.crearCita.seleccionar') }}</option>
            <option v-for="e in estilistasFiltrados" :key="e.id" :value="e.id">{{ e.nombre_completo }}</option>
          </select>
        </div>

        <!-- FECHA Y HORA -->
        <div class="row-2">
          <div class="field">
            <label>{{ $t('recepcionista.crearCita.fecha') }}</label>
            <input type="date" v-model="form.fecha" :min="fechaMin" required />
          </div>
          <div class="field">
            <label>{{ $t('recepcionista.crearCita.horaInicio') }}</label>
            <input type="time" v-model="form.hora_inicio" required />
          </div>
        </div>

        <!-- OBSERVACIONES -->
        <div class="field">
          <label>{{ $t('recepcionista.crearCita.observaciones') }}</label>
          <textarea v-model="form.observaciones" rows="2" :placeholder="$t('recepcionista.crearCita.notasPlaceholder')"></textarea>
        </div>

        <!-- ERRORS -->
        <div v-if="formErrors.length" class="form-errors">
          <p v-for="(e, i) in formErrors" :key="i">{{ e }}</p>
        </div>

        <!-- SUCCESS -->
        <div v-if="success" class="form-success">
          <p>{{ $t('recepcionista.crearCita.success') }}</p>
          <div class="success-actions">
            <router-link to="/recepcionista/citas" class="btn-primary">{{ $t('recepcionista.crearCita.viewAppointments') }}</router-link>
            <button type="button" class="btn-secondary" @click="resetForm">{{ $t('recepcionista.crearCita.createAnother') }}</button>
          </div>
        </div>

        <div v-if="!success" class="form-actions">
          <router-link to="/recepcionista/citas" class="btn-secondary">{{ $t('recepcionista.crearCita.cancel') }}</router-link>
          <button type="submit" class="btn-primary" :disabled="submitting">{{ submitting ? $t('recepcionista.crearCita.creating') : $t('recepcionista.crearCita.submit') }}</button>
        </div>
      </form>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'

const { t } = useI18n()
const { formatCurrency } = useLocale()

const loadingData = ref(false)
const submitting = ref(false)
const success = ref(false)
const formErrors = ref([])

const clientes = ref([])
const peluquerias = ref([])
const servicios = ref([])
const estilistas = ref([])
const busquedaCliente = ref('')
const selectedCliente = ref(null)

const form = ref({ peluqueria_id: '', servicio_id: '', estilista_id: '', fecha: '', hora_inicio: '', observaciones: '' })

const fechaMin = (() => new Date().toISOString().split('T')[0])()

const clientesFiltrados = computed(() => {
  if (!busquedaCliente.value) return []
  const q = busquedaCliente.value.toLowerCase()
  return clientes.value.filter(c =>
    (c.nombre_completo || '').toLowerCase().includes(q) ||
    (c.email || '').toLowerCase().includes(q)
  )
})

const serviciosFiltrados = computed(() =>
  form.value.peluqueria_id ? servicios.value.filter(s => s.peluqueria?.id == form.value.peluqueria_id) : []
)

const estilistasFiltrados = computed(() =>
  form.value.peluqueria_id ? estilistas.value.filter(e => e.peluqueria?.id == form.value.peluqueria_id) : []
)

function onPeluqueriaChange() {
  form.value.servicio_id = ''
  form.value.estilista_id = ''
}
function onServicioChange() { form.value.estilista_id = '' }

function searchClientes() {
  const q = busquedaCliente.value
  const found = clientes.value.find(c => c.nombre_completo + ' (' + c.email + ')' === q)
  selectedCliente.value = found || null
}

async function loadData() {
  loadingData.value = true
  try {
    const [c, s, e] = await Promise.all([
      api.get('/usuarios/?rol=cliente'),
      api.get('/cliente/servicios/'),
      api.get('/cliente/estilistas/'),
    ])
    clientes.value = (c.data.results || c.data).map(u => ({ ...u, nombre_completo: u.first_name + ' ' + u.last_name }))
    const servs = Array.isArray(s.data) ? s.data : (s.data.results || [])
    servicios.value = servs
    const ests = Array.isArray(e.data) ? e.data : (e.data.results || [])
    estilistas.value = ests
    const mapa = new Map()
    servs.forEach(s => { if (s.peluqueria && !mapa.has(s.peluqueria.id)) mapa.set(s.peluqueria.id, s.peluqueria) })
    peluquerias.value = Array.from(mapa.values())
  } catch (e) { console.error(e) } finally { loadingData.value = false }
}

async function crearCita() {
  formErrors.value = []; submitting.value = true
  if (!selectedCliente.value) { formErrors.value = [t('recepcionista.crearCita.selectClient')]; submitting.value = false; return }
  try {
    await api.post('/recepcionista/citas/crear/', {
      cliente_id: selectedCliente.value.id,
      estilista_id: form.value.estilista_id,
      servicio_id: form.value.servicio_id,
      fecha: form.value.fecha,
      hora_inicio: form.value.hora_inicio,
      observaciones: form.value.observaciones || '',
    })
    success.value = true
  } catch (e) {
    if (e.response?.data) formErrors.value = Object.values(e.response.data).flat()
    else formErrors.value = [t('recepcionista.crearCita.errorCreate')]
  } finally { submitting.value = false }
}

function resetForm() {
  form.value = { peluqueria_id: '', servicio_id: '', estilista_id: '', fecha: '', hora_inicio: '', observaciones: '' }
  busquedaCliente.value = ''; selectedCliente.value = null; success.value = false; formErrors.value = []
}

onMounted(loadData)
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.form { max-width: 600px; }
.field { margin-bottom: 1rem; }
.field label { display: block; font-size: 0.75rem; font-weight: 500; color: #888; margin-bottom: 0.3rem; }
.field input, .field select, .field textarea {
  width: 100%; padding: 0.5rem 0.7rem; background: #161616; border: 1px solid #252525;
  border-radius: 8px; color: #e8e8e8; font-size: 0.85rem; font-family: inherit; box-sizing: border-box;
}
.field input:focus, .field select:focus, .field textarea:focus { outline: none; border-color: #555; }
.field textarea { resize: vertical; min-height: 50px; }
.field-hint { font-size: 0.72rem; color: #5fa868; margin-top: 0.2rem; display: block; }
.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-errors { padding: 0.6rem 0.75rem; background: #1a1212; border: 1px solid #2a1a1a; border-radius: 8px; margin-bottom: 0.75rem; }
.form-errors p { margin: 0; padding: 0.15rem 0; color: #c47a7a; font-size: 0.8rem; }
.form-success { padding: 1rem; background: #122218; border: 1px solid #1a3020; border-radius: 8px; margin-bottom: 1rem; text-align: center; }
.form-success p { color: #5fa868; font-size: 0.9rem; margin: 0 0 0.75rem; }
.success-actions { display: flex; gap: 0.5rem; justify-content: center; }
.form-actions { display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 0.5rem; }
.btn-primary { padding: 0.5rem 1rem; background: #e8e8e8; color: #0c0c0c; border: none; border-radius: 8px; font-size: 0.8rem; font-weight: 600; font-family: inherit; cursor: pointer; text-decoration: none; transition: opacity 0.15s; }
.btn-primary:hover { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-secondary { padding: 0.5rem 1rem; background: none; color: #888; border: 1px solid #2a2a2a; border-radius: 8px; font-size: 0.8rem; font-weight: 500; font-family: inherit; cursor: pointer; text-decoration: none; transition: all 0.15s; }
.btn-secondary:hover { color: #ccc; border-color: #444; }
.empty-state { padding: 2.5rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
@media (max-width: 768px) { .page { padding: 1rem; } .row-2 { grid-template-columns: 1fr; } }
</style>