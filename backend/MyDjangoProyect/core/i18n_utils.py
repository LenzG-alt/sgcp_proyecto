"""
Utilidades de internacionalizacion y localizacion para SGCP.

Define la configuracion regional por pais:
- Peru (es-PE): Espanol, Soles (S/.), DD/MM/YYYY, America/Lima
- EEUU (en-US): Ingles, Dolares ($), MM/DD/YYYY, America/New_York
- Brasil (pt-BR): Portugues, Reales (R$), DD/MM/YYYY, America/Sao_Paulo
"""

from zoneinfo import ZoneInfo
from datetime import datetime, date, time as dt_time, timedelta
from django.conf import settings


LOCALE_CONFIG = {
    'es-PE': {
        'code': 'es',
        'region': 'PE',
        'name': 'Peru',
        'name_native': 'Peru',
        'language': 'es',
        'currency_code': 'PEN',
        'currency_symbol': 'S/.',
        'currency_position': 'prefix',
        'date_format': 'DD/MM/YYYY',
        'date_locale': 'es-PE',
        'timezone': 'America/Lima',
        'utc_offset': '-05:00',
        'number_locale': 'es-PE',
        'first_day_of_week': 1,  # lunes
    },
    'en-US': {
        'code': 'en',
        'region': 'US',
        'name': 'United States',
        'name_native': 'United States',
        'language': 'en',
        'currency_code': 'USD',
        'currency_symbol': '$',
        'currency_position': 'prefix',
        'date_format': 'MM/DD/YYYY',
        'date_locale': 'en-US',
        'timezone': 'America/New_York',
        'utc_offset': '-04:00',  # EDT (hora de verano); se actualiza dinámicamente
        'number_locale': 'en-US',
        'first_day_of_week': 0,  # domingo
    },
    'pt-BR': {
        'code': 'pt',
        'region': 'BR',
        'name': 'Brazil',
        'name_native': 'Brasil',
        'language': 'pt-br',
        'currency_code': 'BRL',
        'currency_symbol': 'R$',
        'currency_position': 'prefix',
        'date_format': 'DD/MM/YYYY',
        'date_locale': 'pt-BR',
        'timezone': 'America/Sao_Paulo',
        'utc_offset': '-03:00',
        'number_locale': 'pt-BR',
        'first_day_of_week': 0,  # domingo
    },
}

VALID_LOCALES = set(LOCALE_CONFIG.keys())


def get_locale_config(locale_key='es-PE'):
    """Retorna la configuracion regional para un locale dado."""
    config = LOCALE_CONFIG.get(locale_key, LOCALE_CONFIG['es-PE']).copy()
    # Calcular el offset UTC dinámicamente (para manejar DST/horario de verano)
    config['utc_offset'] = get_dynamic_utc_offset(config['timezone'])
    return config


def get_dynamic_utc_offset(timezone_name):
    """
    Calcula el offset UTC actual para una zona horaria dada.
    Esto maneja automáticamente el horario de verano (DST).
    Retorna un string como '-05:00', '+00:00', etc.
    """
    try:
        tz = ZoneInfo(timezone_name)
        now = datetime.now(tz)
        offset = now.utcoffset()
        if offset is None:
            return '+00:00'
        total_seconds = int(offset.total_seconds())
        hours = total_seconds // 3600
        minutes = abs(total_seconds % 3600) // 60
        sign = '+' if hours >= 0 else '-'
        return f'{sign}{abs(hours):02d}:{minutes:02d}'
    except Exception:
        return '+00:00'


def get_tz(timezone_name):
    """Retorna un objeto ZoneInfo para la zona horaria dada."""
    try:
        return ZoneInfo(timezone_name)
    except Exception:
        return ZoneInfo('America/Lima')


def convert_utc_to_locale(utc_dt, timezone_name='America/Lima'):
    """
    Convierte un datetime UTC (o naive asumido como UTC) a la zona horaria local.

    Args:
        utc_dt: datetime object (aware o naive; si es naive se asume UTC)
        timezone_name: nombre IANA de la zona horaria destino

    Returns:
        datetime en la zona horaria destino
    """
    if utc_dt is None:
        return None

    tz = get_tz(timezone_name)

    # Si es naive, asumir que es UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=ZoneInfo('UTC'))

    return utc_dt.astimezone(tz)


