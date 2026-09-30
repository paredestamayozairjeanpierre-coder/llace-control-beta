import hashlib
import hmac
import secrets


ALGORITMO = "sha256"
ITERACIONES = 310_000


def generar_hash_password(password: str) -> str:
    """
    Genera un hash seguro para almacenar una contraseña.
    La contraseña original nunca se guarda.
    """

    salt = secrets.token_hex(16)

    hash_password = hashlib.pbkdf2_hmac(
        ALGORITMO,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERACIONES,
    )

    return f"pbkdf2_{ALGORITMO}${ITERACIONES}${salt}${hash_password.hex()}"


def verificar_password(password: str, password_hash: str) -> bool:
    """
    Comprueba si una contraseña coincide con el hash almacenado.
    """

    try:
        algoritmo, iteraciones, salt, hash_guardado = password_hash.split("$")

        if algoritmo != f"pbkdf2_{ALGORITMO}":
            return False

        hash_calculado = hashlib.pbkdf2_hmac(
            ALGORITMO,
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iteraciones),
        )

        return hmac.compare_digest(
            hash_calculado.hex(),
            hash_guardado,
        )

    except (ValueError, TypeError):
        return False