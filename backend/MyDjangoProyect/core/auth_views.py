"""
Serializers y vistas de autenticacion para SGCP.

Contiene:
1. CustomTokenObtainPairSerializer — Incluye datos del usuario
   (rol, nombre, email) en la respuesta del login.
2. RegistroSerializer — Valida la creacion de nuevos usuarios.
3. registro_view — Endpoint POST /api/registro/ para crear cuentas.
4. perfil_view — Endpoint GET /api/perfil/ para obtener datos del
   usuario autenticado (util para que el frontend sepa que mostrar).
"""

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.translation import gettext_lazy, gettext


from .models import Usuario


# =============================================================================
# 1. CUSTOM TOKEN SERIALIZER
# =============================================================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extiende el serializer por defecto de SimpleJWT para incluir
    informacion del usuario tanto en el payload del token como
    en la respuesta del login.

    El frontend usa estos datos para:
    - Decidir que layout/rutas mostrar segun el rol.
    - Mostrar el nombre del usuario en la interfaz.
    - Verificar si la cuenta esta activa.
    """

    @classmethod
    def get_token(cls, user):
        """Inyecta datos del usuario en el payload del JWT."""
        token = super().get_token(user)

        # Datos del usuario en el token (accesibles via decode)
        token['user_id'] = user.id
        token['rol'] = user.rol
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_active'] = user.is_active

        return token

    def validate(self, attrs):
        """Agrega datos del usuario en la respuesta del login."""
        data = super().validate(attrs)

        # Si la cuenta esta inactiva, no permitir login
        if not self.user.is_active:
            raise serializers.ValidationError({
                'detail': gettext('Tu cuenta esta desactivada. Contacta al administrador.')
            })

        # Informacion del usuario para el frontend
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'rol': self.user.rol,
            'is_active': self.user.is_active,
            'telefono': self.user.telefono or '',
            'nombre_completo': (
                self.user.get_full_name() or self.user.username
            ),
            # Datos adicionales para estilistas
            'especialidad': self.user.especialidad or '',
            'peluqueria_id': self.user.peluqueria_id,
        }

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista de login que usa el serializer personalizado."""
    serializer_class = CustomTokenObtainPairSerializer


# =============================================================================
# 2. REGISTRO SERIALIZER
# =============================================================================

class RegistroSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de nuevos usuarios.

    Por defecto crea usuarios con rol='cliente'.
    Solo un administrador puede crear usuarios con otros roles
    (eso se hace via el endpoint de usuarios, no este).
    """

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        error_messages={
            'min_length': 'La contraseña debe tener al menos 6 caracteres.',
        },
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text='Confirmacion de la contraseña',
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'telefono',
        ]

    def validate_email(self, value):
        """Verifica que el email no este ya registrado."""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                gettext_lazy('Ya existe una cuenta con este correo electronico.')
            )
        return value

    def validate_username(self, value):
        """Verifica que el username no este ya registrado."""
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                gettext_lazy('Este nombre de usuario ya esta en uso.')
            )
        return value

    def validate(self, attrs):
        """Verifica que las contraseñas coincidan."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        return attrs

    def create(self, validated_data):
        """
        Crea el usuario usando create_user() para hashear la contraseña.
        Todos los registros publicos tienen rol='cliente'.
        """
        validated_data.pop('password_confirm')

        user = Usuario.objects.create_user(
            rol='cliente',  # Registro publico siempre es cliente
            **validated_data,
        )
        return user


# =============================================================================
# 3. REGISTRO VIEW
# =============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def registro_view(request):
    """
    Endpoint publico para crear nuevas cuentas de cliente.

    POST /api/registro/
    Body: { username, email, password, password_confirm, first_name, last_name, telefono }
    Response: { user: {...}, access: "...", refresh: "..." }
    """
    serializer = RegistroSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()

    # Generar tokens para auto-login despues del registro
    token_serializer = CustomTokenObtainPairSerializer()
    token_serializer.user = user
    tokens = token_serializer.get_token(user)

    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    # Inyectar datos adicionales en el token
    for key, value in {
        'user_id': user.id,
        'rol': user.rol,
        'email': user.email,
    }.items():
        refresh[key] = value

    return Response(
        {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'rol': user.rol,
                'nombre_completo': user.get_full_name() or user.username,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
        status=status.HTTP_201_CREATED,
    )


# =============================================================================
# 4. PERFIL VIEW
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_view(request):
    """
    Endpoint para que el usuario autenticado obtenga su propio perfil.

    GET /api/perfil/
    Response: { id, username, email, first_name, last_name, rol, ... }

    El frontend lo usa para:
    - Verificar que el token sigue siendo valido.
    - Obtener datos frescos del usuario al cargar la app.
    - Decidir que layout mostrar segun el rol.
    """
    user = request.user

    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'telefono': user.telefono or '',
        'rol': user.rol,
        'is_active': user.is_active,
        'nombre_completo': user.get_full_name() or user.username,
        'especialidad': user.especialidad or '',
        'peluqueria_id': user.peluqueria_id,
        'date_joined': user.date_joined.isoformat(),
    }

    # Si es estilista, incluir datos de la peluqueria
    if user.rol == 'estilista' and user.peluqueria_id:
        from .models import Peluqueria
        peluqueria = Peluqueria.objects.filter(pk=user.peluqueria_id).first()
        if peluqueria:
            data['peluqueria'] = {
                'id': peluqueria.id,
                'nombre': peluqueria.nombre,
                'direccion': peluqueria.direccion,
                'telefono': peluqueria.telefono,
            }

    # Si es cliente, incluir resumen rapido de sus citas
    if user.rol == 'cliente':
        from .models import Cita
        from datetime import date

        hoy = date.today()
        citas_cliente = Cita.objects.filter(
            cliente=user,
        ).order_by('-fecha', '-hora_inicio')

        data['resumen_citas'] = {
            'total': citas_cliente.count(),
            'pendientes': citas_cliente.filter(
                estado='pendiente', fecha__gte=hoy,
            ).count(),
            'proxima_cita': None,
        }

        proxima = (
            citas_cliente
            .filter(estado__in=['pendiente', 'confirmada'], fecha__gte=hoy)
            .first()
        )
        if proxima:
            data['resumen_citas']['proxima_cita'] = {
                'id': proxima.id,
                'fecha': proxima.fecha.isoformat(),
                'hora_inicio': proxima.hora_inicio.isoformat(),
                'hora_fin': proxima.hora_fin.isoformat(),
                'estado': proxima.estado,
                'servicio': proxima.servicio.nombre,
                'estilista': (
                    proxima.estilista.get_full_name()
                    or proxima.estilista.username
                ),
            }

    return Response(data)