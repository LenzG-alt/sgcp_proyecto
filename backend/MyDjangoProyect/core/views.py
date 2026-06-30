"""
Vistas de la API REST del sistema SGCP.

Cada ViewSet tiene permisos personalizados segun el rol:
- Administrador: CRUD completo en todos los endpoints.
- Recepcionista: Lectura en todo, escritura limitada en citas.
- Estilista: Solo lectura de su propio horario y citas.
- Publico: Solo el endpoint de datos publicos (landing).

Se importan permisos personalizados desde core.permissions.
"""

from django.db.models import Q

from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Peluqueria, Usuario, Servicio, Cita, Horario
from .serializers import (
    PeluqueriaSerializer,
    UsuarioSerializer,
    ServicioSerializer,
    CitaSerializer,
    HorarioSerializer,
    UsuarioSummarySerializer,
    # Serializers del portal del cliente
    CitaClienteSerializer,
    CrearCitaSerializer,
    ServicioPublicoSerializer,
    EstilistaDisponibleSerializer,
    HorarioEstilistaSerializer,
)
from .permissions import (
    EsAdministrador,
    EsCliente,
    EsClienteORecepcionista,
    EsPersonalInterno,
    EsAdminORecepcionista,
    EsAdminOEstilista,
    SoloLecturaSiNoEsAdmin,
)


# =============================================================================
# ENDPOINTS PUBLICOS (no requieren autenticacion)
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def datos_publicos(request):
    """
    Endpoint publico que devuelve informacion del negocio para la
    landing page. Cualquier persona puede acceder sin autenticacion.

    GET /api/publico/
    Response: { peluquerias: [...], servicios: [...] }
    """
    from .models import Peluqueria, Servicio
    from .serializers import PeluqueriaSummarySerializer, ServicioSummarySerializer

    peluquerias = Peluqueria.objects.filter(status='active')
    servicios = Servicio.objects.filter(status='active').select_related('hair_salon')[:12]

    return Response({
        'peluquerias': PeluqueriaSummarySerializer(peluquerias, many=True).data,
        'servicios': ServicioSummarySerializer(servicios, many=True).data,
    })


# =============================================================================
# VIEWSETS CON PERMISOS POR ROL
# =============================================================================

class PeluqueriaViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de peluquerias.

    Permisos:
    - Administrador: total (crear, leer, actualizar, eliminar).
    - Personal interno (estilista, recepcionista): solo lectura.
    - Publico: sin acceso.
    """

    queryset = Peluqueria.objects.all().order_by('nombre')
    serializer_class = PeluqueriaSerializer
    permission_classes = [EsPersonalInterno]

    def get_permissions(self):
        """El admin tiene acceso total; otros roles solo lectura."""
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [EsAdministrador()]
        return [EsPersonalInterno()]


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de usuarios.

    Permisos:
    - Administrador: total.
    - Recepcionista: solo lectura.
    - Cualquier otro rol: sin acceso.
    """

    queryset = Usuario.objects.all().order_by('first_name')
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [EsAdministrador()]
        if self.request.user.rol == 'recepcionista':
            return [EsAdminORecepcionista()]
        return [EsAdministrador()]

    def get_queryset(self):
        qs = super().get_queryset()
        rol = self.request.query_params.get('rol')
        if rol:
            qs = qs.filter(rol=rol)
        return qs


class ServicioViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de servicios.

    Permisos:
    - Administrador: total.
    - Personal interno: solo lectura.
    """

    queryset = Servicio.objects.all().order_by('nombre')
    serializer_class = ServicioSerializer
    permission_classes = [EsPersonalInterno]

    def get_permissions(self):
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [EsAdministrador()]
        return [EsPersonalInterno()]


class CitaViewSet(viewsets.ModelViewSet):
    """
    CRUD de citas con permisos diferenciados.

    Permisos:
    - Administrador: total.
    - Recepcionista: lectura + creacion/actualizacion (no eliminacion).
    - Estilista: solo lectura de sus propias citas.
    - Publico: sin acceso.
    """

    queryset = Cita.objects.select_related(
        'cliente', 'estilista', 'servicio__hair_salon',
    ).order_by('-fecha', 'hora_inicio')
    serializer_class = CitaSerializer

    def get_permissions(self):
        """Permisos granulares segun metodo HTTP y rol."""
        if self.request.method == 'DELETE':
            return [EsAdministrador()]
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return [EsAdminORecepcionista()]
        # GET, HEAD, OPTIONS
        return [EsPersonalInterno()]

    def get_queryset(self):
        """
        Los estilistas solo ven sus propias citas.
        Los demas roles ven todas.
        """
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.rol == 'estilista':
            return qs.filter(estilista=user)

        return qs


class HorarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de horarios de estilistas.

    Permisos:
    - Administrador: total.
    - Estilista: solo lectura de sus propios horarios.
    - Recepcionista: solo lectura (para ver disponibilidad).
    """

    queryset = Horario.objects.select_related(
        'estilista',
    ).order_by('estilista__first_name', 'dia_semana')
    serializer_class = HorarioSerializer

    def get_permissions(self):
        """Solo el admin puede crear/modificar/eliminar horarios."""
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [EsAdministrador()]
        return [EsPersonalInterno()]

    def get_queryset(self):
        """
        Los estilistas solo ven sus propios horarios.
        El admin y recepcionista ven todos.
        """
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.rol == 'estilista':
            return qs.filter(estilista=user)

        return qs


