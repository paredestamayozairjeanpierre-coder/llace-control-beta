from fastapi import FastAPI

app = FastAPI(
    title="LLACE CONTROL",
    version="0.1.0"
)


@app.get("/")
def inicio():
    return {
        "ok": True,
        "sistema": "LLACE CONTROL",
        "mensaje": "API funcionando correctamente"
    }