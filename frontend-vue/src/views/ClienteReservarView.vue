<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('cliente.reservar.title') }}</h1>
    </div>

    <!-- STEPS INDICATOR -->
    <div class="steps">
      <div :class="['step', { active: step >= 1, done: step > 1 }]">
        <span class="step-num">1</span> {{ $t('cliente.reservar.step1') }}
      </div>
      <div class="step-line" :class="{ active: step > 1 }"></div>
      <div :class="['step', { active: step >= 2, done: step > 2 }]">
        <span class="step-num">2</span> {{ $t('cliente.reservar.step2') }}
      </div>
      <div class="step-line" :class="{ active: step > 2 }"></div>
      <div :class="['step', { active: step >= 3, done: step > 3 }]">
        <span class="step-num">3</span> {{ $t('cliente.reservar.step3') }}
      </div>
    </div>

    <!-- LOADING / ERROR -->
    <div v-if="loadingData" class="empty-state">{{ $t('cliente.reservar.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>

    <template v-else>
      <!-- ========== STEP 1: Seleccionar Servicio ========== -->
      <div v-if="step === 1" class="step-content">
        <p class="step-desc">{{ $t('cliente.reservar.step1Desc') }}</p>

        <!-- Filtro por peluqueria -->
        <div v-if="peluquerias.length > 1" class="filters">
          <select v-model="filtroPeluqueria" class="select-filter">
            <option value="">{{ $t('cliente.reservar.allBranches') }}</option>
            <option v-for="p in peluquerias" :key="p.id" :value="p.id">{{ p.nombre }}</option>
          </select>
        </div>

        <div v-if="serviciosFiltrados.length === 0" class="empty-state">
          {{ $t('cliente.reservar.noServices') }}
        </div>
        <div v-else class="cards-grid">
          <div
            v-for="s in serviciosFiltrados"
            :key="s.id"
            :class="['card', { selected: form.servicio_id === s.id }]"
            @click="seleccionarServicio(s)"
          >
            <div class="card-name strong">{{ s.nombre }}</div>
            <div class="card-desc muted">{{ s.descripcion || $t('cliente.reservar.noDescription') }}</div>
            <div class="card-footer">
              <span class="card-precio">{{ formatCurrency(s.precio) }}</span>
              <span class="card-duracion muted">{{ s.duracion_minutos }} {{ $t('common.min') }}</span>
            </div>
            <div v-if="s.peluqueria" class="card-peluqueria muted">{{ s.peluqueria.nombre }}</div>
          </div>
        </div>

        <div class="step-actions">
          <button class="btn-primary" :disabled="!form.servicio_id" @click="step = 2">
            {{ $t('cliente.reservar.nextStylist') }}
          </button>
        </div>
      </div>

      <!-- ========== STEP 2: Seleccionar Estilista ========== -->
      <div v-if="step === 2" class="step-content">
        <p class="step-desc">{{ $t('cliente.reservar.step2Desc') }}</p>

        <div v-if="estilistasDisponibles.length === 0" class="empty-state">
          {{ $t('cliente.reservar.noStylists') }}
        </div>
        <div v-else class="cards-grid">
          <div
            v-for="e in estilistasDisponibles"
            :key="e.id"
            :class="['card', { selected: form.estilista_id === e.id }]"
            @click="seleccionarEstilista(e)"
          >
            <div class="card-name strong">{{ e.nombre_completo }}</div>
            <div v-if="e.especialidad" class="card-desc muted">{{ e.especialidad }}</div>
            <div v-if="e.peluqueria" class="card-peluqueria muted">{{ e.peluqueria.nombre }}</div>
            <div v-if="e.horario && e.horario.length > 0" class="card-horario">
              <div v-for="h in e.horario.slice(0, 5)" :key="h.dia_semana" class="horario-item muted">
                <span class="dia">{{ formatDay(h.dia_semana) }}</span>
                <span>{{ h.hora_inicio?.substring(0, 5) }} — {{ h.hora_fin?.substring(0, 5) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <button class="btn-secondary" @click="step = 1">{{ $t('cliente.reservar.previous') }}</button>
          <button class="btn-primary" :disabled="!form.estilista_id" @click="irPaso3">
            {{ $t('cliente.reservar.nextDate') }}
          </button>
        </div>
      </div>

      <!-- ========== STEP 3: Fecha y Hora ========== -->
      <div v-if="step === 3" class="step-content">
        <p class="step-desc">{{ $t('cliente.reservar.step3Desc') }}</p>

        <div class="resumen-servicio">
          <span class="strong">{{ servicioSeleccionado?.nombre }}</span>
          <span class="muted">— {{ servicioSeleccionado?.duracion_minutos }} {{ $t('common.min') }} — {{ formatCurrency(servicioSeleccionado?.precio) }}</span>
        </div>
        <div class="resumen-servicio">
          <span>{{ $t('cliente.reservar.stylistLabel') }}: <strong>{{ estilistaSeleccionado?.nombre_completo }}</strong></span>
        </div>

        <form @submit.prevent="crearCita" class="form">
          <div class="field">
            <label for="f-fecha">{{ $t('cliente.reservar.dateLabel') }}</label>
            <input
              id="f-fecha"
              v-model="form.fecha"
              type="date"
              :min="fechaMinima"
              required
            />
          </div>
          <div class="field">
            <label for="f-hora">{{ $t('cliente.reservar.startTimeLabel') }}</label>
            <input id="f-hora" v-model="form.hora_inicio" type="time" required />
          </div>
          <div v-if="estilistaSeleccionado" class="horario-ref muted">
            {{ $t('cliente.reservar.scheduleLabel') }}
            <span v-for="h in (estilistaSeleccionado.horario || [])" :key="h.dia_semana" class="horario-tag">
              {{ formatDay(h.dia_semana) }} {{ h.hora_inicio?.substring(0,5) }}-{{ h.hora_fin?.substring(0,5) }}
            </span>
          </div>
          <div class="field">
            <label for="f-obs">{{ $t('cliente.reservar.obsLabel') }}</label>
            <textarea id="f-obs" v-model="form.observaciones" rows="2" :placeholder="$t('cliente.reservar.obsPlaceholder')"></textarea>
          </div>

          <div v-if="formErrors.length > 0" class="form-errors">
            <p v-for="(e, i) in formErrors" :key="i">{{ e }}</p>
          </div>

          <div class="step-actions">
            <button type="button" class="btn-secondary" @click="step = 2">{{ $t('cliente.reservar.previous') }}</button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? $t('cliente.reservar.submitting') : $t('cliente.reservar.confirmBooking') }}
            </button>
          </div>
        </form>
      </div>

      <!-- ========== EXITO ========== -->
      <div v-if="step === 4" class="exito">
        <div class="exito-icon">OK</div>
        <h2>{{ $t('cliente.reservar.successTitle') }}</h2>
        <p>{{ $t('cliente.reservar.successMsg', { state: t('common.states.pendiente') }) }}</p>
        <div class="exito-actions">
          <router-link to="/cliente/mis-citas" class="btn-primary">{{ $t('cliente.reservar.viewAppointments') }}</router-link>
          <button class="btn-secondary" @click="resetForm">{{ $t('cliente.reservar.bookAnother') }}</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '@/services/api'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'

const { t } = useI18n()
const { formatCurrency } = useLocale()

// ============================================================================
// STATE
// ============================================================================
const step = ref(1)
const loadingData = ref(false)
const submitting = ref(false)
const error = ref(null)
const formErrors = ref([])

const servicios = ref([])
const estilistas = ref([])
const peluquerias = ref([])
const filtroPeluqueria = ref('')

const form = ref({
  servicio_id: null,
  estilista_id: null,
  fecha: '',
  hora_inicio: '',
  observaciones: '',
})

const servicioSeleccionado = computed(() =>
  servicios.value.find(s => s.id === form.value.servicio_id)
)

const estilistaSeleccionado = computed(() =>
  estilistas.value.find(e => e.id === form.value.estilista_id)
)

const serviciosFiltrados = computed(() => {
  if (!filtroPeluqueria.value) return servicios.value
  return servicios.value.filter(s => s.peluqueria?.id === filtroPeluqueria.value)
})

const estilistasDisponibles = computed(() => {
  if (!servicioSeleccionado.value?.peluqueria) return estilistas.value
  const peluqueriaId = servicioSeleccionado.value.peluqueria.id
  return estilistas.value.filter(e => e.peluqueria?.id === peluqueriaId)
})

const fechaMinima = (() => {
  const hoy = new Date()
  return hoy.toISOString().split('T')[0]
})()

// ============================================================================
// HELPERS
// ============================================================================
function formatDay(dia) {
  if (!dia) return '—'
  const key = 'common.days.' + dia
  const translated = t(key)
  return translated !== key ? translated : dia.charAt(0).toUpperCase() + dia.slice(1)
}

// ============================================================================
// LOAD DATA
// ============================================================================
async function loadServicios() {
  try {
    const res = await api.get('/cliente/servicios/')
    servicios.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
    // Extraer peluquerias unicas
    const mapa = new Map()
    servicios.value.forEach(s => {
      if (s.peluqueria && !mapa.has(s.peluqueria.id)) {
        mapa.set(s.peluqueria.id, s.peluqueria)
      }
    })
    peluquerias.value = Array.from(mapa.values())
  } catch (err) {
    console.error('Error cargando servicios:', err)
  }
}

async function loadEstilistas() {
  try {
    const res = await api.get('/cliente/estilistas/')
    estilistas.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (err) {
    console.error('Error cargando estilistas:', err)
  }
}

// ============================================================================
// SELECTION
// ============================================================================
function seleccionarServicio(s) {
  form.value.servicio_id = s.id
  form.value.estilista_id = null // Reset estilista al cambiar servicio
}

function seleccionarEstilista(e) {
  form.value.estilista_id = e.id
}

function irPaso3() {
  // Cargar horario detallado del estilista si no lo tiene
  if (estilistaSeleccionado.value && !estilistaSeleccionado.value.horario) {
    loadHorarioEstilista(estilistaSeleccionado.value.id)
  }
  step.value = 3
}

async function loadHorarioEstilista(id) {
  try {
    const res = await api.get(`/cliente/estilistas/${id}/horario/`)
    const e = estilistas.value.find(x => x.id === id)
    if (e) e.horario = res.data.horario
  } catch (err) {
    console.error('Error cargando horario:', err)
  }
}

// ============================================================================
// CREAR CITA
// ============================================================================
async function crearCita() {
  formErrors.value = []
  submitting.value = true

  try {
    await api.post('/cliente/mis-citas/crear/', {
      estilista_id: form.value.estilista_id,
      servicio_id: form.value.servicio_id,
      fecha: form.value.fecha,
      hora_inicio: form.value.hora_inicio,
      observaciones: form.value.observaciones || '',
    })
    step.value = 4
  } catch (err) {
    if (err.response?.data) {
      const errors = err.response.data
      formErrors.value = Object.values(errors).flat()
    } else {
      formErrors.value = [t('cliente.reservar.createError')]
    }
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  form.value = { servicio_id: null, estilista_id: null, fecha: '', hora_inicio: '', observaciones: '' }
  step.value = 1
  formErrors.value = []
}

// ============================================================================
// INIT
// ============================================================================
onMounted(async () => {
  loadingData.value = true
  error.value = null
  try {
    await Promise.all([loadServicios(), loadEstilistas()])
  } catch (err) {
    error.value = t('cliente.reservar.loadError')
  } finally {
    loadingData.value = false
  }
})
</script>

<style scoped>
.page {
  background: #0c0c0c;
  min-height: 100vh;
  color: #ccc;
  font-family: 'Inter', system-ui, sans-serif;
}

.page-header { margin-bottom: 1.5rem; }
.page-header h1 {
  font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0;
}

/* ===== STEPS ===== */
.steps {
  display: flex; align-items: center; gap: 0;
  margin-bottom: 2rem; padding: 0 1rem;
}
.step {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.78rem; color: #555; font-weight: 500;
  white-space: nowrap;
}
.step.active { color: #e8e8e8; }
.step.done { color: #5fa868; }
.step-num {
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 600;
  background: #1a1a1a; border: 1px solid #333; color: #666;
}
.step.active .step-num { background: #e8e8e8; color: #0c0c0c; border-color: #e8e8e8; }
.step.done .step-num { background: #122218; color: #5fa868; border-color: #1a3a22; }

.step-line {
  flex: 1; height: 1px; background: #222; margin: 0 0.75rem; min-width: 20px;
}
.step-line.active { background: #5fa868; }

.step-desc { font-size: 0.85rem; color: #888; margin: 0 0 1.25rem; }

/* ===== CARDS GRID ===== */
.cards-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.75rem; margin-bottom: 1.5rem;
}

.card {
  padding: 1rem 1.15rem; background: #141414;
  border: 1px solid #1e1e1e; border-radius: 10px;
  cursor: pointer; transition: all 0.15s;
  display: flex; flex-direction: column; gap: 0.3rem;
}
.card:hover { border-color: #333; }
.card.selected { border-color: #5fa868; background: #111a14; }

.card-name { font-size: 0.9rem; }
.card-desc { font-size: 0.78rem; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 0.3rem; }
.card-precio { font-size: 0.9rem; font-weight: 600; color: #e8e8e8; }
.card-duracion { font-size: 0.75rem; }
.card-peluqueria { font-size: 0.72rem; margin-top: 0.15rem; }

/* Horario en tarjeta de estilista */
.card-horario { margin-top: 0.4rem; }
.horario-item {
  display: flex; justify-content: space-between;
  font-size: 0.72rem; padding: 0.1rem 0;
}
.dia { color: #888; font-weight: 500; }

/* ===== FORM ===== */
.form { margin-top: 0.5rem; }
.field { margin-bottom: 1rem; }
.field label {
  display: block; font-size: 0.75rem; font-weight: 500;
  color: #888; margin-bottom: 0.3rem;
}
.field input[type="date"],
.field input[type="time"],
.field textarea {
  width: 100%; padding: 0.55rem 0.75rem; background: #1a1a1a;
  border: 1px solid #252525; border-radius: 8px;
  color: #e8e8e8; font-size: 0.85rem; font-family: inherit;
  box-sizing: border-box; transition: border-color 0.15s;
}
.field input::placeholder, .field textarea::placeholder { color: #444; }
.field input:focus, .field textarea:focus { outline: none; border-color: #555; }
.field textarea { resize: vertical; min-height: 50px; }

.horario-ref {
  font-size: 0.75rem; margin-bottom: 1rem;
  display: flex; flex-wrap: wrap; gap: 0.35rem; align-items: center;
}
.horario-tag {
  padding: 0.15rem 0.45rem; background: #161616;
  border: 1px solid #222; border-radius: 4px; font-size: 0.7rem;
}

.resumen-servicio {
  font-size: 0.85rem; color: #888; margin-bottom: 0.3rem;
}

/* ===== FILTERS ===== */
.filters { margin-bottom: 1.25rem; }
.select-filter {
  padding: 0.5rem 0.75rem; background: #161616;
  border: 1px solid #252525; border-radius: 8px;
  color: #e8e8e8; font-size: 0.8rem; font-family: inherit; cursor: pointer;
}
.select-filter:focus { outline: none; border-color: #555; }

/* ===== BUTTONS ===== */
.btn-primary {
  padding: 0.5rem 1rem; background: #e8e8e8; color: #0c0c0c;
  border: none; border-radius: 8px; font-size: 0.8rem;
  font-weight: 600; font-family: inherit; cursor: pointer;
  text-decoration: none; transition: opacity 0.15s;
}
.btn-primary:hover { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-secondary {
  padding: 0.5rem 1rem; background: none; color: #888;
  border: 1px solid #2a2a2a; border-radius: 8px;
  font-size: 0.8rem; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: all 0.15s;
}
.btn-secondary:hover { color: #ccc; border-color: #444; }

.step-actions {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 1.5rem; flex-wrap: wrap; gap: 0.5rem;
}

/* ===== ERRORS ===== */
.form-errors {
  padding: 0.6rem 0.75rem; background: #1a1212;
  border: 1px solid #2a1a1a; border-radius: 8px; margin-bottom: 0.75rem;
}
.form-errors p { margin: 0; padding: 0.15rem 0; color: #c47a7a; font-size: 0.8rem; }

/* ===== EXITO ===== */
.exito {
  text-align: center; padding: 3rem 1rem;
}
.exito-icon {
  width: 50px; height: 50px; border-radius: 50%;
  background: #122218; color: #5fa868; font-size: 1.5rem;
  display: inline-flex; align-items: center; justify-content: center;
  margin-bottom: 1rem;
}
.exito h2 { font-size: 1.1rem; color: #e8e8e8; margin: 0 0 0.5rem; }
.exito p { color: #888; font-size: 0.85rem; margin: 0 0 1.5rem; }
.exito-actions { display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; }

/* ===== EMPTY / HELPERS ===== */
.empty-state { padding: 2.5rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }
.strong { color: #e8e8e8; font-weight: 500; }
.muted { color: #666; }

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .cards-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .steps { padding: 0; }
  .step span:not(.step-num) { display: none; }
  .step-line { margin: 0 0.4rem; }
}
</style>