# =============================================================================
# ENDPOINT ESPECIAL: Dashboard con datos anidados (solo admin)
# =============================================================================

@api_view(['GET'])
@permission_classes([EsAdministrador])
def nested_dashboard_data(request):
    """
    Endpoint que devuelve datos anidados para el dashboard del admin.

    CORRECCIONES aplicadas:
    1. No se consulta el modelo eliminado 'Estilista'.
    2. Se usan related_names correctos.
    3. Se usa get_full_name() en lugar de campo 'nombre'.
    4. Se usa is_active en lugar de 'status'.
    """

    estilistas_qs = (
        Usuario.objects
        .filter(rol='estilista')
        .select_related('peluqueria')
        .prefetch_related('horarios')
        .order_by('first_name')
    )

    clientes_qs = (
        Usuario.objects
        .filter(rol='cliente')
        .prefetch_related(
            'citas_como_cliente__servicio',
            'citas_como_cliente__estilista__peluqueria',
        )
        .order_by('first_name')
    )

    payload = []

    for estilista in estilistas_qs:
        payload.append({
            'usuario_id': estilista.id,
            'nombre_completo': estilista.get_full_name() or estilista.username,
            'correo_electronico': estilista.email,
            'telefono': estilista.telefono,
            'rol': estilista.rol,
            'estado_cuenta': 'activo' if estilista.is_active else 'inactivo',
            'perfil_estilista': {
                'especialidad': estilista.especialidad or '',
                'peluqueria_asignada': (
                    {
                        'nombre_comercial': estilista.peluqueria.nombre,
                        'telefono_contacto': estilista.peluqueria.telefono,
                        'direccion_fisica': estilista.peluqueria.direccion,
                        'descripcion': estilista.peluqueria.descripcion,
                    }
                    if estilista.peluqueria
                    else None
                ),
                'horarios_atencion': [
                    {
                        'dia_semana': horario.dia_semana,
                        'hora_inicio': horario.hora_inicio.isoformat(),
                        'hora_fin': horario.hora_fin.isoformat(),
                        'activo': horario.activo,
                    }
                    for horario in estilista.horarios.all()
                ],
            },
        })

    for cliente in clientes_qs:
        citas_data = []
        for cita in cliente.citas_como_cliente.all():
            citas_data.append({
                'fecha_reserva': cita.fecha.isoformat(),
                'hora_inicio': cita.hora_inicio.isoformat(),
                'hora_fin': cita.hora_fin.isoformat(),
                'estado_cita': cita.estado,
                'lugar_cita': (
                    {
                        'nombre_comercial': cita.estilista.peluqueria.nombre,
                        'direccion_fisica': cita.estilista.peluqueria.direccion,
                    }
                    if cita.estilista.peluqueria
                    else None
                ),
                'servicio_solicitado': {
                    'nombre_servicio': cita.servicio.nombre,
                    'descripcion': cita.servicio.descripcion,
                    'costo': float(cita.servicio.precio),
                    'duracion_minutos': cita.servicio.duracion_minutos,
                },
                'profesional_asignado': {
                    'nombre': (
                        cita.estilista.get_full_name()
                        or cita.estilista.username
                    ),
                    'especialidad': cita.estilista.especialidad or '',
                },
            })

        payload.append({
            'usuario_id': cliente.id,
            'nombre_completo': cliente.get_full_name() or cliente.username,
            'correo_electronico': cliente.email,
            'telefono': cliente.telefono,
            'rol': cliente.rol,
            'estado_cuenta': 'activo' if cliente.is_active else 'inactivo',
            'historial_citas': citas_data,
        })

    return Response(payload)


# =============================================================================
# ENDPOINT: Resumen para estilista (sus propias citas y horarios)
# =============================================================================

@api_view(['GET'])
@permission_classes([EsAdminOEstilista])
def mi_panel_estilista(request):
    """
    Devuelve los datos del panel de un estilista:
    - Sus citas de hoy y proximas.
    - Su horario semanal.
    - Estadisticas basicas.

    Si el usuario es admin, puede pasar ?usuario_id=X para ver
    el panel de cualquier estilista.
    """
    user = request.user

    # El admin puede ver el panel de otro estilista
    if user.rol == 'administrador':
        target_id = request.query_params.get('usuario_id')
        if target_id:
            user = Usuario.objects.filter(
                pk=target_id, rol='estilista'
            ).first()
            if not user:
                return Response(
                    {'detail': gettext('Estilista no encontrado.')},
                    status=404,
                )

    from datetime import date
    hoy = date.today()

    citas_qs = (
        Cita.objects
        .filter(estilista=user, fecha__gte=hoy)
        .select_related('cliente', 'servicio')
        .order_by('fecha', 'hora_inicio')
    )

    horarios = Horario.objects.filter(
        estilista=user, activo=True
    ).order_by('dia_semana')

    return Response({
        'estilista': {
            'id': user.id,
            'nombre_completo': user.get_full_name() or user.username,
            'especialidad': user.especialidad or '',
        },
        'citas_proximas': CitaSerializer(citas_qs, many=True).data,
        'horarios': HorarioSerializer(horarios, many=True).data,
        'total_citas_hoy': citas_qs.filter(fecha=hoy).count(),
        'total_citas_pendientes': citas_qs.filter(estado='pendiente').count(),
    })


