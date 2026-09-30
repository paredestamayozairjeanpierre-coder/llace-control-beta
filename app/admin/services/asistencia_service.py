from datetime import date, datetime, time

from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.core import tiempo
from database.config import TIENDA_CODIGO, PERMITIR_OTRA_TIENDA
from database.connection import SessionLocal
from database.models import Trabajador, Asistencia, Tienda


# =========================================================
# CONFIGURACIÓN DE ASISTENCIA
# =========================================================

HORA_ENTRADA = time(9, 0)
HORA_LIMITE_PUNTUAL = time(9, 10)
HORA_CIERRE = time(15, 0)


# =========================================================
# OBTENER TRABAJADOR POR CÓDIGO
# =========================================================

def obtener_trabajador_por_codigo(codigo: str):

    codigo = str(codigo).strip()

    if not codigo:
        return None

    with SessionLocal() as session:

        trabajador = session.scalar(
            select(Trabajador)
            .options(
                joinedload(Trabajador.tienda)
            )
            .where(
                Trabajador.codigo == codigo,
                Trabajador.activo.is_(True)
            )
        )

        return trabajador


# =========================================================
# OBTENER ASISTENCIA DE UN TRABAJADOR EN UNA FECHA
# =========================================================

def obtener_asistencia_del_dia(
    trabajador_id: int,
    fecha: date | None = None
):

    if fecha is None:
        fecha = tiempo.hoy()

    with SessionLocal() as session:

        asistencia = session.scalar(
            select(Asistencia)
            .where(
                Asistencia.trabajador_id == trabajador_id,
                Asistencia.fecha == fecha
            )
        )

        return asistencia


# =========================================================
# DETERMINAR ESTADO SEGÚN LA HORA
# =========================================================

def determinar_estado(hora_marcacion: time):

    if hora_marcacion <= HORA_LIMITE_PUNTUAL:
        return "PUNTUAL"

    return "TARDANZA"


# =========================================================
# CALCULAR MINUTOS DE TARDANZA
# =========================================================

