from dataclasses import dataclass


@dataclass
class UsuarioSesion:
    id: int
    nombre: str
    usuario: str
    rol: str


class Sesion:
    """
    Mantiene la información del usuario actualmente autenticado.
    """

    def __init__(self):
        self.usuario: UsuarioSesion | None = None

    def iniciar(self, usuario_db):
        """
        Guarda los datos necesarios del usuario autenticado.
        """

        self.usuario = UsuarioSesion(
            id=usuario_db.id,
            nombre=usuario_db.nombre,
            usuario=usuario_db.usuario,
            rol=usuario_db.rol,
        )

    def cerrar(self):
        """
        Cierra la sesión actual.
        """

        self.usuario = None

    def esta_activa(self) -> bool:
        """
        Indica si existe una sesión activa.
        """

        return self.usuario is not None

    def es_superadmin(self) -> bool:
        """
        Comprueba si el usuario actual es Superadmin.
        """

        return (
            self.usuario is not None
            and self.usuario.rol == "SUPERADMIN"
        )

    def es_admin(self) -> bool:
        """
        Comprueba si el usuario actual es Admin.
        """

        return (
            self.usuario is not None
            and self.usuario.rol == "ADMIN"
        )


# Una única sesión para toda la aplicación
sesion_actual = Sesion()