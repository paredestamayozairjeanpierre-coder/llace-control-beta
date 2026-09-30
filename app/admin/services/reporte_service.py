
from app.core import tiempo
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.models import Trabajador, Asistencia, Descuento
from app.core.permisos import exigir_admin


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

CENTAVO = Decimal("0.01")
CERO = Decimal("0.00")

ESTADOS_ASISTENCIA = (
    "PUNTUAL",
    "TARDANZA",
    "FALTA",
    "JUSTIFICADO",
)


# ==========================================================
# UTILIDADES
# ==========================================================

def _dinero(valor):
    """Convierte valores a Decimal seguro, con dos decimales."""
    try:
        resultado = Decimal(str(valor or 0))

        if not resultado.is_finite():
            raise ValueError

        return resultado.quantize(
            CENTAVO,
            rounding=ROUND_HALF_UP,
        )

    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(
            "Se encontró un valor monetario no válido."
        )


def _validar_fecha(fecha):
    if not isinstance(fecha, date):
        raise ValueError(
            "La fecha de referencia no es válida."
        )


def obtener_periodo_semanal(fecha_referencia=None):
    """Devuelve el periodo laboral de lunes a sábado."""
    if fecha_referencia is None:
        fecha_referencia = tiempo.hoy()
    _validar_fecha(fecha_referencia)
    lunes = fecha_referencia - timedelta(days=fecha_referencia.weekday())
    sabado = lunes + timedelta(days=5)
    return lunes, sabado


def calcular_dias_corresponden(fecha_ingreso, fecha_inicio, fecha_fin):
    """Cuenta días laborables (lunes-sábado) desde el ingreso en el periodo."""
    if not isinstance(fecha_ingreso, date):
        raise ValueError("La fecha de ingreso del trabajador no es válida.")
    if not isinstance(fecha_inicio, date) or not isinstance(fecha_fin, date):
        raise ValueError("El periodo de liquidación no es válido.")
    if fecha_fin < fecha_inicio:
        raise ValueError("El fin del periodo no puede ser anterior al inicio.")
    desde = max(fecha_ingreso, fecha_inicio)
    if desde > fecha_fin:
        return 0
    return sum(1 for desplazamiento in range((fecha_fin - desde).days + 1)
               if (desde + timedelta(days=desplazamiento)).weekday() < 6)


def calcular_sueldo_proporcional(sueldo_semanal, dias_corresponden):
    """Calcula sueldo diario sobre 6 días y redondea a centavos."""
    sueldo = _dinero(sueldo_semanal)
    if sueldo < CERO:
        raise ValueError("El sueldo semanal no puede ser negativo.")
    if not isinstance(dias_corresponden, int) or not 0 <= dias_corresponden <= 6:
        raise ValueError("Los días correspondientes deben estar entre 0 y 6.")
    sueldo_diario = sueldo / Decimal("6")
    return _dinero(sueldo_diario * Decimal(dias_corresponden))


