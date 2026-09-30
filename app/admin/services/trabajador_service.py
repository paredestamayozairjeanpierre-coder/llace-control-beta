from decimal import Decimal, InvalidOperation

from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from database.connection import SessionLocal
from database.models import Trabajador, Tienda


# ============================================================
# GENERAR CÓDIGO DE TRABAJADOR
# ============================================================

def generar_codigo_trabajador():
    """
    Genera automáticamente un código numérico de 4 dígitos.
    Busca un código disponible entre 1000 y 9999.
    """

    with SessionLocal() as session:

        trabajadores = session.scalars(
            select(Trabajador.codigo)
        ).all()

        codigos_usados = set(trabajadores)

        for numero in range(1000, 10000):
            codigo = str(numero)

            if codigo not in codigos_usados:
                return codigo

        raise ValueError(
            "No hay códigos de trabajador disponibles."
        )


# ============================================================
# CREAR TRABAJADOR
# ============================================================

def crear_trabajador(
    nombre_completo,
    dni,
    tienda_id,
    sueldo_semanal,
    codigo=None,
    fecha_ingreso=None,
):
    """
    Crea un nuevo trabajador.

    Si no se proporciona código, el sistema genera
    automáticamente uno de 4 dígitos.
    """

    nombre_completo = nombre_completo.strip()
    dni = dni.strip()

    if not nombre_completo:
        raise ValueError("El nombre completo es obligatorio.")

    if not dni:
        raise ValueError("El DNI es obligatorio.")

    if not tienda_id:
        raise ValueError("Debe seleccionar una tienda.")

    # Validar sueldo
    try:
        sueldo = Decimal(str(sueldo_semanal))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("El sueldo semanal no es válido.")

    if sueldo < 0:
        raise ValueError("El sueldo semanal no puede ser negativo.")

    # Generar código automáticamente
    if codigo is None or str(codigo).strip() == "":
        codigo = generar_codigo_trabajador()
    else:
        codigo = str(codigo).strip()

        if not codigo.isdigit() or len(codigo) != 4:
            raise ValueError(
                "El código debe tener exactamente 4 dígitos."
            )

    with SessionLocal() as session:

        # Verificar tienda
        tienda = session.scalar(
            select(Tienda).where(
                Tienda.id == tienda_id,
                Tienda.activa.is_(True)
            )
        )

        if not tienda:
            raise ValueError(
                "La tienda seleccionada no existe o está inactiva."
            )

        # Verificar código
        codigo_existente = session.scalar(
            select(Trabajador).where(
                Trabajador.codigo == codigo
            )
        )

        if codigo_existente:
            raise ValueError(
                f"El código {codigo} ya está registrado."
            )

        # Verificar DNI
        dni_existente = session.scalar(
            select(Trabajador).where(
                Trabajador.dni == dni
            )
        )

        if dni_existente:
            raise ValueError(
                f"El DNI {dni} ya está registrado."
            )

        trabajador = Trabajador(
            codigo=codigo,
            nombre_completo=nombre_completo,
            dni=dni,
            tienda_id=tienda_id,
            sueldo_semanal=sueldo,
            activo=True,
            fecha_ingreso=fecha_ingreso,
        )

        session.add(trabajador)

        try:
            session.commit()
            session.refresh(trabajador)

        except IntegrityError:
            session.rollback()
            raise ValueError(
                "No se pudo crear el trabajador. "
                "El código o DNI podría estar duplicado."
            )

        return trabajador


# ============================================================
# OBTENER UN TRABAJADOR
# ============================================================

def obtener_trabajador(trabajador_id):
    """
    Obtiene un trabajador por su ID.
    """

    with SessionLocal() as session:

        trabajador = session.scalar(
            select(Trabajador)
            .options(joinedload(Trabajador.tienda))
            .where(Trabajador.id == trabajador_id)
        )

        return trabajador


# ============================================================
# LISTAR TRABAJADORES
# ============================================================

def listar_trabajadores(activos_solo=True):
    """
    Devuelve todos los trabajadores.

    Por defecto solamente devuelve trabajadores activos.
    """

    with SessionLocal() as session:

        consulta = (
            select(Trabajador)
            .options(joinedload(Trabajador.tienda))
            .order_by(Trabajador.nombre_completo)
        )

        if activos_solo:
            consulta = consulta.where(
                Trabajador.activo.is_(True)
            )

        trabajadores = session.scalars(consulta).all()

        return trabajadores


