from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Tienda(Base):
    __tablename__ = "tiendas"

    id: Mapped[int] = mapped_column(primary_key=True)

    codigo: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    activa: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    trabajadores: Mapped[list["Trabajador"]] = relationship(
        back_populates="tienda"
    )


class Trabajador(Base):
    __tablename__ = "trabajadores"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    codigo: Mapped[str] = mapped_column(
        String(4),
        unique=True,
        nullable=False,
    )

    nombre_completo: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    dni: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    tienda_id: Mapped[int] = mapped_column(
        ForeignKey("tiendas.id"),
        nullable=False,
    )

    sueldo_semanal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    fecha_ingreso: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "codigo ~ '^[0-9]{4}$'",
            name="ck_trabajador_codigo_4_digitos",
        ),
        CheckConstraint(
            "sueldo_semanal >= 0",
            name="ck_trabajador_sueldo_no_negativo",
        ),
    )

    tienda: Mapped["Tienda"] = relationship(
        back_populates="trabajadores"
    )

    asistencias: Mapped[list["Asistencia"]] = relationship(
        back_populates="trabajador"
    )

    descuentos: Mapped[list["Descuento"]] = relationship(
        back_populates="trabajador"
    )


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    usuario: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    rol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class Asistencia(Base):
    __tablename__ = "asistencias"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    trabajador_id: Mapped[int] = mapped_column(
        ForeignKey("trabajadores.id"),
        nullable=False,
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    # Tienda donde se hizo la marcación (puede diferir de la tienda
    # habitual del trabajador si rota). NULL solo en registros antiguos.
    tienda_id: Mapped[int | None] = mapped_column(
        ForeignKey("tiendas.id"),
        nullable=True,
        index=True,
    )

    hora_marcacion: Mapped[datetime | None] = mapped_column(
    DateTime,
    nullable=True
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    minutos_tardanza: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "trabajador_id",
            "fecha",
            name="uq_asistencia_trabajador_fecha",
        ),
        CheckConstraint(
            "minutos_tardanza >= 0",
            name="ck_asistencia_minutos_no_negativos",
        ),
    )

    trabajador: Mapped["Trabajador"] = relationship(
        back_populates="asistencias"
    )

    tienda: Mapped["Tienda | None"] = relationship()

    justificacion: Mapped["Justificacion | None"] = relationship(
        back_populates="asistencia",
        uselist=False,
    )

    descuentos: Mapped[list["Descuento"]] = relationship(
        back_populates="asistencia"
    )


class Justificacion(Base):
    __tablename__ = "justificaciones"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    asistencia_id: Mapped[int] = mapped_column(
        ForeignKey("asistencias.id"),
        unique=True,
        nullable=False,
    )

    motivo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    observacion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    justificado_por: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
    )

    fecha_justificacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    asistencia: Mapped["Asistencia"] = relationship(
        back_populates="justificacion"
    )


class Descuento(Base):
    __tablename__ = "descuentos"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    trabajador_id: Mapped[int] = mapped_column(
        ForeignKey("trabajadores.id"),
        nullable=False,
    )

    asistencia_id: Mapped[int | None] = mapped_column(
        ForeignKey("asistencias.id"),
        nullable=True,
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    monto: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    observacion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    registrado_por: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=False,
    )

    trabajador: Mapped["Trabajador"] = relationship(
        back_populates="descuentos"
    )

    asistencia: Mapped["Asistencia | None"] = relationship(
        back_populates="descuentos"
    )