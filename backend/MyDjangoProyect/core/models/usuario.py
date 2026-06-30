from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy


from .base import ModeloAuditable, validar_telefono

from django.contrib.auth.models import UserManager

class UsuarioManager(UserManager):

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'administrador')

        return super().create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )

class Rol(models.TextChoices):
    """Roles disponibles en el sistema.
    
    Se agrega ESTILISTA para que los estilistas sean simplemente
    registros de Usuario con este rol, eliminando la necesidad
    de un modelo Estilista separado.
    """

    CLIENTE = 'cliente', gettext_lazy('Cliente')
    ESTILISTA = 'estilista', gettext_lazy('Estilista')
    ADMINISTRADOR = 'administrador', gettext_lazy('Administrador')
    RECEPCIONISTA = 'recepcionista', gettext_lazy('Recepcionista')


class Usuario(ModeloAuditable, AbstractUser):
    """
    Modelo de usuario personalizado.

    Hereda de ModeloAuditable (campos de auditoria: created, modified, etc.)
    y de AbstractUser (password, username, is_active, date_joined, etc.).

    El orden de herencia importa: los mixins primero, AbstractUser al final.
    
    NOTA: No se usan campos 'nombre' ni 'contraseña' inventados.
    AbstractUser provee first_name, last_name, password, is_active, etc.
    Para obtener el nombre completo usar siempre get_full_name().
    """

    # AbstractUser ya trae 'username', 'password', 'first_name', 'last_name',
    # 'email', 'is_active', 'is_staff', 'is_superuser', 'date_joined', etc.
    objects = UsuarioManager()

    # Sobrescribimos email para asegurar unicidad
    email = models.EmailField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.CLIENTE,
        help_text=gettext_lazy('Rol del usuario en el sistema'),
    )

    # FK opcional: solo los estilistas tendran una peluqueria asignada.
    # Se usa SET_NULL para que si se elimina la peluqueria,
    # el estilista no se pierda, solo queda sin peluqueria asignada.
    peluqueria = models.ForeignKey(
        'Peluqueria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estilistas',
        help_text=gettext_lazy('Peluqueria asignada (requerido para rol estilista)'),
    )

    # Campo para especialidad de estilistas (opcional, solo aplicable a estilistas)
    especialidad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=gettext_lazy('Especialidad del estilista (ej: colorista, barbero)'),
    )

    def clean(self):
        # Validacion personalizada del telefono
        if self.telefono:
            validar_telefono(self.telefono)

        # Si el rol es estilista, deberia tener peluqueria asignada
        if self.rol == Rol.ESTILISTA and not self.peluqueria_id:
            raise ValidationError({
                'peluqueria': gettext_lazy('Un estilista debe tener una peluqueria asignada.'),
            })

        return super().clean()

    class Meta:
        db_table = 'users'
        verbose_name = gettext_lazy('Usuario')
        verbose_name_plural = gettext_lazy('Usuarios')

    def __str__(self):
        # get_full_name() retorna 'first_name last_name' o cadena vacia si ambos estan vacios
        nombre_completo = self.get_full_name() or self.username
        return f"{nombre_completo} ({self.email})"