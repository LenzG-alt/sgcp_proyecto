"""
URL configuration del proyecto SGCP.

Rutas:
- /admin/                → Django admin (solo superusers)
- /api/publico/          → Datos publicos para la landing (AllowAny)
- /api/token/            → Login JWT (usa CustomTokenObtainPairView)
- /api/token/refresh/    → Refresh JWT
- /api/registro/         → Registro publico (crea clientes)
- /api/perfil/           → Perfil del usuario autenticado
- /api/peluquerias/      → CRUD (admin write, personal lectura)
- /api/usuarios/         → CRUD (solo admin)
- /api/servicios/        → CRUD (admin write, personal lectura)
- /api/citas/            → CRUD (permisos diferenciados por rol)
- /api/horarios/         → CRUD (admin write, personal lectura)
- /api/data-anidada/     → Dashboard anidado (solo admin)
- /api/panel-estilista/  → Panel del estilista (admin o estilista)
- /api/panel-recepcionista/ → Panel de la recepcionista
- /api/cliente/panel/    → Panel/dashboard del cliente
- /api/cliente/mis-citas/       → Citas del cliente (GET lista, POST crear)
- /api/cliente/mis-citas/<id>/  → Detalle de una cita del cliente
- /api/cliente/mis-citas/<id>/cancelar/ → Cancelar cita
- /api/cliente/servicios/       → Catalogo de servicios
- /api/cliente/estilistas/      → Estilistas con horario
- /api/cliente/estilistas/<id>/horario/ → Horario de un estilista
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from core.views import (
    CitaViewSet,
    HorarioViewSet,
    PeluqueriaViewSet,
    ServicioViewSet,
    UsuarioViewSet,
    nested_dashboard_data,
    datos_publicos,
    mi_panel_estilista,
    panel_recepcionista,
    # Vistas del portal del cliente
    panel_cliente,
    mis_citas,
    detalle_cita,
    crear_cita,
    cancelar_cita,
    servicios_disponibles,
    estilistas_disponibles,
    horario_estilista_detalle,
    # Vistas del portal de recepcionista
    citas_recepcionista,
    crear_cita_recepcionista,
    cambiar_estado_cita_recepcionista,
    # Vistas del portal de estilista (adicionales)
    citas_estilista,
    cambiar_estado_cita_estilista,
    editar_perfil_estilista,
    servicios_estilista,
    estadisticas_estilista,
)
from core.i18n_views import locale_config_view
from core.auth_views import (
    CustomTokenObtainPairView,
    registro_view,
    perfil_view,
)

router = DefaultRouter()
router.register(r'peluquerias', PeluqueriaViewSet, basename='peluqueria')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
# ELIMINADO: estilistas — se gestionan via /usuarios/?rol=estilista
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'citas', CitaViewSet, basename='cita')
router.register(r'horarios', HorarioViewSet, basename='horario')

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # API REST
    path('api/', include(router.urls)),

    # --- Endpoints publicos (sin autenticacion) ---
    path('api/publico/', datos_publicos, name='datos-publicos'),
    path('api/registro/', registro_view, name='registro'),
    path('api/locale-config/', locale_config_view, name='locale-config'),

    # --- Autenticacion JWT ---
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- Perfil del usuario autenticado ---
    path('api/perfil/', perfil_view, name='perfil'),

    # --- Dashboards por rol ---
    path('api/data-anidada/', nested_dashboard_data, name='nested-dashboard-data'),
    path('api/panel-estilista/', mi_panel_estilista, name='panel-estilista'),
    path('api/panel-recepcionista/', panel_recepcionista, name='panel-recepcionista'),

    # --- Portal del cliente (solo rol='cliente') ---
    path('api/cliente/panel/', panel_cliente, name='panel-cliente'),
    path('api/cliente/mis-citas/', mis_citas, name='mis-citas'),
    path('api/cliente/mis-citas/crear/', crear_cita, name='crear-cita'),
    path('api/cliente/mis-citas/<int:cita_id>/', detalle_cita, name='detalle-cita'),
    path(
        'api/cliente/mis-citas/<int:cita_id>/cancelar/',
        cancelar_cita, name='cancelar-cita',
    ),
    path(
        'api/cliente/servicios/',
        servicios_disponibles, name='servicios-disponibles',
    ),
    path(
        'api/cliente/estilistas/',
        estilistas_disponibles, name='estilistas-disponibles',
    ),
    path(
        'api/cliente/estilistas/<int:estilista_id>/horario/',
        horario_estilista_detalle, name='horario-estilista-detalle',
    ),

    # --- Portal de recepcionista ---
    path(
        'api/recepcionista/citas/',
        citas_recepcionista, name='recepcionista-citas',
    ),
    path(
        'api/recepcionista/citas/crear/',
        crear_cita_recepcionista, name='recepcionista-crear-cita',
    ),
    path(
        'api/recepcionista/citas/<int:cita_id>/cambiar-estado/',
        cambiar_estado_cita_recepcionista, name='recepcionista-cambiar-estado',
    ),

    # --- Portal de estilista (adicionales al panel) ---
    path(
        'api/estilista/mis-citas/',
        citas_estilista, name='estilista-mis-citas',
    ),
    path(
        'api/estilista/mis-citas/<int:cita_id>/cambiar-estado/',
        cambiar_estado_cita_estilista, name='estilista-cambiar-estado',
    ),
    path(
        'api/estilista/perfil/',
        editar_perfil_estilista, name='estilista-editar-perfil',
    ),
    path(
        'api/estilista/servicios/',
        servicios_estilista, name='estilista-servicios',
    ),
    path(
        'api/estilista/estadisticas/',
        estadisticas_estilista, name='estilista-estadisticas',
    ),
]