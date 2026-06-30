<template>
  <div class="landing">
    <div class="locale-switcher-wrapper"><LocaleSwitcher /></div>
    <!-- HERO -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">{{ $t('landing.systemTitle') }}</div>
        <h1 class="hero-title">
          {{ $t('landing.brand1') }}<br><span>{{ $t('landing.brand2') }}</span>
        </h1>
        <p class="hero-subtitle">
          {{ $t('landing.tagline') }}
          {{ $t('landing.subtitle') }}
        </p>
        <div class="hero-actions">
          <router-link to="/login" class="btn btn-primary">{{ $t('landing.login') }}</router-link>
          <router-link to="/registro" class="btn btn-outline">{{ $t('landing.register') }}</router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="card-float card-1">
          <div class="card-icon">&#128197;</div>
          <div>
            <div class="card-label">{{ $t('landing.confirmedAppointment') }}</div>
            <div class="card-sub">Maria Garcia - Corte y color</div>
          </div>
        </div>
        <div class="card-float card-2">
          <div class="card-icon">&#9201;</div>
          <div>
            <div class="card-label">{{ $t('landing.nextAppointment') }}</div>
            <div class="card-sub">Hoy, 14:00 - 15:30</div>
          </div>
        </div>
        <div class="card-float card-3">
          <div class="card-icon">&#9733;</div>
          <div>
            <div class="card-label">{{ $t('landing.satisfaction') }}</div>
            <div class="card-sub">{{ $t('landing.satisfactionScore') }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- SERVICIOS -->
    <section class="section" v-if="servicios.length > 0">
      <div class="section-header">
        <h2>{{ $t('landing.ourServices') }}</h2>
        <p>{{ $t('landing.servicesSubtitle') }}</p>
      </div>
      <div class="services-grid">
        <div v-for="s in servicios" :key="s.id" class="service-card">
          <div class="service-price">{{ formatCurrency(s.precio) }}</div>
          <h3 class="service-name">{{ s.nombre }}</h3>
          <p class="service-desc">{{ s.descripcion || $t('landing.professionalService') }}</p>
          <div class="service-meta">
            <span>{{ s.duracion_minutos }} {{ $t('common.min') }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- PELUQUERIAS -->
    <section class="section" v-if="peluquerias.length > 0">
      <div class="section-header">
        <h2>{{ $t('landing.ourBranches') }}</h2>
        <p>{{ $t('landing.branchesSubtitle') }}</p>
      </div>
      <div class="locations-grid">
        <div v-for="p in peluquerias" :key="p.id" class="location-card">
          <h3>{{ p.nombre }}</h3>
          <p class="location-dir">{{ p.direccion || $t('landing.addressNotAvailable') }}</p>
          <p class="location-tel" v-if="p.telefono">{{ p.telefono }}</p>
          <p class="location-desc" v-if="p.descripcion">{{ p.descripcion }}</p>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <h2>{{ $t('landing.bookNow') }}</h2>
      <p>{{ $t('landing.bookNowSubtitle') }}</p>
      <div class="hero-actions">
        <router-link to="/registro" class="btn btn-primary">{{ $t('landing.createFreeAccount') }}</router-link>
        <router-link to="/login" class="btn btn-ghost">{{ $t('landing.alreadyHaveAccount') }}</router-link>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand">
          <span class="footer-logo">SGCP</span>
          <span>{{ $t('landing.systemTitle') }}</span>
        </div>
        <div class="footer-links">
          <router-link to="/login">{{ $t('landing.login') }}</router-link>
          <router-link to="/registro">{{ $t('landing.register') }}</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import LocaleSwitcher from '@/components/LocaleSwitcher.vue'
import { useLocale } from '@/composables/useLocale'

const { formatCurrency } = useLocale()

const servicios = ref([])
const peluquerias = ref([])

onMounted(async () => {
  try {
    const res = await api.get('/publico/')
    servicios.value = res.data.servicios || []
    peluquerias.value = res.data.peluquerias || []
  } catch (err) {
    // Si falla, la landing se muestra sin datos dinamicos
  }
})
</script>

<style scoped>
.landing {
  min-height: 100vh;
  background: #0c0c0c;
  position: relative;
}

.locale-switcher-wrapper {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  z-index: 10;
}

/* ===== HERO ===== */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 4rem;
  max-width: 1100px;
  margin: 0 auto;
}

.hero-content {
  flex: 1;
  max-width: 520px;
}

.hero-badge {
  display: inline-block;
  padding: 0.35rem 0.85rem;
  background: #1a1a1a;
  border: 1px solid #252525;
  border-radius: 20px;
  font-size: 0.75rem;
  color: #888;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  color: #e8e8e8;
  line-height: 1.1;
  margin: 0 0 1.25rem;
  letter-spacing: -0.03em;
}

.hero-title span {
  background: linear-gradient(135deg, #c9a0dc, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.05rem;
  color: #666;
  line-height: 1.7;
  margin: 0 0 2rem;
}

.hero-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.7rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  font-family: inherit;
  transition: all 0.15s ease;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: #e8e8e8;
  color: #0c0c0c;
}
.btn-primary:hover {
  background: #d4d4d4;
}

.btn-outline {
  background: none;
  border: 1px solid #2a2a2a;
  color: #ccc;
}
.btn-outline:hover {
  border-color: #444;
  color: #fff;
}

.btn-ghost {
  background: none;
  color: #888;
  padding: 0.7rem 1rem;
}
.btn-ghost:hover {
  color: #ccc;
}

/* Hero Visual */
.hero-visual {
  flex: 1;
  max-width: 400px;
  position: relative;
  min-height: 320px;
}

.card-float {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 1rem 1.25rem;
  background: #141414;
  border: 1px solid #1f1f1f;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  animation: float 6s ease-in-out infinite;
}

.card-float .card-icon {
  font-size: 1.5rem;
}

.card-float .card-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #e8e8e8;
}