def calcular_minutos_tardanza(hora_marcacion: time):

    if hora_marcacion <= HORA_LIMITE_PUNTUAL:
        return 0

    segundos = (
        datetime.combine(tiempo.hoy(), hora_marcacion)
        - datetime.combine(tiempo.hoy(), HORA_ENTRADA)
    ).total_seconds()

    minutos = int(segundos // 60)

    return max(minutos, 0)


# =========================================================
# TIENDA DONDE SE ESTÁ MARCANDO
# =========================================================

def _resolver_tienda_marcacion(session, trabajador) -> int:
    """
    Devuelve el id de la tienda donde queda registrada la marcación.

    - Equipo sin TIENDA_CODIGO (ej. PC del admin): la tienda del trabajador.
    - Marcador con TIENDA_CODIGO: esa tienda. Si el trabajador es de otra
      tienda, se rechaza salvo que MARCADOR_PERMITIR_OTRA_TIENDA=1.
    """

    if not TIENDA_CODIGO:
        return trabajador.tienda_id

    tienda = session.scalar(
        select(Tienda).where(
            Tienda.codigo == TIENDA_CODIGO
        )
    )

    if tienda is None:
        raise ValueError(
            f"La tienda configurada en este equipo "
            f"({TIENDA_CODIGO}) no existe en el sistema."
        )

    if (
        tienda.id != trabajador.tienda_id
        and not PERMITIR_OTRA_TIENDA
    ):
        raise ValueError(
            "Este trabajador pertenece a otra tienda "
            f"({trabajador.tienda.nombre}). "
            "Debe marcar en su propia tienda."
        )

    return tienda.id


# =========================================================
# MARCAR ASISTENCIA
# =========================================================

def marcar_asistencia(codigo: str):

    codigo = str(codigo).strip()

    if not codigo:
        raise ValueError(
            "El código de trabajador está vacío."
        )

    with SessionLocal() as session:

        # -------------------------------------------------
        # HORA OFICIAL: la del servidor (Lima), no la de la PC
        # -------------------------------------------------

        ahora = tiempo.ahora_servidor(session)

        fecha_actual = ahora.date()

        hora_actual = ahora.time().replace(
            microsecond=0
        )

        hora_marcacion = ahora.replace(
            microsecond=0
        )

        # -------------------------------------------------
        # BUSCAR TRABAJADOR
        # -------------------------------------------------

        trabajador = session.scalar(
            select(Trabajador)
            .options(
                joinedload(Trabajador.tienda)
            )
            .where(
                Trabajador.codigo == codigo,
                Trabajador.activo.is_(True)
            )
        )

        if trabajador is None:

            raise ValueError(
                "Código no encontrado."
            )

        # -------------------------------------------------
        # VALIDAR TIENDA DEL MARCADOR
        # -------------------------------------------------

        tienda_marcacion_id = _resolver_tienda_marcacion(
            session,
            trabajador
        )

        # -------------------------------------------------
        # VALIDAR HORARIO DE CIERRE
        # -------------------------------------------------

        if hora_actual >= HORA_CIERRE:

            raise ValueError(
                "La marcación del día ya está cerrada."
            )

        # -------------------------------------------------
        # VALIDAR DOBLE MARCACIÓN
        # -------------------------------------------------

        asistencia_existente = session.scalar(
            select(Asistencia)
            .where(
                Asistencia.trabajador_id == trabajador.id,
                Asistencia.fecha == fecha_actual
            )
        )

        if asistencia_existente is not None:

            raise ValueError(
                "El trabajador ya tiene una marcación registrada hoy."
            )

        # -------------------------------------------------
        # DETERMINAR ESTADO
        # -------------------------------------------------

        estado = determinar_estado(
            hora_actual
        )

        minutos_tardanza = calcular_minutos_tardanza(
            hora_actual
        )

        # -------------------------------------------------
        # CREAR ASISTENCIA
        # -------------------------------------------------

        asistencia = Asistencia(
            trabajador_id=trabajador.id,
            tienda_id=tienda_marcacion_id,
            fecha=fecha_actual,
            hora_marcacion=hora_marcacion,
            estado=estado,
            minutos_tardanza=minutos_tardanza
        )

        session.add(asistencia)

        # -------------------------------------------------
        # GUARDAR
        # -------------------------------------------------

        try:

            session.commit()

            session.refresh(
                asistencia
            )

        except IntegrityError:

            session.rollback()

            raise ValueError(
                "El trabajador ya tiene una marcación registrada hoy."
            )

        # -------------------------------------------------
        # DEVOLVER RESULTADO
        # -------------------------------------------------

        return {
            "trabajador": trabajador,
            "asistencia": asistencia,
            "estado": estado,
            "minutos_tardanza": minutos_tardanza,
        }


# =========================================================
# CERRAR EL DÍA Y GENERAR FALTAS
# =========================================================

def cerrar_asistencias_del_dia(
    fecha: date | None = None
):

    if fecha is None:
        fecha = tiempo.hoy()

    with SessionLocal() as session:

        trabajadores = session.scalars(
            select(Trabajador)
            .where(
                Trabajador.activo.is_(True)
            )
        ).all()

        faltas_creadas = 0

        for trabajador in trabajadores:

            asistencia = session.scalar(
                select(Asistencia)
                .where(
                    Asistencia.trabajador_id == trabajador.id,
                    Asistencia.fecha == fecha
                )
            )

            # Ya tiene asistencia
            if asistencia is not None:
                continue

            asistencia = Asistencia(
                trabajador_id=trabajador.id,
                tienda_id=trabajador.tienda_id,
                fecha=fecha,
                hora_marcacion=None,
                estado="FALTA",
                minutos_tardanza=0
            )

            session.add(
                asistencia
            )

            faltas_creadas += 1

        session.commit()

        return faltas_creadas


# =========================================================
# LISTAR ASISTENCIAS
# =========================================================

def listar_asistencias(
    fecha: date | None = None,
    tienda_id: int | None = None,
    estado: str | None = None,
    busqueda: str | None = None,
):

    if fecha is None:
        fecha = tiempo.hoy()

    with SessionLocal() as session:

        consulta = (
            select(Asistencia)
            .options(
                joinedload(
                    Asistencia.trabajador
                ).joinedload(
                    Trabajador.tienda
                )
            )
            .join(Trabajador)
            .where(
                Asistencia.fecha == fecha
            )
        )

        # -------------------------------------------------
        # FILTRO POR TIENDA
        # -------------------------------------------------

        if tienda_id is not None:

            consulta = consulta.where(
                Trabajador.tienda_id == tienda_id
            )

        # -------------------------------------------------
        # FILTRO POR ESTADO
        # -------------------------------------------------

        if estado is not None and estado != "TODOS":

            consulta = consulta.where(
                Asistencia.estado == estado
            )

        # -------------------------------------------------
        # BÚSQUEDA
        # -------------------------------------------------

        if busqueda:

            busqueda = busqueda.strip()

            consulta = consulta.where(
                or_(
                    Trabajador.codigo.ilike(
                        f"%{busqueda}%"
                    ),
                    Trabajador.nombre_completo.ilike(
                        f"%{busqueda}%"
                    ),
                    Trabajador.dni.ilike(
                        f"%{busqueda}%"
                    ),
                )
            )

        # -------------------------------------------------
        # ORDEN
        # -------------------------------------------------

        consulta = consulta.order_by(
            Trabajador.nombre_completo
        )

        asistencias = session.scalars(
            consulta
        ).all()

        return asistencias


# =========================================================
# LISTAR ASISTENCIAS DE UN TRABAJADOR
# =========================================================

def listar_asistencias_trabajador(
    trabajador_id: int,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None
):

    with SessionLocal() as session:

        consulta = (
            select(Asistencia)
            .where(
                Asistencia.trabajador_id == trabajador_id
            )
            .order_by(
                Asistencia.fecha.desc()
            )
        )

        if fecha_inicio is not None:

            consulta = consulta.where(
                Asistencia.fecha >= fecha_inicio
            )

        if fecha_fin is not None:

            consulta = consulta.where(
                Asistencia.fecha <= fecha_fin
            )

        return session.scalars(
            consulta
        ).all()


# =========================================================
# OBTENER RESUMEN DE ASISTENCIA
# =========================================================

def obtener_resumen_asistencias(
    fecha: date | None = None
):

    if fecha is None:
        fecha = tiempo.hoy()

    with SessionLocal() as session:

        asistencias = session.scalars(
            select(Asistencia)
            .where(
                Asistencia.fecha == fecha
            )
        ).all()

        resumen = {
            "total": len(asistencias),
            "puntuales": 0,
            "tardanzas": 0,
            "faltas": 0,
            "justificados": 0,
        }

        for asistencia in asistencias:

            estado = asistencia.estado

            if estado == "PUNTUAL":

                resumen["puntuales"] += 1

            elif estado == "TARDANZA":

                resumen["tardanzas"] += 1

            elif estado == "FALTA":

                resumen["faltas"] += 1

            elif estado == "JUSTIFICADO":

                resumen["justificados"] += 1

        return resumen


# =========================================================
# CAMBIAR ESTADO A JUSTIFICADO
# =========================================================

def marcar_como_justificado(
    asistencia_id: int
):

    with SessionLocal() as session:

        asistencia = session.get(
            Asistencia,
            asistencia_id
        )

        if asistencia is None:

            raise ValueError(
                "La asistencia no existe."
            )

        asistencia.estado = "JUSTIFICADO"

        session.commit()

        return asistencia


# =========================================================
# CORREGIR ESTADO
# =========================================================

def actualizar_estado_asistencia(
    asistencia_id: int,
    nuevo_estado: str
):

    estados_validos = {
        "PUNTUAL",
        "TARDANZA",
        "FALTA",
        "JUSTIFICADO",
    }

    if nuevo_estado not in estados_validos:

        raise ValueError(
            "Estado de asistencia no válido."
        )

    with SessionLocal() as session:

        asistencia = session.get(
            Asistencia,
            asistencia_id
        )

        if asistencia is None:

            raise ValueError(
                "La asistencia no existe."
            )

        asistencia.estado = nuevo_estado

        session.commit()

        return asistencia