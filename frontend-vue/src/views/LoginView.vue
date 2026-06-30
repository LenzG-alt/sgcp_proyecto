<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
          <router-link to="/" class="back-link">&larr; {{ $t('common.back') }}</router-link>
          <LocaleSwitcher />
        </div>
        <div class="logo-area">
          <span class="logo-icon">&#9986;</span>
          <h1>{{ $t('login.brand') }}</h1>
          <p>{{ $t('login.title') }}</p>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="field">
          <label for="username">{{ $t('login.usernameLabel') }}</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="tu_usuario"
            required
            autocomplete="username"
            autofocus
          />
        </div>

        <div class="field">
          <label for="password">{{ $t('login.passwordLabel') }}</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;"
            required
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="btn-login" :disabled="authStore.loading">
          <span v-if="authStore.loading" class="loader"></span>
          {{ authStore.loading ? $t('login.submitting') : $t('login.submit') }}
        </button>

        <p v-if="authStore.error" class="error">{{ authStore.error }}</p>
      </form>

      <div class="login-footer">
        <span>{{ $t('login.noAccount') }}</span>
        <router-link to="/registro" class="link">{{ $t('login.registerHere') }}</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LocaleSwitcher from '@/components/LocaleSwitcher.vue'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')

const handleSubmit = async () => {
  try {
    await authStore.login(username.value, password.value)
    // El router redirige automaticamente segun el rol
    // gracias al navigation guard
    const rol = authStore.userRol
    switch (rol) {
      case 'administrador': router.push('/admin'); break
      case 'estilista': router.push('/estilista'); break
      case 'recepcionista': router.push('/recepcionista'); break
      default: router.push('/')
    }
  } catch (e) {
    // Error manejado en el store
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0c0c0c;
  padding: 1.5rem;
}

.login-card {
  width: 100%;
  max-width: 380px;
}

.login-header {
  margin-bottom: 2rem;
}

.back-link {
  display: inline-block;
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 2rem;
  transition: color 0.15s;
}

.back-link:hover {
  color: #ccc;
}

.logo-area {
  text-align: center;
}

.logo-icon {
  display: block;
  font-size: 1.5rem;
  margin-bottom: 0.75rem;
  opacity: 0.6;
}

.logo-area h1 {
  font-size: 1.6rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0 0 0.35rem;
}

.logo-area p {
  font-size: 0.85rem;
  color: #666;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.field {
  margin-bottom: 1.15rem;
}

label {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
  color: #888;
  margin-bottom: 0.4rem;
}

input {
  width: 100%;
  padding: 0.7rem 0.85rem;
  background: #161616;
  border: 1px solid #252525;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 0.9rem;
  font-family: inherit;
  transition: border-color 0.15s;
}

input::placeholder { color: #444; }
input:focus { outline: none; border-color: #555; }

.btn-login {
  width: 100%;
  padding: 0.75rem;
  margin-top: 0.5rem;
  background: #e8e8e8;
  color: #0c0c0c;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: opacity 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-login:hover { opacity: 0.85; }
.btn-login:disabled { opacity: 0.4; cursor: not-allowed; }

.loader {
  width: 14px;
  height: 14px;
  border: 1.5px solid transparent;
  border-top-color: #0c0c0c;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.error {
  margin-top: 1rem;
  padding: 0.65rem 0.85rem;
  background: #1a1212;
  border: 1px solid #2a1a1a;
  border-radius: 8px;
  color: #c47a7a;
  font-size: 0.825rem;
}

.login-footer {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.8rem;
  color: #555;
}

.link {
  color: #a78bfa;
  margin-left: 0.3rem;
  transition: opacity 0.15s;
}

.link:hover {
  opacity: 0.8;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>