.card-float .card-sub {
  font-size: 0.75rem;
  color: #666;
  margin-top: 0.15rem;
}

.card-1 { top: 10%; left: 0; animation-delay: 0s; }
.card-2 { top: 45%; right: 0; animation-delay: 2s; }
.card-3 { bottom: 10%; left: 10%; animation-delay: 4s; }

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* ===== SECTIONS ===== */
.section {
  padding: 4rem 2rem;
  max-width: 1100px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0 0 0.5rem;
}

.section-header p {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

/* Services Grid */
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.service-card {
  padding: 1.5rem;
  background: #111;
  border: 1px solid #1a1a1a;
  border-radius: 12px;
  transition: border-color 0.15s;
}

.service-card:hover {
  border-color: #333;
}

.service-price {
  font-size: 1.25rem;
  font-weight: 600;
  color: #a78bfa;
  margin-bottom: 0.5rem;
}

.service-name {
  font-size: 1rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0 0 0.5rem;
}

.service-desc {
  font-size: 0.8rem;
  color: #666;
  line-height: 1.5;
  margin: 0 0 0.75rem;
}

.service-meta {
  font-size: 0.75rem;
  color: #555;
}

/* Locations Grid */
.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.location-card {
  padding: 1.5rem;
  background: #111;
  border: 1px solid #1a1a1a;
  border-radius: 12px;
}

.location-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0 0 0.75rem;
}

.location-dir, .location-tel {
  font-size: 0.8rem;
  color: #888;
  margin: 0 0 0.35rem;
}

.location-desc {
  font-size: 0.8rem;
  color: #555;
  margin: 0.75rem 0 0;
  line-height: 1.5;
}

/* CTA */
.cta-section {
  text-align: center;
  padding: 5rem 2rem;
  border-top: 1px solid #1a1a1a;
}

.cta-section h2 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #e8e8e8;
  margin: 0 0 0.5rem;
}

.cta-section p {
  font-size: 0.9rem;
  color: #666;
  margin: 0 0 2rem;
}

.cta-section .hero-actions {
  justify-content: center;
}

/* Footer */
.footer {
  border-top: 1px solid #1a1a1a;
  padding: 2rem;
}

.footer-content {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #555;
}

.footer-logo {
  font-weight: 700;
  color: #888;
  font-size: 0.9rem;
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-links a {
  font-size: 0.8rem;
  color: #666;
  transition: color 0.15s;
}

.footer-links a:hover {
  color: #e8e8e8;
}

/* Responsive */
@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    text-align: center;
    padding: 3rem 1.5rem;
    gap: 2rem;
  }
  .hero-title { font-size: 2.5rem; }
  .hero-actions { justify-content: center; }
  .hero-visual { display: none; }
  .footer-content { flex-direction: column; text-align: center; }
}
</style>