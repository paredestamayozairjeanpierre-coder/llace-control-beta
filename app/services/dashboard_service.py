from app.core import tiempo
from datetime import date

from sqlalchemy import func, select

from database.connection import SessionLocal
from database.models import Tienda, Trabajador, Asistencia


def obtener_resumen_dashboard():
    """
    Obtiene los datos principales que necesita
    el Dashboard del SUPERADMIN.
    """

    with SessionLocal() as session:

        # ------------------------------------------------------
        # TIENDAS ACTIVAS
        # ------------------------------------------------------

        tiendas_activas = session.scalar(
            select(func.count(Tienda.id)).where(
                Tienda.activa.is_(True)
            )
        ) or 0

        # ------------------------------------------------------
        # TRABAJADORES ACTIVOS
        # ------------------------------------------------------

        trabajadores_activos = session.scalar(
            select(func.count(Trabajador.id)).where(
                Trabajador.activo.is_(True)
            )
        ) or 0

        # ------------------------------------------------------
        # ASISTENCIAS DE HOY
        # ------------------------------------------------------

        hoy = tiempo.hoy()

        asistencias_hoy = session.scalar(
            select(func.count(Asistencia.id)).where(
                Asistencia.fecha == hoy
            )
        ) or 0

        # ------------------------------------------------------
        # FALTAS DE HOY
        # ------------------------------------------------------

        faltas_hoy = session.scalar(
            select(func.count(Asistencia.id)).where(
                Asistencia.fecha == hoy,
                Asistencia.estado == "FALTA"
            )
        ) or 0

        return {
            "tiendas": tiendas_activas,
            "trabajadores": trabajadores_activos,
            "asistencias_hoy": asistencias_hoy,
            "faltas_hoy": faltas_hoy,
        }