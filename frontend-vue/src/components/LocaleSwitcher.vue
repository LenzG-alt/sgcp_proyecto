<template>
  <div class="locale-switcher">
    <div class="locale-dropdown" @click="isOpen = !isOpen" :title="$t('locale.selectRegion')">
      <span class="locale-flag">{{ currentFlag }}</span>
      <span class="locale-label">{{ currentLabel }}</span>
      <span v-if="currentTime" class="locale-time">{{ currentTime }}</span>
      <svg class="locale-arrow" :class="{ open: isOpen }" width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <Transition name="dropdown">
      <div v-if="isOpen" class="locale-menu">
        <button
          v-for="loc in locales"
          :key="loc.key"
          class="locale-option"
          :class="{ active: region === loc.key }"
          @click="changeRegion(loc.key)"
        >
          <span class="locale-flag">{{ loc.flag }}</span>
          <div class="locale-option-info">
            <span class="locale-name">{{ loc.label }}</span>
            <span class="locale-tz">{{ loc.timezoneLabel }}</span>
          </div>
          <span class="locale-currency">{{ loc.currency }}</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocaleByRegion } from '@/i18n'
import { useLocale } from '@/composables/useLocale'

const { t } = useI18n()
const { region, setRegion, formatCurrentTime, timezoneAbbr, utcOffset } = useLocale()

const isOpen = ref(false)
const currentTime = ref('')
let timeInterval = null

const locales = [
  { key: 'es-PE', flag: '🇵🇪', label: t('locale.peru'), currency: 'S/.', timezoneLabel: 'UTC-5  Lima' },
  { key: 'en-US', flag: '🇺🇸', label: t('locale.usa'), currency: '$', timezoneLabel: 'UTC-5/-4  New York' },
  { key: 'pt-BR', flag: '🇧🇷', label: t('locale.brazil'), currency: 'R$', timezoneLabel: 'UTC-3  Sao Paulo' },
]

const currentFlag = computed(() => {
  const loc = locales.find(l => l.key === region.value)
  return loc ? loc.flag : '🇵🇪'
})

const currentLabel = computed(() => {
  const loc = locales.find(l => l.key === region.value)
  return loc ? loc.label : 'Peru'
})

function changeRegion(key) {
  setLocaleByRegion(key)
  setRegion(key)
  // Guardar region para los headers de timezone en la API
  localStorage.setItem('locale_region', key)
  isOpen.value = false
  // Reload to apply all changes
  window.location.reload()
}

function updateClock() {
  currentTime.value = formatCurrentTime()
}

function handleClickOutside(e) {
  const el = e.target.closest('.locale-switcher')
  if (!el) isOpen.value = false
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  updateClock()
  timeInterval = setInterval(updateClock, 30000) // update every 30s
})
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style scoped>
.locale-switcher {
  position: relative;
  display: inline-flex;
}

.locale-dropdown {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  background: rgba(255,255,255,0.08);
  color: #fff;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s, border-color 0.2s;
  user-select: none;
}

.locale-dropdown:hover {
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.35);
}

.locale-flag {
  font-size: 18px;
  line-height: 1;
}

.locale-label {
  font-weight: 500;
}

.locale-arrow {
  transition: transform 0.2s;
  opacity: 0.7;
}

.locale-arrow.open {
  transform: rotate(180deg);
}

.locale-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 200px;
  background: #1e293b;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 10px;
  padding: 6px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.4);
  z-index: 1000;
}

.locale-option {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #e2e8f0;
  cursor: pointer;
  font-size: 14px;
  text-align: left;
  transition: background 0.15s;
}

.locale-option:hover {
  background: rgba(255,255,255,0.1);
}

.locale-option.active {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
}

.locale-flag {
  font-size: 20px;
}

.locale-name {
  flex: 1;
}

.locale-currency {
  font-size: 12px;
  opacity: 0.6;
  font-weight: 500;
}

.locale-time {
  font-size: 11px;
  opacity: 0.7;
  font-variant-numeric: tabular-nums;
  margin-right: 4px;
}

.locale-option-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.locale-tz {
  font-size: 11px;
  opacity: 0.5;
}

/* Transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>