# =============================================================================
# ENDPOINT: Panel de recepcionista
# =============================================================================

@api_view(['GET'])
@permission_classes([EsAdminORecepcionista])
def panel_recepcionista(request):
    """
    Devuelve datos para el panel de la recepcionista:
    - Citas de hoy.
    - Estilistas disponibles con sus horarios de hoy.
    - Servicios disponibles.
    """
    from datetime import date

    hoy = date.today()
    dia_hoy = hoy.strftime('%A').lower()

    # Mapear dia en ingles a espanol
    from django.utils.translation import gettext as _
    dias_map = {
        'monday': _('Monday').lower(), 'tuesday': _('Tuesday').lower(),
        'wednesday': _('Wednesday').lower(), 'thursday': _('Thursday').lower(),
        'friday': _('Friday').lower(), 'saturday': _('Saturday').lower(),
        'sunday': _('Sunday').lower(),
    }
    dia_es = dias_map.get(dia_hoy, dia_hoy)

    citas_hoy = (
        Cita.objects
        .filter(fecha=hoy)
        .select_related('cliente', 'estilista', 'servicio')
        .order_by('hora_inicio')
    )

    # Estilistas que trabajan hoy
    estilistas_hoy = (
        Usuario.objects
        .filter(
            rol='estilista',
            is_active=True,
            horarios__dia_semana=dia_es,
            horarios__activo=True,
        )
        .distinct()
        .select_related('peluqueria')
    )

    return Response({
        'fecha_hoy': hoy.isoformat(),
        'dia_semana': dia_es,
        'citas_hoy': CitaSerializer(citas_hoy, many=True).data,
        'estilistas_disponibles': UsuarioSummarySerializer(
            estilistas_hoy, many=True
        ).data,
        'total_citas_hoy': citas_hoy.count(),
        'pendientes_hoy': citas_hoy.filter(estado='pendiente').count(),
        'confirmadas_hoy': citas_hoy.filter(estado='confirmada').count(),
    })


# =============================================================================
# ENDPOINTS DEL PORTAL DEL CLIENTE
# =============================================================================
# Todas estas vistas requieren que el usuario este autenticado
# con rol='cliente'. El cliente solo puede ver y gestionar
# SUS PROPIAS citas, no las de otros clientes.
# =============================================================================

@api_view(['GET'])
@permission_classes([EsCliente])
def panel_cliente(request):
    """
    Dashboard del cliente: resumen de su actividad.

    GET /api/cliente/panel/
    Response: {
        perfil: { id, nombre_completo, email, telefono },
        estadisticas: {
            total_citas, pendientes, confirmadas,
            completadas, canceladas,
            proxima_cita: { ... } | null
        },
        citas_proximas: [ ... ]
    }
    """
    from datetime import date

    user = request.user
    hoy = date.today()

    # Todas las citas del cliente
    citas_qs = Cita.objects.filter(
        cliente=user,
    ).select_related(
        'estilista', 'servicio', 'estilista__peluqueria',
    ).order_by('fecha', 'hora_inicio')

    total = citas_qs.count()
    pendientes = citas_qs.filter(estado='pendiente').count()
    confirmadas = citas_qs.filter(estado='confirmada').count()
    completadas = citas_qs.filter(estado='completada').count()
    canceladas = citas_qs.filter(estado='cancelada').count()

    # Proxima cita (pendiente o confirmada, fecha >= hoy)
    proxima = (
        citas_qs
        .filter(fecha__gte=hoy, estado__in=['pendiente', 'confirmada'])
        .first()
    )

    # Citas proximas (las 5 mas cercanas)
    proximas_qs = citas_qs.filter(
        fecha__gte=hoy, estado__in=['pendiente', 'confirmada'],
    )[:5]

    return Response({
        'perfil': {
            'id': user.id,
            'nombre_completo': user.get_full_name() or user.username,
            'email': user.email,
            'telefono': user.telefono or '',
        },
        'estadisticas': {
            'total_citas': total,
            'pendientes': pendientes,
            'confirmadas': confirmadas,
            'completadas': completadas,
            'canceladas': canceladas,
            'proxima_cita': (
                CitaClienteSerializer(proxima).data if proxima else None
            ),
        },
        'citas_proximas': CitaClienteSerializer(proximas_qs, many=True).data,
    })


