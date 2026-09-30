from sqlalchemy.exc import InterfaceError, OperationalError

from app.admin.services.asistencia_service import (
    obtener_trabajador_por_codigo,
    obtener_asistencia_del_dia,
    marcar_asistencia,
)


# Errores que indican que no hay comunicación con la base de datos
ERRORES_DE_CONEXION = (OperationalError, InterfaceError)


def _sin_conexion():
    """Respuesta uniforme cuando no hay internet o el servidor no responde."""

    return {
        "ok": False,
        "tipo": "SIN_CONEXION",
        "mensaje": (
            "No hay conexión con el servidor.\n"
            "Revisa el internet e inténtalo de nuevo.\n"
            "Tu marcación NO se ha registrado."
        ),
    }


# ============================================================
# VALIDAR CÓDIGO
# ============================================================

def validar_codigo(codigo: str):

    codigo = str(codigo).strip()

    if not codigo:
        return None

    return obtener_trabajador_por_codigo(
        codigo
    )


# ============================================================
# OBTENER ESTADO DE MARCACIÓN
# ============================================================

def obtener_estado_marcacion(codigo: str):

    try:

        trabajador = validar_codigo(
            codigo
        )

        # ----------------------------------------------------
        # CÓDIGO NO ENCONTRADO
        # ----------------------------------------------------

        if trabajador is None:

            return {
                "ok": False,
                "tipo": "CODIGO_NO_ENCONTRADO",
                "mensaje": "Código no encontrado.",
            }

        # ----------------------------------------------------
        # BUSCAR MARCACIÓN DEL DÍA
        # ----------------------------------------------------

        from app.core import tiempo

        asistencia = obtener_asistencia_del_dia(
            trabajador.id,
            tiempo.hoy()
        )

    except ERRORES_DE_CONEXION:

        return _sin_conexion()

    # --------------------------------------------------------
    # YA MARCÓ
    # --------------------------------------------------------

    if asistencia is not None:

        return {
            "ok": False,
            "tipo": "YA_MARCO",
            "mensaje": (
                "El trabajador ya tiene una "
                "marcación registrada hoy."
            ),
            "trabajador": trabajador,
            "asistencia": asistencia,
        }

    # --------------------------------------------------------
    # LISTO PARA MARCAR
    # --------------------------------------------------------

    return {
        "ok": True,
        "tipo": "LISTO_PARA_MARCAR",
        "mensaje": "Trabajador encontrado.",
        "trabajador": trabajador,
    }


# ============================================================
# REGISTRAR MARCACIÓN
# ============================================================

def registrar_marcacion(codigo: str):

    try:

        trabajador = validar_codigo(
            codigo
        )

    except ERRORES_DE_CONEXION:

        return _sin_conexion()

    # --------------------------------------------------------
    # CÓDIGO NO ENCONTRADO
    # --------------------------------------------------------

    if trabajador is None:

        return {
            "ok": False,
            "tipo": "CODIGO_NO_ENCONTRADO",
            "mensaje": "Código no encontrado.",
        }

    # --------------------------------------------------------
    # INTENTAR REGISTRAR
    # --------------------------------------------------------

    try:

        resultado = marcar_asistencia(
            codigo
        )

        # ----------------------------------------------------
        # DEVOLVER RESULTADO LIMPIO
        # ----------------------------------------------------

        return {
            "ok": True,
            "tipo": "MARCACION_REGISTRADA",
            "mensaje": (
                "Marcación registrada correctamente."
            ),
            "trabajador": resultado["trabajador"],
            "asistencia": resultado["asistencia"],
            "estado": resultado["estado"],
            "minutos_tardanza": (
                resultado["minutos_tardanza"]
            ),
        }

    # --------------------------------------------------------
    # ERROR CONTROLADO
    # --------------------------------------------------------

    except ValueError as error:

        return {
            "ok": False,
            "tipo": "ERROR_MARCACION",
            "mensaje": str(error),
            "trabajador": trabajador,
        }

    # --------------------------------------------------------
    # SIN CONEXIÓN
    # --------------------------------------------------------

    except ERRORES_DE_CONEXION:

        return _sin_conexion()

    # --------------------------------------------------------
    # ERROR DEL SISTEMA
    # --------------------------------------------------------

    except Exception as error:

        return {
            "ok": False,
            "tipo": "ERROR_SISTEMA",
            "mensaje": (
                f"No se pudo registrar la marcación: {error}"
            ),
            "trabajador": trabajador,
        }
