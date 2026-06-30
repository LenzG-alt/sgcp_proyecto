<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ $t('estilista.perfil.title') }}</h1>
    </div>

    <div v-if="loading" class="empty-state">{{ $t('estilista.perfil.loading') }}</div>
    <template v-else>
      <form @submit.prevent="guardar" class="form" v-if="form">
        <div class="field">
          <label>{{ $t('estilista.perfil.nombre') }}</label>
          <input v-model="form.first_name" :placeholder="$t('estilista.perfil.nombrePlaceholder')" />
        </div>
        <div class="field">
          <label>{{ $t('estilista.perfil.apellido') }}</label>
          <input v-model="form.last_name" :placeholder="$t('estilista.perfil.apellidoPlaceholder')" />
        </div>
        <div class="field">
          <label>{{ $t('estilista.perfil.especialidad') }}</label>
          <input v-model="form.especialidad" :placeholder="$t('estilista.perfil.especialidadPlaceholder')" />
        </div>
        <div class="field">
          <label>{{ $t('estilista.perfil.telefono') }}</label>
          <input v-model="form.telefono" :placeholder="$t('estilista.perfil.telefonoPlaceholder')" />
        </div>

        <div v-if="formErrors.length" class="form-errors">
          <p v-for="(e, i) in formErrors" :key="i">{{ e }}</p>
        </div>

        <div v-if="saved" class="form-success">
          <p>{{ $t('estilista.perfil.success') }}</p>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? $t('estilista.perfil.saving') : $t('estilista.perfil.save') }}</button>
        </div>
      </form>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const { t } = useI18n()
const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const saved = ref(false)
const formErrors = ref([])

const form = ref(null)

async function loadProfile() {
  loading.value = true
  try {
    const res = await api.get('/perfil/')
    const u = res.data
    form.value = {
      first_name: u.first_name || '',
      last_name: u.last_name || '',
      especialidad: u.especialidad || '',
      telefono: u.telefono || '',
    }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function guardar() {
  formErrors.value = []; saving.value = true; saved.value = false
  try {
    const res = await api.patch('/estilista/perfil/', {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      especialidad: form.value.especialidad,
      telefono: form.value.telefono,
    })
    saved.value = true
    // Actualizar store
    if (authStore.user) {
      authStore.user.first_name = res.data.first_name
      authStore.user.last_name = res.data.last_name
      authStore.user.especialidad = res.data.especialidad
      authStore.user.telefono = res.data.telefono
    }
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e) {
    if (e.response?.data) formErrors.value = Object.values(e.response.data).flat()
    else formErrors.value = [t('estilista.perfil.saveError')]
  } finally { saving.value = false }
}

onMounted(loadProfile)
</script>

<style scoped>
.page { padding: 1.5rem; background: #0c0c0c; min-height: 100vh; color: #ccc; font-family: 'Inter', system-ui, sans-serif; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.1rem; font-weight: 600; color: #e8e8e8; margin: 0; }
.form { max-width: 480px; }
.field { margin-bottom: 1rem; }
.field label { display: block; font-size: 0.75rem; font-weight: 500; color: #888; margin-bottom: 0.3rem; }
.field input { width: 100%; padding: 0.5rem 0.7rem; background: #161616; border: 1px solid #252525; border-radius: 8px; color: #e8e8e8; font-size: 0.85rem; font-family: inherit; box-sizing: border-box; }
.field input:focus { outline: none; border-color: #555; }
.form-errors { padding: 0.6rem 0.75rem; background: #1a1212; border: 1px solid #2a1a1a; border-radius: 8px; margin-bottom: 0.75rem; }
.form-errors p { margin: 0; padding: 0.15rem 0; color: #c47a7a; font-size: 0.8rem; }
.form-success { padding: 0.6rem 0.75rem; background: #122218; border: 1px solid #1a3020; border-radius: 8px; margin-bottom: 0.75rem; }
.form-success p { margin: 0; color: #5fa868; font-size: 0.8rem; }
.form-actions { margin-top: 0.5rem; }
.btn-primary { padding: 0.5rem 1rem; background: #e8e8e8; color: #0c0c0c; border: none; border-radius: 8px; font-size: 0.8rem; font-weight: 600; font-family: inherit; cursor: pointer; transition: opacity 0.15s; }
.btn-primary:hover { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.empty-state { padding: 2.5rem 1rem; text-align: center; color: #555; font-size: 0.85rem; }
@media (max-width: 768px) { .page { padding: 1rem; } }
</style>