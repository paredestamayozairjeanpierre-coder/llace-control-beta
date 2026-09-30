
import os
from pathlib import Path
from dotenv import load_dotenv

# Ruta principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar el .env ubicado en la carpeta principal
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "No se encontró DATABASE_URL. "
        "Verifica que exista el archivo .env "
        "y que contenga la conexión a PostgreSQL."
    )


# ----------------------------------------------------------------
# Configuración propia de cada equipo
# ----------------------------------------------------------------

# Código de la tienda donde está instalado ESTE marcador (ej. "PL").
# En la PC del administrador se deja vacío.
TIENDA_CODIGO = (os.getenv("TIENDA_CODIGO") or "").strip().upper() or None

# Si es "1", un trabajador puede marcar en una tienda que no es la suya
# (la asistencia queda guardada con la tienda donde marcó).
PERMITIR_OTRA_TIENDA = (
    os.getenv("MARCADOR_PERMITIR_OTRA_TIENDA", "0").strip() == "1"
)
