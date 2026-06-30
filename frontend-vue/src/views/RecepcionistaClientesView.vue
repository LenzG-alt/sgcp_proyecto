<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('recepcionista.clientes.title') }}</h1>
    </div>

    <div class="search-bar">
      <input v-model="busqueda" :placeholder="$t('recepcionista.clientes.searchPlaceholder')" class="search-input" />
    </div>

    <div v-if="loading" class="empty-state">{{ $t('recepcionista.clientes.loading') }}</div>
    <div v-else-if="error" class="empty-state error-state">{{ error }}</div>
    <template v-else>
      <div v-if="clientesFiltrados.length === 0" class="empty-state">{{ $t('recepcionista.clientes.noResults') }}</div>
      <ul class="client-list">
        <li v-for="c in clientesFiltrados" :key="c.id" class="client-card">
          <div class="client-avatar">{{ getInitials(c) }}</div>
          <div class="client-info">
            <span class="client-name">{{ c.first_name }} {{ c.last_name }}</span>
            <span class="client-detail">{{ c.email || '—' }}</span>
            <span class="client-detail" v-if="c.telefono">{{ c.telefono }}</span>
          </div>
          <button class="btn-sm" @click="irCrearCita(c)">{{ $t('recepcionista.clientes.schedule') }}</button>
        </li>
      </ul>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'

const { t } = useI18n()
useLocale()

const router = useRouter()
const loading = ref(false)
const error = ref(null)
const clientes = ref([])
const busqueda = ref('')

const clientesFiltrados = computed(() => {
  if (!busqueda.value) return clientes.value
  const q = busqueda.value.toLowerCase()
  return clientes.value.filter(c =>
    ((c.first_name || '') + ' ' + (c.last_name || '')).toLowerCase().includes(q) ||
    (c.email || '').toLowerCase().includes(q) ||
    (c.telefono || '').includes(q)
  )
})

function getInitials(c) {
  const name = ((c.first_name || '') + ' ' + (c.last_name || '')).trim()
  if (!name) return '?'
  const parts = name.split(/\s+/)
  return parts.length >= 2 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : name.substring(0, 2).toUpperCase()
}

function irCrearCita(cliente) {
  router.push({ name: 'recepcionista-crear-cita', query: { cliente: cliente.id, nombre: (cliente.first_name || '') + ' ' + (cliente.last_name || '') } })
}

async function loadClientes() {
  loading.value = true
  try {
    const res = await api.get('/usuarios/?rol=cliente&page_size=100')
    clientes.value = res.data.results || res.data || []
  } catch (e) { error.value = t('recepcionista.clientes.errorLoad'); console.error(e) }
  finally { loading.value = false }
}

onMounted(loadClientes)
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { margin-bottom: 1.25rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.search-bar { margin-bottom: 1.25rem; }
.search-input { width: 100%; max-width: 400px; padding: 0.5rem 0.7rem; background: #161616; border: 1px solid #252525; border-radius: 8px; color: #e8e8e8; font-size: 0.85rem; font-family: inherit; box-sizing: border-box; }
.search-input:focus { outline: none; border-color: #555; }
.empty-state { padding: 2.5rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
.error-state { color: #b05a5a; }
.client-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.client-card { display: flex; align-items: center; gap: 0.85rem; padding: 0.85rem 1rem; background: #141414; border: 1px solid #1e1e1e; border-radius: 10px; transition: border-color 0.15s; }
.client-card:hover { border-color: #2a2a2a; }
.client-avatar { width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: #122218; color: #5fa868; font-size: 0.75rem; font-weight: 600; flex-shrink: 0; }
.client-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.1rem; }
.client-name { font-size: 0.85rem; color: #e8e8e8; font-weight: 500; }
.client-detail { font-size: 0.72rem; color: #666; }
.btn-sm { padding: 0.3rem 0.65rem; background: #1a2a1a; border: 1px solid #1a3020; border-radius: 6px; color: #5fa868; font-size: 0.72rem; font-weight: 500; cursor: pointer; font-family: inherit; transition: opacity 0.15s; flex-shrink: 0; }
.btn-sm:hover { opacity: 0.8; }
@media (max-width: 768px) { .page { padding: 1rem; } }
</style>