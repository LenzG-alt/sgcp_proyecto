<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('recepcionista.citas.title') }}</h1>
      <span class="count" v-if="total">{{ total }} {{ total !== 1 ? $t('recepcionista.citas.results') : $t('recepcionista.citas.result') }}</span>
    </div>

    <!-- FILTERS -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>{{ $t('recepcionista.citas.filter.estado') }}</label>
        <select v-model="filtros.estado" @change="page=1;loadCitas()">
          <option value="">{{ $t('recepcionista.citas.filter.all') }}</option>
          <option value="pendiente">{{ t('common.states.pendiente') }}</option>
          <option value="confirmada">{{ t('common.states.confirmada') }}</option>
          <option value="completada">{{ t('common.states.completada') }}</option>
          <option value="cancelada">{{ t('common.states.cancelada') }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label>{{ $t('recepcionista.citas.filter.desde') }}</label>
        <input type="date" v-model="filtros.desde" @change="page=1;loadCitas()" />
      </div>
      <div class="filter-group">
        <label>{{ $t('recepcionista.citas.filter.hasta') }}</label>
        <input type="date" v-model="filtros.hasta" @change="page=1;loadCitas()" />
      </div>
      <div class="filter-group">
        <label>{{ $t('recepcionista.citas.filter.estilista') }}</label>
        <select v-model="filtros.estilista_id" @change="page=1;loadCitas()">
          <option value="">{{ $t('recepcionista.citas.filter.all') }}</option>
          <option v-for="e in estilistas" :key="e.id" :value="e.id">{{ e.nombre_completo }}</option>
        </select>
      </div>
      <button class="btn-clear" @click="clearFilters">{{ $t('recepcionista.citas.clearFilters') }}</button>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="empty-state">{{ $t('recepcionista.citas.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>

    <!-- TABLE -->
    <template v-else>
      <div v-if="citas.length === 0" class="empty-state">{{ $t('recepcionista.citas.noResults') }}</div>
      <div v-else class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>{{ $t('recepcionista.citas.th.fecha') }}</th>
              <th>{{ $t('recepcionista.citas.th.hora') }}</th>
              <th>{{ $t('recepcionista.citas.th.cliente') }}</th>
              <th>{{ $t('recepcionista.citas.th.estilista') }}</th>
              <th>{{ $t('recepcionista.citas.th.servicio') }}</th>
              <th>{{ $t('recepcionista.citas.th.estado') }}</th>
              <th>{{ $t('recepcionista.citas.th.acciones') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in citas" :key="c.id">
              <td class="mono">{{ localeFormatDate(c.fecha) }}</td>
              <td class="mono">{{ localeFormatTime(c.hora_inicio) }}</td>
              <td class="strong">{{ c.cliente?.nombre_completo || '—' }}</td>
              <td>{{ c.estilista?.nombre_completo || '—' }}</td>
              <td>{{ c.servicio?.nombre || '—' }}</td>
              <td><span :class="['badge','estado-'+c.estado]">{{ t('common.states.' + c.estado) }}</span></td>
              <td class="actions-cell">
                <button v-if="c.estado==='pendiente'" class="btn-sm btn-confirm" @click="cambiarEstado(c.id,'confirmada')">{{ $t('recepcionista.citas.confirmar') }}</button>
                <button v-if="c.estado==='confirmada'" class="btn-sm btn-complete" @click="cambiarEstado(c.id,'completada')">{{ $t('recepcionista.citas.completar') }}</button>
                <button v-if="c.estado!=='cancelada' && c.estado!=='completada'" class="btn-sm btn-cancel" @click="cambiarEstado(c.id,'cancelada')">{{ $t('recepcionista.citas.cancelar') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- PAGINATION -->
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page<=1" @click="page--;loadCitas()">{{ $t('recepcionista.citas.previous') }}</button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button :disabled="page>=totalPages" @click="page++;loadCitas()">{{ $t('recepcionista.citas.next') }}</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'

const { t } = useI18n()
const { formatDate: localeFormatDate, formatTime: localeFormatTime } = useLocale()

const citas = ref([])
const estilistas = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const error = ref(null)
const pageSize = 20

const filtros = ref({ estado: '', desde: '', hasta: '', estilista_id: '' })
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

function clearFilters() {
  filtros.value = { estado: '', desde: '', hasta: '', estilista_id: '' }
  page.value = 1
  loadCitas()
}

async function loadEstilistas() {
  try {
    const res = await api.get('/cliente/estilistas/')
    estilistas.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (e) { console.error(e) }
}

async function loadCitas() {
  loading.value = true; error.value = null
  try {
    const params = new URLSearchParams({ page: page.value, page_size: pageSize })
    if (filtros.value.estado) params.set('estado', filtros.value.estado)
    if (filtros.value.desde) params.set('desde', filtros.value.desde)
    if (filtros.value.hasta) params.set('hasta', filtros.value.hasta)
    if (filtros.value.estilista_id) params.set('estilista_id', filtros.value.estilista_id)
    const res = await api.get(`/recepcionista/citas/?${params}`)
    const data = res.data
    citas.value = data.results || []
    total.value = data.count || 0
  } catch (e) {
    error.value = t('recepcionista.citas.errorLoad')
    console.error(e)
  } finally { loading.value = false }
}

async function cambiarEstado(id, estado) {
  try {
    await api.patch(`/recepcionista/citas/${id}/cambiar-estado/`, { estado })
    loadCitas()
  } catch (e) {
    const msg = e.response?.data
    alert(Object.values(msg).flat().join('\n') || t('recepcionista.citas.errorChangeState'))
  }
}

onMounted(() => { loadEstilistas(); loadCitas() })
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.count { font-size: 0.78rem; color: #555; }
.filters-bar { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1.5rem; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 0.25rem; }
.filter-group label { font-size: 0.68rem; color: #555; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 500; }
.filter-group select, .filter-group input {
  padding: 0.4rem 0.6rem; background: #161616; border: 1px solid #252525; border-radius: 6px;
  color: #e8e8e8; font-size: 0.8rem; font-family: inherit;
}
.filter-group select:focus, .filter-group input:focus { outline: none; border-color: #555; }
.btn-clear { padding: 0.4rem 0.75rem; background: none; border: 1px solid #2a2a2a; border-radius: 6px; color: #888; font-size: 0.75rem; cursor: pointer; font-family: inherit; }
.btn-clear:hover { color: #ccc; border-color: #444; }
.empty-state { padding: 2.5rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }
.table-wrapper { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
thead th { text-align: left; padding: 0.6rem 0.75rem; color: #666; font-weight: 500; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #222; }
tbody td { padding: 0.55rem 0.75rem; border-bottom: 1px solid #181818; color: #bbb; vertical-align: middle; }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: #111; }
.strong { color: #e8e8e8; font-weight: 500; }
.mono { font-variant-numeric: tabular-nums; }
.badge { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.68rem; font-weight: 500; }
.estado-pendiente { background: #1a1810; color: #b8a44a; }
.estado-confirmada { background: #122218; color: #5fa868; }
.estado-completada { background: #121820; color: #5a8fbf; }
.estado-cancelada { background: #1a1212; color: #b05a5a; }
.actions-cell { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.btn-sm { padding: 0.25rem 0.55rem; border: none; border-radius: 4px; font-size: 0.7rem; font-weight: 500; cursor: pointer; font-family: inherit; transition: opacity 0.15s; }
.btn-sm:hover { opacity: 0.8; }
.btn-confirm { background: #1a2a1a; color: #5fa868; }
.btn-complete { background: #121820; color: #5a8fbf; }
.btn-cancel { background: #1a1212; color: #b05a5a; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.25rem; }
.pagination button { padding: 0.35rem 0.75rem; background: #161616; border: 1px solid #252525; border-radius: 6px; color: #888; font-size: 0.78rem; cursor: pointer; font-family: inherit; }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }
.pagination button:hover:not(:disabled) { border-color: #444; color: #ccc; }
.page-info { font-size: 0.78rem; color: #555; }
@media (max-width: 768px) { .page { padding: 1rem; } .filters-bar { flex-direction: column; } .table { font-size: 0.72rem; } }
</style>