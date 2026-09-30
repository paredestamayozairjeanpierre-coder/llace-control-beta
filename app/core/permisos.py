from app.core.session import sesion_actual

from app.core.permissions import (
    puede_gestionar_usuarios as _puede_gestionar_usuarios,
    puede_gestionar_trabajadores as _puede_gestionar_trabajadores,
    puede_ver_asistencias as _puede_ver_asistencias,
    puede_justificar as _puede_justificar,
    puede_registrar_descuentos as _puede_registrar_descuentos,
    puede_configurar_sistema as _puede_configurar_sistema,
)


# ==========================================================
# ROLES
# ==========================================================

ROL_SUPERADMIN = "SUPERADMIN"
ROL_ADMIN = "ADMIN"


# ==========================================================
# SESIÓN ACTUAL
# ==========================================================

def hay_sesion():
    """
    Indica si existe una sesión activa.
    """
    return sesion_actual.esta_activa()


def obtener_rol_actual():
    """
    Obtiene el rol del usuario actualmente conectado.
    """
    if not hay_sesion():
        return None

    return sesion_actual.usuario.rol


# ==========================================================
# IDENTIFICACIÓN DEL ROL ACTUAL
# ==========================================================

def es_superadmin():
    """
    Indica si el usuario actualmente conectado
    es SUPERADMIN.
    """
    return obtener_rol_actual() == ROL_SUPERADMIN


def es_admin():
    """
    Indica si el usuario actualmente conectado
    es ADMIN.
    """
    return obtener_rol_actual() == ROL_ADMIN


# ==========================================================
# PERMISOS DEL USUARIO ACTUAL
# ==========================================================

def puede_gestionar_usuarios():
    return _puede_gestionar_usuarios(
        obtener_rol_actual()
    )


def puede_gestionar_trabajadores():
    return _puede_gestionar_trabajadores(
        obtener_rol_actual()
    )


def puede_ver_asistencias():
    return _puede_ver_asistencias(
        obtener_rol_actual()
    )


def puede_justificar():
    return _puede_justificar(
        obtener_rol_actual()
    )


def puede_registrar_descuentos():
    return _puede_registrar_descuentos(
        obtener_rol_actual()
    )


def puede_configurar_sistema():
    return _puede_configurar_sistema(
        obtener_rol_actual()
    )


# ==========================================================
# PERMISOS ADICIONALES
# ==========================================================

def puede_gestionar_tiendas():
    """
    SUPERADMIN y ADMIN pueden gestionar tiendas.
    """
    rol = obtener_rol_actual()

    return rol in (
        ROL_SUPERADMIN,
        ROL_ADMIN,
    )


def puede_ver_reportes():
    """
    SUPERADMIN y ADMIN pueden consultar reportes.
    """
    rol = obtener_rol_actual()

    return rol in (
        ROL_SUPERADMIN,
        ROL_ADMIN,
    )


# ==========================================================
# VALIDACIONES DE ACCESO
# ==========================================================

def exigir_sesion():
    """
    Exige que exista una sesión activa.
    """
    if not hay_sesion():
        raise PermissionError(
            "No existe una sesión activa."
        )

    return True


def exigir_superadmin():
    """
    Exige que el usuario actual sea SUPERADMIN.
    """
    exigir_sesion()

    if not es_superadmin():
        raise PermissionError(
            "No tienes permisos de SUPERADMIN."
        )

    return True


def exigir_admin():
    """
    Permite ADMIN o SUPERADMIN.
    """
    exigir_sesion()

    if not (
        es_superadmin()
        or es_admin()
    ):
        raise PermissionError(
            "No tienes permisos de administrador."
        )

    return True