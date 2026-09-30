from getpass import getpass

from sqlalchemy.orm import Session

from database.connection import engine
from database.models import Usuario
from app.core.security import generar_hash_password


def crear_superadmin():
    print("=" * 50)
    print("      CREAR SUPERADMIN - LLACE CONTROL")
    print("=" * 50)

    nombre = input("Nombre completo: ").strip()
    usuario = input("Usuario de acceso: ").strip()

    if not nombre:
        print("ERROR: El nombre no puede estar vacío.")
        return

    if not usuario:
        print("ERROR: El usuario no puede estar vacío.")
        return

    with Session(engine) as session:

        usuario_existente = (
            session.query(Usuario)
            .filter_by(usuario=usuario)
            .first()
        )

        if usuario_existente:
            print("ERROR: Ese usuario ya existe.")
            return

        password = getpass("Contraseña: ")
        confirmar = getpass("Confirmar contraseña: ")

        if not password:
            print("ERROR: La contraseña no puede estar vacía.")
            return

        if password != confirmar:
            print("ERROR: Las contraseñas no coinciden.")
            return

        nuevo_usuario = Usuario(
            nombre=nombre,
            usuario=usuario,
            password_hash=generar_hash_password(password),
            rol="SUPERADMIN",
            activo=True,
        )

        session.add(nuevo_usuario)
        session.commit()

        print()
        print("=" * 50)
        print("SUPERADMIN CREADO CORRECTAMENTE")
        print("=" * 50)
        print(f"Nombre : {nombre}")
        print(f"Usuario: {usuario}")
        print("Rol    : SUPERADMIN")
        print("=" * 50)


if __name__ == "__main__":
    crear_superadmin()