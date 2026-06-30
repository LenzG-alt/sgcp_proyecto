"""
Vista de configuracion regional para SGCP.

GET /api/locale-config/?region=es-PE
Response: {
    "locales": [...],
    "current": { ...locale config con timezone y utc_offset... },
    "translations": { ...backend UI strings in current language... },
    "server_time": { ...hora/fecha actual en la zona horaria del locale... }
}
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .i18n_utils import (
    LOCALE_CONFIG, VALID_LOCALES, get_locale_config,
    get_current_datetime_in_locale, get_dynamic_utc_offset,
)


@api_view(['GET'])
@permission_classes([AllowAny])
def locale_config_view(request):
    """
    Devuelve la configuracion regional disponible y la configuracion
    del locale solicitado (o por defecto es-PE).

    Query params:
    - region: es-PE | en-US | pt-BR (opcional, default: es-PE)

    La respuesta incluye:
    - locales: lista de todos los locales disponibles con sus datos
    - current: configuracion del locale seleccionado (con timezone y utc_offset)
    - translations: strings traducidos del backend para el locale actual
    - server_time: hora y fecha actual del servidor en la zona horaria del locale
    """
    region = request.query_params.get('region', 'es-PE')

    if region not in VALID_LOCALES:
        region = 'es-PE'

    current = get_locale_config(region)

    # Strings del backend traducidos para este locale
    from django.utils.translation import activate, gettext

    # Activar temporalmente el idioma
    lang = current['language']
    activate(lang)

    translations = {
        # Roles
        'roles': {
            'cliente': gettext('Cliente'),
            'estilista': gettext('Estilista'),
            'administrador': gettext('Administrador'),
            'recepcionista': gettext('Recepcionista'),
        },
        # Estados de cita
        'appointment_states': {
            'pendiente': gettext('Pendiente'),
            'confirmada': gettext('Confirmada'),
            'completada': gettext('Completada'),
            'cancelada': gettext('Cancelada'),
        },
        # Dias de la semana
        'days_of_week': {
            'monday': gettext('Monday'),
            'tuesday': gettext('Tuesday'),
            'wednesday': gettext('Wednesday'),
            'thursday': gettext('Thursday'),
            'friday': gettext('Friday'),
            'saturday': gettext('Saturday'),
            'sunday': gettext('Sunday'),
        },
        # Estado activo/inactivo
        'active_states': {
            'active': gettext('Estado'),
            'inactive': gettext('Estado'),
        },
    }

    # Hora/fecha actual en la zona horaria del locale
    now_locale = get_current_datetime_in_locale(current['timezone'])

    # Formatear lista de locales para el frontend (incluyendo timezone info)
    locales_list = []
    for key, cfg in LOCALE_CONFIG.items():
        locales_list.append({
            'key': key,
            'code': cfg['code'],
            'region': cfg['region'],
            'name': cfg['name'],
            'name_native': cfg['name_native'],
            'currency_symbol': cfg['currency_symbol'],
            'timezone': cfg['timezone'],
            'utc_offset': get_dynamic_utc_offset(cfg['timezone']),
        })

    return Response({
        'locales': locales_list,
        'current': current,
        'translations': translations,
        'server_time': {
            'datetime': now_locale.strftime('%Y-%m-%d %H:%M:%S'),
            'date': now_locale.strftime('%Y-%m-%d'),
            'time': now_locale.strftime('%H:%M'),
            'timezone': current['timezone'],
            'utc_offset': current['utc_offset'],
        },
    })