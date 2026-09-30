from sqlalchemy.orm import Session

from database.connection import engine
from database.models import Tienda


TIENDAS_INICIALES = [
    {
        "codigo": "PL",
        "nombre": "Peru Llaves",
    },
    {
        "codigo": "EC",
        "nombre": "El Cerrojo",
    },
    {
        "codigo": "GL",
        "nombre": "Grupo LLACE — Almacén",
    },
]


def sembrar_tiendas():
    with Session(engine) as session:
        for datos in TIENDAS_INICIALES:
            tienda = session.query(Tienda).filter_by(
                codigo=datos["codigo"]
            ).first()

            if tienda is None:
                tienda = Tienda(
                    codigo=datos["codigo"],
                    nombre=datos["nombre"],
                    activa=True,
                )
                session.add(tienda)
                print(f"Tienda creada: {datos['nombre']}")
            else:
                print(f"Tienda ya existe: {datos['nombre']}")

        session.commit()


if __name__ == "__main__":
    sembrar_tiendas()
    print("DATOS INICIALES CARGADOS CORRECTAMENTE")