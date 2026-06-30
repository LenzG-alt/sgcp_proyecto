<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('estilista.historial.title') }}</h1>
      <div class="filters-bar">
        <div class="filter-group">
          <label>{{ $t('estilista.historial.desde') }}</label>
          <input type="date" v-model="filtros.desde" @change="page=1;load()" />
        </div>
        <div class="filter-group">
          <label>{{ $t('estilista.historial.hasta') }}</label>
          <input type="date" v-model="filtros.hasta" @change="page=1;load()" />
        </div>
      </div>
    </div>

    <div v-if="loading" class="empty-state">{{ $t('estilista.historial.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <template v-else>
      <div v-if="citas.length === 0" class="empty-state">{{ $t('estilista.historial.empty') }}</div>
      <div v-else>
        <div class="summary-bar">
          <span>{{ $t('estilista.historial.totalCompleted', { count: total }) }}</span>
          <span>{{ $t('estilista.historial.earnings') }} <strong>{{ formatCurrency(ingresosTotales) }}</strong></span>
        </div>
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>{{ $t('estilista.historial.fecha') }}</th>
                <th>{{ $t('estilista.historial.hora') }}</th>
                <th>{{ $t('estilista.historial.cliente') }}</th>
                <th>{{ $t('estilista.historial.servicio') }}</th>
                <th>{{ $t('estilista.historial.precio') }}</th>
                <th>{{ $t('estilista.historial.duracion') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in citas" :key="c.id">
                <td class="mono">{{ formatDate(c.fecha) }}</td>
                <td class="mono">{{ formatTime(c.hora_inicio) }}</td>
                <td class="strong">{{ c.cliente?.nombre_completo || '—' }}</td>
                <td>{{ c.servicio?.nombre || '—' }}</td>
                <td>{{ c.servicio?.precio ? formatCurrency(c.servicio.precio) : '—' }}</td>
                <td>{{ c.servicio?.duracion_minutos || '—' }} {{ $t('common.minutes') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination" v-if="totalPages > 1">
          <button :disabled="page<=1" @click="page--;load()">{{ $t('estilista.historial.anterior') }}</button>
          <span class="page-info">{{ page }} / {{ totalPages }}</span>
          <button :disabled="page>=totalPages" @click="page++;load()">{{ $t('estilista.historial.siguiente') }}</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'
import api from '@/services/api'

const { t } = useI18n()
const { formatDate, formatTime, formatCurrency } = useLocale()

const citas = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const error = ref(null)
const pageSize = 20
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const ingresosTotales = computed(() =>
  citas.value.reduce((sum, c) => sum + (parseFloat(c.servicio?.precio) || 0), 0).toFixed(2)
)

const filtros = ref({ desde: '', hasta: '' })

async function load() {
  loading.value = true; error.value = null
  try {
    const params = new URLSearchParams({ page: page.value, page_size: pageSize, pasadas: 'true', estado: 'completada' })
    if (filtros.value.desde) params.set('desde', filtros.value.desde)
    if (filtros.value.hasta) params.set('hasta', filtros.value.hasta)
    const res = await api.get(`/estilista/mis-citas/?${params}`)
    citas.value = res.data.results || []
    total.value = res.data.count || 0
  } catch (e) { error.value = t('estilista.historial.loadError'); console.error(e) }
  finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.75rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.filters-bar { display: flex; gap: 0.75rem; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 0.2rem; }
.filter-group label { font-size: 0.68rem; color: #555; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 500; }
.filter-group input { padding: 0.35rem 0.55rem; background: #161616; border: 1px solid #252525; border-radius: 6px; color: #e8e8e8; font-size: 0.78rem; font-family: inherit; }
.filter-group input:focus { outline: none; border-color: #555; }
.summary-bar { display: flex; gap: 1.5rem; margin-bottom: 1rem; padding: 0.6rem 0.85rem; background: #141414; border-radius: 8px; font-size: 0.8rem; color: #888; }
.summary-bar strong { color: #5fa868; }
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
.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.25rem; }
.pagination button { padding: 0.35rem 0.75rem; background: #161616; border: 1px solid #252525; border-radius: 6px; color: #888; font-size: 0.78rem; cursor: pointer; font-family: inherit; }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }
.pagination button:hover:not(:disabled) { border-color: #444; color: #ccc; }
.page-info { font-size: 0.78rem; color: #555; }
@media (max-width: 768px) { .page { padding: 1rem; } .page-header { flex-direction: column; } .filters-bar { flex-direction: column; width: 100%; } }
</style>