def _calcular_descuentos_periodo(
    descuentos,
    asistencias_por_id,
    fecha_inicio,
    fecha_fin,
    ids_trabajadores,
):
    """Agrupa descuentos por fecha de incidencia, no por fecha de registro.

    Para descuentos vinculados a una asistencia, se utiliza Asistencia.fecha.
    Los descuentos manuales sin asistencia vinculada usan Descuento.fecha.
    Si una misma asistencia tiene descuentos duplicados del mismo tipo, se
    toma el importe mayor y se marca al trabajador para revisión.
    """
    totales = {
        trabajador_id: {"FALTA": CERO, "TARDANZA": CERO, "OTROS": CERO}
        for trabajador_id in ids_trabajadores
    }
    faltas_cubiertas = {trabajador_id: 0 for trabajador_id in ids_trabajadores}
    duplicados = set()
    descuentos_vinculados = {}
    descuentos_manuales = {}

    for descuento in descuentos:
        trabajador_id = descuento.trabajador_id
        asistencia_id = getattr(descuento, "asistencia_id", None)
        asistencia = asistencias_por_id.get(asistencia_id) if asistencia_id is not None else None
        fecha_incidencia = (
            asistencia.fecha if asistencia is not None
            else getattr(descuento, "fecha", None)
        )
        if not isinstance(fecha_incidencia, date):
            continue
        if not fecha_inicio <= fecha_incidencia <= fecha_fin:
            continue

        tipo = str(getattr(descuento, "tipo", "") or "").strip().upper()
        categoria = tipo if tipo in ("FALTA", "TARDANZA") else "OTROS"
        monto = _dinero(getattr(descuento, "monto", CERO))

        if asistencia_id is not None:
            clave = (trabajador_id, categoria, asistencia_id)
            if clave in descuentos_vinculados:
                duplicados.add(trabajador_id)
                monto_anterior = descuentos_vinculados[clave]
                if monto > monto_anterior:
                    totales[trabajador_id][categoria] += monto - monto_anterior
                    descuentos_vinculados[clave] = monto
            else:
                descuentos_vinculados[clave] = monto
                totales[trabajador_id][categoria] += monto
        elif categoria in ("FALTA", "TARDANZA"):
            # Sin asistencia vinculada, agrupar por trabajador/tipo/fecha
            # evita contabilizar dos veces la misma incidencia diaria.
            clave = (trabajador_id, categoria, fecha_incidencia)
            if clave in descuentos_manuales:
                duplicados.add(trabajador_id)
                monto_anterior = descuentos_manuales[clave]
                if monto > monto_anterior:
                    totales[trabajador_id][categoria] += monto - monto_anterior
                    descuentos_manuales[clave] = monto
            else:
                descuentos_manuales[clave] = monto
                totales[trabajador_id][categoria] += monto
        else:
            # Otros descuentos pueden ser conceptos independientes el mismo día.
            totales[trabajador_id][categoria] += monto

    for (trabajador_id, categoria, _fecha), _monto in descuentos_manuales.items():
        if categoria == "FALTA":
            faltas_cubiertas[trabajador_id] += 1

    # Cada descuento FALTA vinculado a una asistencia FALTA cubre una incidencia.
    for (trabajador_id, categoria, asistencia_id), _monto in descuentos_vinculados.items():
        if categoria != "FALTA":
            continue
        asistencia = asistencias_por_id.get(asistencia_id)
        estado = str(getattr(asistencia, "estado", "") or "").strip().upper()
        if asistencia is not None and estado == "FALTA":
            faltas_cubiertas[trabajador_id] += 1

    return totales, faltas_cubiertas, duplicados


# ==========================================================
# LIQUIDACIÓN SEMANAL
# ==========================================================

