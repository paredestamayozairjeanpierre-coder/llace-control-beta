"""
Migración v2 (idempotente: se puede ejecutar varias veces sin problema).

- Agrega asistencias.tienda_id (tienda donde se marcó).
- Rellena las asistencias antiguas con la tienda del trabajador.
- Crea índices para que las consultas del admin sean rápidas con 3 tiendas.

Ejecutar UNA VEZ con el usuario dueño de la base (no el del marcador):
    python -m scripts.migrar_v2
"""

from sqlalchemy import text

from database.connection import engine


def migrar():
    with engine.begin() as conexion:

        conexion.execute(text("""
            ALTER TABLE asistencias
            ADD COLUMN IF NOT EXISTS tienda_id INTEGER
            REFERENCES tiendas(id);
        """))

        resultado = conexion.execute(text("""
            UPDATE asistencias a
            SET tienda_id = t.tienda_id
            FROM trabajadores t
            WHERE a.trabajador_id = t.id
              AND a.tienda_id IS NULL;
        """))

        conexion.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_asistencias_tienda_id "
            "ON asistencias (tienda_id);"
        ))

        conexion.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_asistencias_fecha "
            "ON asistencias (fecha);"
        ))

    print("MIGRACION v2 APLICADA CORRECTAMENTE")
    print(f"Asistencias antiguas actualizadas con su tienda: {resultado.rowcount}")


if __name__ == "__main__":
    migrar()
