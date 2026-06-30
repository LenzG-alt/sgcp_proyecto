<template>
  <div class="page">
    <!-- HEADER -->
    <div class="page-header">
      <h1>{{ $t('cliente.servicios.title') }}</h1>
      <router-link to="/cliente/reservar" class="btn-primary">{{ $t('cliente.servicios.book') }}</router-link>
    </div>

    <!-- FILTROS -->
    <div class="filters">
      <select v-model="filtroPeluqueria" class="select-filter" @change="loadServicios">
        <option value="">{{ $t('cliente.servicios.allBranches') }}</option>
        <option v-for="p in peluquerias" :key="p.id" :value="p.id">{{ p.nombre }}</option>
      </select>
      <input
        v-model="search"
        type="text"
        :placeholder="$t('cliente.servicios.searchPlaceholder')"
        class="input-search"
        @input="debouncedLoad"
      />
    </div>

    <!-- LOADING / ERROR / EMPTY -->
    <div v-if="loading" class="empty-state">{{ $t('cliente.servicios.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <div v-else-if="serviciosFiltrados.length === 0" class="empty-state">{{ $t('cliente.servicios.notFound') }}</div>

    <!-- GRID -->
    <div v-else class="cards-grid">
      <div v-for="s in serviciosFiltrados" :key="s.id" class="card">
        <div class="card-top">
          <span class="card-name strong">{{ s.nombre }}</span>
          <span v-if="s.peluqueria" class="card-peluqueria">{{ s.peluqueria.nombre }}</span>
        </div>
        <p class="card-desc muted">{{ s.descripcion || $t('cliente.servicios.noDescription') }}</p>
        <div class="card-footer">
          <span class="card-precio">{{ formatCurrency(s.precio) }}</span>
          <span class="card-duracion muted">{{ s.duracion_minutos }} {{ $t('common.min') }}</span>
        </div>
        <button class="btn-reservar" @click="irReservar(s)">
          {{ $t('cliente.servicios.bookThisService') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'

const { t } = useI18n()
const { formatCurrency } = useLocale()
const router = useRouter()

const servicios = ref([])
const peluquerias = ref([])
const loading = ref(false)
const error = ref(null)
const search = ref('')
const filtroPeluqueria = ref('')

const serviciosFiltrados = computed(() => {
  let list = servicios.value
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(s =>
      s.nombre.toLowerCase().includes(q) ||
      (s.descripcion || '').toLowerCase().includes(q)
    )
  }
  return list
})

let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadServicios(), 300)
}

async function loadServicios() {
  loading.value = true
  error.value = null
  try {
    const params = {}
    if (filtroPeluqueria.value) params.peluqueria_id = filtroPeluqueria.value

    const res = await api.get('cliente/servicios/', { params })
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
    error.value = t('cliente.servicios.loadError')
    console.error(err)
  } finally {
    loading.value = false
  }
}

function irReservar(servicio) {
  router.push({ name: 'cliente-reservar', query: { servicio_id: servicio.id } })
}

onMounted(() => { loadServicios() })
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

.input-search {
  flex: 1; min-width: 180px; padding: 0.5rem 0.75rem;
  background: #161616; border: 1px solid #252525; border-radius: 8px;
  color: #e8e8e8; font-size: 0.8rem; font-family: inherit;
  transition: border-color 0.15s;
}
.input-search::placeholder { color: #444; }
.input-search:focus { outline: none; border-color: #555; }

.select-filter {
  padding: 0.5rem 0.75rem; background: #161616;
  border: 1px solid #252525; border-radius: 8px;
  color: #e8e8e8; font-size: 0.8rem; font-family: inherit; cursor: pointer;
}
.select-filter:focus { outline: none; border-color: #555; }

/* ===== CARDS ===== */
.cards-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
}

.card {
  padding: 1.15rem; background: #141414;
  border: 1px solid #1e1e1e; border-radius: 10px;
  display: flex; flex-direction: column; gap: 0.3rem;
  transition: border-color 0.15s;
}
.card:hover { border-color: #333; }

.card-top {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 0.5rem;
}
.card-name { font-size: 0.9rem; }
.card-peluqueria { font-size: 0.68rem; color: #555; white-space: nowrap; background: #1a1a1a; padding: 0.15rem 0.45rem; border-radius: 4px; }
.card-desc { font-size: 0.78rem; margin: 0; line-height: 1.5; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 0.3rem; }
.card-precio { font-size: 0.95rem; font-weight: 600; color: #e8e8e8; }
.card-duracion { font-size: 0.75rem; }

.btn-reservar {
  margin-top: 0.5rem; padding: 0.5rem 0.75rem;
  background: #161616; color: #5fa868; border: 1px solid #1a3a22;
  border-radius: 8px; font-size: 0.8rem; font-weight: 500;
  font-family: inherit; cursor: pointer; transition: all 0.15s;
}
.btn-reservar:hover { background: #122218; border-color: #2a5a32; }

/* ===== EMPTY / HELPERS ===== */
.empty-state { padding: 3rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }
.strong { color: #e8e8e8; font-weight: 500; }
.muted { color: #666; }

@media (max-width: 768px) { .cards-grid { grid-template-columns: 1fr; } }
</style>