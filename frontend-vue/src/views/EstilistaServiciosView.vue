<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('estilista.servicios.title') }}</h1>
      <span v-if="data.peluqueria" class="sucursal-tag">{{ data.peluqueria }}</span>
    </div>

    <div v-if="loading" class="empty-state">{{ $t('estilista.servicios.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <template v-else>
      <div v-if="servicios.length === 0" class="empty-state">{{ $t('estilista.servicios.empty') }}</div>
      <div class="cards-grid">
        <div v-for="s in servicios" :key="s.id" class="card">
          <div class="card-name">{{ s.nombre }}</div>
          <div class="card-desc">{{ s.descripcion || $t('estilista.servicios.noDescription') }}</div>
          <div class="card-footer">
            <span class="card-precio">{{ formatCurrency(s.precio) }}</span>
            <span class="card-duracion">{{ s.duracion_minutos }} {{ $t('common.minutes') }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const { t } = useI18n()
const { formatCurrency } = useLocale()
const authStore = useAuthStore()
const loading = ref(false)
const error = ref(null)
const servicios = ref([])
const data = ref({})

async function load() {
  loading.value = true
  try {
    const res = await api.get('/estilista/servicios/')
    servicios.value = res.data || []
    data.value.peluqueria = authStore.user?.peluqueria?.nombre || ''
  } catch (e) {
    error.value = e.response?.data?.detail || t('estilista.servicios.loadError')
    console.error(e)
  } finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.sucursal-tag { padding: 0.2rem 0.55rem; background: #121820; border: 1px solid #1a2530; border-radius: 4px; font-size: 0.72rem; color: #5a8fbf; font-weight: 500; }
.empty-state { padding: 2.5rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }
.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.75rem; }
.card { padding: 1rem 1.15rem; background: #141414; border: 1px solid #1e1e1e; border-radius: 10px; display: flex; flex-direction: column; gap: 0.3rem; }
.card-name { font-size: 0.9rem; color: #e8e8e8; font-weight: 500; }
.card-desc { font-size: 0.78rem; color: #666; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 0.3rem; }
.card-precio { font-size: 0.9rem; font-weight: 600; color: #e8e8e8; }
.card-duracion { font-size: 0.75rem; color: #666; }
@media (max-width: 768px) { .page { padding: 1rem; } .cards-grid { grid-template-columns: 1fr; } }
</style>