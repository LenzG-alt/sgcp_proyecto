"""
Permisos personalizados para el sistema SGCP.

Estas clases se usan en los ViewSets para restringir el acceso
segun el rol del usuario autenticado.

Uso en un ViewSet:
    from .permissions import EsAdministrador

    class PeluqueriaViewSet(viewsets.ModelViewSet):
        permission_classes = [EsAdministrador]
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class EsAdministrador(BasePermission):
    """
    Solo permite acceso a usuarios autenticados con rol='administrador'.

    Se usa en todos los endpoints de gestion (CRUD completo) que
    solo un administrador deberia poder modificar: peluquerias,
    usuarios, servicios, citas, horarios.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == 'administrador'
        )


class EsEstilista(BasePermission):
    """
    Solo permite acceso a usuarios autenticados con rol='estilista'.

    Se usa en endpoints especificos para estilistas, como ver
    su propio horario y sus citas asignadas.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == 'estilista'
        )


class EsRecepcionista(BasePermission):
    """
    Solo permite acceso a usuarios autenticados con rol='recepcionista'.

    Se usa en endpoints especificos para recepcionistas, como
    crear y gestionar citas.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == 'recepcionista'
        )


class EsPersonalInterno(BasePermission):
    """
    Permite acceso a cualquier usuario autenticado que tenga un rol
    de personal interno: administrador, estilista o recepcionista.

    Excluye a los clientes (rol='cliente') de los endpoints
    de gestion interna.
    """

    ROLES_PERMITIDOS = {'administrador', 'estilista', 'recepcionista'}

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in self.ROLES_PERMITIDOS
        )


class EsAdminORecepcionista(BasePermission):
    """
    Permite acceso a administradores y recepcionistas.

    Se usa en endpoints donde ambos roles necesitan acceso, como
    la gestion de citas (el admin gestiona todo, la recepcionista
    crea/gestiona citas del dia a dia).
    """

    ROLES_PERMITIDOS = {'administrador', 'recepcionista'}

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in self.ROLES_PERMITIDOS
        )


class EsAdminOEstilista(BasePermission):
    """
    Permite acceso a administradores y estilistas.

    Se usa en endpoints donde el estilista necesita ver su propia
    informacion, y el administrador necesita ver la de todos.
    """

    ROLES_PERMITIDOS = {'administrador', 'estilista'}

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in self.ROLES_PERMITIDOS
        )


class EsCliente(BasePermission):
    """
    Solo permite acceso a usuarios autenticados con rol='cliente'.

    Se usa en endpoints del portal del cliente: ver sus citas,
    crear reservas, cancelar citas, ver servicios disponibles.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == 'cliente'
        )


class EsClienteORecepcionista(BasePermission):
    """
    Permite acceso a clientes y recepcionistas.

    Se usa en endpoints de lectura compartida: catalogo de servicios,
    lista de estilistas disponibles, etc.
    """
    ROLES_PERMITIDOS = {'cliente', 'recepcionista'}

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in self.ROLES_PERMITIDOS
        )


class SoloLecturaSiNoEsAdmin(BasePermission):
    """
    Permite escritura (POST, PUT, PATCH, DELETE) solo a administradores.
    Los demas roles autenticados solo pueden leer (GET, HEAD, OPTIONS).

    Util para endpoints como Citas donde la recepcionista necesita
    leer pero solo el admin puede eliminar o modificar ciertos campos.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # El admin tiene acceso total
        if request.user.rol == 'administrador':
            return True

        # Los demas roles solo pueden leer
        return request.method in SAFE_METHODS