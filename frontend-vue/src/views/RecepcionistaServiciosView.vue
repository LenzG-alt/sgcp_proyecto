<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('recepcionista.servicios.title') }}</h1>
      <div v-if="peluquerias.length > 1" class="filter-group">
        <select v-model="filtroPeluqueria" class="select-filter">
          <option value="">{{ $t('recepcionista.servicios.allBranches') }}</option>
          <option v-for="p in peluquerias" :key="p.id" :value="p.id">{{ p.nombre }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="empty-state">{{ $t('recepcionista.servicios.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <template v-else>
      <div v-if="serviciosFiltrados.length === 0" class="empty-state">{{ $t('recepcionista.servicios.noServices') }}</div>
      <div class="cards-grid">
        <div v-for="s in serviciosFiltrados" :key="s.id" class="card">
          <div class="card-name">{{ s.nombre }}</div>
          <div class="card-desc">{{ s.descripcion || $t('recepcionista.servicios.noDescription') }}</div>
          <div class="card-footer">
            <span class="card-precio">{{ formatCurrency(s.precio) }}</span>
            <span class="card-duracion">{{ s.duracion_minutos }} {{ $t('recepcionista.servicios.min') }}</span>
          </div>
          <div v-if="s.peluqueria" class="card-peluqueria">{{ s.peluqueria.nombre }}</div>
        </div>
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
const { formatCurrency } = useLocale()

const loading = ref(false)
const error = ref(null)
const servicios = ref([])
const peluquerias = ref([])
const filtroPeluqueria = ref('')

const serviciosFiltrados = computed(() => {
  if (!filtroPeluqueria.value) return servicios.value
  return servicios.value.filter(s => s.peluqueria?.id === filtroPeluqueria.value)
})

async function load() {
  loading.value = true
  try {
    const res = await api.get('/cliente/servicios/')
    servicios.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
    const mapa = new Map()
    servicios.value.forEach(s => { if (s.peluqueria && !mapa.has(s.peluqueria.id)) mapa.set(s.peluqueria.id, s.peluqueria) })
    peluquerias.value = Array.from(mapa.values())
  } catch (e) { error.value = t('recepcionista.servicios.errorLoad'); console.error(e) }
  finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.select-filter { padding: 0.45rem 0.65rem; background: #161616; border: 1px solid #252525; border-radius: 6px; color: #e8e8e8; font-size: 0.8rem; font-family: inherit; cursor: pointer; }
.select-filter:focus { outline: none; border-color: #555; }
.empty-state { padding: 2.5rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }
.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.75rem; }
.card { padding: 1rem 1.15rem; background: #141414; border: 1px solid #1e1e1e; border-radius: 10px; display: flex; flex-direction: column; gap: 0.3rem; }
.card-name { font-size: 0.9rem; color: #e8e8e8; font-weight: 500; }
.card-desc { font-size: 0.78rem; color: #666; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 0.3rem; }
.card-precio { font-size: 0.9rem; font-weight: 600; color: #e8e8e8; }
.card-duracion { font-size: 0.75rem; color: #666; }
.card-peluqueria { font-size: 0.72rem; color: #555; margin-top: 0.15rem; }
@media (max-width: 768px) { .page { padding: 1rem; } .cards-grid { grid-template-columns: 1fr; } }
</style>