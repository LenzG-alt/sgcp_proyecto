from datetime import datetime
from django.utils.translation import gettext_lazy


from django.core.exceptions import ValidationError
from django.db import models

from .base import ModeloAuditable


class EstadoCita(models.TextChoices):
    """Estados validos para una cita.
    
    Django valida automaticamente los choices, pero mantenemos la
    validacion explicita en clean() como defensa adicional.
    """
    PENDIENTE = 'pendiente', gettext_lazy('Pendiente')
    CONFIRMADA = 'confirmada', gettext_lazy('Confirmada')
    COMPLETADA = 'completada', gettext_lazy('Completada')
    CANCELADA = 'cancelada', gettext_lazy('Cancelada')


class Cita(ModeloAuditable):
    """
    Gestiona las reservas de citas en la peluqueria.

    RELACIONES:
    - cliente:    FK hacia Usuario (related_name='citas_como_cliente')
    - estilista:  FK hacia Usuario con limit_choices_to (related_name='citas_como_estilista')
    - servicio:   FK hacia Servicio (related_name='citas')

    Se eliminan los campos redundantes:
    - 'fecha_creacion': ya lo provee ModeloAuditable como 'created'
    - 'user' fue renombrado a 'cliente' para claridad semantica
    - 'stylist' fue renombrado a 'estilista' y ahora apunta a Usuario
    """

    # --- Foreign Keys ---

    # El cliente es un Usuario (tipicamente con rol='cliente')
    cliente = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='citas_como_cliente',
        help_text=gettext_lazy('Cliente que reserva la cita'),
    )

    # El estilista es un Usuario con rol='estilista'.
    # limit_choices_to restringe el queryset en el admin y forms de DRF
    # para que solo muestre usuarios con rol estilista.
    estilista = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='citas_como_estilista',
        limit_choices_to={'rol': 'estilista'},
        help_text=gettext_lazy('Estilista asignado a la cita'),
    )

    # El servicio solicitado
    servicio = models.ForeignKey(
        'Servicio',
        on_delete=models.CASCADE,
        related_name='citas',
        help_text=gettext_lazy('Servicio reservado'),
    )

    # --- Campos de la cita ---

    fecha = models.DateField(help_text=gettext_lazy('Fecha de la cita'))
    hora_inicio = models.TimeField(help_text=gettext_lazy('Hora de inicio'))
    hora_fin = models.TimeField(help_text=gettext_lazy('Hora de fin'))

    # Se usa TextChoices para validar automaticamente los valores
    estado = models.CharField(
        max_length=20,
        choices=EstadoCita.choices,
        default=EstadoCita.PENDIENTE,
        help_text=gettext_lazy('Estado actual de la cita'),
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text=gettext_lazy('Notas adicionales sobre la cita'),
    )

    # NOTA: No se define 'fecha_creacion' ni 'status' porque:
    # - ModeloAuditable ya provee 'created' (equivalente a fecha_creacion)
    # - ModeloAuditable ya provee 'status' (registro activo/inactivo)

    def clean(self):
        """Validaciones de negocio para la cita."""

        # 1. La hora de fin debe ser posterior a la hora de inicio
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError(
                gettext_lazy('La hora de fin debe ser mayor que la hora de inicio.')
            )

        # 2. Validar que el estado sea uno de los permitidos
        # (Django ya lo valida por choices, pero lo mantenemos como defensa)
        estados_validos = {choice.value for choice in EstadoCita}
        if self.estado not in estados_validos:
            raise ValidationError(
                {'estado': gettext_lazy('Estado de cita no valido.')}
            )

        # 3. Validaciones que requieren que el servicio ya exista en BD
        if self.servicio_id:
            # La duracion real de la cita debe coincidir con la duracion del servicio
            inicio = datetime.combine(self.fecha, self.hora_inicio)
            fin = datetime.combine(self.fecha, self.hora_fin)
            duracion_real = int((fin - inicio).total_seconds() / 60)

            if duracion_real != self.servicio.duracion_minutos:
                raise ValidationError({
                    'hora_fin': (
                        gettext_lazy('La duracion de la cita debe coincidir con la duracion del servicio.')
                    ),
                })

            # El estilista y el servicio deben pertenecer a la misma peluqueria.
            # Ahora accedemos via usuario.estilista.peluqueria (FK en Usuario)
            # y servicio.hair_salon (FK en Servicio).
            if (
                self.estilista.peluqueria_id
                and self.estilista.peluqueria_id != self.servicio.hair_salon_id
            ):
                raise ValidationError(
                    gettext_lazy('El estilista y el servicio deben pertenecer a la misma peluqueria.')
                )

        # 4. Detectar conflictos de horario para el mismo estilista
        #    Se usa el related_name 'citas_como_estilista' indirectamente
        #    filtrando directamente por el campo FK.
        conflictos = Cita.objects.filter(
            estilista=self.estilista,
            fecha=self.fecha,
        ).exclude(pk=self.pk)

        for otra_cita in conflictos:
            # Dos intervalos se superponen si:
            # inicio_actual < fin_otra AND fin_actual > inicio_otra
            if (
                self.hora_inicio < otra_cita.hora_fin
                and self.hora_fin > otra_cita.hora_inicio
            ):
                raise ValidationError(
                    gettext_lazy('La cita se cruza con otra reserva del estilista.')
                )

    class Meta:
        db_table = 'appointments'
        verbose_name = gettext_lazy('Cita')
        verbose_name_plural = gettext_lazy('Citas')
        ordering = ['-fecha', 'hora_inicio']

    def __str__(self):
        # Usamos get_full_name() en lugar de un campo 'nombre' inventado
        cliente_nombre = self.cliente.get_full_name() or self.cliente.username
        estilista_nombre = self.estilista.get_full_name() or self.estilista.username
        return f"Cita #{self.id} | {cliente_nombre} con {estilista_nombre}"