@api_view(['GET'])
@permission_classes([EsCliente])
def mis_citas(request):
    """
    Lista las citas del cliente autenticado con filtros opcionales.

    GET /api/cliente/mis-citas/
    Query params (todos opcionales):
    - estado: pendiente | confirmada | completada | cancelada
    - desde: fecha YYYY-MM-DD (inclusive)
    - hasta: fecha YYYY-MM-DD (inclusive)
    - proximas: "true" — solo citas desde hoy en adelante

    Response: [ CitaClienteSerializer, ... ]
    """
    from datetime import date

    user = request.user
    qs = Cita.objects.filter(
        cliente=user,
    ).select_related(
        'estilista', 'servicio', 'estilista__peluqueria',
    ).order_by('-fecha', '-hora_inicio')

    # Filtro por estado
    estado = request.query_params.get('estado')
    if estado:
        qs = qs.filter(estado=estado)

    # Filtro por rango de fechas
    desde = request.query_params.get('desde')
    if desde:
        qs = qs.filter(fecha__gte=desde)

    hasta = request.query_params.get('hasta')
    if hasta:
        qs = qs.filter(fecha__lte=hasta)

    # Citas proximas (hoy en adelante)
    if request.query_params.get('proximas') == 'true':
        qs = qs.filter(fecha__gte=date.today())

    # Paginacion manual (page_size por defecto 20, maximo 50)
    page_size = min(int(request.query_params.get('page_size', 20)), 50)
    page = int(request.query_params.get('page', 1))
    inicio = (page - 1) * page_size
    fin = inicio + page_size
    pagina_qs = qs[inicio:fin]

    return Response({
        'count': qs.count(),
        'next': page + 1 if fin < qs.count() else None,
        'previous': page - 1 if page > 1 else None,
        'results': CitaClienteSerializer(pagina_qs, many=True).data,
    })


@api_view(['GET'])
@permission_classes([EsCliente])
def detalle_cita(request, cita_id):
    """
    Detalle de una cita especifica del cliente.

    GET /api/cliente/mis-citas/<cita_id>/
    Response: CitaClienteSerializer

    El cliente solo puede ver SUS propias citas.
    Si intenta ver una cita de otro cliente, retorna 404
    (no revela que la cita existe).
    """
    try:
        cita = Cita.objects.select_related(
            'estilista', 'servicio', 'estilista__peluqueria',
        ).get(pk=cita_id, cliente=request.user)
    except Cita.DoesNotExist:
        return Response(
            {'detail': gettext('Cita no encontrada.')},
            status=404,
        )

    return Response(CitaClienteSerializer(cita).data)


@api_view(['POST'])
@permission_classes([EsCliente])
def crear_cita(request):
    """
    Crea una nueva cita para el cliente autenticado.

    POST /api/cliente/mis-citas/
    Body: {
        estilista_id: int,
        servicio_id: int,
        fecha: "YYYY-MM-DD",
        hora_inicio: "HH:MM",
        observaciones: "" (opcional)
    }
    Response: CitaClienteSerializer (la cita creada)

    El campo cliente se asigna automaticamente como request.user.
    El campo hora_fin se calcula segun la duracion del servicio.
    El estado se establece como 'pendiente' por defecto.
    """
    serializer = CrearCitaSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=400,
        )

    # Crear la cita con el cliente automatico
    cita = serializer.save(
        cliente=request.user,
        estado='pendiente',
    )

    # Reconsultar con las relaciones para el serializer de respuesta
    cita_resp = Cita.objects.select_related(
        'estilista', 'servicio', 'estilista__peluqueria',
    ).get(pk=cita.id)

    return Response(
        CitaClienteSerializer(cita_resp).data,
        status=201,
    )


@api_view(['PATCH'])
@permission_classes([EsCliente])
def cancelar_cita(request, cita_id):
    """
    Cancela una cita del cliente (cambia estado a 'cancelada').

    PATCH /api/cliente/mis-citas/<cita_id>/cancelar/
    Body (opcional): { "motivo": "No puedo asistir" }

    Reglas:
    - Solo se pueden cancelar citas en estado 'pendiente' o 'confirmada'.
    - No se pueden cancelar citas pasadas.
    - El motivo se guarda en el campo observaciones.
    """
    try:
        cita = Cita.objects.select_related(
            'estilista', 'servicio', 'estilista__peluqueria',
        ).get(pk=cita_id, cliente=request.user)
    except Cita.DoesNotExist:
        return Response(
            {'detail': gettext('Cita no encontrada.')},
            status=404,
        )

    # Validar que se puede cancelar
    if cita.estado not in ('pendiente', 'confirmada'):
        return Response(
            {
                'detail': (
                    gettext('No se puede cancelar una cita en estado "{estado}". Solo se pueden cancelar citas pendientes o confirmadas.').format(estado=cita.estado)
                ),
            },
            status=400,
        )

    from datetime import date
    if cita.fecha < date.today():
        return Response(
            {'detail': gettext('No se pueden cancelar citas de fechas pasadas.')},
            status=400,
        )

    # Si el cliente envio un motivo, concatenarlo a las observaciones
    motivo = request.data.get('motivo', '')
    if motivo:
        prefijo = gettext('Motivo de cancelacion: ')
        if cita.observaciones:
            cita.observaciones = (
                f'{cita.observaciones}\n{prefijo}{motivo}'
            )
        else:
            cita.observaciones = f'{prefijo}{motivo}'

    cita.estado = 'cancelada'
    cita.save(update_fields=['estado', 'observaciones', 'modified'])

    return Response(CitaClienteSerializer(cita).data)


