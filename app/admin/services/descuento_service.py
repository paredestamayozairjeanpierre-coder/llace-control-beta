from app.core import tiempo
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy import desc, select
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.models import Asistencia, Descuento, Trabajador

from app.core.permisos import (
    exigir_admin,
    puede_registrar_descuentos,
)


TIPO_FALTA = "FALTA"
TIPO_TARDANZA = "TARDANZA"

DIAS_SEMANA = 6


# ==========================================================
# VALIDACIONES
# ==========================================================

def _convertir_monto(monto):
    try:
        valor = Decimal(str(monto).strip())
        if not valor.is_finite():
            raise ValueError
        valor = valor.quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        raise ValueError("El monto debe ser un número válido y finito.")

    if valor < 0:
        raise ValueError("El monto del descuento no puede ser negativo.")
    if valor > Decimal("999999999.99"):
        raise ValueError("El monto supera el máximo permitido.")
    return valor


def _validar_tipo(tipo):
    tipo = str(tipo).strip().upper()

    if tipo not in (TIPO_FALTA, TIPO_TARDANZA):
        raise ValueError(
            "El tipo de descuento debe ser FALTA o TARDANZA."
        )

    return tipo


def _exigir_permiso_descuentos():
    if not puede_registrar_descuentos():
        exigir_admin()


# ==========================================================
# TRABAJADORES
# ==========================================================

def obtener_trabajador_por_id(trabajador_id):
    with SessionLocal() as session:
        return session.get(Trabajador, trabajador_id)


def obtener_trabajadores_activos():
    with SessionLocal() as session:
        consulta = (
            select(Trabajador)
            .where(Trabajador.activo.is_(True))
            .order_by(Trabajador.nombre_completo)
        )

        return session.scalars(consulta).all()


# ==========================================================
# CÁLCULO DEL DESCUENTO POR FALTA
# ==========================================================

def calcular_descuento_por_falta(trabajador_id):
    """
    Calcula el descuento correspondiente a una falta injustificada.

    Regla del sistema:
        sueldo semanal / 6 días laborables
    """

    trabajador = obtener_trabajador_por_id(trabajador_id)

    if trabajador is None:
        raise ValueError("El trabajador no existe.")

    sueldo = Decimal(str(trabajador.sueldo_semanal or 0))

    if sueldo <= 0:
        raise ValueError(
            "El trabajador no tiene un sueldo semanal válido."
        )

    descuento = sueldo / Decimal(DIAS_SEMANA)

    return descuento.quantize(Decimal("0.01"))


# ==========================================================
# ASISTENCIA
# ==========================================================

def obtener_asistencia_por_id(asistencia_id):
    with SessionLocal() as session:
        consulta = (
            select(Asistencia)
            .options(
                joinedload(Asistencia.trabajador)
            )
            .where(Asistencia.id == asistencia_id)
        )

        return session.scalar(consulta)


def obtener_asistencia_del_trabajador_en_fecha(
    trabajador_id,
    fecha=None
):
    if fecha is None:
        fecha = tiempo.hoy()

    with SessionLocal() as session:
        consulta = (
            select(Asistencia)
            .where(
                Asistencia.trabajador_id == trabajador_id,
                Asistencia.fecha == fecha,
            )
        )

        return session.scalar(consulta)


# ==========================================================
# COMPROBAR DESCUENTOS EXISTENTES
# ==========================================================

def existe_descuento_para_asistencia(
    asistencia_id,
    tipo
):
    tipo = _validar_tipo(tipo)

    with SessionLocal() as session:
        consulta = (
            select(Descuento)
            .where(
                Descuento.asistencia_id == asistencia_id,
                Descuento.tipo == tipo,
            )
        )

        return session.scalar(consulta) is not None


# ==========================================================
# REGISTRAR DESCUENTO
# ==========================================================

