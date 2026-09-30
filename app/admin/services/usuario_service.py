from sqlalchemy import select, or_

from database.connection import SessionLocal
from database.models import Usuario

from app.core.security import generar_hash_password
from app.core.permisos import exigir_superadmin



# ==============================================================
# ROLES PERMITIDOS
# ==============================================================

ROLES_PERMITIDOS = {
    "SUPERADMIN",
    "ADMIN",
}


# ==============================================================
# LISTAR USUARIOS
# ==============================================================

def listar_usuarios():
    """
    Devuelve todos los usuarios registrados.
    """

    with SessionLocal() as session:

        consulta = (
            select(Usuario)
            .order_by(Usuario.nombre)
        )

        return session.scalars(consulta).all()


# ==============================================================
# LISTAR USUARIOS ACTIVOS
# ==============================================================

def listar_usuarios_activos():
    """
    Devuelve únicamente los usuarios activos.
    """

    with SessionLocal() as session:

        consulta = (
            select(Usuario)
            .where(
                Usuario.activo.is_(True)
            )
            .order_by(Usuario.nombre)
        )

        return session.scalars(consulta).all()


# ==============================================================
# BUSCAR USUARIOS
# ==============================================================

def buscar_usuarios(texto: str = ""):
    """
    Busca usuarios por nombre, usuario o rol.
    """

    texto = str(texto).strip()

    with SessionLocal() as session:

        consulta = (
            select(Usuario)
            .order_by(Usuario.nombre)
        )

        if texto:

            patron = f"%{texto}%"

            consulta = consulta.where(
                or_(
                    Usuario.nombre.ilike(patron),
                    Usuario.usuario.ilike(patron),
                    Usuario.rol.ilike(patron),
                )
            )

        return session.scalars(consulta).all()


# ==============================================================
# OBTENER USUARIO POR ID
# ==============================================================

def obtener_usuario_por_id(usuario_id: int):

    with SessionLocal() as session:

        return session.get(
            Usuario,
            usuario_id
        )


# ==============================================================
# OBTENER USUARIO POR USERNAME
# ==============================================================

def obtener_usuario_por_username(usuario: str):

    usuario = str(usuario).strip().lower()

    if not usuario:
        return None

    with SessionLocal() as session:

        consulta = select(Usuario).where(
            Usuario.usuario.ilike(usuario)
        )

        return session.scalar(consulta)


# ==============================================================
# COMPROBAR SI EXISTE USERNAME
# ==============================================================

def existe_usuario(usuario: str):

    usuario = str(usuario).strip().lower()

    if not usuario:
        return False

    with SessionLocal() as session:

        consulta = select(Usuario.id).where(
            Usuario.usuario.ilike(usuario)
        )

        resultado = session.scalar(consulta)

        return resultado is not None


# ==============================================================
# CREAR USUARIO
# ==============================================================

def crear_usuario(
    nombre: str,
    usuario: str,
    password: str,
    rol: str,
):
    """
    Crea un usuario nuevo.

    La contraseña recibida se convierte inmediatamente
    en un hash seguro antes de guardarse.
    """

    exigir_superadmin()

    nombre = str(nombre).strip()
    usuario = str(usuario).strip().lower()
    password = str(password)
    rol = str(rol).strip().upper()

    # ----------------------------------------------------------
    # VALIDACIONES
    # ----------------------------------------------------------

    if not nombre:
        raise ValueError(
            "El nombre del usuario es obligatorio."
        )

    if not usuario:
        raise ValueError(
            "El nombre de usuario es obligatorio."
        )

    if not password:
        raise ValueError(
            "La contraseña es obligatoria."
        )

    if len(password) < 6:
        raise ValueError(
            "La contraseña debe tener al menos 6 caracteres."
        )

    if rol not in ROLES_PERMITIDOS:
        raise ValueError(
            "El rol indicado no es válido."
        )

    with SessionLocal() as session:

        # ------------------------------------------------------
        # COMPROBAR USERNAME DUPLICADO
        # ------------------------------------------------------

        usuario_existente = session.scalar(
            select(Usuario).where(
                Usuario.usuario.ilike(usuario)
            )
        )

        if usuario_existente is not None:

            raise ValueError(
                f"El usuario '{usuario}' ya está registrado."
            )

        # ------------------------------------------------------
        # GENERAR HASH
        # ------------------------------------------------------

        password_hash = generar_hash_password(
            password
        )

        # ------------------------------------------------------
        # CREAR USUARIO
        # ------------------------------------------------------

        nuevo_usuario = Usuario(
            nombre=nombre,
            usuario=usuario,
            password_hash=password_hash,
            rol=rol,
            activo=True,
        )

        session.add(nuevo_usuario)

        try:

            session.commit()

            session.refresh(
                nuevo_usuario
            )

        except Exception:

            session.rollback()

            raise

        return nuevo_usuario