@api_view(['GET'])
@permission_classes([EsClienteORecepcionista])
def servicios_disponibles(request):
    """
    Catalogo de servicios disponibles para que el cliente elija.

    GET /api/cliente/servicios/
    Query params (opcionales):
    - peluqueria_id: filtra servicios de una sucursal especifica
    - precio_min: precio minimo
    - precio_max: precio maximo

    Response: [ ServicioPublicoSerializer, ... ]
    """
    qs = (
        Servicio.objects
        .filter(status='active')
        .select_related('hair_salon')
        .order_by('hair_salon__nombre', 'nombre')
    )

    # Filtros opcionales
    peluqueria_id = request.query_params.get('peluqueria_id')
    if peluqueria_id:
        qs = qs.filter(hair_salon_id=peluqueria_id)

    precio_min = request.query_params.get('precio_min')
    if precio_min:
        qs = qs.filter(precio__gte=precio_min)

    precio_max = request.query_params.get('precio_max')
    if precio_max:
        qs = qs.filter(precio__lte=precio_max)

    return Response(
        ServicioPublicoSerializer(qs, many=True).data
    )


@api_view(['GET'])
@permission_classes([EsClienteORecepcionista])
def estilistas_disponibles(request):
    """
    Lista estilistas activos con su peluqueria y horario semanal.

    GET /api/cliente/estilistas/
    Query params (opcionales):
    - peluqueria_id: filtra estilistas de una sucursal
    - dia: "lunes"|"martes"|... — filtra los que trabajan ese dia
    - servicio_id: filtra estilistas cuya peluqueria ofrece ese servicio

    Response: [
        {
            id, nombre_completo, especialidad,
            peluqueria: { id, nombre, direccion, telefono },
            horario: [ { dia_semana, hora_inicio, hora_fin, activo } ]
        },
        ...
    ]
    """
    qs = (
        Usuario.objects
        .filter(rol='estilista', is_active=True)
        .select_related('peluqueria')
        .prefetch_related('horarios')
        .order_by('first_name')
    )

    # Filtro por peluqueria
    peluqueria_id = request.query_params.get('peluqueria_id')
    if peluqueria_id:
        qs = qs.filter(peluqueria_id=peluqueria_id)

    # Filtro por dia de la semana
    dia = request.query_params.get('dia')
    if dia:
        qs = qs.filter(
            horarios__dia_semana=dia, horarios__activo=True,
        ).distinct()

    # Filtro por servicio (estilistas cuya peluqueria ofrece ese servicio)
    servicio_id = request.query_params.get('servicio_id')
    if servicio_id:
        servicio = Servicio.objects.filter(pk=servicio_id).first()
        if servicio:
            qs = qs.filter(peluqueria_id=servicio.hair_salon_id)

    resultado = []
    for estilista in qs:
        # Solo incluir horarios activos
        horarios = estilista.horarios.filter(activo=True).order_by('dia_semana')
        # Si se filtro por dia, ya se aplico en el queryset,
        # pero igual filtramos aqui para el detalle
        if dia:
            horarios = horarios.filter(dia_semana=dia)

        resultado.append({
            'id': estilista.id,
            'nombre_completo': estilista.get_full_name() or estilista.username,
            'especialidad': estilista.especialidad or '',
            'peluqueria': (
                {
                    'id': estilista.peluqueria.id,
                    'nombre': estilista.peluqueria.nombre,
                    'direccion': estilista.peluqueria.direccion,
                    'telefono': estilista.peluqueria.telefono,
                }
                if estilista.peluqueria
                else None
            ),
            'horario': HorarioEstilistaSerializer(
                horarios, many=True
            ).data,
        })

    return Response(resultado)


