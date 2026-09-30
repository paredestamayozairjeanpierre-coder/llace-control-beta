"""
Hora oficial del sistema.

La fecha y hora que cuentan para la asistencia son las del SERVIDOR de la
base de datos (zona America/Lima), nunca las de la PC de la tienda.
Así, cambiar el reloj de Windows no permite marcar "puntual".

Uso:
    from app.core import tiempo
    tiempo.hoy()      -> date   (hoy en Lima)
    tiempo.ahora()    -> datetime sin zona horaria (ahora en Lima)

Para registrar una marcación se usa ahora_servidor(session), que pregunta
la hora dentro de la misma transacción (es la fuente de verdad).
"""

import threading
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("America/Lima")

# Cada cuántos segundos se vuelve a sincronizar con el servidor
_REFRESCO_SEGUNDOS = 300
# Si no hay conexión, cada cuántos segundos se reintenta
_REINTENTO_SEGUNDOS = 30

_lock = threading.Lock()
_base_servidor: datetime | None = None
_base_monotonico: float = 0.0
_ultimo_intento: float = 0.0


def ahora_servidor(conexion) -> datetime:
    """
    Hora actual del servidor PostgreSQL, en Lima (sin zona horaria).
    Acepta una Session o una Connection de SQLAlchemy.
    """
    from sqlalchemy import text

    return conexion.execute(
        text("SELECT (now() AT TIME ZONE 'America/Lima')")
    ).scalar()


def _hora_local_lima() -> datetime:
    """Respaldo cuando no hay conexión: reloj de la PC, pero en hora de Lima."""
    return datetime.now(ZONA).replace(tzinfo=None)


def _sincronizar() -> None:
    """Pregunta la hora al servidor y guarda una referencia."""
    global _base_servidor, _base_monotonico, _ultimo_intento

    try:
        from database.connection import engine

        with engine.connect() as conexion:
            t0 = time.monotonic()
            servidor = ahora_servidor(conexion)
            t1 = time.monotonic()

        with _lock:
            # Se compensa la mitad de la latencia de la consulta
            _base_servidor = servidor + timedelta(seconds=(t1 - t0) / 2)
            _base_monotonico = t1

    except Exception:
        # Sin conexión: se conserva la última referencia (si existe)
        pass

    finally:
        _ultimo_intento = time.monotonic()


def _sincronizar_en_segundo_plano() -> None:
    """Reintenta sin bloquear la pantalla."""
    global _ultimo_intento

    with _lock:
        # Marca el intento ya, para no lanzar varios hilos a la vez
        _ultimo_intento = time.monotonic()

    threading.Thread(target=_sincronizar, daemon=True).start()


def ahora() -> datetime:
    """
    Fecha y hora actual en Lima según el servidor.

    Usa el reloj monotónico entre sincronizaciones, por lo que cambiar
    la hora de Windows no la afecta. Nunca bloquea después de la primera
    llamada.
    """
    if _ultimo_intento == 0.0:
        # Primera vez: sincroniza (máximo unos segundos por el timeout)
        _sincronizar()
    else:
        intervalo = (
            _REFRESCO_SEGUNDOS
            if _base_servidor is not None
            else _REINTENTO_SEGUNDOS
        )
        if time.monotonic() - _ultimo_intento > intervalo:
            _sincronizar_en_segundo_plano()

    with _lock:
        base = _base_servidor
        base_mono = _base_monotonico

    if base is None:
        return _hora_local_lima()

    return base + timedelta(seconds=time.monotonic() - base_mono)


def hoy() -> date:
    """Fecha de hoy en Lima según el servidor."""
    return ahora().date()
