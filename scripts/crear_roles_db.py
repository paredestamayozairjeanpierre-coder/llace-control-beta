"""
Crea dos usuarios de base de datos con permisos limitados, para no usar
nunca el superusuario 'postgres' en las PCs de las tiendas.

  llace_marcador  -> PCs de las tiendas. Solo puede:
                     leer tiendas y trabajadores,
                     leer e insertar asistencias.
                     NO puede modificar ni borrar nada.

  llace_admin     -> PC del administrador. Lectura y escritura de las tablas
                     de la app (sin permisos para crear/borrar tablas).

Ejecutar con el usuario DUEÑO de la base (el DATABASE_URL del .env actual):
    python -m scripts.crear_roles_db

Si ejecutas de nuevo el script, actualiza las contraseñas y permisos.
"""

from getpass import getpass

from psycopg import sql

from database.connection import engine

ROL_MARCADOR = "llace_marcador"
ROL_ADMIN = "llace_admin"


def _pedir_password(rol: str) -> str:
    while True:
        clave = getpass(f"Contraseña para {rol} (mínimo 12 caracteres): ")
        if len(clave) < 12:
            print("  Muy corta. Usa al menos 12 caracteres.")
            continue
        if clave != getpass("  Repite la contraseña: "):
            print("  No coinciden.")
            continue
        return clave


def _crear_o_actualizar_rol(cursor, rol: str, clave: str):
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (rol,))
    existe = cursor.fetchone() is not None

    accion = "ALTER ROLE {} WITH LOGIN PASSWORD {}" if existe else \
             "CREATE ROLE {} LOGIN PASSWORD {}"

    cursor.execute(
        sql.SQL(accion).format(sql.Identifier(rol), sql.Literal(clave))
    )


def main():
    print("=" * 55)
    print("  CREAR USUARIOS DE BASE DE DATOS - LLACE CONTROL")
    print("=" * 55)

    clave_marcador = _pedir_password(ROL_MARCADOR)
    clave_admin = _pedir_password(ROL_ADMIN)

    conexion = engine.raw_connection()

    try:
        cursor = conexion.cursor()

        cursor.execute("SELECT current_database()")
        base = cursor.fetchone()[0]

        _crear_o_actualizar_rol(cursor, ROL_MARCADOR, clave_marcador)
        _crear_o_actualizar_rol(cursor, ROL_ADMIN, clave_admin)

        marcador = sql.Identifier(ROL_MARCADOR)
        admin = sql.Identifier(ROL_ADMIN)

        # Punto de partida limpio: sin permisos heredados
        for rol in (marcador, admin):
            cursor.execute(sql.SQL(
                "REVOKE ALL ON ALL TABLES IN SCHEMA public FROM {}"
            ).format(rol))
            cursor.execute(sql.SQL(
                "REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM {}"
            ).format(rol))
            cursor.execute(sql.SQL(
                "GRANT CONNECT ON DATABASE {} TO {}"
            ).format(sql.Identifier(base), rol))
            cursor.execute(sql.SQL(
                "GRANT USAGE ON SCHEMA public TO {}"
            ).format(rol))

        # ---- MARCADOR: solo lo imprescindible para marcar ----
        cursor.execute(sql.SQL(
            "GRANT SELECT ON tiendas, trabajadores TO {}"
        ).format(marcador))
        cursor.execute(sql.SQL(
            "GRANT SELECT, INSERT ON asistencias TO {}"
        ).format(marcador))

        cursor.execute("SELECT pg_get_serial_sequence('asistencias', 'id')")
        secuencia = cursor.fetchone()[0]
        if secuencia:
            cursor.execute(sql.SQL(
                "GRANT USAGE ON SEQUENCE {} TO {}"
            ).format(sql.SQL(secuencia), marcador))

        # ---- ADMIN: datos, sin cambiar la estructura ----
        cursor.execute(sql.SQL(
            "GRANT SELECT, INSERT, UPDATE, DELETE "
            "ON ALL TABLES IN SCHEMA public TO {}"
        ).format(admin))
        cursor.execute(sql.SQL(
            "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {}"
        ).format(admin))

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()

    print()
    print("USUARIOS CREADOS / ACTUALIZADOS CORRECTAMENTE")
    print(f"  {ROL_MARCADOR}: usar en las PCs de las tiendas")
    print(f"  {ROL_ADMIN}: usar en la PC del administrador")
    print("Ahora configura el .env de cada PC (ver .env.*.example).")


if __name__ == "__main__":
    main()