@api_view(['GET'])
@permission_classes([EsCliente])
def horario_estilista_detalle(request, estilista_id):
    """
    Muestra el horario semanal de un estilista especifico.

    GET /api/cliente/estilistas/<estilista_id>/horario/
    Response: {
        estilista: { id, nombre_completo, especialidad },
        peluqueria: { id, nombre, direccion },
        horario: [ { dia_semana, hora_inicio, hora_fin, activo } ]
    }

    El cliente usa esto para saber en que dias y horas puede
    reservar con un estilista especifico antes de crear la cita.
    """
    estilista = (
        Usuario.objects
        .filter(pk=estilista_id, rol='estilista', is_active=True)
        .select_related('peluqueria')
        .prefetch_related('horarios')
        .first()
    )

    if not estilista:
        return Response(
            {'detail': 'Estilista no encontrado o no disponible.'},
            status=404,
        )

    horarios = estilista.horarios.filter(activo=True).order_by('dia_semana')

    return Response({
        'estilista': {
            'id': estilista.id,
            'nombre_completo': estilista.get_full_name() or estilista.username,
            'especialidad': estilista.especialidad or '',
        },
        'peluqueria': (
            {
                'id': estilista.peluqueria.id,
                'nombre': estilista.peluqueria.nombre,
                'direccion': estilista.peluqueria.direccion,
            }
            if estilista.peluqueria
            else None
        ),
        'horario': HorarioEstilistaSerializer(horarios, many=True).data,
    })


# =============================================================================
# ENDPOINTS DEL PORTAL DE RECEPCIONISTA
# =============================================================================

@api_view(['GET'])
@permission_classes([EsAdminORecepcionista])
def citas_recepcionista(request):
    """
    Lista todas las citas con filtros avanzados para la recepcionista.

    GET /api/recepcionista/citas/
    Query params:
    - estado: pendiente|confirmada|completada|cancelada
    - fecha: YYYY-MM-DD (fecha exacta)
    - desde: YYYY-MM-DD (inclusive)
    - hasta: YYYY-MM-DD (inclusive)
    - estilista_id: int
    - cliente_id: int
    - peluqueria_id: int
    - page, page_size
    """
    from datetime import date as date_type

    qs = Cita.objects.select_related(
        'cliente', 'estilista', 'servicio', 'estilista__peluqueria',
    ).order_by('-fecha', '-hora_inicio')

    # --- Filtros ---
    estado = request.query_params.get('estado')
    if estado:
        qs = qs.filter(estado=estado)

    fecha = request.query_params.get('fecha')
    if fecha:
        qs = qs.filter(fecha=fecha)

    desde = request.query_params.get('desde')
    if desde:
        qs = qs.filter(fecha__gte=desde)

    hasta = request.query_params.get('hasta')
    if hasta:
        qs = qs.filter(fecha__lte=hasta)

    estilista_id = request.query_params.get('estilista_id')
    if estilista_id:
        qs = qs.filter(estilista_id=estilista_id)

    cliente_id = request.query_params.get('cliente_id')
    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)

    peluqueria_id = request.query_params.get('peluqueria_id')
    if peluqueria_id:
        qs = qs.filter(servicio__hair_salon_id=peluqueria_id)

    # --- Paginacion ---
    page_size = min(int(request.query_params.get('page_size', 20)), 50)
    page = int(request.query_params.get('page', 1))
    inicio = (page - 1) * page_size
    fin = inicio + page_size
    pagina_qs = qs[inicio:fin]

    return Response({
        'count': qs.count(),
        'next': page + 1 if fin < qs.count() else None,
        'previous': page - 1 if page > 1 else None,
        'results': CitaSerializer(pagina_qs, many=True).data,
    })


@api_view(['POST'])
@permission_classes([EsAdminORecepcionista])
def crear_cita_recepcionista(request):
    """
    Permite a la recepcionista crear una cita en nombre de un cliente.

    POST /api/recepcionista/citas/crear/
    Body: {
        cliente_id, estilista_id, servicio_id,
        fecha, hora_inicio, observaciones (opcional)
    }
    """
    from .serializers import CrearCitaRecepcionistaSerializer

    serializer = CrearCitaRecepcionistaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    cita = serializer.save(estado='pendiente')
    cita_resp = Cita.objects.select_related(
        'cliente', 'estilista', 'servicio', 'estilista__peluqueria',
    ).get(pk=cita.id)

    return Response(CitaSerializer(cita_resp).data, status=201)


@api_view(['PATCH'])
@permission_classes([EsAdminORecepcionista])
def cambiar_estado_cita_recepcionista(request, cita_id):
    """
    Cambia el estado de una cita (confirmar, completar, cancelar).

    PATCH /api/recepcionista/citas/<id>/cambiar-estado/
    Body: { "estado": "confirmada"|"completada"|"cancelada", "observaciones": "..." }
    """
    try:
        cita = Cita.objects.select_related(
            'cliente', 'estilista', 'servicio', 'estilista__peluqueria',
        ).get(pk=cita_id)
    except Cita.DoesNotExist:
        return Response({'detail': gettext('Cita no encontrada.')}, status=404)

    nuevo_estado = request.data.get('estado')
    if not nuevo_estado:
        return Response({'estado': 'Debes enviar el campo estado.'}, status=400)

    estados_validos = {'pendiente', 'confirmada', 'completada', 'cancelada'}
    if nuevo_estado not in estados_validos:
        return Response(
            {'estado': f'Estado no valido. Opciones: {", ".join(estados_validos)}'},
            status=400,
        )

    if cita.estado == 'cancelada':
        return Response(
            {'estado': 'No se puede modificar una cita cancelada.'},
            status=400,
        )

    if cita.estado == 'completada' and nuevo_estado != 'cancelada':
        return Response(
            {'estado': 'No se puede modificar una cita completada.'},
            status=400,
        )

    observaciones = request.data.get('observaciones', '')
    if observaciones:
        prefijo = f'Cambio por recepcionista a {nuevo_estado}: '
        if cita.observaciones:
            cita.observaciones = f'{cita.observaciones}\n{prefijo}{observaciones}'
        else:
            cita.observaciones = f'{prefijo}{observaciones}'

    cita.estado = nuevo_estado
    cita.save(update_fields=['estado', 'observaciones', 'modified'])

    return Response(CitaSerializer(cita).data)


