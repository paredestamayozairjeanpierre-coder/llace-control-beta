from enum import Enum


class Rol(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"


def es_superadmin(rol: str) -> bool:
    return rol == Rol.SUPERADMIN.value


def es_admin(rol: str) -> bool:
    return rol == Rol.ADMIN.value


def puede_gestionar_usuarios(rol: str) -> bool:
    """
    Crear, modificar o desactivar usuarios del sistema.
    Solo el Superadmin puede hacerlo.
    """
    return es_superadmin(rol)


def puede_gestionar_trabajadores(rol: str) -> bool:
    """
    Gestionar trabajadores y sus datos.
    Superadmin y Admin pueden hacerlo.
    """
    return es_superadmin(rol) or es_admin(rol)


def puede_ver_asistencias(rol: str) -> bool:
    """
    Consultar las asistencias.
    """
    return es_superadmin(rol) or es_admin(rol)


def puede_justificar(rol: str) -> bool:
    """
    Crear o modificar justificaciones.
    """
    return es_superadmin(rol) or es_admin(rol)


def puede_registrar_descuentos(rol: str) -> bool:
    """
    Registrar descuentos por tardanza u otros conceptos.
    """
    return es_superadmin(rol) or es_admin(rol)


def puede_configurar_sistema(rol: str) -> bool:
    """
    Cambiar configuraciones generales del sistema.
    Solo Superadmin.
    """
    return es_superadmin(rol)