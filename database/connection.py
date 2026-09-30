from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from database.config import DATABASE_URL


def _argumentos_de_conexion() -> dict:
    """
    - connect_timeout: si no hay internet, falla en 5 s en vez de colgarse.
    - sslmode=require: cuando la base NO está en esta misma PC, la conexión
      viaja cifrada (obligatorio para una base en la nube).
    """
    url = make_url(DATABASE_URL)

    argumentos = {"connect_timeout": 5}

    servidor = (url.host or "").lower()
    es_local = servidor in ("", "localhost", "127.0.0.1", "::1")

    if not es_local and "sslmode" not in url.query:
        argumentos["sslmode"] = "require"

    return argumentos


# Conexión principal a PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=5,
    connect_args=_argumentos_de_conexion(),
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
