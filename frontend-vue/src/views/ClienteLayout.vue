<template>
  <div class="layout">
    <!-- HEADER -->
    <header class="header">
      <div class="header-left">
        <router-link to="/cliente" class="logo">SGCP</router-link>
        <span class="role-badge role-cliente">{{ $t('cliente.role') }}</span>
      </div>
      <div class="header-right">
        <LocaleSwitcher />
        <span class="user-name">{{ authStore.userName }}</span>
        <button @click="handleLogout" class="btn-logout">{{ $t('cliente.logout') }}</button>
      </div>
    </header>

    <!-- NAV -->
    <nav class="nav">
      <div class="nav-inner">
        <router-link to="/cliente" class="nav-link" exact-active-class="active">
          <span class="nav-icon">P</span> {{ $t('cliente.nav.panel') }}
        </router-link>
        <router-link to="/cliente/mis-citas" class="nav-link" active-class="active">
          <span class="nav-icon">C</span> {{ $t('cliente.nav.misCitas') }}
        </router-link>
        <router-link to="/cliente/reservar" class="nav-link" active-class="active">
          <span class="nav-icon">+</span> {{ $t('cliente.nav.reservar') }}
        </router-link>
        <router-link to="/cliente/servicios" class="nav-link" active-class="active">
          <span class="nav-icon">✂</span> {{ $t('cliente.nav.servicios') }}
        </router-link>
        <router-link to="/cliente/estilistas" class="nav-link" active-class="active">
          <span class="nav-icon">E</span> {{ $t('cliente.nav.estilistas') }}
        </router-link>
      </div>
    </nav>

    <!-- CONTENT -->
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import LocaleSwitcher from '@/components/LocaleSwitcher.vue'

const { t: _t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: #0c0c0c;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid #1a1a1a;
  position: sticky;
  top: 0;
  background: #0c0c0c;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  font-size: 0.95rem;
  font-weight: 700;
  color: #e8e8e8;
  text-decoration: none;
}

.role-badge {
  padding: 0.2rem 0.55rem;
  background: #121a14;
  border: 1px solid #1a2a1e;
  border-radius: 4px;
  font-size: 0.7rem;
  color: #5fa868;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-name { font-size: 0.8rem; color: #888; }

.btn-logout {
  padding: 0.35rem 0.75rem;
  background: none;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  color: #888;
  font-size: 0.8rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-logout:hover { color: #c47a7a; border-color: #3a2222; }

/* ===== NAV ===== */
.nav {
  border-bottom: 1px solid #1a1a1a;
  background: #0e0e0e;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.nav-inner {
  display: flex;
  gap: 0.25rem;
  padding: 0 1.5rem;
  max-width: 800px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.65rem 0.85rem;
  color: #666;
  text-decoration: none;
  font-size: 0.78rem;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.15s;
  white-space: nowrap;
}

.nav-link:hover { color: #bbb; }

.nav-link.active {
  color: #e8e8e8;
  border-bottom-color: #5fa868;
}

.nav-icon {
  font-size: 0.85rem;
}

.content {
  padding: 1.5rem;
}

@media (max-width: 640px) {
  .header { padding: 0.65rem 1rem; }
  .content { padding: 1rem; }
  .user-name { display: none; }
  .nav-inner { padding: 0 1rem; }
  .nav-link { padding: 0.6rem 0.65rem; font-size: 0.75rem; }
}
</style>