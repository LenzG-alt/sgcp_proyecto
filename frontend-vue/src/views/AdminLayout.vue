<template>
  <div class="layout">
    <!-- HEADER -->
    <header class="header">
      <div class="header-left">
        <span class="logo">SGCP</span>
        <span class="role-badge">{{ $t('admin.role') }}</span>
      </div>
      <div class="header-right">
        <LocaleSwitcher />
        <span class="user-name">{{ authStore.userName }}</span>
        <button @click="handleLogout" class="btn-logout">{{ $t('admin.logout') }}</button>
      </div>
    </header>

    <!-- NAV -->
    <nav class="nav">
      <router-link to="/admin" class="nav-link" exact-active-class="active">
        <span class="nav-icon">&#9632;</span> {{ $t('admin.nav.dashboard') }}
      </router-link>
      <router-link to="/admin/peluquerias" class="nav-link" active-class="active">
        <span class="nav-icon">&#127970;</span> {{ $t('admin.nav.peluquerias') }}
      </router-link>
      <router-link to="/admin/usuarios" class="nav-link" active-class="active">
        <span class="nav-icon">&#128100;</span> {{ $t('admin.nav.usuarios') }}
      </router-link>
      <router-link to="/admin/estilistas" class="nav-link" active-class="active">
        <span class="nav-icon">&#9986;</span> {{ $t('admin.nav.estilistas') }}
      </router-link>
      <router-link to="/admin/servicios" class="nav-link" active-class="active">
        <span class="nav-icon">&#9733;</span> {{ $t('admin.nav.servicios') }}
      </router-link>
      <router-link to="/admin/citas" class="nav-link" active-class="active">
        <span class="nav-icon">&#128197;</span> {{ $t('admin.nav.citas') }}
      </router-link>
      <router-link to="/admin/horarios" class="nav-link" active-class="active">
        <span class="nav-icon">&#9200;</span> {{ $t('admin.nav.horarios') }}
      </router-link>
    </nav>

    <!-- CONTENT -->
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import LocaleSwitcher from '@/components/LocaleSwitcher.vue'

const { t } = useI18n()
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
}

.role-badge {
  padding: 0.2rem 0.55rem;
  background: #1a1212;
  border: 1px solid #2a1a1a;
  border-radius: 4px;
  font-size: 0.7rem;
  color: #b05a5a;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-name {
  font-size: 0.8rem;
  color: #888;
}

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

.btn-logout:hover {
  color: #c47a7a;
  border-color: #3a2222;
}

.nav {
  display: flex;
  gap: 0;
  padding: 0 1.5rem;
  border-bottom: 1px solid #1a1a1a;
  overflow-x: auto;
}

.nav-link {
  padding: 0.65rem 0.85rem;
  color: #555;
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.15s;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.nav-link:hover { color: #aaa; }
.nav-link.active {
  color: #e8e8e8;
  border-bottom-color: #e8e8e8;
}

.nav-icon {
  font-size: 0.85rem;
  opacity: 0.7;
}

.content {
  padding: 1.5rem;
}

@media (max-width: 640px) {
  .header { padding: 0.65rem 1rem; }
  .nav { padding: 0 1rem; }
  .content { padding: 1rem; }
  .user-name { display: none; }
}
</style>