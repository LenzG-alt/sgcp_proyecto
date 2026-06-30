"""
Middleware de zona horaria para SGCP.

Activa dinámicamente la zona horaria correcta según la región
solicitada en el header X-Timezone o en el parámetro ?region=.

Prioridad de detección:
1. Header X-Timezone (ej: 'America/Lima', 'America/New_York')
2. Header X-Locale-Region (ej: 'es-PE', 'en-US', 'pt-BR') → mapea a timezone
3. Query param ?region= (ej: 'es-PE')
4. Fallback: America/Lima (Perú)

Este middleware debe ir DESPUÉS de LocaleMiddleware en settings.py
para que tanto el idioma como la zona horaria se activen por request.
"""

from django.utils import timezone as django_timezone
from .i18n_utils import LOCALE_CONFIG, VALID_LOCALES


class TimezoneMiddleware:
    """
    Activa la zona horaria correspondiente al locale del request.
    
    Django usa timezone.activate() para que los templates y serializers
    conviertan automáticamente los datetimes al timezone activo.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_name = self._resolve_timezone(request)

        # Activar la zona horaria para este request
        try:
            tz = django_timezone.pytz.timezone(tz_name)
            django_timezone.activate(tz)
        except Exception:
            # Fallback: no activar timezone (usar settings.TIME_ZONE)
            pass

        # Guardar el timezone en el request para uso en vistas/serializers
        request.timezone_name = tz_name

        response = self.get_response(request)

        # Desactivar al terminar (limpieza)
        django_timezone.deactivate()

        return response

    def _resolve_timezone(self, request):
        """Resuelve el timezone desde los headers o query params del request."""

        # 1. Header directo X-Timezone
        x_tz = request.META.get('HTTP_X_TIMEZONE', '')
        if x_tz:
            return self._validate_timezone(x_tz)

        # 2. Header X-Locale-Region (mapea a timezone)
        x_locale = request.META.get('HTTP_X_LOCALE_REGION', '')
        if x_locale:
            config = LOCALE_CONFIG.get(x_locale)
            if config:
                return config['timezone']

        # 3. Query param ?region=
        region = request.GET.get('region', '')
        if region and region in VALID_LOCALES:
            return LOCALE_CONFIG[region]['timezone']

        # 4. Fallback: America/Lima
        return 'America/Lima'

    def _validate_timezone(self, tz_name):
        """Valida que el timezone sea un nombre IANA válido."""
        try:
            django_timezone.pytz.timezone(tz_name)
            return tz_name
        except Exception:
            return 'America/Lima'