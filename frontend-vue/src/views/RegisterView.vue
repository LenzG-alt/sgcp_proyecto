<template>
  <div class="register-page">
    <div class="register-card">
      <div class="register-header">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <router-link to="/" class="back-link">&larr; {{ $t('common.back') }}</router-link>
          <LocaleSwitcher />
        </div>
        <div class="logo-area">
          <span class="logo-icon">&#9986;</span>
          <h1>{{ $t('register.title') }}</h1>
          <p>{{ $t('register.subtitle') }}</p>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="register-form">
        <div class="field">
          <label for="username">{{ $t('register.username') }}</label>
          <input id="username" v-model="form.username" type="text" placeholder="tu_usuario" required autocomplete="username" />
        </div>

        <div class="field">
          <label for="email">{{ $t('register.email') }}</label>
          <input id="email" v-model="form.email" type="email" placeholder="tu@email.com" required autocomplete="email" />
        </div>

        <div class="row">
          <div class="field">
            <label for="first_name">{{ $t('register.firstName') }}</label>
            <input id="first_name" v-model="form.first_name" type="text" placeholder="Juan" required />
          </div>
          <div class="field">
            <label for="last_name">{{ $t('register.lastName') }}</label>
            <input id="last_name" v-model="form.last_name" type="text" placeholder="Garcia" required />
          </div>
        </div>

        <div class="field">
          <label for="telefono">{{ $t('register.phone') }}</label>
          <input id="telefono" v-model="form.telefono" type="tel" placeholder="+51 999 888 777" />
        </div>

        <div class="row">
          <div class="field">
            <label for="password">{{ $t('register.password') }}</label>
            <input id="password" v-model="form.password" type="password" :placeholder="$t('register.passwordHint')" required minlength="6" />
          </div>
          <div class="field">
            <label for="password_confirm">{{ $t('register.confirmPassword') }}</label>
            <input id="password_confirm" v-model="form.password_confirm" type="password" :placeholder="$t('register.confirmPasswordHint')" required />
          </div>
        </div>

        <button type="submit" class="btn-register" :disabled="authStore.loading">
          <span v-if="authStore.loading" class="loader"></span>
          {{ authStore.loading ? $t('register.submitting') : $t('register.submit') }}
        </button>

        <p v-if="authStore.error" class="error">{{ authStore.error }}</p>
      </form>

      <div class="register-footer">
        <span>{{ $t('register.haveAccount') }}</span>
        <router-link to="/login" class="link">{{ $t('register.loginHere') }}</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import LocaleSwitcher from '@/components/LocaleSwitcher.vue'

const { t } = useI18n()

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  telefono: '',
  password: '',
  password_confirm: '',
})

const handleSubmit = async () => {
  if (form.password !== form.password_confirm) {
    authStore.error = t('register.passwordMismatch')
    return
  }

  try {
    await authStore.register(form)
    // Cliente registrado: ir a landing o al panel segun rol
    router.push('/')
  } catch (e) {
    // Error manejado en el store
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0c0c0c;
  padding: 1.5rem;
}

.register-card {
  width: 100%;
  max-width: 440px;
}

.register-header {
  margin-bottom: 2rem;
}

.back-link {
  display: inline-block;
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 1.5rem;
  transition: color 0.15s;
}
.back-link:hover { color: #ccc; }

.logo-area { text-align: center; }
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

.register-form { display: flex; flex-direction: column; }

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.field { margin-bottom: 1rem; }

label {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
  color: #888;
  margin-bottom: 0.35rem;
}

input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  background: #161616;
  border: 1px solid #252525;
  border-radius: 8px;
  color: #e8e8e8;
  font-size: 0.875rem;
  font-family: inherit;
  transition: border-color 0.15s;
}
input::placeholder { color: #444; }
input:focus { outline: none; border-color: #555; }

.btn-register {
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
.btn-register:hover { opacity: 0.85; }
.btn-register:disabled { opacity: 0.4; cursor: not-allowed; }

.loader {
  width: 14px; height: 14px;
  border: 1.5px solid transparent;
  border-top-color: #0c0c0c;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.error {
  margin-top: 0.75rem;
  padding: 0.6rem 0.85rem;
  background: #1a1212;
  border: 1px solid #2a1a1a;
  border-radius: 8px;
  color: #c47a7a;
  font-size: 0.825rem;
}

.register-footer {
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
.link:hover { opacity: 0.8; }

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .row { grid-template-columns: 1fr; }
}
</style>