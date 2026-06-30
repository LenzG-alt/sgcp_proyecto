<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('recepcionista.calendario.title') }}</h1>
      <div class="header-right">
        <input type="date" v-model="fechaSeleccionada" @change="loadAgenda" class="date-input" />
      </div>
    </div>

    <div v-if="loading" class="empty-state">{{ $t('recepcionista.calendario.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <template v-else>
      <div v-if="grupos.length === 0" class="empty-state">{{ $t('recepcionista.calendario.noAppointments') }}</div>

      <div v-for="grupo in grupos" :key="grupo.estilista_id" class="estilista-block">
        <div class="estilista-header">
          <span class="estilista-name">{{ grupo.nombre }}</span>
          <span class="estilista-count">{{ grupo.citas.length }} {{ grupo.citas.length !== 1 ? $t('recepcionista.calendario.citas') : $t('recepcionista.calendario.cita') }}</span>
        </div>
        <div class="timeline">
          <div v-for="c in grupo.citas" :key="c.id" class="timeline-item" :class="'border-' + c.estado">
            <div class="time-block">
              <span class="time-start">{{ localeFormatTime(c.hora_inicio) }}</span>
              <span class="time-sep">-</span>
              <span class="time-end">{{ localeFormatTime(c.hora_fin) }}</span>
            </div>
            <div class="cita-info">
              <span class="cliente-name">{{ c.cliente?.nombre_completo || '—' }}</span>
              <span class="servicio-name">{{ c.servicio?.nombre || '' }}</span>
            </div>
            <span :class="['badge','estado-'+c.estado]">{{ t('common.states.' + c.estado) }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'

const { t } = useI18n()
const { formatTime: localeFormatTime } = useLocale()

const loading = ref(false)
const error = ref(null)
const grupos = ref([])
const fechaSeleccionada = (() => new Date().toISOString().split('T')[0])()

async function loadAgenda() {
  loading.value = true; error.value = null
  try {
    const res = await api.get(`/recepcionista/citas/?fecha=${fechaSeleccionada}&page_size=50`)
    const citas = res.data.results || []
    const map = new Map()
    citas.forEach(c => {
      const eid = c.estilista_id || c.estilista?.id
      if (!map.has(eid)) map.set(eid, { estilista_id: eid, nombre: c.estilista?.nombre_completo || t('recepcionista.calendario.unassigned'), citas: [] })
      map.get(eid).citas.push(c)
    })
    map.forEach(g => g.citas.sort((a, b) => (a.hora_inicio || '').localeCompare(b.hora_inicio || '')))
    grupos.value = Array.from(map.values())
  } catch (e) { error.value = t('recepcionista.calendario.errorLoad'); console.error(e) }
  finally { loading.value = false }
}

onMounted(loadAgenda)
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.date-input { padding: 0.4rem 0.6rem; background: #161616; border: 1px solid #252525; border-radius: 6px; color: #e8e8e8; font-size: 0.8rem; font-family: inherit; }
.date-input:focus { outline: none; border-color: #555; }
.empty-state { padding: 2.5rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }
.estilista-block { margin-bottom: 1.5rem; }
.estilista-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; padding: 0 0.25rem; }
.estilista-name { font-size: 0.9rem; font-weight: 600; color: #e8e8e8; }
.estilista-count { font-size: 0.72rem; color: #555; }
.timeline { display: flex; flex-direction: column; gap: 0.4rem; }
.timeline-item { display: flex; align-items: center; gap: 1rem; padding: 0.65rem 0.85rem; background: #141414; border-radius: 8px; border-left: 3px solid #333; }
.timeline-item.border-pendiente { border-left-color: #b8a44a; }
.timeline-item.border-confirmada { border-left-color: #5fa868; }
.timeline-item.border-completada { border-left-color: #5a8fbf; }
.timeline-item.border-cancelada { border-left-color: #b05a5a; }
.time-block { display: flex; align-items: center; gap: 0.25rem; min-width: 90px; }
.time-start, .time-end { font-size: 0.82rem; color: #e8e8e8; font-weight: 500; font-variant-numeric: tabular-nums; }
.time-sep { font-size: 0.7rem; color: #444; }
.cita-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.1rem; }
.cliente-name { font-size: 0.82rem; color: #e8e8e8; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.servicio-name { font-size: 0.72rem; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.badge { display: inline-block; padding: 0.12rem 0.45rem; border-radius: 4px; font-size: 0.65rem; font-weight: 500; flex-shrink: 0; }
.estado-pendiente { background: #1a1810; color: #b8a44a; }
.estado-confirmada { background: #122218; color: #5fa868; }
.estado-completada { background: #121820; color: #5a8fbf; }
.estado-cancelada { background: #1a1212; color: #b05a5a; }
@media (max-width: 768px) { .page { padding: 1rem; } .timeline-item { flex-wrap: wrap; gap: 0.5rem; } }
</style>