# =============================================================================
# ENDPOINTS DEL PORTAL DE ESTILISTA (adicionales al panel)
# =============================================================================

@api_view(['GET'])
@permission_classes([EsAdminOEstilista])
def citas_estilista(request):
    """
    Lista las citas del estilista autenticado con filtros.

    GET /api/estilista/mis-citas/
    Query params:
    - estado: pendiente|confirmada|completada|cancelada
    - desde/hasta: YYYY-MM-DD
    - pasadas: "true"  (solo anteriores a hoy)
    - proximas: "true" (solo desde hoy)
    - page, page_size
    """
    from datetime import date as date_type

    user = request.user

    # Admin puede ver citas de cualquier estilista
    if user.rol == 'administrador':
        target_id = request.query_params.get('estilista_id')
        if target_id:
            user = Usuario.objects.filter(pk=target_id, rol='estilista').first()
            if not user:
                return Response({'detail': gettext('Estilista no encontrado.')}, status=404)

    qs = Cita.objects.filter(
        estilista=user,
    ).select_related(
        'cliente', 'servicio', 'estilista__peluqueria',
    ).order_by('-fecha', '-hora_inicio')

    estado = request.query_params.get('estado')
    if estado:
        qs = qs.filter(estado=estado)

    desde = request.query_params.get('desde')
    if desde:
        qs = qs.filter(fecha__gte=desde)

    hasta = request.query_params.get('hasta')
    if hasta:
        qs = qs.filter(fecha__lte=hasta)

    if request.query_params.get('pasadas') == 'true':
        qs = qs.filter(fecha__lt=date_type.today())

    if request.query_params.get('proximas') == 'true':
        qs = qs.filter(fecha__gte=date_type.today())

    # Paginacion
    page_size = min(int(request.query_params.get('page_size', 20)), 50)
    page = int(request.query_params.get('page', 1))
    inicio = (page - 1) * page_size
    fin = inicio + page_size
    pagina_qs = qs[inicio:fin]

    return Response({
        'count': qs.count(),
        'next': page + 1 if fin < qs.count() else None,
        'previous': page - 1 if page > 1 else None,
        'results': CitaSerializer(pagina_qs, many=True).data,
    })


@api_view(['PATCH'])
@permission_classes([EsAdminOEstilista])
def cambiar_estado_cita_estilista(request, cita_id):
    """
    El estilista cambia el estado de SUS propias citas.
    Puede confirmar pendientes y completar confirmadas.
    No puede cancelar (eso lo hace la recepcionista).

    PATCH /api/estilista/mis-citas/<id>/cambiar-estado/
    Body: { "estado": "confirmada"|"completada", "observaciones": "..." }
    """
    try:
        cita = Cita.objects.select_related(
            'cliente', 'estilista', 'servicio', 'estilista__peluqueria',
        ).get(pk=cita_id, estilista=request.user)
    except Cita.DoesNotExist:
        return Response({'detail': gettext('Cita no encontrada.')}, status=404)

    nuevo_estado = request.data.get('estado')
    if not nuevo_estado:
        return Response({'estado': 'Debes enviar el campo estado.'}, status=400)

    estados_validos = {'pendiente', 'confirmada', 'completada', 'cancelada'}
    if nuevo_estado not in estados_validos:
        return Response({'estado': 'Estado no valido.'}, status=400)

    if cita.estado == 'cancelada':
        return Response({'estado': 'No se puede modificar una cita cancelada.'}, status=400)

    if cita.estado == 'completada':
        return Response({'estado': 'No se puede modificar una cita completada.'}, status=400)

    if nuevo_estado == 'completada' and cita.estado != 'confirmada':
        return Response(
            {'estado': 'Solo se pueden completar citas confirmadas. Confirma primero.'},
            status=400,
        )

    observaciones = request.data.get('observaciones', '')
    if observaciones:
        if cita.observaciones:
            cita.observaciones = f'{cita.observaciones}\n{observaciones}'
        else:
            cita.observaciones = observaciones

    cita.estado = nuevo_estado
    cita.save(update_fields=['estado', 'observaciones', 'modified'])

    return Response(CitaSerializer(cita).data)


