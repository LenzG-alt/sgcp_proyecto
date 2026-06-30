<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('cliente.estilistas.title') }}</h1>
      <router-link to="/cliente/reservar" class="btn-primary">{{ $t('cliente.estilistas.book') }}</router-link>
    </div>

    <!-- FILTROS -->
    <div class="filters">
      <select v-model="filtroPeluqueria" class="select-filter" @change="loadEstilistas">
        <option value="">{{ $t('cliente.estilistas.allBranches') }}</option>
        <option v-for="p in peluquerias" :key="p.id" :value="p.id">{{ p.nombre }}</option>
      </select>
      <select v-model="filtroDia" class="select-filter" @change="loadEstilistas">
        <option value="">{{ $t('cliente.estilistas.allDays') }}</option>
        <option v-for="d in diasSemana" :key="d" :value="d">{{ formatDay(d) }}</option>
      </select>
    </div>

    <!-- LOADING / ERROR / EMPTY -->
    <div v-if="loading" class="empty-state">{{ $t('cliente.estilistas.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <div v-else-if="estilistas.length === 0" class="empty-state">{{ $t('cliente.estilistas.notFound') }}</div>

    <!-- LISTA -->
    <div v-else class="estilistas-list">
      <div v-for="e in estilistas" :key="e.id" class="estilista-card">
        <div class="estilista-main">
          <div class="estilista-header">
            <span class="estilista-nombre strong">{{ e.nombre_completo }}</span>
            <span v-if="e.especialidad" class="especialidad-tag">{{ e.especialidad }}</span>
          </div>
          <div v-if="e.peluqueria" class="estilista-sucursal muted">
            {{ e.peluqueria.nombre }} — {{ e.peluqueria.direccion }}
            <span v-if="e.peluqueria.telefono" class="sep">·</span>
            <span v-if="e.peluqueria.telefono">{{ e.peluqueria.telefono }}</span>
          </div>

          <!-- Horario colapsable -->
          <button v-if="e.horario && e.horario.length > 0" class="btn-horario" @click="toggleHorario(e.id)">
            {{ expandedId === e.id ? $t('cliente.estilistas.hideSchedule') : $t('cliente.estilistas.showSchedule') }}
          </button>
          <div v-if="expandedId === e.id && e.horario" class="horario-grid">
            <div v-for="h in e.horario" :key="h.dia_semana + h.hora_inicio" class="horario-item">
              <span class="dia">{{ formatDay(h.dia_semana) }}</span>
              <span class="horas mono">{{ h.hora_inicio?.substring(0, 5) }} — {{ h.hora_fin?.substring(0, 5) }}</span>
            </div>
          </div>
        </div>

        <div class="estilista-actions">
          <button class="btn-reservar" @click="irReservar(e)">
            {{ $t('cliente.estilistas.bookAction') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()

const estilistas = ref([])
const peluquerias = ref([])
const loading = ref(false)
const error = ref(null)
const filtroPeluqueria = ref('')
const filtroDia = ref('')
const expandedId = ref(null)

const diasSemana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

function formatDay(dia) {
  if (!dia) return '—'
  const key = 'common.days.' + dia
  const translated = t(key)
  return translated !== key ? translated : dia.charAt(0).toUpperCase() + dia.slice(1)
}

function toggleHorario(id) {
  expandedId.value = expandedId.value === id ? null : id
}

async function loadEstilistas() {
  loading.value = true
  error.value = null
  try {
    const params = {}
    if (filtroPeluqueria.value) params.peluqueria_id = filtroPeluqueria.value
    if (filtroDia.value) params.dia = filtroDia.value

    const res = await api.get('/cliente/estilistas/', { params })
    estilistas.value = Array.isArray(res.data) ? res.data : (res.data.results || [])

    // Extraer peluquerias unicas
    const mapa = new Map()
    estilistas.value.forEach(e => {
      if (e.peluqueria && !mapa.has(e.peluqueria.id)) {
        mapa.set(e.peluqueria.id, e.peluqueria)
      }
    })
    peluquerias.value = Array.from(mapa.values())
  } catch (err) {
    error.value = t('cliente.estilistas.loadError')
    console.error(err)
  } finally {
    loading.value = false
  }
}

function irReservar(estilista) {
  router.push({ name: 'cliente-reservar', query: { estilista_id: estilista.id } })
}

onMounted(() => { loadEstilistas() })
</script>

<style scoped>
.page {
  background: #0c0c0c; min-height: 100vh;
  color: #ccc; font-family: 'Inter', system-ui, sans-serif;
}

.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem;
}
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }

.btn-primary {
  padding: 0.5rem 1rem; background: #e8e8e8; color: #0c0c0c;
  border: none; border-radius: 8px; font-size: 0.8rem;
  font-weight: 600; font-family: inherit; cursor: pointer;
  text-decoration: none; transition: opacity 0.15s;
}
.btn-primary:hover { opacity: 0.85; }

/* ===== FILTERS ===== */
.filters { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }

.select-filter {
  padding: 0.5rem 0.75rem; background: #161616;
  border: 1px solid #252525; border-radius: 8px;
  color: #e8e8e8; font-size: 0.8rem; font-family: inherit; cursor: pointer;
}
.select-filter:focus { outline: none; border-color: #555; }

/* ===== ESTILISTAS LIST ===== */
.estilistas-list {
  display: flex; flex-direction: column; gap: 0.5rem;
}

.estilista-card {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 1.15rem; background: #141414;
  border: 1px solid #1e1e1e; border-radius: 10px;
  transition: border-color 0.15s; gap: 1rem;
}
.estilista-card:hover { border-color: #333; }

.estilista-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.3rem; }

.estilista-header { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
.estilista-nombre { font-size: 0.95rem; }

.especialidad-tag {
  padding: 0.15rem 0.5rem; background: #1a1812;
  border: 1px solid #2a2518; border-radius: 4px;
  font-size: 0.68rem; color: #b8a44a; font-weight: 500;
}

.estilista-sucursal { font-size: 0.78rem; }
.sep { color: #333; }

.btn-horario {
  align-self: flex-start; padding: 0.3rem 0.65rem;
  background: none; border: 1px solid #2a2a2a; border-radius: 6px;
  color: #888; font-size: 0.75rem; font-family: inherit;
  cursor: pointer; transition: all 0.15s; margin-top: 0.2rem;
}
.btn-horario:hover { color: #e8e8e8; border-color: #444; }

/* ===== HORARIO GRID ===== */
.horario-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.35rem; margin-top: 0.5rem; padding-top: 0.5rem;
  border-top: 1px solid #1a1a1a;
}

.horario-item {
  display: flex; justify-content: space-between;
  padding: 0.3rem 0.5rem; background: #111; border-radius: 4px;
  font-size: 0.75rem;
}
.dia { color: #888; font-weight: 500; }
.horas { color: #bbb; }

.estilista-actions { flex-shrink: 0; align-self: center; }

.btn-reservar {
  padding: 0.45rem 1rem; background: #161616; color: #5fa868;
  border: 1px solid #1a3a22; border-radius: 8px;
  font-size: 0.8rem; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: all 0.15s; white-space: nowrap;
}
.btn-reservar:hover { background: #122218; border-color: #2a5a32; }

/* ===== EMPTY / HELPERS ===== */
.empty-state { padding: 3rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }
.strong { color: #e8e8e8; font-weight: 500; }
.muted { color: #666; }
.mono { font-variant-numeric: tabular-nums; }

@media (max-width: 768px) {
  .estilista-card { flex-direction: column; }
  .estilista-actions { align-self: stretch; }
  .btn-reservar { width: 100%; text-align: center; }
  .horario-grid { grid-template-columns: 1fr; }
}
</style>