def obtener_liquidacion_semanal(
    fecha_referencia=None,
    tienda_id=None,
    trabajador_id=None,
):
    """
    Genera una liquidación semanal estimada por trabajador.

    Reglas actuales:
    - El periodo comprende de lunes a sábado.
    - El sueldo se prorratea según los días laborables desde la fecha de
      ingreso dentro de la semana (lunes a sábado), usando sueldo semanal / 6.
    - El sueldo se prorratea desde la fecha de ingreso, sobre seis días.
    - Las faltas en estado FALTA descuentan un sueldo diario, salvo que ya
      tengan un descuento FALTA registrado para esa incidencia.
    - Los descuentos vinculados a una asistencia se asignan por la fecha
      de incidencia de Asistencia; los manuales usan Descuento.fecha.
    - Los descuentos duplicados para una misma asistencia y tipo se cuentan
      una sola vez (importe mayor) y requieren revisión.
    - Se muestran trabajadores activos e inactivos
      que ya hayan ingresado hasta el final del periodo.
    - No se registra ningún pago en la base de datos.
    """

    exigir_admin()

    fecha_inicio, fecha_fin = obtener_periodo_semanal(
        fecha_referencia
    )

    if tienda_id is not None:
        try:
            tienda_id = int(tienda_id)
            if tienda_id <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError(
                "El filtro de tienda no es válido."
            )

    if trabajador_id is not None:
        try:
            trabajador_id = int(trabajador_id)
            if trabajador_id <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError(
                "El filtro de trabajador no es válido."
            )

    with SessionLocal() as session:

        # --------------------------------------------------
        # 1. OBTENER TRABAJADORES
        # --------------------------------------------------

        consulta_trabajadores = (
            select(Trabajador)
            .options(
                joinedload(Trabajador.tienda)
            )
            .where(
                Trabajador.fecha_ingreso <= fecha_fin,
                Trabajador.activo.is_(True)
                
            )
            .order_by(
                Trabajador.nombre_completo
            )
        )

        if tienda_id is not None:
            consulta_trabajadores = (
                consulta_trabajadores.where(
                    Trabajador.tienda_id == tienda_id
                )
            )

        if trabajador_id is not None:
            consulta_trabajadores = (
                consulta_trabajadores.where(
                    Trabajador.id == trabajador_id
                )
            )

        trabajadores = session.scalars(
            consulta_trabajadores
        ).unique().all()

        if not trabajadores:
            return {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "trabajadores": [],
                "totales": _crear_totales_vacios(),
            }

        ids_trabajadores = [
            trabajador.id
            for trabajador in trabajadores
        ]

        # --------------------------------------------------
        # 2. OBTENER ASISTENCIAS DEL PERIODO
        # --------------------------------------------------

        consulta_asistencias = (
            select(Asistencia)
            .where(
                Asistencia.trabajador_id.in_(
                    ids_trabajadores
                ),
                Asistencia.fecha >= fecha_inicio,
                Asistencia.fecha <= fecha_fin,
            )
            .order_by(Asistencia.fecha)
        )

        asistencias = session.scalars(
            consulta_asistencias
        ).all()

        asistencias_por_trabajador = {
            trabajador_id: []
            for trabajador_id in ids_trabajadores
        }

        for asistencia in asistencias:
            asistencias_por_trabajador[
                asistencia.trabajador_id
            ].append(asistencia)

        # --------------------------------------------------
        # 3. OBTENER DESCUENTOS DEL PERIODO
        # --------------------------------------------------

        # Se consultan todos los descuentos de los trabajadores seleccionados,
        # porque un descuento puede registrarse días después de la incidencia.
        consulta_descuentos = select(Descuento).where(
            Descuento.trabajador_id.in_(ids_trabajadores)
        )
        descuentos = session.scalars(consulta_descuentos).all()

        # Resolver la fecha de incidencia de cada descuento vinculado. Se
        # incluyen asistencias fuera del periodo para no confundirlas con
        # descuentos manuales cuya fecha es la propia fecha de incidencia.
        ids_asistencias_descuentos = {
            getattr(descuento, "asistencia_id", None)
            for descuento in descuentos
            if getattr(descuento, "asistencia_id", None) is not None
        }
        asistencias_por_id = {
            asistencia.id: asistencia
            for registros in asistencias_por_trabajador.values()
            for asistencia in registros
        }
        ids_asistencias_faltantes = ids_asistencias_descuentos - set(asistencias_por_id)
        if ids_asistencias_faltantes:
            asistencias_vinculadas = session.scalars(
                select(Asistencia).where(
                    Asistencia.id.in_(ids_asistencias_faltantes)
                )
            ).all()
            asistencias_por_id.update({
                asistencia.id: asistencia for asistencia in asistencias_vinculadas
            })

        (descuentos_por_trabajador,
         faltas_cubiertas_por_descuento,
         trabajadores_con_descuentos_duplicados) = _calcular_descuentos_periodo(
            descuentos,
            asistencias_por_id,
            fecha_inicio,
            fecha_fin,
            ids_trabajadores,
        )

        # --------------------------------------------------
        # 4. CALCULAR LIQUIDACIÓN POR TRABAJADOR
        # --------------------------------------------------

        filas = []

        for trabajador in trabajadores:

            registros = asistencias_por_trabajador[
                trabajador.id
            ]

            conteo = {
                estado: 0
                for estado in ESTADOS_ASISTENCIA
            }

            for asistencia in registros:
                estado = str(
                    asistencia.estado or ""
                ).strip().upper()

                if estado in conteo:
                    conteo[estado] += 1

            descuentos_trabajador = (
                descuentos_por_trabajador[
                    trabajador.id
                ]
            )

            sueldo_semanal = _dinero(trabajador.sueldo_semanal)
            if sueldo_semanal < CERO:
                raise ValueError(
                    f"El sueldo semanal de {trabajador.nombre_completo} no puede ser negativo."
                )
            dias_corresponden = calcular_dias_corresponden(
                trabajador.fecha_ingreso,
                fecha_inicio,
                fecha_fin,
            )
            sueldo_proporcional = calcular_sueldo_proporcional(
                sueldo_semanal,
                dias_corresponden,
            )
            estados_desconocidos = sorted({
                str(asistencia.estado or "").strip().upper()
                for asistencia in registros
                if str(asistencia.estado or "").strip().upper() not in conteo
            })

            # Las faltas injustificadas (estado FALTA) descuentan el valor
            # diario solo si aún no existe un descuento explícito para ellas.
            faltas_sin_descuento = max(
                0,
                conteo["FALTA"] - faltas_cubiertas_por_descuento[trabajador.id],
            )
            sueldo_diario = _dinero(sueldo_semanal / Decimal("6"))
            descuento_faltas_automatico = _dinero(
                sueldo_diario * Decimal(faltas_sin_descuento)
            )
            descuento_faltas = _dinero(
                descuentos_trabajador["FALTA"] + descuento_faltas_automatico
            )

            descuento_tardanzas = _dinero(
                descuentos_trabajador["TARDANZA"]
            )

            otros_descuentos = _dinero(
                descuentos_trabajador["OTROS"]
            )

            total_descuentos = _dinero(
                descuento_faltas
                + descuento_tardanzas
                + otros_descuentos
            )

            neto_estimado = _dinero(
                sueldo_proporcional - total_descuentos
            )

            tienda = trabajador.tienda

            fila = {
                "trabajador_id": trabajador.id,
                "codigo": trabajador.codigo,
                "nombre": trabajador.nombre_completo,
                "dni": trabajador.dni,
                "tienda_id": trabajador.tienda_id,
                "tienda": (
                    tienda.nombre
                    if tienda is not None
                    else "Sin tienda"
                ),
                "activo": bool(trabajador.activo),
                "sueldo_semanal": sueldo_semanal,
                "dias_corresponden": dias_corresponden,
                "sueldo_proporcional": sueldo_proporcional,
                "estados_desconocidos": estados_desconocidos,

                "dias_con_marcacion": (
                    conteo["PUNTUAL"]
                    + conteo["TARDANZA"]
                ),

                "puntuales": conteo["PUNTUAL"],
                "tardanzas": conteo["TARDANZA"],
                "faltas": conteo["FALTA"],
                "justificados": conteo["JUSTIFICADO"],

                "descuento_faltas": descuento_faltas,
                "descuento_tardanzas": descuento_tardanzas,
                "otros_descuentos": otros_descuentos,
                "total_descuentos": total_descuentos,
                "neto_estimado": neto_estimado,

                "requiere_revision": (
                    neto_estimado < CERO
                    or bool(estados_desconocidos)
                    or trabajador.id in trabajadores_con_descuentos_duplicados
                ),
            }

            filas.append(fila)

        # --------------------------------------------------
        # 5. TOTALES GENERALES
        # --------------------------------------------------

        totales = _crear_totales_vacios()
        totales["trabajadores"] = len(filas)

        for fila in filas:
            for campo in (
                "dias_con_marcacion",
                "puntuales",
                "tardanzas",
                "faltas",
                "justificados",
            ):
                totales[campo] += fila[campo]

            for campo in (
                "sueldo_semanal",
                "sueldo_proporcional",
                "descuento_faltas",
                "descuento_tardanzas",
                "otros_descuentos",
                "total_descuentos",
                "neto_estimado",
            ):
                totales[campo] += fila[campo]

            if fila["requiere_revision"]:
                totales["casos_revision"] += 1

        for campo in (
            "sueldo_semanal",
            "sueldo_proporcional",
            "descuento_faltas",
            "descuento_tardanzas",
            "otros_descuentos",
            "total_descuentos",
            "neto_estimado",
        ):
            totales[campo] = _dinero(
                totales[campo]
            )

        return {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "trabajadores": filas,
            "totales": totales,
        }


# ==========================================================
# TOTALES INICIALES
# ==========================================================

def _crear_totales_vacios():
    return {
        "trabajadores": 0,
        "dias_con_marcacion": 0,
        "puntuales": 0,
        "tardanzas": 0,
        "faltas": 0,
        "justificados": 0,
        "sueldo_semanal": CERO,
        "sueldo_proporcional": CERO,
        "descuento_faltas": CERO,
        "descuento_tardanzas": CERO,
        "otros_descuentos": CERO,
        "total_descuentos": CERO,
        "neto_estimado": CERO,
        "casos_revision": 0,
    }