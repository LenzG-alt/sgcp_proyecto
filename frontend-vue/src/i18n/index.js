import { createI18n } from 'vue-i18n'
import es from './locales/es.json'
import en from './locales/en.json'
import pt from './locales/pt.json'

// Region to locale mapping
const REGION_LOCALE_MAP = {
  'es-PE': 'es',
  'en-US': 'en',
  'pt-BR': 'pt',
}

// Get saved locale from localStorage or default to es-PE (Peru)
const savedRegion = localStorage.getItem('app_region') || 'es-PE'
const savedLocale = REGION_LOCALE_MAP[savedRegion] || 'es'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'es',
  messages: {
    es,
    en,
    pt,
  },
})

export default i18n

export { REGION_LOCALE_MAP }

/**
 * Set the application locale by region key (es-PE, en-US, pt-BR).
 * This changes both the vue-i18n locale and the API Accept-Language header.
 */
export function setLocaleByRegion(region) {
  const locale = REGION_LOCALE_MAP[region]
  if (locale && i18n.global.availableLocales.includes(locale)) {
    i18n.global.locale.value = locale
    localStorage.setItem('app_region', region)
    localStorage.setItem('app_locale', locale)
    localStorage.setItem('locale_region', region)  // For timezone headers

    // Update HTML lang attribute
    document.documentElement.lang = locale === 'pt' ? 'pt-BR' : locale

    // Update API Accept-Language header
    const apiLangMap = { es: 'es', en: 'en', pt: 'pt-br' }
    localStorage.setItem('api_accept_language', apiLangMap[locale] || 'es')
  }
}

/**
 * Get the current region key.
 */
export function getCurrentRegion() {
  return localStorage.getItem('app_region') || 'es-PE'
}