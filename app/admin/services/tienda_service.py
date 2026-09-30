from sqlalchemy import select, func

from database.connection import SessionLocal
from database.models import Tienda, Trabajador


# ============================================================
# LISTAR TIENDAS
# ============================================================

def listar_tiendas():

    with SessionLocal() as session:

        consulta = (
            select(Tienda)
            .order_by(Tienda.nombre)
        )

        tiendas = session.scalars(
            consulta
        ).all()

        return tiendas


# ============================================================
# BUSCAR TIENDAS
# ============================================================

def buscar_tiendas(texto: str = ""):

    texto = str(texto).strip()

    with SessionLocal() as session:

        consulta = (
            select(Tienda)
            .order_by(Tienda.nombre)
        )

        if texto:

            consulta = consulta.where(
                Tienda.codigo.ilike(f"%{texto}%")
                | Tienda.nombre.ilike(f"%{texto}%")
            )

        tiendas = session.scalars(
            consulta
        ).all()

        return tiendas


# ============================================================
# CONTAR TRABAJADORES DE UNA TIENDA
# ============================================================

def contar_trabajadores_tienda(
    tienda_id: int
):

    with SessionLocal() as session:

        cantidad = session.scalar(
            select(
                func.count(Trabajador.id)
            ).where(
                Trabajador.tienda_id == tienda_id,
                Trabajador.activo.is_(True)
            )
        )

        return cantidad or 0


# ============================================================
# OBTENER TIENDA POR ID
# ============================================================

def obtener_tienda_por_id(
    tienda_id: int
):

    with SessionLocal() as session:

        return session.get(
            Tienda,
            tienda_id
        )


# ============================================================
# OBTENER TIENDA POR CÓDIGO
# ============================================================

def obtener_tienda_por_codigo(
    codigo: str
):

    codigo = str(codigo).strip().upper()

    if not codigo:
        return None

    with SessionLocal() as session:

        return session.scalar(
            select(Tienda)
            .where(
                Tienda.codigo == codigo
            )
        )


# ============================================================
# CREAR TIENDA
# ============================================================

def crear_tienda(
    codigo: str,
    nombre: str
):

    codigo = str(codigo).strip().upper()
    nombre = str(nombre).strip()

    if not codigo:
        raise ValueError(
            "El código de la tienda es obligatorio."
        )

    if not nombre:
        raise ValueError(
            "El nombre de la tienda es obligatorio."
        )

    with SessionLocal() as session:

        # ----------------------------------------------------
        # VALIDAR CÓDIGO REPETIDO
        # ----------------------------------------------------

        tienda_existente = session.scalar(
            select(Tienda)
            .where(
                Tienda.codigo == codigo
            )
        )

        if tienda_existente is not None:

            raise ValueError(
                f"El código '{codigo}' ya está registrado."
            )

        # ----------------------------------------------------
        # CREAR TIENDA
        # ----------------------------------------------------

        tienda = Tienda(
            codigo=codigo,
            nombre=nombre,
            activa=True
        )

        session.add(tienda)

        try:

            session.commit()

            session.refresh(tienda)

        except Exception:

            session.rollback()

            raise

        return tienda


# ============================================================
# ACTUALIZAR TIENDA
# ============================================================

def actualizar_tienda(
    tienda_id: int,
    codigo: str,
    nombre: str
):

    codigo = str(codigo).strip().upper()
    nombre = str(nombre).strip()

    if not codigo:
        raise ValueError(
            "El código de la tienda es obligatorio."
        )

    if not nombre:
        raise ValueError(
            "El nombre de la tienda es obligatorio."
        )

    with SessionLocal() as session:

        # ----------------------------------------------------
        # BUSCAR TIENDA
        # ----------------------------------------------------

        tienda = session.get(
            Tienda,
            tienda_id
        )

        if tienda is None:

            raise ValueError(
                "La tienda no existe."
            )

        # ----------------------------------------------------
        # VALIDAR CÓDIGO REPETIDO
        # ----------------------------------------------------

        tienda_existente = session.scalar(
            select(Tienda)
            .where(
                Tienda.codigo == codigo,
                Tienda.id != tienda_id
            )
        )

        if tienda_existente is not None:

            raise ValueError(
                f"El código '{codigo}' ya está registrado."
            )

        # ----------------------------------------------------
        # ACTUALIZAR
        # ----------------------------------------------------

        tienda.codigo = codigo
        tienda.nombre = nombre

        try:

            session.commit()

            session.refresh(tienda)

        except Exception:

            session.rollback()

            raise

        return tienda


# ============================================================
# CAMBIAR ESTADO DE TIENDA
# ============================================================

def cambiar_estado_tienda(
    tienda_id: int,
    activa: bool
):

    with SessionLocal() as session:

        tienda = session.get(
            Tienda,
            tienda_id
        )

        if tienda is None:

            raise ValueError(
                "La tienda no existe."
            )

        tienda.activa = bool(activa)

        try:

            session.commit()

            session.refresh(tienda)

        except Exception:

            session.rollback()

            raise

        return tienda