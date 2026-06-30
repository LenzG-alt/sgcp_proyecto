from rest_framework import serializers
from django.utils.translation import gettext_lazy, gettext


from .models import Peluqueria, Usuario, Servicio, Cita, Horario


# =============================================================================
# SERIALIZERS DE RESUMEN (para incrustar en relaciones anidadas)
# =============================================================================

class PeluqueriaSummarySerializer(serializers.ModelSerializer):
    """Resumen de peluqueria para relaciones anidadas.

    Se usa en ServicioSerializer y en el dashboard para mostrar
    datos basicos de la peluqueria sin exponer todos sus campos.
    """

    class Meta:
        model = Peluqueria
        fields = ['id', 'nombre', 'direccion', 'telefono', 'descripcion']


class UsuarioSummarySerializer(serializers.ModelSerializer):
    """Resumen de usuario para relaciones anidadas (Cita, Horario).

    CORRECCIONES respecto al codigo anterior:
    - Se elimina el campo 'nombre': AbstractUser NO tiene ese campo.
      Se agrega 'nombre_completo' como campo computado que invoca
      get_full_name() del modelo.
    - Se elimina 'status': para saber si un usuario esta activo se
      debe usar 'is_active' que provee AbstractUser por defecto (Regla #7).
    """

    # Campo computado: invoca get_full_name() del modelo Usuario
    nombre_completo = serializers.CharField(
        source='get_full_name',
        read_only=True,
    )

    class Meta:
        model = Usuario
        fields = [
            'id',
            'nombre_completo',
            'email',
            'telefono',
            'rol',
            'is_active',
        ]


class ServicioSummarySerializer(serializers.ModelSerializer):
    """Resumen de servicio para relaciones anidadas (Cita)."""

    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'descripcion', 'precio', 'duracion_minutos']


# =============================================================================
# SERIALIZERS PRINCIPALES (CRUD completo por modelo)
# =============================================================================

class PeluqueriaSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Peluqueria.

    No se modifican campos en este modelo, solo se limpia
    la consistencia del serializer.
    """

    class Meta:
        model = Peluqueria
        fields = [
            'id', 'nombre', 'direccion', 'telefono',
            'descripcion', 'fecha_registro',
        ]
        read_only_fields = ['id', 'fecha_registro']


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Usuario.

    CORRECCIONES criticas respecto al codigo anterior:
    - Se elimina 'nombre': AbstractUser provee 'first_name' y 'last_name'.
    - Se elimina 'contraseña': AbstractUser provee 'password' directamente.
    - Se elimina 'status': se usa 'is_active' de AbstractUser (Regla #7).
    - Se elimina 'fecha_registro': AbstractUser provee 'date_joined'.
    - La relacion 'citas' ahora usa el related_name 'citas_como_cliente'
      definido en el modelo Cita (Regla #3).
    - Se exponen 'peluqueria' y 'especialidad' para estilistas.
    - Se agrega 'password' (write_only) para que el admin pueda crear
      usuarios con contrasena desde el panel de gestion.
    """

    # Se usa el related_name 'citas_como_cliente' definido en Cita.cliente
    citas_como_cliente = serializers.SerializerMethodField()

    # Campo de contrasena: solo escritura, opcional.
    # Si se envia en POST, se hashea automaticamente.
    # Si se envia en PATCH/PUT, se actualiza la contrasena.
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=6,
        allow_blank=True,
        help_text=gettext_lazy('Contrasena del usuario (minimo 6 caracteres). Solo al crear.'),
    )

    # Resumen de peluqueria para lectura
    peluqueria_data = PeluqueriaSummarySerializer(
        source='peluqueria', read_only=True
    )

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'telefono',
            'rol',
            'is_active',
            'password',
            'peluqueria',
            'peluqueria_data',
            'especialidad',
            'citas_como_cliente',
        ]
        read_only_fields = ['id', 'date_joined']

    def get_citas_como_cliente(self, obj):
        """Retorna las citas donde este usuario es el cliente.

        Usa el related_name 'citas_como_cliente' definido en
        Cita.cliente (Regla #3) en lugar de hacer joins manuales.
        """
        return CitaSerializer(
            obj.citas_como_cliente.all(),
            many=True,
        ).data

    def create(self, validated_data):
        """Crea un usuario usando create_user() para hashear la contrasena.

        Si se proporciona 'password', se usa create_user().
        Si no se proporciona, se usa create() (el usuario no podra
        iniciar sesion hasta que se le asigne una contrasena).
        """
        password = validated_data.pop('password', None)

        if password:
            user = Usuario.objects.create_user(password=password, **validated_data)
        else:
            user = Usuario.objects.create(**validated_data)

        return user

    def update(self, instance, validated_data):
        """Actualiza un usuario. Si se envia 'password', se actualiza la contrasena."""
        password = validated_data.pop('password', None)

        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save(update_fields=['password'])

        return user


class ServicioSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Servicio.

    Incluye la peluqueria anidada en modo lectura.
    """

    # Relacion anidada de solo lectura
    hair_salon = PeluqueriaSummarySerializer(read_only=True)

    class Meta:
        model = Servicio
        fields = [
            'id', 'nombre', 'descripcion', 'precio',
            'duracion_minutos', 'hair_salon',
        ]
        read_only_fields = ['id']


class CitaSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Cita.

    CORRECCIONES criticas respecto al codigo anterior:
    - 'user' renombrado a 'cliente' (FK a Usuario, related_name='citas_como_cliente').
    - 'stylist' renombrado a 'estilista' (FK a Usuario, NO al modelo eliminado Estilista).
    - 'service' renombrado a 'servicio' (coherencia con el nombre del modelo Servicio).
    - 'fecha_creacion' eliminado: se usa 'created' heredado de ModeloAuditable.
    - Se eliminan todas las referencias al modelo Estilista y EstilistaSummarySerializer.

    PATRON DE LECTURA/ESCRITURA:
    - Para lectura (GET): se usan los campos anidados (UsuarioSummarySerializer, etc.)
      que muestran datos ricos del usuario, servicio, etc.
    - Para escritura (POST/PUT/PATCH): se exponen campos *_id con PrimaryKeyRelatedField
      para que el cliente envie solo los IDs.
    """

    # --- Campos de lectura (anidados, read_only) ---
    cliente = UsuarioSummarySerializer(read_only=True)
    estilista = UsuarioSummarySerializer(read_only=True)
    servicio = ServicioSummarySerializer(read_only=True)

    # --- Campos de escritura (solo IDs, write_only) ---
    # Permite crear/actualizar citas enviando los IDs directamente.
    # El parametro 'source' conecta con el nombre del campo en el modelo.
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        write_only=True,
        source='cliente',
    )
    estilista_id = serializers.PrimaryKeyRelatedField(
        # Solo muestra usuarios con rol='estilista' (limit_choices_to del modelo)
        queryset=Usuario.objects.filter(rol='estilista'),
        write_only=True,
        source='estilista',
    )
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.all(),
        write_only=True,
        source='servicio',
    )

    class Meta:
        model = Cita
        fields = [
            'id',
            # Lectura (anidados)
            'cliente',
            'estilista',
            'servicio',
            # Escritura (IDs)
            'cliente_id',
            'estilista_id',
            'servicio_id',
            # Datos de la cita
            'fecha',
            'hora_inicio',
            'hora_fin',
            'estado',
            'observaciones',
            'created',
        ]
        read_only_fields = ['id', 'created']


# =============================================================================
# SERIALIZERS DEL PORTAL DEL CLIENTE
# =============================================================================

class CitaClienteSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para que el cliente vea SUS citas.

    Diferencias con CitaSerializer general:
    - No expone cliente_id (el cliente es siempre request.user).
    - Muestra el nombre del estilista y sus datos de contacto.
    - Muestra el servicio con precio y duracion.
    - Incluye la peluqueria donde se realizara la cita.
    """

    # Datos anidados de solo lectura
    estilista = serializers.SerializerMethodField()
    servicio = ServicioSummarySerializer(read_only=True)
    peluqueria = serializers.SerializerMethodField()

    class Meta:
        model = Cita
        fields = [
            'id',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'estado',
            'observaciones',
            'created',
            'estilista',
            'servicio',
            'peluqueria',
        ]
        read_only_fields = fields

    def get_estilista(self, obj):
        """Retorna datos publicos del estilista (nombre, especialidad)."""
        u = obj.estilista
        return {
            'id': u.id,
            'nombre_completo': u.get_full_name() or u.username,
            'especialidad': u.especialidad or '',
        }

    def get_peluqueria(self, obj):
        """Retorna datos de la peluqueria donde es la cita."""
        p = obj.estilista.peluqueria
        if not p:
            return None
        return {
            'id': p.id,
            'nombre': p.nombre,
            'direccion': p.direccion,
            'telefono': p.telefono,
        }


class CrearCitaSerializer(serializers.ModelSerializer):
    """
    Serializer para que un CLIENTE cree una nueva cita.

    El cliente NO envia cliente_id: se toma automaticamente de
    request.user en la vista.

    Validaciones:
    - El estilista debe estar activo y tener peluqueria asignada.
    - El servicio debe pertenecer a la misma peluqueria del estilista.
    - La duracion de la cita debe coincidir con la del servicio.
    - No debe haber conflictos de horario con otras citas del estilista.
    - El estilista debe tener horario activo ese dia y hora.
    """

    estilista_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(
            rol='estilista', is_active=True,
        ).select_related('peluqueria'),
        write_only=True,
        source='estilista',
        error_messages={
            'does_not_exist': gettext_lazy('El estilista seleccionado no existe o no esta disponible.'),
        },
    )
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.filter(status='active').select_related('hair_salon'),
        write_only=True,
        source='servicio',
        error_messages={
            'does_not_exist': gettext_lazy('El servicio seleccionado no existe.'),
        },
    )

    class Meta:
        model = Cita
        fields = [
            'estilista_id',
            'servicio_id',
            'fecha',
            'hora_inicio',
            'observaciones',
        ]

    def validate(self, attrs):
        """
        Validaciones de negocio para la creacion de citas:

        1. La fecha debe ser hoy o futura.
        2. El estilista y el servicio deben ser de la misma peluqueria.
        3. Calcular hora_fin automaticamente segun duracion del servicio.
        4. El estilista debe tener horario activo ese dia.
        5. La hora solicitada debe estar dentro del horario del estilista.
        6. No debe haber conflictos con otras citas.
        """
        from datetime import date, datetime, timedelta

        estilista = attrs['estilista']
        servicio = attrs['servicio']
        fecha = attrs['fecha']
        hora_inicio = attrs['hora_inicio']

        # 1. La fecha no puede ser pasada
        hoy = date.today()
        if fecha < hoy:
            raise serializers.ValidationError({
                'fecha': gettext_lazy('No se pueden crear citas en fechas pasadas.'),
            })

        # 2. Estilista y servicio deben pertenecer a la misma peluqueria
        if (
            estilista.peluqueria_id
            and estilista.peluqueria_id != servicio.hair_salon_id
        ):
            raise serializers.ValidationError({
                'estilista_id': (
                    gettext_lazy('El estilista seleccionado no pertenece a la misma sucursal donde se ofrece este servicio.')
                ),
            })

        # 3. Calcular hora_fin segun la duracion del servicio
        hora_fin_dt = (
            datetime.combine(fecha, hora_inicio)
            + timedelta(minutes=servicio.duracion_minutos)
        )
        attrs['hora_fin'] = hora_fin_dt.time()

        # 4. Verificar que el estilista tiene horario activo ese dia
        from .models import Horario
        dias_map = {
            0: 'lunes', 1: 'martes', 2: 'miercoles',
            3: 'jueves', 4: 'viernes', 5: 'sabado', 6: 'domingo',
        }
        dia_semana = dias_map.get(fecha.weekday(), '')

        horarios_dia = Horario.objects.filter(
            estilista=estilista,
            dia_semana=dia_semana,
            activo=True,
        )

        if not horarios_dia.exists():
            raise serializers.ValidationError({
                'fecha': (
                    gettext('El estilista no tiene horario disponible el dia {dia_semana}').format(dia_semana=dia_semana)
                ),
            })

        # 5. La hora solicitada debe estar dentro de algun turno
        hora_esta_dentro = False
        for horario in horarios_dia:
            if horario.hora_inicio <= hora_inicio < horario.hora_fin:
                # Tambien verificar que hora_fin cae dentro del turno
                if attrs['hora_fin'] <= horario.hora_fin:
                    hora_esta_dentro = True
                    break

        if not hora_esta_dentro:
            raise serializers.ValidationError({
                'hora_inicio': (
                    gettext_lazy('La hora seleccionada esta fuera del horario de atencion del estilista.')
                ),
            })

        # 6. Detectar conflictos con otras citas del estilista
        conflictos = Cita.objects.filter(
            estilista=estilista,
            fecha=fecha,
            estado__in=['pendiente', 'confirmada'],
        )

        for otra in conflictos:
            if (
                hora_inicio < otra.hora_fin
                and attrs['hora_fin'] > otra.hora_inicio
            ):
                raise serializers.ValidationError({
                    'hora_inicio': (
                        'El estilista ya tiene una cita asignada '
                        f'entre las {otra.hora_inicio} y {otra.hora_fin}.'
                    ),
                })

        return attrs


class ServicioPublicoSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar servicios disponibles al cliente.

    Incluye la peluqueria donde se ofrece el servicio y
    los estilistas disponibles para ese servicio.
    """
    peluqueria = PeluqueriaSummarySerializer(source='hair_salon', read_only=True)

    class Meta:
        model = Servicio
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio',
            'duracion_minutos',
            'peluqueria',
        ]


class EstilistaDisponibleSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar estilistas disponibles al cliente.

    Incluye nombre, especialidad, peluqueria y los servicios
    que ofrece (basado en la peluqueria a la que pertenece).
    """
    nombre_completo = serializers.CharField(
        source='get_full_name', read_only=True,
    )
    peluqueria = PeluqueriaSummarySerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id',
            'nombre_completo',
            'especialidad',
            'peluqueria',
        ]


class HorarioEstilistaSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para mostrar el horario de un estilista
    al momento de que el cliente elige fecha y hora.
    """

    class Meta:
        model = Horario
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'activo']


class HorarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Horario (antes HorarioEstilista).

    CORRECCIONES:
    - 'stylist' renombrado a 'estilista' (FK a Usuario, NO a Estilista).
    - Se usa UsuarioSummarySerializer para mostrar datos del estilista.
    - Se agrega estilista_id para escritura via PrimaryKeyRelatedField.
    """

    # --- Campo de lectura (anidado, read_only) ---
    estilista = UsuarioSummarySerializer(read_only=True)

    # --- Campo de escritura (solo ID, write_only) ---
    estilista_id = serializers.PrimaryKeyRelatedField(
        # Solo muestra usuarios con rol='estilista'
        queryset=Usuario.objects.filter(rol='estilista'),
        write_only=True,
        source='estilista',
    )

    class Meta:
        model = Horario
        fields = [
            'id',
            'estilista',
            'estilista_id',
            'dia_semana',
            'hora_inicio',
            'hora_fin',
            'activo',
        ]
        read_only_fields = ['id']


class CrearCitaRecepcionistaSerializer(CrearCitaSerializer):
    """
    Serializer para que la RECEPCIONISTA cree una cita.
    Igual que CrearCitaSerializer pero incluye cliente_id
    (el cliente no es request.user, sino quien la recepcionista seleccione).
    """

    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(rol='cliente', is_active=True),
        write_only=True,
        source='cliente',
        error_messages={
            'does_not_exist': gettext_lazy('El cliente seleccionado no existe o no esta activo.'),
        },
    )

    class Meta(CrearCitaSerializer.Meta):
        fields = CrearCitaSerializer.Meta.fields + ['cliente_id']