@api_view(['PATCH'])
@permission_classes([EsAdminOEstilista])
def editar_perfil_estilista(request):
    """
    El estilista edita su especialidad, telefono y nombre.
    El admin puede editar el de otro estilista pasando usuario_id.

    PATCH /api/estilista/perfil/
    Body: { "especialidad": "...", "telefono": "...", "first_name": "...", "last_name": "..." }
    """
    user = request.user

    if user.rol == 'administrador':
        target_id = request.data.get('usuario_id')
        if target_id:
            user = Usuario.objects.filter(pk=target_id, rol='estilista').first()
            if not user:
                return Response({'detail': gettext('Estilista no encontrado.')}, status=404)

    campos_permitidos = ['especialidad', 'telefono', 'first_name', 'last_name']
    actualizados = []

    for campo in campos_permitidos:
        if campo in request.data:
            setattr(user, campo, request.data[campo])
            actualizados.append(campo)

    if not actualizados:
        return Response(
            {'detail': f'No se envio ningun campo editable. Campos: {", ".join(campos_permitidos)}'},
            status=400,
        )

    user.save(update_fields=actualizados + ['modified'])

    return Response({
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'nombre_completo': user.get_full_name() or user.username,
        'email': user.email,
        'telefono': user.telefono,
        'especialidad': user.especialidad,
        'rol': user.rol,
    })


@api_view(['GET'])
@permission_classes([EsAdminOEstilista])
def servicios_estilista(request):
    """
    Servicios disponibles en la peluqueria del estilista.

    GET /api/estilista/servicios/
    """
    user = request.user

    if user.rol == 'administrador':
        target_id = request.query_params.get('estilista_id')
        if target_id:
            user = Usuario.objects.filter(pk=target_id, rol='estilista').first()
            if not user:
                return Response({'detail': gettext('Estilista no encontrado.')}, status=404)

    if not user.peluqueria_id:
        return Response(
            {'detail': 'El estilista no tiene peluqueria asignada.'},
            status=404,
        )

    servicios = Servicio.objects.filter(
        hair_salon_id=user.peluqueria_id,
        status='active',
    ).order_by('nombre')

    return Response(ServicioPublicoSerializer(servicios, many=True).data)


@api_view(['GET'])
@permission_classes([EsAdminOEstilista])
def estadisticas_estilista(request):
    """
    Estadisticas de productividad del estilista.

    GET /api/estilista/estadisticas/
    Query params:
    - periodo: "mes" (default) | "semana" | "hoy"
    """
    from datetime import date as date_type, timedelta
    from django.db.models import Count, Sum

    user = request.user

    if user.rol == 'administrador':
        target_id = request.query_params.get('estilista_id')
        if target_id:
            user = Usuario.objects.filter(pk=target_id, rol='estilista').first()
            if not user:
                return Response({'detail': gettext('Estilista no encontrado.')}, status=404)

    hoy = date_type.today()
    periodo = request.query_params.get('periodo', 'mes')

    if periodo == 'hoy':
        desde = hoy
    elif periodo == 'semana':
        desde = hoy - timedelta(days=hoy.weekday())
    else:
        desde = hoy.replace(day=1)

    citas_qs = Cita.objects.filter(
        estilista=user,
        fecha__gte=desde,
        fecha__lte=hoy,
    ).select_related('servicio', 'cliente')

    completadas = citas_qs.filter(estado='completada')
    canceladas = citas_qs.filter(estado='cancelada')
    pendientes = citas_qs.filter(estado='pendiente')
    confirmadas = citas_qs.filter(estado='confirmada')

    ingresos = completadas.aggregate(total=Sum('servicio__precio'))['total'] or 0

    # Servicios mas solicitados
    servicios_top = list(
        completadas
        .values('servicio__nombre')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')[:5]
    )

    # Clientes frecuentes
    clientes_top = list(
        completadas
        .values('cliente__id', 'cliente__first_name', 'cliente__last_name')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')[:5]
    )

    # Citas por dia
    citas_por_dia = list(
        citas_qs
        .values('fecha')
        .annotate(total=Count('id'), completadas_dia=Count('id', filter=Q(estado='completada')))
        .order_by('fecha')
    )

    return Response({
        'periodo': periodo,
        'desde': desde.isoformat(),
        'hasta': hoy.isoformat(),
        'resumen': {
            'total_citas': citas_qs.count(),
            'completadas': completadas.count(),
            'canceladas': canceladas.count(),
            'pendientes': pendientes.count(),
            'confirmadas': confirmadas.count(),
            'ingresos_estimados': float(ingresos),
        },
        'servicios_top': servicios_top,
        'clientes_frecuentes': [
            {
                'cliente_id': c['cliente__id'],
                'nombre': (
                    (c['cliente__first_name'] or '')
                    + ' '
                    + (c['cliente__last_name'] or '')
                ).strip(),
                'citas': c['cantidad'],
            }
            for c in clientes_top
        ],
        'citas_por_dia': [
            {
                'fecha': str(c['fecha']),
                'total': c['total'],
                'completadas': c['completadas_dia'],
            }
            for c in citas_por_dia
        ],
    })