def registrar_descuento(
    trabajador_id,
    monto,
    tipo,
    observacion="",
    asistencia_id=None,
):
    """
    Registra un descuento manual.

    ADMIN y SUPERADMIN pueden registrar descuentos.

    Para FALTA:
        normalmente debe utilizarse registrar_descuento_por_falta(),
        que calcula automáticamente sueldo_semanal / 6.

    Para TARDANZA:
        el monto lo decide manualmente el ADMIN o SUPERADMIN.
    """

    _exigir_permiso_descuentos()

    tipo = _validar_tipo(tipo)
    monto = _convertir_monto(monto)
    observacion = str(observacion or "").strip()

    if monto <= 0:
        raise ValueError("El monto del descuento debe ser mayor que 0.")

    if not observacion:
        raise ValueError(
            "Debes indicar una observación para el descuento."
        )

    usuario_actual = sesion_actual_usuario_id()

    with SessionLocal() as session:
        trabajador = session.get(Trabajador, trabajador_id)

        if trabajador is None:
            raise ValueError("El trabajador no existe.")

        if not trabajador.activo:
            raise ValueError(
                "No se puede registrar un descuento a un trabajador inactivo."
            )

        asistencia = None

        if asistencia_id is not None:
            asistencia = session.get(Asistencia, asistencia_id)

            if asistencia is None:
                raise ValueError("La asistencia no existe.")

            if asistencia.trabajador_id != trabajador_id:
                raise ValueError(
                    "La asistencia no corresponde al trabajador seleccionado."
                )

            if asistencia.estado != tipo:
                raise ValueError(
                    f"El descuento {tipo} no coincide con el estado de la asistencia ({asistencia.estado})."
                )

            descuento_existente = session.scalar(
                select(Descuento).where(
                    Descuento.asistencia_id == asistencia_id,
                    Descuento.tipo == tipo,
                )
            )

            if descuento_existente is not None:
                raise ValueError(
                    "Ya existe un descuento de este tipo para esta asistencia."
                )

        descuento = Descuento(
            trabajador_id=trabajador_id,
            asistencia_id=asistencia_id,
            tipo=tipo,
            monto=monto,
            observacion=observacion,
            fecha=tiempo.hoy(),
            registrado_por=usuario_actual,
        )

        session.add(descuento)

        try:
            session.commit()
            session.refresh(descuento)
        except Exception:
            session.rollback()
            raise

        return descuento


# ==========================================================
# REGISTRAR FALTA
# ==========================================================

def registrar_descuento_por_falta(
    trabajador_id,
    asistencia_id=None,
    observacion="Falta injustificada",
):
    """
    Registra automáticamente el descuento de una falta.

    Fórmula:
        sueldo semanal / 6
    """

    _exigir_permiso_descuentos()

    trabajador = obtener_trabajador_por_id(trabajador_id)

    if trabajador is None:
        raise ValueError("El trabajador no existe.")

    if asistencia_id is not None:
        asistencia = obtener_asistencia_por_id(asistencia_id)

        if asistencia is None:
            raise ValueError("La asistencia no existe.")

        if asistencia.trabajador_id != trabajador_id:
            raise ValueError(
                "La asistencia no corresponde al trabajador."
            )

        if asistencia.estado != "FALTA":
            raise ValueError(
                "Solo se puede generar este descuento para una asistencia "
                "con estado FALTA."
            )

        if existe_descuento_para_asistencia(
            asistencia_id,
            TIPO_FALTA,
        ):
            raise ValueError(
                "Esta falta ya tiene un descuento registrado."
            )

    monto = calcular_descuento_por_falta(trabajador_id)

    return registrar_descuento(
        trabajador_id=trabajador_id,
        monto=monto,
        tipo=TIPO_FALTA,
        observacion=observacion,
        asistencia_id=asistencia_id,
    )


# ==========================================================
# REGISTRAR TARDANZA
# ==========================================================

