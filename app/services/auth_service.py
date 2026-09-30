from sqlalchemy.orm import Session

from database.connection import engine
from database.models import Usuario
from app.core.security import verificar_password


def autenticar_usuario(usuario: str, password: str):
    """
    Busca un usuario activo y verifica su contraseña.

    Retorna el objeto Usuario si las credenciales son correctas.
    Retorna None si no son válidas.
    """

    usuario = usuario.strip()

    if not usuario or not password:
        return None

    with Session(engine) as session:
        usuario_db = (
            session.query(Usuario)
            .filter(
                Usuario.usuario == usuario,
                Usuario.activo.is_(True),
            )
            .first()
        )

        if usuario_db is None:
            return None

        if not verificar_password(
            password,
            usuario_db.password_hash,
        ):
            return None

        return usuario_db