# ==============================================================
# ACTUALIZAR USUARIO
# ==============================================================

def actualizar_usuario(
    usuario_id: int,
    nombre: str,
    usuario: str,
    rol: str,
):
    """
    Actualiza nombre, usuario y rol.

    La contraseña no se modifica aquí.
    """

    exigir_superadmin()

    if not isinstance(usuario_id, int) or isinstance(usuario_id, bool) or usuario_id <= 0:
        raise ValueError("El ID del usuario no es válido.")

    nombre = str(nombre).strip()
    usuario = str(usuario).strip().lower()
    rol = str(rol).strip().upper()

    if not nombre:
        raise ValueError(
            "El nombre del usuario es obligatorio."
        )

    if not usuario:
        raise ValueError(
            "El nombre de usuario es obligatorio."
        )

    if rol not in ROLES_PERMITIDOS:
        raise ValueError(
            "El rol indicado no es válido."
        )

    with SessionLocal() as session:

        usuario_db = session.get(
            Usuario,
            usuario_id
        )

        if usuario_db is None:

            raise ValueError(
                "El usuario no existe."
            )

        # ------------------------------------------------------
        # PROTEGER SUPERADMIN
        # ------------------------------------------------------

        if (
            usuario_db.rol == "SUPERADMIN"
            and rol != "SUPERADMIN"
        ):

            raise ValueError(
                "No se puede cambiar el rol del SUPERADMIN."
            )

        # ------------------------------------------------------
        # COMPROBAR USERNAME DUPLICADO
        # ------------------------------------------------------

        usuario_existente = session.scalar(
            select(Usuario).where(
                Usuario.usuario.ilike(usuario),
                Usuario.id != usuario_id,
            )
        )

        if usuario_existente is not None:

            raise ValueError(
                f"El usuario '{usuario}' ya está registrado."
            )

        # ------------------------------------------------------
        # ACTUALIZAR
        # ------------------------------------------------------

        usuario_db.nombre = nombre
        usuario_db.usuario = usuario
        usuario_db.rol = rol

        try:

            session.commit()

            session.refresh(
                usuario_db
            )

        except Exception:

            session.rollback()

            raise

        return usuario_db


# ==============================================================
# CAMBIAR CONTRASEÑA
# ==============================================================

def cambiar_password(
    usuario_id: int,
    nueva_password: str,
):
    """
    Cambia la contraseña de un usuario.

    La contraseña anterior nunca se necesita conocer.
    Se genera un nuevo salt automáticamente.
    """

    exigir_superadmin()

    if not isinstance(usuario_id, int) or isinstance(usuario_id, bool) or usuario_id <= 0:
        raise ValueError("El ID del usuario no es válido.")

    nueva_password = str(nueva_password)

    if not nueva_password:
        raise ValueError(
            "La nueva contraseña es obligatoria."
        )

    if len(nueva_password) < 6:
        raise ValueError(
            "La contraseña debe tener al menos 6 caracteres."
        )

    with SessionLocal() as session:

        usuario_db = session.get(
            Usuario,
            usuario_id
        )

        if usuario_db is None:

            raise ValueError(
                "El usuario no existe."
            )

        # ------------------------------------------------------
        # GENERAR NUEVO HASH
        # ------------------------------------------------------

        usuario_db.password_hash = (
            generar_hash_password(
                nueva_password
            )
        )

        try:

            session.commit()

            session.refresh(
                usuario_db
            )

        except Exception:

            session.rollback()

            raise

        return usuario_db


# ==============================================================
# CAMBIAR ESTADO
# ==============================================================

def cambiar_estado_usuario(
    usuario_id: int,
    activo: bool,
):
    """
    Activa o desactiva un usuario.

    El SUPERADMIN no puede ser desactivado.
    """

    exigir_superadmin()

    if not isinstance(usuario_id, int) or isinstance(usuario_id, bool) or usuario_id <= 0:
        raise ValueError("El ID del usuario no es válido.")

    if not isinstance(activo, bool):
        raise ValueError("El estado del usuario debe ser verdadero o falso.")

    with SessionLocal() as session:

        usuario_db = session.get(
            Usuario,
            usuario_id
        )

        if usuario_db is None:

            raise ValueError(
                "El usuario no existe."
            )

        # ------------------------------------------------------
        # PROTEGER SUPERADMIN
        # ------------------------------------------------------

        if usuario_db.rol == "SUPERADMIN":

            if not activo:

                raise ValueError(
                    "El SUPERADMIN no puede ser desactivado."
                )

        # ------------------------------------------------------
        # CAMBIAR ESTADO
        # ------------------------------------------------------

        usuario_db.activo = activo

        try:

            session.commit()

            session.refresh(
                usuario_db
            )

        except Exception:

            session.rollback()

            raise

        return usuario_db




