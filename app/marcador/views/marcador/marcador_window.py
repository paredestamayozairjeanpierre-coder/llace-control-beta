from app.core import tiempo
import tkinter as tk
from tkinter import messagebox

from app.marcador.services.marcador_service import (
    obtener_estado_marcacion,
    registrar_marcacion,
)


class MarcadorWindow(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("LLACE CONTROL BETA - Marcador")
        self.configure(bg="#0D0D0D")
        self.state("zoomed")

        self.codigo_actual = ""
        self.trabajador_actual = None

        self.crear_interfaz()

    # ==========================================================
    # UTILIDADES
    # ==========================================================

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def crear_interfaz(self):
        self.mostrar_pantalla_codigo()

    # ==========================================================
    # ENCABEZADO
    # ==========================================================

    def crear_encabezado(self, contenedor):

        encabezado = tk.Frame(
            contenedor,
            bg="#0D0D0D"
        )
        encabezado.pack(
            fill="x",
            padx=50,
            pady=(30, 10)
        )

        logo = tk.Label(
            encabezado,
            text="LLACE",
            font=("Arial", 34, "bold"),
            fg="#FFFFFF",
            bg="#0D0D0D"
        )
        logo.pack(side="left")

        beta = tk.Label(
            encabezado,
            text=" CONTROL BETA",
            font=("Arial", 18, "bold"),
            fg="#F5C400",
            bg="#0D0D0D"
        )
        beta.pack(
            side="left",
            pady=(12, 0)
        )

        reloj = tk.Label(
            encabezado,
            text="",
            font=("Arial", 22, "bold"),
            fg="#FFFFFF",
            bg="#0D0D0D"
        )
        reloj.pack(side="right")

        self.actualizar_reloj(reloj)

    def actualizar_reloj(self, etiqueta):

        ahora = tiempo.ahora()

        etiqueta.config(
            text=ahora.strftime("%H:%M")
        )

        self.after(
            1000,
            lambda: self.actualizar_reloj(etiqueta)
        )

    # ==========================================================
    # PANTALLA 1 - INGRESO DE CÓDIGO
    # ==========================================================

    def mostrar_pantalla_codigo(self):

        self.limpiar_pantalla()

        contenedor = tk.Frame(
            self,
            bg="#0D0D0D"
        )
        contenedor.pack(
            fill="both",
            expand=True
        )

        self.crear_encabezado(contenedor)

        centro = tk.Frame(
            contenedor,
            bg="#0D0D0D"
        )
        centro.pack(expand=True)

        titulo = tk.Label(
            centro,
            text="INGRESA TU CÓDIGO",
            font=("Arial", 34, "bold"),
            fg="#FFFFFF",
            bg="#0D0D0D"
        )
        titulo.pack(
            pady=(30, 5)
        )

        subtitulo = tk.Label(
            centro,
            text="Para registrar tu asistencia",
            font=("Arial", 17),
            fg="#BDBDBD",
            bg="#0D0D0D"
        )
        subtitulo.pack(
            pady=(0, 30)
        )

        caja = tk.Frame(
            centro,
            bg="#181818",
            highlightbackground="#F5C400",
            highlightthickness=2,
            width=430,
            height=80
        )
        caja.pack()
        caja.pack_propagate(False)

        self.entrada_codigo = tk.Entry(
            caja,
            font=("Arial", 32, "bold"),
            justify="center",
            fg="#FFFFFF",
            bg="#181818",
            insertbackground="#F5C400",
            relief="flat",
            bd=0
        )
        self.entrada_codigo.pack(
            fill="both",
            expand=True,
            padx=20
        )

        self.entrada_codigo.focus_set()

        boton = tk.Button(
            centro,
            text="→   CONTINUAR",
            font=("Arial", 18, "bold"),
            fg="#111111",
            bg="#F5C400",
            activebackground="#FFD633",
            activeforeground="#111111",
            relief="flat",
            cursor="hand2",
            width=25,
            height=2,
            command=self.procesar_codigo
        )
        boton.pack(pady=30)

        self.entrada_codigo.bind(
            "<Return>",
            lambda evento: self.procesar_codigo()
        )

        pie = tk.Label(
            contenedor,
            text="LLACE CONTROL BETA   •   SISTEMA DE ASISTENCIA",
            font=("Arial", 11),
            fg="#777777",
            bg="#0D0D0D"
        )
        pie.pack(pady=20)

    # ==========================================================
    # PROCESAR CÓDIGO
    # ==========================================================

    def procesar_codigo(self):

        codigo = self.entrada_codigo.get().strip()

        if not codigo:

            messagebox.showwarning(
                "Código",
                "Ingresa tu código de trabajador."
            )

            return

        resultado = obtener_estado_marcacion(codigo)

        if not resultado["ok"]:

            if resultado["tipo"] == "YA_MARCO":

                messagebox.showinfo(
                    "Asistencia",
                    resultado["mensaje"]
                )

            else:

                messagebox.showerror(
                    "Código no encontrado",
                    resultado["mensaje"]
                )

            self.entrada_codigo.delete(
                0,
                tk.END
            )

            self.entrada_codigo.focus_set()

            return

        self.codigo_actual = codigo
        self.trabajador_actual = resultado["trabajador"]

        self.mostrar_confirmacion()

    # ==========================================================
    # PANTALLA 2 - CONFIRMACIÓN
    # ==========================================================

    def mostrar_confirmacion(self):

        self.limpiar_pantalla()

        contenedor = tk.Frame(
            self,
            bg="#0D0D0D"
        )
        contenedor.pack(
            fill="both",
            expand=True
        )

        self.crear_encabezado(contenedor)

        centro = tk.Frame(
            contenedor,
            bg="#0D0D0D"
        )
        centro.pack(expand=True)

        nombre = self.trabajador_actual.nombre_completo
        codigo = self.trabajador_actual.codigo
        tienda = self.trabajador_actual.tienda.nombre

        titulo = tk.Label(
            centro,
            text=f"¡HOLA, {nombre.split()[0].upper()}!",
            font=("Arial", 34, "bold"),
            fg="#FFFFFF",
            bg="#0D0D0D"
        )
        titulo.pack(
            pady=(30, 25)
        )

        tarjeta = tk.Frame(
            centro,
            bg="#181818",
            highlightbackground="#F5C400",
            highlightthickness=1,
            width=600,
            height=210
        )
        tarjeta.pack()
        tarjeta.pack_propagate(False)

        datos = tk.Label(
            tarjeta,
            text=(
                f"👤  {nombre.upper()}\n\n"
                f"▣  Código: {codigo}\n\n"
                f"🏪  {tienda.upper()}"
            ),
            font=("Arial", 17),
            justify="left",
            anchor="w",
            fg="#FFFFFF",
            bg="#181818"
        )
        datos.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        pregunta = tk.Label(
            centro,
            text="¿ERES TÚ?",
            font=("Arial", 28, "bold"),
            fg="#FFFFFF",
            bg="#0D0D0D"
        )
        pregunta.pack(pady=25)

        botones = tk.Frame(
            centro,
            bg="#0D0D0D"
        )
        botones.pack()

        confirmar = tk.Button(
            botones,
            text="✓  SÍ, MARCAR",
            font=("Arial", 16, "bold"),
            fg="#FFFFFF",
            bg="#20B84B",
            activebackground="#28D45A",
            relief="flat",
            cursor="hand2",
            width=18,
            height=2,
            command=self.confirmar_marcacion
        )
        confirmar.pack(
            side="left",
            padx=10
        )

        cancelar = tk.Button(
            botones,
            text="✕  NO",
            font=("Arial", 16, "bold"),
            fg="#FFFFFF",
            bg="#C62828",
            activebackground="#E53935",
            relief="flat",
            cursor="hand2",
            width=12,
            height=2,
            command=self.mostrar_pantalla_codigo
        )
        cancelar.pack(
            side="left",
            padx=10
        )

    # ==========================================================
    # CONFIRMAR MARCACIÓN
    # ==========================================================

    def confirmar_marcacion(self):

        resultado = registrar_marcacion(
            self.codigo_actual
        )

        if not resultado["ok"]:

            messagebox.showerror(
                "Error",
                resultado["mensaje"]
            )

            self.mostrar_pantalla_codigo()

            return

        self.trabajador_actual = resultado["trabajador"]

        self.mostrar_marcacion_registrada(
            resultado["asistencia"]
        )

    # ==========================================================
    # PANTALLA 3 - MARCACIÓN REGISTRADA
    # ==========================================================

    def mostrar_marcacion_registrada(
        self,
        asistencia
    ):

        self.limpiar_pantalla()

        contenedor = tk.Frame(
            self,
            bg="#0D0D0D"
        )
        contenedor.pack(
            fill="both",
            expand=True
        )

        self.crear_encabezado(contenedor)

        centro = tk.Frame(
            contenedor,
            bg="#0D0D0D"
        )
        centro.pack(expand=True)

        # CHECK VERDE

        check = tk.Label(
            centro,
            text="✓",
            font=("Arial", 70, "bold"),
            fg="#35D45A",
            bg="#0D0D0D"
        )
        check.pack()

        # TÍTULO

        titulo = tk.Label(
            centro,
            text="¡MARCACIÓN REGISTRADA!",
            font=("Arial", 38, "bold"),
            fg="#FFFFFF",
            bg="#0D0D0D"
        )
        titulo.pack(
            pady=(5, 25)
        )

        nombre = self.trabajador_actual.nombre_completo
        codigo = self.trabajador_actual.codigo
        tienda = self.trabajador_actual.tienda.nombre

        # TARJETA

        tarjeta = tk.Frame(
            centro,
            bg="#181818",
            highlightbackground="#F5C400",
            highlightthickness=1,
            width=650,
            height=230
        )
        tarjeta.pack()
        tarjeta.pack_propagate(False)

        datos = tk.Label(
            tarjeta,
            text=(
                f"👤  {nombre.upper()}\n\n"
                f"▣  Código: {codigo}\n\n"
                f"🏪  {tienda.upper()}"
            ),
            font=("Arial", 18),
            justify="left",
            anchor="w",
            fg="#FFFFFF",
            bg="#181818"
        )
        datos.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

        # HORA

        hora = asistencia.hora_marcacion
        hora_texto = hora.strftime("%H:%M:%S")

        reloj = tk.Label(
            centro,
            text=f"◷  {hora_texto}",
            font=("Arial", 32, "bold"),
            fg="#FFFFFF",
            bg="#0D0D0D"
        )
        reloj.pack(
            pady=(25, 10)
        )

        # ESTADO

        estado = asistencia.estado

        if estado == "PUNTUAL":

            texto_estado = "●  PUNTUAL"
            color_estado = "#20B84B"

        elif estado == "TARDANZA":

            texto_estado = "●  TARDANZA"
            color_estado = "#F5A400"

        elif estado == "FALTA":

            texto_estado = "●  FALTA"
            color_estado = "#C62828"

        else:

            texto_estado = f"●  {estado}"
            color_estado = "#3976D3"

        estado_label = tk.Label(
            centro,
            text=texto_estado,
            font=("Arial", 17, "bold"),
            fg="#FFFFFF",
            bg=color_estado,
            padx=25,
            pady=8
        )
        estado_label.pack()

        # MENSAJE

        mensaje = tk.Label(
            centro,
            text="¡QUE TENGAS UN BUEN DÍA!",
            font=("Arial", 22, "bold"),
            fg="#FFFFFF",
            bg="#0D0D0D"
        )
        mensaje.pack(
            pady=30
        )

        # VOLVER AL INICIO

        self.after(
            5000,
            self.mostrar_pantalla_codigo
        )


# ==============================================================
# EJECUTAR MARCADOR
# ==============================================================

if __name__ == "__main__":

    app = MarcadorWindow()
    app.mainloop()  