def convert_locale_to_utc(local_dt, timezone_name='America/Lima'):
    """
    Convierte un datetime local a UTC.

    Args:
        local_dt: datetime en la zona horaria local (aware o naive)
        timezone_name: nombre IANA de la zona horaria origen

    Returns:
        datetime en UTC
    """
    if local_dt is None:
        return None

    tz = get_tz(timezone_name)

    # Si es naive, asumir que ya está en la zona horaria indicada
    if local_dt.tzinfo is None:
        local_dt = local_dt.replace(tzinfo=tz)

    return local_dt.astimezone(ZoneInfo('UTC'))


def get_current_datetime_in_locale(timezone_name='America/Lima'):
    """
    Retorna la fecha y hora actual en la zona horaria indicada.

    Args:
        timezone_name: nombre IANA de la zona horaria

    Returns:
        datetime aware en la zona horaria destino
    """
    tz = get_tz(timezone_name)
    return datetime.now(tz)


def get_current_time_in_locale(timezone_name='America/Lima'):
    """
    Retorna la hora actual en la zona horaria indicada como string HH:MM.

    Args:
        timezone_name: nombre IANA de la zona horaria

    Returns:
        string con la hora actual en formato HH:MM
    """
    now = get_current_datetime_in_locale(timezone_name)
    return now.strftime('%H:%M')


def get_current_date_in_locale(timezone_name='America/Lima'):
    """
    Retorna la fecha actual en la zona horaria indicada.

    Args:
        timezone_name: nombre IANA de la zona horaria

    Returns:
        date object con la fecha actual en la zona horaria
    """
    now = get_current_datetime_in_locale(timezone_name)
    return now.date()


def format_datetime_for_locale(dt, timezone_name='America/Lima', fmt=None):
    """
    Formatea un datetime a la zona horaria local con formato personalizado.

    Args:
        dt: datetime (UTC o naive)
        timezone_name: zona horaria destino
        fmt: formato strftime (default: '%d/%m/%Y %H:%M')

    Returns:
        string formateado
    """
    if dt is None:
        return ''

    if fmt is None:
        fmt = '%d/%m/%Y %H:%M'

    local_dt = convert_utc_to_locale(dt, timezone_name)
    if local_dt is None:
        return ''

    return local_dt.strftime(fmt)


def is_business_hours_in_locale(timezone_name='America/Lima'):
    """
    Verifica si actualmente es horario de atención (9:00 - 21:00) en la zona horaria dada.

    Returns:
        tuple (is_open: bool, current_time_str: str)
    """
    now = get_current_datetime_in_locale(timezone_name)
    current_hour = now.hour
    is_open = 9 <= current_hour < 21
    time_str = now.strftime('%H:%M')
    return is_open, time_str


def resolve_language_from_accept(accept_language):
    """
    Resuelve el codigo de lenguaje Django desde un header Accept-Language.

    Mapea:
    - es, es-PE, es-419 → 'es'
    - en, en-US, en-GB → 'en'
    - pt, pt-BR, pt-PT → 'pt-br'
    """
    if not accept_language:
        return 'es'

    accept_lower = accept_language.lower().replace('_', '-')

    # Orden por prioridad (primer lenguaje listado)
    langs = [lang.strip().split(';')[0].strip() for lang in accept_lower.split(',')]

    for lang in langs:
        # Remover calidad (q=0.8)
        lang = lang.split(';')[0].strip()

        # Mapeo directo
        lang_map = {
            'es-pe': 'es', 'es-419': 'es', 'es': 'es',
            'en-us': 'en', 'en-gb': 'en', 'en': 'en',
            'pt-br': 'pt-br', 'pt-pt': 'pt-br', 'pt': 'pt-br',
        }

        if lang in lang_map:
            return lang_map[lang]

        # Prefijo
        prefix = lang.split('-')[0]
        prefix_map = {'es': 'es', 'en': 'en', 'pt': 'pt-br'}
        if prefix in prefix_map:
            return prefix_map[prefix]

    return 'es'