# ==============================================================
# GUARDAR USUARIO COMPLETO (OPERACION ATOMICA)
# ==============================================================

def guardar_usuario_completo(
    nombre: str,
    usuario: str,
    rol: str,
    activo: bool,
    password: str = "",
    usuario_id: int = None,
):
    """Crea o actualiza una cuenta en una sola transaccion."""

    exigir_superadmin()

    nombre = str(nombre).strip()
    usuario = str(usuario).strip().lower()
    rol = str(rol).strip().upper()
    password = str(password)

    if not nombre:
        raise ValueError("El nombre del usuario es obligatorio.")
    if len(nombre) < 3:
        raise ValueError("El nombre debe tener al menos 3 caracteres.")
    if not usuario or " " in usuario or len(usuario) < 3:
        raise ValueError("El nombre de usuario no es válido.")
    if rol not in ROLES_PERMITIDOS:
        raise ValueError("El rol indicado no es válido.")
    if not isinstance(activo, bool):
        raise ValueError("El estado del usuario debe ser verdadero o falso.")
    if rol == "SUPERADMIN" and not activo:
        raise ValueError("El SUPERADMIN no puede ser creado como inactivo.")
    if password and len(password) < 6:
        raise ValueError("La contraseña debe tener al menos 6 caracteres.")
    if usuario_id is not None and (
        not isinstance(usuario_id, int)
        or isinstance(usuario_id, bool)
        or usuario_id <= 0
    ):
        raise ValueError("El ID del usuario no es válido.")
    if usuario_id is None and not password:
        raise ValueError("La contraseña es obligatoria.")

    with SessionLocal() as session:
        try:
            if usuario_id is None:
                usuario_existente = session.scalar(
                    select(Usuario).where(Usuario.usuario.ilike(usuario))
                )
                if usuario_existente is not None:
                    raise ValueError(f"El usuario '{usuario}' ya está registrado.")

                usuario_db = Usuario(
                    nombre=nombre,
                    usuario=usuario,
                    password_hash=generar_hash_password(password),
                    rol=rol,
                    activo=activo,
                )
                session.add(usuario_db)
            else:
                usuario_db = session.get(Usuario, usuario_id)
                if usuario_db is None:
                    raise ValueError("El usuario no existe.")
                if usuario_db.rol == "SUPERADMIN" and rol != "SUPERADMIN":
                    raise ValueError("No se puede cambiar el rol del SUPERADMIN.")
                if usuario_db.rol == "SUPERADMIN" and not activo:
                    raise ValueError("El SUPERADMIN no puede ser desactivado.")

                usuario_existente = session.scalar(
                    select(Usuario).where(
                        Usuario.usuario.ilike(usuario),
                        Usuario.id != usuario_id,
                    )
                )
                if usuario_existente is not None:
                    raise ValueError(f"El usuario '{usuario}' ya está registrado.")

                usuario_db.nombre = nombre
                usuario_db.usuario = usuario
                usuario_db.rol = rol
                usuario_db.activo = activo
                if password:
                    usuario_db.password_hash = generar_hash_password(password)

            session.commit()
            session.refresh(usuario_db)
            return usuario_db
        except Exception:
            session.rollback()
            raise


# ==============================================================
# ACTIVAR USUARIO
# ==============================================================

def activar_usuario(usuario_id: int):

    return cambiar_estado_usuario(
        usuario_id,
        True
    )


# ==============================================================
# DESACTIVAR USUARIO
# ==============================================================

def desactivar_usuario(usuario_id: int):

    return cambiar_estado_usuario(
        usuario_id,
        False
    )


# ==============================================================
# CONTAR USUARIOS
# ==============================================================

def contar_usuarios():

    with SessionLocal() as session:

        return session.query(
            Usuario
        ).count()


# ==============================================================
# CONTAR USUARIOS ACTIVOS
# ==============================================================

def contar_usuarios_activos():

    with SessionLocal() as session:

        return session.query(
            Usuario
        ).filter(
            Usuario.activo.is_(True)
        ).count()