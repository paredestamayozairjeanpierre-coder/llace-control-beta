# Poner LLACE CONTROL en la nube (3 tiendas + admin)

Todas las PCs se conectan a **la misma base PostgreSQL en la nube**.
Cada marcación queda con la tienda donde se hizo, y el admin ve las 3 tiendas.

```
PC Tienda PL ──┐
PC Tienda EC ──┼──► PostgreSQL en la nube ◄── PC Admin
PC Tienda GL ──┘
```

## 1. Crear la base en la nube

Usa un PostgreSQL administrado (Supabase, Neon o Railway).

- Elige la región más cercana a Lima (São Paulo / `sa-east-1` si está disponible).
- Copia la cadena de conexión **directa** (puerto 5432) y conviértela al formato de la app:
  `postgresql+psycopg://USUARIO:CLAVE@HOST:5432/NOMBRE_BD`
- Verifica en tu plan si incluye **respaldos automáticos**. Si no, programa un
  `pg_dump` diario (ver sección 6).

## 2. Preparar la base (desde tu PC, una sola vez)

Pon esa cadena (la del usuario dueño) en tu `.env` y ejecuta, en este orden:

```
pip install -r requirements.txt
python -m scripts.crear_base          # crea las tablas
python -m scripts.sembrar_datos       # crea las 3 tiendas
python -m scripts.crear_superadmin    # crea tu usuario admin
python -m scripts.migrar_v2           # tienda_id + índices (seguro repetirlo)
python -m scripts.crear_roles_db      # crea llace_marcador y llace_admin
```

**Si ya tienes datos reales en una base local**, en vez de los 3 primeros pasos
cópialos a la nube:

```
pg_dump -Fc --no-owner "postgresql://postgres:CLAVE@localhost/llace_control" -f llace.dump
pg_restore --no-owner -d "CADENA_DE_LA_NUBE" llace.dump
```

y luego ejecuta `migrar_v2` y `crear_roles_db`.

## 3. Configurar cada PC

Copia el ejemplo como `.env` (NO subir ni compartir este archivo):

| PC | Archivo de ejemplo | Detalle |
|---|---|---|
| Tienda | `.env.marcador.example` | usuario `llace_marcador`, y `TIENDA_CODIGO` de esa tienda |
| Administrador | `.env.admin.example` | usuario `llace_admin`, sin `TIENDA_CODIGO` |

Nunca uses el usuario dueño (`postgres`) en las PCs de las tiendas.

## 4. Qué cambió en esta versión

- **Hora oficial = hora del servidor (Lima).** Cambiar el reloj de Windows ya no
  permite marcar puntual. La marcación toma la hora dentro de la misma transacción.
- **Cada asistencia guarda `tienda_id`** (donde se marcó).
- **El marcador conoce su tienda** (`TIENDA_CODIGO`). Un trabajador de otra tienda
  es rechazado, salvo `MARCADOR_PERMITIR_OTRA_TIENDA=1`.
- **Sin internet:** el marcador muestra "No hay conexión... tu marcación NO se ha
  registrado" (falla en 5 s, no se cuelga ni se cierra).
- **Conexión cifrada (SSL)** automática cuando la base no está en la misma PC.
- **Permisos mínimos:** el marcador solo puede leer e insertar asistencias.
- Índices en `asistencias` (fecha, tienda) para consultas rápidas.

## 5. Prueba antes de usarlo en serio

1. Marcar desde la PC de la tienda A con un trabajador de A → OK.
2. Marcar desde la PC de la tienda A con un trabajador de B → debe rechazarlo.
3. Abrir el panel admin → deben verse ambas marcaciones.
4. Desconectar el internet y marcar → debe avisar "sin conexión".
5. Cambiar la hora de Windows y marcar → debe seguir usando la hora real.

## 6. Respaldo manual diario (si tu plan no lo incluye)

```
pg_dump -Fc "CADENA_DE_LA_NUBE" -f respaldo_AAAA-MM-DD.dump
```

Prográmalo con el Programador de tareas de Windows y guarda copias fuera de la PC.

## 7. Siguiente etapa recomendada (fase 2)

Que solo un servidor (tu FastAPI en `backend/`) hable con la base, y las apps
usen `https://` con login. Así las PCs ya no guardan ninguna contraseña de base
de datos. Los `services/` se reutilizan casi sin cambios.
