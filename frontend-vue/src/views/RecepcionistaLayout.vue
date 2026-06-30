<template>
  <div class="layout">
    <!-- HEADER -->
    <header class="header">
      <div class="header-left">
        <button class="menu-btn" @click="sidebarOpen = !sidebarOpen">
          <span class="menu-icon">&#9776;</span>
        </button>
        <span class="logo">SGCP</span>
        <span class="role-badge role-recep">{{ $t('recepcionista.role') }}</span>
      </div>
      <div class="header-right">
        <span class="user-name">{{ authStore.userName }}</span>
        <LocaleSwitcher />
        <button @click="handleLogout" class="btn-logout">{{ $t('recepcionista.logout') }}</button>
      </div>
    </header>

    <!-- BODY ROW: sidebar + content -->
    <div class="body-row">
      <aside :class="['sidebar', { open: sidebarOpen }]">
        <nav class="nav">
          <router-link to="/recepcionista" class="nav-item" exact-active-class="active" @click="sidebarOpen = false">
            <span class="nav-icon">&#9632;</span>
            <span>{{ $t('recepcionista.nav.panel') }}</span>
          </router-link>
          <router-link to="/recepcionista/citas" class="nav-item" active-class="active" @click="sidebarOpen = false">
            <span class="nav-icon">&#9638;</span>
            <span>{{ $t('recepcionista.nav.citas') }}</span>
          </router-link>
          <router-link to="/recepcionista/citas/crear" class="nav-item" active-class="active" @click="sidebarOpen = false">
            <span class="nav-icon">+</span>
            <span>{{ $t('recepcionista.nav.crearCita') }}</span>
          </router-link>
          <router-link to="/recepcionista/calendario" class="nav-item" active-class="active" @click="sidebarOpen = false">
            <span class="nav-icon">&#9638;</span>
            <span>{{ $t('recepcionista.nav.agenda') }}</span>
          </router-link>
          <router-link to="/recepcionista/clientes" class="nav-item" active-class="active" @click="sidebarOpen = false">
            <span class="nav-icon">&#9679;</span>
            <span>{{ $t('recepcionista.nav.clientes') }}</span>
          </router-link>
          <router-link to="/recepcionista/servicios" class="nav-item" active-class="active" @click="sidebarOpen = false">
            <span class="nav-icon">&#9733;</span>
            <span>{{ $t('recepcionista.nav.servicios') }}</span>
          </router-link>
        </nav>
      </aside>

      <!-- OVERLAY (mobile) -->
      <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

      <!-- CONTENT -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/composables/useLocale'
import LocaleSwitcher from '@/components/LocaleSwitcher.vue'

const { t } = useI18n()
useLocale()

const router = useRouter()
const authStore = useAuthStore()
const sidebarOpen = ref(false)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout { min-height: 100vh; background: #0c0c0c; display: flex; flex-direction: column; }

/* ===== HEADER ===== */
.header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.75rem 1.5rem; border-bottom: 1px solid #1a1a1a;
  background: #0c0c0c; z-index: 50; position: sticky; top: 0;
}
.header-left { display: flex; align-items: center; gap: 0.75rem; }
.menu-btn { display: none; background: none; border: none; color: #888; font-size: 1.2rem; cursor: pointer; padding: 0.2rem; }
.logo { font-size: 0.95rem; font-weight: 700; color: #e8e8e8; }
.role-badge { padding: 0.2rem 0.55rem; background: #122218; border: 1px solid #1a3020; border-radius: 4px; font-size: 0.7rem; color: #5fa868; font-weight: 500; }
.role-recep { background: #122218; border-color: #1a3020; color: #5fa868; }
.header-right { display: flex; align-items: center; gap: 1rem; }
.user-name { font-size: 0.8rem; color: #888; }
.btn-logout { padding: 0.35rem 0.75rem; background: none; border: 1px solid #2a2a2a; border-radius: 6px; color: #888; font-size: 0.8rem; font-family: inherit; cursor: pointer; transition: all 0.15s; }
.btn-logout:hover { color: #c47a7a; border-color: #3a2222; }

/* ===== BODY ROW ===== */
.body-row { display: flex; flex: 1; min-height: 0; }

/* ===== SIDEBAR ===== */
.sidebar {
  width: 200px; flex-shrink: 0;
  border-right: 1px solid #1a1a1a;
  background: #0e0e0e;
  padding: 0.75rem 0;
  overflow-y: auto;
}
.nav { display: flex; flex-direction: column; gap: 0.15rem; padding: 0 0.5rem; }
.nav-item {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.55rem 0.75rem; border-radius: 6px;
  color: #666; font-size: 0.8rem; text-decoration: none;
  transition: all 0.12s;
}
.nav-item:hover { background: #161616; color: #bbb; }
.nav-item.active { background: #1a1a1a; color: #e8e8e8; font-weight: 500; }
.nav-icon { font-size: 0.85rem; width: 18px; text-align: center; flex-shrink: 0; }

/* ===== CONTENT ===== */
.content { flex: 1; min-width: 0; }

/* ===== MOBILE ===== */
.sidebar-overlay { display: none; }

@media (max-width: 768px) {
  .menu-btn { display: block; }
  .user-name { display: none; }
  .sidebar {
    position: fixed; top: 0; left: 0; bottom: 0; z-index: 100;
    transform: translateX(-100%); transition: transform 0.25s ease;
  }
  .sidebar.open { transform: translateX(0); }
  .sidebar-overlay { display: block; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 99; }
}
</style>
