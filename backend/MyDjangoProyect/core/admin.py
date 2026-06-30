from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy


# CORREGIDO: Se eliminan Estilista y HorarioEstilista (modelos eliminados).
# Se importa Horario en su lugar.
from .models import (
    Peluqueria,
    Usuario,
    Servicio,
    Cita,
    Horario,
)


@admin.register(Peluqueria)
class PeluqueriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'direccion', 'status')
    search_fields = ('nombre', 'direccion', 'telefono')
    list_filter = ('status',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """
    CORREGIDO respecto al codigo anterior:
    - 'nombre' no existe en AbstractUser → se usan 'first_name' y 'last_name'.
    - 'status' se reemplaza por 'is_active' (campo nativo de Django, Regla #7).
    - 'fecha_registro' no existe → se usa 'date_joined' de AbstractUser.
    - Se agrega 'peluqueria' y 'especialidad' para gestionar estilistas.
    - Se agrega list_editable para togglear is_active rapidamente.
    """

    list_display = (
        'first_name',
        'last_name',
        'email',
        'rol',
        'is_active',
        'peluqueria',
        'date_joined',
    )
    search_fields = ('first_name', 'last_name', 'email', 'telefono', 'username')
    list_filter = ('rol', 'is_active', 'peluqueria')
    list_editable = ('is_active',)

    fieldsets = (
        (gettext_lazy('Credenciales'), {
            'fields': ('username', 'password', 'email'),
        }),
        (gettext_lazy('Datos personales'), {
            'fields': ('first_name', 'last_name', 'telefono'),
        }),
        (gettext_lazy('Rol y estado'), {
            'fields': ('rol', 'is_active', 'peluqueria', 'especialidad'),
        }),
    )

    def get_queryset(self, request):
        """Precarga la peluqueria para evitar queries extra en list_display."""
        return super().get_queryset(request).select_related('peluqueria')


# ELIMINADO: EstilistaAdmin
# Los estilistas ahora son Usuarios con rol='estilista'.
# Se gestionan desde UsuarioAdmin filtrando por rol.


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'hair_salon', 'precio', 'duracion_minutos', 'status')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('hair_salon', 'status')


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    """
    CORREGIDO: Antes se llamaba HorarioEstilistaAdmin y usaba 'stylist'.
    Ahora se llama HorarioAdmin y usa 'estilista' (FK a Usuario).
    """

    list_display = ('estilista', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo')
    search_fields = ('estilista__first_name', 'estilista__last_name', 'dia_semana')
    list_filter = ('dia_semana', 'activo')

    def get_queryset(self, request):
        """Precarga el estilista para evitar N+1 en list_display."""
        return super().get_queryset(request).select_related('estilista')


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """
    CORREGIDO respecto al codigo anterior:
    - 'user'     → 'cliente'   (related_name='citas_como_cliente')
    - 'stylist'  → 'estilista' (related_name='citas_como_estilista', FK a Usuario)
    - 'service'  → 'servicio'  (related_name='citas')
    - 'fecha_creacion' → 'created' (heredado de ModeloAuditable)
    - Los search_fields usan los campos reales de Usuario (first_name, last_name).
    """

    list_display = (
        'id',
        'cliente',
        'estilista',
        'servicio',
        'fecha',
        'hora_inicio',
        'estado_badge',
    )
    search_fields = (
        'cliente__first_name',
        'cliente__last_name',
        'estilista__first_name',
        'estilista__last_name',
        'servicio__nombre',
        'observaciones',
    )
    list_filter = ('estado', 'fecha')
    autocomplete_fields = ('cliente', 'estilista', 'servicio')
    date_hierarchy = 'fecha'

    def get_queryset(self, request):
        """Precarga todas las FK para evitar N+1 en list_display."""
        return super().get_queryset(request).select_related(
            'cliente', 'estilista', 'servicio',
        )

    @admin.display(description=gettext_lazy('Estado'))
    def estado_badge(self, obj):
        colores = {
            'pendiente': '#f59e0b',
            'confirmada': '#2563eb',
            'completada': '#16a34a',
            'cancelada': '#dc2626',
        }
        color = colores.get(obj.estado, '#475569')
        return format_html(
            '<strong style="color: {}">{}</strong>',
            color,
            obj.estado.capitalize(),
        )