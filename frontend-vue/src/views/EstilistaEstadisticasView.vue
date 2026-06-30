<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('estilista.estadisticas.title') }}</h1>
      <div class="tabs">
        <button :class="['tab',{active:periodo==='hoy'}]" @click="periodo='hoy';load()">{{ $t('estilista.estadisticas.tabHoy') }}</button>
        <button :class="['tab',{active:periodo==='semana'}]" @click="periodo='semana';load()">{{ $t('estilista.estadisticas.tabSemana') }}</button>
        <button :class="['tab',{active:periodo==='mes'}]" @click="periodo='mes';load()">{{ $t('estilista.estadisticas.tabMes') }}</button>
      </div>
    </div>

    <div v-if="loading" class="empty-state">{{ $t('estilista.estadisticas.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <template v-else-if="data.resumen">
      <!-- STATS CARDS -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-value">{{ data.resumen.total_citas }}</span>
          <span class="stat-label">{{ $t('estilista.estadisticas.totalCitas') }}</span>
        </div>
        <div class="stat-card accent-green">
          <span class="stat-value">{{ data.resumen.completadas }}</span>
          <span class="stat-label">{{ $t('estilista.estadisticas.completadas') }}</span>
        </div>
        <div class="stat-card accent-red">
          <span class="stat-value">{{ data.resumen.canceladas }}</span>
          <span class="stat-label">{{ $t('estilista.estadisticas.canceladas') }}</span>
        </div>
        <div class="stat-card accent-blue">
          <span class="stat-value">{{ formatCurrency(data.resumen.ingresos_estimados) }}</span>
          <span class="stat-label">{{ $t('estilista.estadisticas.ingresos') }}</span>
        </div>
        <div class="stat-card accent-yellow">
          <span class="stat-value">{{ data.resumen.pendientes }}</span>
          <span class="stat-label">{{ $t('estilista.estadisticas.pendientes') }}</span>
        </div>
      </div>

      <!-- TWO COLUMNS -->
      <div class="cols">
        <!-- TOP SERVICIOS -->
        <section class="section">
          <h2 class="section-title">{{ $t('estilista.estadisticas.topServicios') }}</h2>
          <div v-if="data.servicios_top.length === 0" class="mini-empty">{{ $t('estilista.estadisticas.noData') }}</div>
          <ul v-else class="rank-list">
            <li v-for="(s, i) in data.servicios_top" :key="i" class="rank-item">
              <span class="rank-num">{{ i + 1 }}</span>
              <span class="rank-name">{{ s.servicio__nombre }}</span>
              <span class="rank-count">{{ s.cantidad }}</span>
            </li>
          </ul>
        </section>

        <!-- TOP CLIENTES -->
        <section class="section">
          <h2 class="section-title">{{ $t('estilista.estadisticas.topClientes') }}</h2>
          <div v-if="data.clientes_frecuentes.length === 0" class="mini-empty">{{ $t('estilista.estadisticas.noData') }}</div>
          <ul v-else class="rank-list">
            <li v-for="(c, i) in data.clientes_frecuentes" :key="i" class="rank-item">
              <span class="rank-num">{{ i + 1 }}</span>
              <span class="rank-name">{{ c.nombre || '—' }}</span>
              <span class="rank-count">{{ $t('estilista.estadisticas.citasCount', { count: c.citas }) }}</span>
            </li>
          </ul>
        </section>
      </div>

      <!-- ACTIVITY CHART (simple bar) -->
      <section class="section" v-if="data.citas_por_dia.length > 0">
        <h2 class="section-title">{{ $t('estilista.estadisticas.actividadPorDia') }}</h2>
        <div class="chart">
          <div v-for="d in data.citas_por_dia" :key="d.fecha" class="chart-bar-group">
            <div class="chart-bars">
              <div class="chart-bar total-bar" :style="{ height: barHeight(d.total) + 'px' }" :title="$t('estilista.estadisticas.totalTooltip', { count: d.total })">
                <span class="bar-val" v-if="d.total">{{ d.total }}</span>
              </div>
              <div class="chart-bar completed-bar" :style="{ height: barHeight(d.completadas) + 'px' }" :title="$t('estilista.estadisticas.completedTooltip', { count: d.completadas })">
                <span class="bar-val" v-if="d.completadas">{{ d.completadas }}</span>
              </div>
            </div>
            <span class="chart-label">{{ formatDate(d.fecha) }}</span>
          </div>
        </div>
        <div class="chart-legend">
          <span class="legend-item"><span class="legend-dot total-dot"></span> {{ $t('estilista.estadisticas.legendTotal') }}</span>
          <span class="legend-item"><span class="legend-dot completed-dot"></span> {{ $t('estilista.estadisticas.legendCompleted') }}</span>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'
import api from '@/services/api'

const { t } = useI18n()
const { formatCurrency, formatDate } = useLocale()

const loading = ref(false)
const error = ref(null)
const periodo = ref('mes')
const data = ref({ resumen: null, servicios_top: [], clientes_frecuentes: [], citas_por_dia: [] })

const maxTotal = ref(1)

function barHeight(val) {
  if (!val || maxTotal.value === 0) return 0
  return Math.max(4, (val / maxTotal.value) * 120)
}

async function load() {
  loading.value = true; error.value = null
  try {
    const res = await api.get(`/estilista/estadisticas/?periodo=${periodo.value}`)
    data.value = res.data
    const maxVal = Math.max(...(res.data.citas_por_dia || []).map(d => d.total || 0), 1)
    maxTotal.value = maxVal
  } catch (e) { error.value = t('estilista.estadisticas.loadError'); console.error(e) }
  finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.tabs { display: flex; gap: 0.25rem; background: #141414; border-radius: 8px; padding: 0.2rem; }
.tab { padding: 0.35rem 0.7rem; background: none; border: none; border-radius: 6px; color: #666; font-size: 0.78rem; font-weight: 500; cursor: pointer; font-family: inherit; }
.tab.active { background: #1e1e1e; color: #e8e8e8; }
.tab:hover:not(.active) { color: #999; }
.empty-state { padding: 2.5rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.75rem; margin-bottom: 2rem; }
.stat-card { display: flex; flex-direction: column; gap: 0.3rem; padding: 1rem; background: #141414; border: 1px solid #222; border-radius: 10px; border-top: 3px solid #333; }
.stat-card.accent-green { border-top-color: #5fa868; }
.stat-card.accent-red { border-top-color: #b05a5a; }
.stat-card.accent-blue { border-top-color: #5a8fbf; }
.stat-card.accent-yellow { border-top-color: #b8a44a; }
.stat-value { font-size: 1.3rem; font-weight: 700; color: #e8e8e8; line-height: 1; }
.stat-label { font-size: 0.7rem; color: #555; text-transform: uppercase; letter-spacing: 0.04em; }

/* Columns */
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }
.section { }
.section-title { font-size: 0.9rem; font-weight: 600; color: #e8e8e8; margin: 0 0 0.75rem; }
.mini-empty { font-size: 0.8rem; color: #555; padding: 1rem 0; }
.rank-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.rank-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.55rem 0.75rem; background: #141414; border-radius: 8px; }
.rank-num { width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: #1e1e1e; color: #888; font-size: 0.7rem; font-weight: 600; flex-shrink: 0; }
.rank-name { flex: 1; font-size: 0.82rem; color: #e8e8e8; }
.rank-count { font-size: 0.78rem; color: #5a8fbf; font-weight: 500; }

/* Chart */
.chart { display: flex; align-items: flex-end; gap: 0.5rem; height: 150px; padding: 0 0.25rem; border-bottom: 1px solid #222; margin-bottom: 0.5rem; }
.chart-bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; min-width: 20px; }
.chart-bars { display: flex; gap: 2px; align-items: flex-end; height: 130px; }
.chart-bar { width: 14px; border-radius: 3px 3px 0 0; display: flex; align-items: flex-start; justify-content: center; transition: height 0.3s; }
.total-bar { background: #2a2a2a; }
.completed-bar { background: #122218; }
.bar-val { font-size: 0.6rem; color: #888; margin-top: -16px; font-weight: 600; }
.chart-label { font-size: 0.6rem; color: #555; margin-top: 0.3rem; }
.chart-legend { display: flex; gap: 1rem; justify-content: center; }
.legend-item { display: flex; align-items: center; gap: 0.35rem; font-size: 0.7rem; color: #666; }
.legend-dot { width: 8px; height: 8px; border-radius: 2px; }
.total-dot { background: #2a2a2a; }
.completed-dot { background: #122218; }

@media (max-width: 768px) { .page { padding: 1rem; } .stats-grid { grid-template-columns: 1fr 1fr; } .cols { grid-template-columns: 1fr; } .page-header { flex-direction: column; align-items: flex-start; } }
@media (max-width: 480px) { .stats-grid { grid-template-columns: 1fr; } .chart-bar { width: 10px; } }
</style>