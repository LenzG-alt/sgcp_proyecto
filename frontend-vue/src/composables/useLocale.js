/**
 * useLocale composable — locale-aware formatting for currency, dates, times, and numbers.
 *
 * Reads the current region from localStorage and provides formatters
 * that adapt to Peru (es-PE), USA (en-US), or Brazil (pt-BR).
 *
 * TIMEZONE SUPPORT:
 * - All date/time formatters use the `timeZone` option from Intl API
 * - UTC datetimes from the backend are converted to the local timezone
 * - The API sends X-Timezone header so the backend also responds in the correct timezone
 * - server_time from locale-config endpoint shows current time in locale's timezone
 */

import { computed, ref } from 'vue'
import { getCurrentRegion } from '@/i18n'

const LOCALE_CONFIGS = {
  'es-PE': {
    currencyCode: 'PEN',
    currencySymbol: 'S/.',
    currencyPosition: 'prefix',
    dateLocale: 'es-PE',
    numberLocale: 'es-PE',
    dateFormat: { day: '2-digit', month: '2-digit', year: 'numeric' },
    dateTimeFormat: { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' },
    timeFormat: { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' },
    timezone: 'America/Lima',
  },
  'en-US': {
    currencyCode: 'USD',
    currencySymbol: '$',
    currencyPosition: 'prefix',
    dateLocale: 'en-US',
    numberLocale: 'en-US',
    dateFormat: { day: '2-digit', month: '2-digit', year: 'numeric' },
    dateTimeFormat: { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' },
    timeFormat: { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' },
    timezone: 'America/New_York',
  },
  'pt-BR': {
    currencyCode: 'BRL',
    currencySymbol: 'R$',
    currencyPosition: 'prefix',
    dateLocale: 'pt-BR',
    numberLocale: 'pt-BR',
    dateFormat: { day: '2-digit', month: '2-digit', year: 'numeric' },
    dateTimeFormat: { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' },
    timeFormat: { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' },
    timezone: 'America/Sao_Paulo',
  },
}

// Reactive region that triggers recomputation when changed
const currentRegion = ref(getCurrentRegion())

// Cache for server time info (updated from locale-config endpoint)
const serverTimeInfo = ref(null)

export function useLocale() {
  const config = computed(() => LOCALE_CONFIGS[currentRegion.value] || LOCALE_CONFIGS['es-PE'])

  /**
   * Get the IANA timezone name for the current locale.
   * @returns {string} e.g. 'America/Lima', 'America/New_York', 'America/Sao_Paulo'
   */
  const timezone = computed(() => config.value.timezone)

  /**
   * Get the UTC offset string for the current timezone.
   * Calculated dynamically using Intl API (handles DST).
   * @returns {string} e.g. '-05:00', '-04:00', '-03:00'
   */
  const utcOffset = computed(() => {
    try {
      const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: config.value.timezone,
        timeZoneName: 'shortOffset',
      })
      const parts = formatter.formatToParts(new Date())
      const tzPart = parts.find(p => p.type === 'timeZoneName')
      if (tzPart) {
        // "GMT-5" → "-05:00", "GMT-3" → "-03:00", "GMT+5" → "+05:00"
        const match = tzPart.value.match(/GMT([+-]?)(\d{1,2})(?::(\d{2}))?/)
        if (match) {
          const sign = match[1] || '+'
          const hours = match[2].padStart(2, '0')
          const mins = match[3] || '00'
          return `${sign}${hours}:${mins}`
        }
      }
    } catch {
      // fallback
    }
    // Manual mapping as fallback
    const offsetMap = { 'America/Lima': '-05:00', 'America/New_York': '-05:00', 'America/Sao_Paulo': '-03:00' }
    return offsetMap[config.value.timezone] || '+00:00'
  })

  /**
   * Format a number as currency for the current locale.
   * @param {number} amount
   * @returns {string} e.g. "S/. 25.00", "$25.00", "R$ 25,00"
   */
  function formatCurrency(amount) {
    if (amount == null) return ''
    try {
      return new Intl.NumberFormat(config.value.numberLocale, {
        style: 'currency',
        currency: config.value.currencyCode,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(amount)
    } catch {
      const formatted = Number(amount).toFixed(2)
      return `${config.value.currencySymbol} ${formatted}`
    }
  }

  /**
   * Format a Date object or date string for the current locale.
   * Uses the locale's timezone to display the date correctly.
   *
   * @param {Date|string} date - Date object or ISO string (UTC)
   * @param {object} options - Override Intl options
   * @returns {string}
   */
  function formatDate(date, options) {
    if (!date) return ''
    const d = typeof date === 'string' ? new Date(date) : date
    if (isNaN(d.getTime())) return ''
    try {
      const opts = {
        timeZone: config.value.timezone,
        ...(options || config.value.dateFormat),
      }
      return d.toLocaleDateString(config.value.dateLocale, opts)
    } catch {
      return d.toISOString().split('T')[0]
    }
  }

  /**
   * Format a time string (HH:MM) for the current locale.
   * Combines the time with today's date and converts to locale timezone.
   *
   * @param {string} timeStr - e.g. "14:00"
   * @param {boolean} showTimezoneName - whether to show timezone abbreviation
   * @returns {string}
   */
  function formatTime(timeStr, showTimezoneName = false) {
    if (!timeStr) return ''
    try {
      // Parse the time and attach to today's date
      const [h, m] = timeStr.split(':')
      const d = new Date()
      d.setHours(parseInt(h), parseInt(m), 0, 0)

      const opts = {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: config.value.timezone,
      }
      if (showTimezoneName) {
        opts.timeZoneName = 'short'
      }
      return d.toLocaleTimeString(config.value.dateLocale, opts)
    } catch {
      return timeStr
    }
  }

  /**
   * Format a date with time for the current locale.
   * Converts the datetime to the locale's timezone before formatting.
   *
   * @param {Date|string} date - Date object or ISO datetime string (UTC)
   * @param {string} timeStr - optional separate time string "HH:MM"
   * @returns {string}
   */
  function formatDateTime(date, timeStr) {
    if (!date) return ''
    const d = typeof date === 'string' ? new Date(date) : date
    if (isNaN(d.getTime())) return ''
    try {
      // If we have a separate time string, combine it
      if (timeStr && typeof date === 'string') {
        const [h, m] = timeStr.split(':')
        d.setHours(parseInt(h) || 0, parseInt(m) || 0, 0, 0)
      }

      return d.toLocaleString(config.value.dateLocale, {
        ...config.value.dateTimeFormat,
        timeZone: config.value.timezone,
      })
    } catch {
      return date
    }
  }

  /**
   * Format a number for the current locale.
   * @param {number} num
   * @returns {string}
   */
  function formatNumber(num) {
    if (num == null) return ''
    try {
      return new Intl.NumberFormat(config.value.numberLocale).format(num)
    } catch {
      return String(num)
    }
  }

  /**
   * Convert a UTC datetime string to the locale's timezone and return
   * a formatted string showing date, time, and timezone.
   *
   * This is the main function for displaying server datetimes.
   *
   * @param {string} utcString - ISO datetime string from the API
   * @param {object} options - Intl format options override
   * @returns {string} Formatted datetime in locale timezone
   */
  function formatUTCDateTime(utcString, options) {
    if (!utcString) return ''
    const d = new Date(utcString)
    if (isNaN(d.getTime())) return ''
    try {
      return d.toLocaleString(config.value.dateLocale, {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: config.value.timezone,
        ...(options || {}),
      })
    } catch {
      return utcString
    }
  }

  /**
   * Get the current time in the locale's timezone.
   * Useful for showing "now" in the correct timezone.
   *
   * @returns {string} Current time formatted in locale timezone
   */
  function formatCurrentTime() {
    try {
      return new Date().toLocaleTimeString(config.value.dateLocale, {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: config.value.timezone,
        timeZoneName: 'short',
      })
    } catch {
      return ''
    }
  }

  /**
   * Get the current date in the locale's timezone.
   * @returns {string} Current date formatted in locale timezone
   */
  function formatCurrentDate() {
    try {
      return new Date().toLocaleDateString(config.value.dateLocale, {
        ...config.value.dateFormat,
        timeZone: config.value.timezone,
      })
    } catch {
      return ''
    }
  }

  /**
   * Get the timezone abbreviation for the current locale.
   * e.g. "PET" (Peru Time), "EDT/EST" (Eastern), "BRT" (Brasilia Time)
   * @returns {string}
   */
  const timezoneAbbr = computed(() => {
    try {
      const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: config.value.timezone,
        timeZoneName: 'short',
      })
      const parts = formatter.formatToParts(new Date())
      const tzPart = parts.find(p => p.type === 'timeZoneName')
      return tzPart ? tzPart.value : ''
    } catch {
      return ''
    }
  })

  /**
   * Get the currency symbol for the current locale.
   */
  const currencySymbol = computed(() => config.value.currencySymbol)

  /**
   * Get the current region key.
   */
  const region = computed(() => currentRegion.value)

  /**
   * Update server time info from locale-config API response.
   * @param {object} serverTime - The server_time object from the API
   */
  function setServerTimeInfo(serverTime) {
    serverTimeInfo.value = serverTime
  }

  /**
   * Get the server time info (from last API call to locale-config).
   */
  const serverTime = computed(() => serverTimeInfo.value)

  /**
   * Change the region and update reactive state.
   * Call this after setLocaleByRegion to update computed values.
   */
  function setRegion(newRegion) {
    if (LOCALE_CONFIGS[newRegion]) {
      currentRegion.value = newRegion
    }
  }

  return {
    region,
    timezone,
    utcOffset,
    timezoneAbbr,
    currencySymbol,
    serverTime,
    formatCurrency,
    formatDate,
    formatTime,
    formatDateTime,
    formatNumber,
    formatUTCDateTime,
    formatCurrentTime,
    formatCurrentDate,
    setRegion,
    setServerTimeInfo,
  }
}