# ============================================================
# BUSCAR TRABAJADORES
# ============================================================

def buscar_trabajadores(
    texto="",
    tienda_id=None,
    activos_solo=True,
):
    """
    Busca trabajadores por:

    - Nombre
    - Código
    - DNI
    - Tienda
    """

    with SessionLocal() as session:

        consulta = (
            select(Trabajador)
            .options(joinedload(Trabajador.tienda))
        )

        # Solo activos
        if activos_solo:
            consulta = consulta.where(
                Trabajador.activo.is_(True)
            )

        # Filtrar por tienda
        if tienda_id is not None:
            consulta = consulta.where(
                Trabajador.tienda_id == tienda_id
            )

        # Buscar texto
        texto = texto.strip()

        if texto:

            patron = f"%{texto}%"

            consulta = consulta.where(
                or_(
                    Trabajador.nombre_completo.ilike(patron),
                    Trabajador.codigo.ilike(patron),
                    Trabajador.dni.ilike(patron),
                )
            )

        consulta = consulta.order_by(
            Trabajador.nombre_completo
        )

        return session.scalars(consulta).all()


# ============================================================
# ACTUALIZAR TRABAJADOR
# ============================================================

def actualizar_trabajador(
    trabajador_id,
    nombre_completo,
    dni,
    tienda_id,
    sueldo_semanal,
    fecha_ingreso=None,
):
    """
    Actualiza los datos de un trabajador.

    El código NO cambia porque es el identificador
    permanente del trabajador.
    """

    nombre_completo = nombre_completo.strip()
    dni = dni.strip()

    if not nombre_completo:
        raise ValueError("El nombre completo es obligatorio.")

    if not dni:
        raise ValueError("El DNI es obligatorio.")

    if not tienda_id:
        raise ValueError("Debe seleccionar una tienda.")

    try:
        sueldo = Decimal(str(sueldo_semanal))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("El sueldo semanal no es válido.")

    if sueldo < 0:
        raise ValueError(
            "El sueldo semanal no puede ser negativo."
        )

    with SessionLocal() as session:

        trabajador = session.get(
            Trabajador,
            trabajador_id
        )

        if not trabajador:
            raise ValueError(
                "El trabajador no existe."
            )

        # Verificar tienda
        tienda = session.scalar(
            select(Tienda).where(
                Tienda.id == tienda_id,
                Tienda.activa.is_(True)
            )
        )

        if not tienda:
            raise ValueError(
                "La tienda seleccionada no existe o está inactiva."
            )

        # Verificar DNI solamente si cambió
        dni_existente = session.scalar(
            select(Trabajador).where(
                Trabajador.dni == dni,
                Trabajador.id != trabajador_id
            )
        )

        if dni_existente:
            raise ValueError(
                f"El DNI {dni} ya pertenece a otro trabajador."
            )

        trabajador.nombre_completo = nombre_completo
        trabajador.dni = dni
        trabajador.tienda_id = tienda_id
        trabajador.sueldo_semanal = sueldo
        trabajador.fecha_ingreso = fecha_ingreso

        try:
            session.commit()
            session.refresh(trabajador)

        except IntegrityError:
            session.rollback()
            raise ValueError(
                "No se pudo actualizar el trabajador."
            )

        return trabajador


# ============================================================
# DESACTIVAR TRABAJADOR
# ============================================================

def desactivar_trabajador(trabajador_id):
    """
    Desactiva un trabajador.

    NO elimina el registro de la base de datos.
    Esto permite conservar su historial de asistencia
    y pagos.
    """

    with SessionLocal() as session:

        trabajador = session.get(
            Trabajador,
            trabajador_id
        )

        if not trabajador:
            raise ValueError(
                "El trabajador no existe."
            )

        trabajador.activo = False

        session.commit()

        return trabajador


# ============================================================
# ACTIVAR TRABAJADOR
# ============================================================

def activar_trabajador(trabajador_id):
    """
    Reactiva un trabajador previamente desactivado.
    """

    with SessionLocal() as session:

        trabajador = session.get(
            Trabajador,
            trabajador_id
        )

        if not trabajador:
            raise ValueError(
                "El trabajador no existe."
            )

        trabajador.activo = True

        session.commit()

        return trabajador