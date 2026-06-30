<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('estilista.citas.title') }}</h1>
      <div class="tabs">
        <button :class="['tab', { active: tab === 'proximas' }]" @click="tab='proximas';page=1;load()">{{ $t('estilista.citas.tabProximas') }}</button>
        <button :class="['tab', { active: tab === 'pendientes' }]" @click="tab='pendientes';page=1;load()">{{ $t('estilista.citas.tabPendientes') }}</button>
        <button :class="['tab', { active: tab === 'todas' }]" @click="tab='todas';page=1;load()">{{ $t('estilista.citas.tabTodas') }}</button>
      </div>
    </div>

    <div v-if="loading" class="empty-state">{{ $t('estilista.citas.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <template v-else>
      <div v-if="citas.length === 0" class="empty-state">{{ $t('estilista.citas.empty') }}</div>
      <div v-else class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>{{ $t('estilista.citas.fecha') }}</th>
              <th>{{ $t('estilista.citas.hora') }}</th>
              <th>{{ $t('estilista.citas.cliente') }}</th>
              <th>{{ $t('estilista.citas.servicio') }}</th>
              <th>{{ $t('estilista.citas.estado') }}</th>
              <th>{{ $t('estilista.citas.acciones') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in citas" :key="c.id">
              <td class="mono">{{ formatDate(c.fecha) }}</td>
              <td class="mono">{{ formatTime(c.hora_inicio) }} - {{ formatTime(c.hora_fin) }}</td>
              <td class="strong">{{ c.cliente?.nombre_completo || '—' }}</td>
              <td>{{ c.servicio?.nombre || '—' }}</td>
              <td><span :class="['badge','estado-'+c.estado]">{{ formatEstado(c.estado) }}</span></td>
              <td class="actions-cell">
                <button v-if="c.estado==='pendiente'" class="btn-sm btn-confirm" @click="cambiarEstado(c.id,'confirmada')">{{ $t('estilista.citas.confirmar') }}</button>
                <button v-if="c.estado==='confirmada'" class="btn-sm btn-complete" @click="cambiarEstado(c.id,'completada')">{{ $t('estilista.citas.completar') }}</button>
                <button v-if="c.estado!=='cancelada' && c.estado!=='completada'" class="btn-sm btn-cancel" @click="cambiarEstado(c.id,'cancelada')">{{ $t('estilista.citas.cancelar') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="page<=1" @click="page--;load()">{{ $t('estilista.citas.anterior') }}</button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button :disabled="page>=totalPages" @click="page++;load()">{{ $t('estilista.citas.siguiente') }}</button>
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
const { formatDate, formatTime } = useLocale()

const citas = ref([])
const total = ref(0)
const page = ref(1)
const tab = ref('proximas')
const loading = ref(false)
const error = ref(null)
const pageSize = 20
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

function formatEstado(estado) {
  const map = {
    pendiente: t('common.states.pendiente'),
    confirmada: t('common.states.confirmada'),
    completada: t('common.states.completada'),
    cancelada: t('common.states.cancelada'),
  }
  return map[estado] || estado
}

async function load() {
  loading.value = true; error.value = null
  try {
    const params = new URLSearchParams({ page: page.value, page_size: pageSize })
    if (tab.value === 'proximas') params.set('proximas', 'true')
    else if (tab.value === 'pendientes') params.set('estado', 'pendiente')
    const res = await api.get(`/estilista/mis-citas/?${params}`)
    citas.value = res.data.results || []
    total.value = res.data.count || 0
  } catch (e) { error.value = t('estilista.citas.loadError'); console.error(e) }
  finally { loading.value = false }
}

async function cambiarEstado(id, estado) {
  try {
    await api.patch(`/estilista/mis-citas/${id}/cambiar-estado/`, { estado })
    load()
  } catch (e) {
    alert(Object.values(e.response?.data || {}).flat().join('\n') || t('estilista.citas.estadoError'))
  }
}

onMounted(load)
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.tabs { display: flex; gap: 0.25rem; background: #141414; border-radius: 8px; padding: 0.2rem; }
.tab { padding: 0.35rem 0.7rem; background: none; border: none; border-radius: 6px; color: #666; font-size: 0.78rem; font-weight: 500; cursor: pointer; font-family: inherit; transition: all 0.15s; }
.tab.active { background: #1e1e1e; color: #e8e8e8; }
.tab:hover:not(.active) { color: #999; }
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
.actions-cell { display: flex; gap: 0.35rem; }
.btn-sm { padding: 0.25rem 0.55rem; border: none; border-radius: 4px; font-size: 0.7rem; font-weight: 500; cursor: pointer; font-family: inherit; }
.btn-confirm { background: #1a2a1a; color: #5fa868; }
.btn-complete { background: #121820; color: #5a8fbf; }
.btn-cancel { background: #1a1212; color: #b05a5a; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.25rem; }
.pagination button { padding: 0.35rem 0.75rem; background: #161616; border: 1px solid #252525; border-radius: 6px; color: #888; font-size: 0.78rem; cursor: pointer; font-family: inherit; }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }
.pagination button:hover:not(:disabled) { border-color: #444; color: #ccc; }
.page-info { font-size: 0.78rem; color: #555; }
@media (max-width: 768px) { .page { padding: 1rem; } .page-header { flex-direction: column; align-items: flex-start; } }
</style>