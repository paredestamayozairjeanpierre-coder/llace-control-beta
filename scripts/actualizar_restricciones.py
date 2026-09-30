from sqlalchemy import text

from database.connection import engine


def actualizar_restricciones():
    with engine.begin() as connection:

        # Código del trabajador: exactamente 4 dígitos
        connection.execute(text("""
            ALTER TABLE trabajadores
            ADD CONSTRAINT ck_trabajador_codigo_4_digitos
            CHECK (codigo ~ '^[0-9]{4}$');
        """))

        # Sueldo semanal: nunca puede ser negativo
        connection.execute(text("""
            ALTER TABLE trabajadores
            ADD CONSTRAINT ck_trabajador_sueldo_no_negativo
            CHECK (sueldo_semanal >= 0);
        """))

        # Minutos de tardanza: nunca pueden ser negativos
        connection.execute(text("""
            ALTER TABLE asistencias
            ADD CONSTRAINT ck_asistencia_minutos_no_negativos
            CHECK (minutos_tardanza >= 0);
        """))

    print("RESTRICCIONES ACTUALIZADAS CORRECTAMENTE")


if __name__ == "__main__":
    actualizar_restricciones()