def registrar_descuento_por_tardanza(
    trabajador_id,
    monto,
    asistencia_id=None,
    observacion="Descuento por tardanza",
):
    """
    Registra un descuento manual por tardanza.

    El sistema NO calcula automáticamente el monto.
    El ADMIN o SUPERADMIN decide cuánto descontar.
    """

    if asistencia_id is not None:
        asistencia = obtener_asistencia_por_id(asistencia_id)

        if asistencia is None:
            raise ValueError("La asistencia no existe.")

        if asistencia.trabajador_id != trabajador_id:
            raise ValueError(
                "La asistencia no corresponde al trabajador."
            )

        if asistencia.estado != "TARDANZA":
            raise ValueError(
                "Solo se puede registrar este descuento para una "
                "asistencia con estado TARDANZA."
            )

    return registrar_descuento(
        trabajador_id=trabajador_id,
        monto=monto,
        tipo=TIPO_TARDANZA,
        observacion=observacion,
        asistencia_id=asistencia_id,
    )


# ==========================================================
# LISTAR DESCUENTOS
# ==========================================================

def listar_descuentos():
    _exigir_permiso_descuentos()

    with SessionLocal() as session:
        consulta = (
            select(Descuento)
            .options(
                joinedload(Descuento.trabajador).joinedload(Trabajador.tienda),
                joinedload(Descuento.asistencia),
            )
            .order_by(
                desc(Descuento.fecha),
                desc(Descuento.id),
            )
        )

        return session.scalars(consulta).unique().all()


def listar_descuentos_trabajador(trabajador_id):
    _exigir_permiso_descuentos()

    with SessionLocal() as session:
        consulta = (
            select(Descuento)
            .options(
                joinedload(Descuento.trabajador).joinedload(Trabajador.tienda),
                joinedload(Descuento.asistencia),
            )
            .where(
                Descuento.trabajador_id == trabajador_id
            )
            .order_by(
                desc(Descuento.fecha),
                desc(Descuento.id),
            )
        )

        return session.scalars(consulta).unique().all()


def listar_descuentos_periodo(
    fecha_inicio,
    fecha_fin,
):
    _exigir_permiso_descuentos()

    if fecha_inicio > fecha_fin:
        raise ValueError(
            "La fecha inicial no puede ser posterior a la fecha final."
        )

    with SessionLocal() as session:
        consulta = (
            select(Descuento)
            .options(
                joinedload(Descuento.trabajador).joinedload(Trabajador.tienda),
                joinedload(Descuento.asistencia),
            )
            .where(
                Descuento.fecha >= fecha_inicio,
                Descuento.fecha <= fecha_fin,
            )
            .order_by(
                desc(Descuento.fecha),
                desc(Descuento.id),
            )
        )

        return session.scalars(consulta).unique().all()


# ==========================================================
# TOTAL DE DESCUENTOS
# ==========================================================

def obtener_total_descuentos_trabajador(
    trabajador_id,
    fecha_inicio=None,
    fecha_fin=None,
):
    _exigir_permiso_descuentos()

    with SessionLocal() as session:
        consulta = select(Descuento).where(
            Descuento.trabajador_id == trabajador_id
        )

        if fecha_inicio is not None:
            consulta = consulta.where(
                Descuento.fecha >= fecha_inicio
            )

        if fecha_fin is not None:
            consulta = consulta.where(
                Descuento.fecha <= fecha_fin
            )

        descuentos = session.scalars(consulta).all()

        total = sum(
            (Decimal(str(item.monto or 0)) for item in descuentos),
            Decimal("0.00"),
        )

        return total.quantize(Decimal("0.01"))


# ==========================================================
# TOTAL DE LA SEMANA
# ==========================================================

def obtener_total_descuentos_semana(trabajador_id):
    hoy = tiempo.hoy()

    # Lunes de la semana actual.
    inicio_semana = hoy - timedelta(
        days=hoy.weekday()
    )

    # Sábado: nuestro período laboral es lunes-sábado.
    fin_semana = inicio_semana + timedelta(days=5)

    return obtener_total_descuentos_trabajador(
        trabajador_id=trabajador_id,
        fecha_inicio=inicio_semana,
        fecha_fin=fin_semana,
    )


# ==========================================================
# SESIÓN
# ==========================================================

def sesion_actual_usuario_id():
    from app.core.session import sesion_actual

    if not sesion_actual.esta_activa():
        raise PermissionError(
            "No existe una sesión activa."
        )

    return sesion_actual.usuario.id
