#!/bin/sh
set -e

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput || echo "collectstatic ignorado (modo desarrollo)"

echo "Cargando datos de prueba (si está activado)..."
if [ "$LOAD_INITIAL_DATA" = "true" ] && [ -f "crear_datos.py" ]; then
    python crear_datos.py || echo "⚠️ Script de datos falló o no es necesario"
fi

echo " - Backend listo. Iniciando servidor..."
exec "$@"