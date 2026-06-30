from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy


from .base import ModeloAuditable


class Horario(ModeloAuditable):
    """
    Describe la disponibilidad semanal de cada estilista.

    RENOMBRADO: antes se llamaba 'HorarioEstilista' y apuntaba al modelo
    eliminado 'Estilista'. Ahora se llama 'Horario' y su FK apunta
    directamente a 'Usuario' con limit_choices_to.

    RELACIONES:
    - estilista: FK hacia Usuario (related_name='horarios')
                 Solo muestra usuarios con rol='estilista'

    Nota: Se elimina el campo 'status' heredado de ModeloAuditable
    en favor de 'activo' que es mas semantico para este modelo.
    Sin embargo, 'status' sigue existiendo por herencia; simplemente
    no se usa en la logica de negocio de este modelo.
    """

    # El estilista es un Usuario con rol='estilista'.
    # related_name='horarios' permite acceder como: usuario.horarios.all()
    estilista = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='horarios',
        limit_choices_to={'rol': 'estilista'},
        help_text=gettext_lazy('Estilista al que pertenece este horario'),
    )

    dia_semana = models.CharField(
        max_length=20,
        help_text=gettext_lazy('Dia de la semana (ej: lunes, martes)'),
    )

    hora_inicio = models.TimeField(help_text=gettext_lazy('Hora de inicio del turno'))
    hora_fin = models.TimeField(help_text=gettext_lazy('Hora de fin del turno'))

    activo = models.BooleanField(
        default=True,
        help_text=gettext_lazy('Indica si este horario esta vigente'),
    )

    def clean(self):
        """Validaciones de negocio para el horario."""

        # 1. La hora de fin debe ser posterior a la hora de inicio
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError(
                gettext_lazy('La hora de fin debe ser mayor que la hora de inicio.')
            )

        # 2. Detectar solapamientos con otros horarios activos
        #    del mismo estilista en el mismo dia.
        #    Usamos el related_name 'horarios' indirectamente filtrando
        #    por el campo FK directamente.
        conflictos = Horario.objects.filter(
            estilista=self.estilista,
            dia_semana=self.dia_semana,
            activo=True,
        ).exclude(pk=self.pk)

        for otro_horario in conflictos:
            if (
                self.hora_inicio < otro_horario.hora_fin
                and self.hora_fin > otro_horario.hora_inicio
            ):
                raise ValidationError(
                    gettext_lazy('El horario se cruza con otro registro activo del mismo estilista en ese dia.')
                )

    class Meta:
        db_table = 'stylist_schedules'
        verbose_name = gettext_lazy('Horario')
        verbose_name_plural = gettext_lazy('Horarios')
        # Ordenamiento por nombre del estilista y dia de la semana
        ordering = ['estilista__first_name', 'dia_semana']

    def __str__(self):
        # Usamos get_full_name() en lugar de un campo 'nombre' inventado
        estilista_nombre = (
            self.estilista.get_full_name() or self.estilista.username
        )
        return (
            f"{estilista_nombre} | "
            f"{self.dia_semana} ({self.hora_inicio} - {self.hora_fin})"
        )