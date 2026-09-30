from database.connection import engine
from database.models import Base


def crear_tablas():
    Base.metadata.create_all(bind=engine)
    print("TABLAS CREADAS CORRECTAMENTE")


if __name__ == "__main__":
    crear_tablas()