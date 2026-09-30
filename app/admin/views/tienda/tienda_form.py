import tkinter as tk
from tkinter import messagebox

from app.admin.services.tienda_service import crear_tienda


# ============================================================
# FORMULARIO NUEVA TIENDA
# ============================================================

class TiendaForm(tk.Toplevel):

    def __init__(self, parent=None, al_guardar=None):

        super().__init__(parent)

        self.al_guardar = al_guardar

        self.title("LLACE CONTROL BETA - Nueva tienda")

        self.geometry("520x390")
        self.minsize(520, 390)
        self.maxsize(520, 390)

        self.configure(
            bg="#F4F5F7"
        )

        # ----------------------------------------------------
        # POSICIONAR EN EL CENTRO
        # ----------------------------------------------------

        self.update_idletasks()

        ancho = 520
        alto = 390

        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()

        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2

        self.geometry(
            f"{ancho}x{alto}+{x}+{y}"
        )

        # ----------------------------------------------------
        # CONFIGURACIÓN DE VENTANA
        # ----------------------------------------------------

        if parent is not None:

            self.transient(parent)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.destroy
        )

        self.crear_interfaz()

        # ----------------------------------------------------
        # MOSTRAR VENTANA
        # ----------------------------------------------------

        self.after(
            100,
            self.mostrar_ventana
        )


    # ========================================================
    # MOSTRAR VENTANA
    # ========================================================

    def mostrar_ventana(self):

        self.deiconify()

        self.lift()

        self.focus_force()

        try:

            self.grab_set()

        except tk.TclError:

            pass

        self.entrada_codigo.focus_set()


    # ========================================================
    # INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        # ----------------------------------------------------
        # ENCABEZADO
        # ----------------------------------------------------

        encabezado = tk.Frame(
            self,
            bg="#FFFFFF"
        )

        encabezado.pack(
            fill="x"
        )

        titulo = tk.Label(
            encabezado,
            text="NUEVA TIENDA",
            font=("Arial", 22, "bold"),
            fg="#111827",
            bg="#FFFFFF"
        )

        titulo.pack(
            anchor="w",
            padx=30,
            pady=(25, 5)
        )

        subtitulo = tk.Label(
            encabezado,
            text="Registra una nueva tienda en LLACE CONTROL",
            font=("Arial", 10),
            fg="#6B7280",
            bg="#FFFFFF"
        )

        subtitulo.pack(
            anchor="w",
            padx=30,
            pady=(0, 20)
        )


        # ----------------------------------------------------
        # CONTENIDO
        # ----------------------------------------------------

        contenido = tk.Frame(
            self,
            bg="#F4F5F7"
        )

        contenido.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )


        # ----------------------------------------------------
        # CÓDIGO
        # ----------------------------------------------------

        label_codigo = tk.Label(
            contenido,
            text="Código",
            font=("Arial", 10, "bold"),
            fg="#374151",
            bg="#F4F5F7"
        )

        label_codigo.pack(
            anchor="w"
        )

        self.entrada_codigo = tk.Entry(
            contenido,
            font=("Arial", 11),
            relief="solid",
            bd=1
        )

        self.entrada_codigo.pack(
            fill="x",
            ipady=8,
            pady=(6, 18)
        )


        # ----------------------------------------------------
        # NOMBRE
        # ----------------------------------------------------

        label_nombre = tk.Label(
            contenido,
            text="Nombre de la tienda",
            font=("Arial", 10, "bold"),
            fg="#374151",
            bg="#F4F5F7"
        )

        label_nombre.pack(
            anchor="w"
        )

        self.entrada_nombre = tk.Entry(
            contenido,
            font=("Arial", 11),
            relief="solid",
            bd=1
        )

        self.entrada_nombre.pack(
            fill="x",
            ipady=8,
            pady=(6, 20)
        )


        # ----------------------------------------------------
        # BOTONES
        # ----------------------------------------------------

        botones = tk.Frame(
            contenido,
            bg="#F4F5F7"
        )

        botones.pack(
            fill="x"
        )


        boton_guardar = tk.Button(
            botones,
            text="GUARDAR",
            font=("Arial", 10, "bold"),
            bg="#FACC15",
            fg="#111827",
            activebackground="#EAB308",
            activeforeground="#111827",
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=11,
            command=self.guardar
        )

        boton_guardar.pack(
            side="right"
        )


        boton_cancelar = tk.Button(
            botones,
            text="CANCELAR",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF",
            fg="#374151",
            activebackground="#E5E7EB",
            activeforeground="#374151",
            relief="solid",
            bd=1,
            cursor="hand2",
            padx=20,
            pady=10,
            command=self.destroy
        )

        boton_cancelar.pack(
            side="right",
            padx=(0, 10)
        )


        # ----------------------------------------------------
        # ENTER
        # ----------------------------------------------------

        self.entrada_codigo.bind(
            "<Return>",
            lambda event: self.entrada_nombre.focus_set()
        )

        self.entrada_nombre.bind(
            "<Return>",
            lambda event: self.guardar()
        )


    # ========================================================
    # GUARDAR
    # ========================================================

    def guardar(self):

        codigo = self.entrada_codigo.get().strip()

        nombre = self.entrada_nombre.get().strip()


        # ----------------------------------------------------
        # VALIDAR CÓDIGO
        # ----------------------------------------------------

        if not codigo:

            messagebox.showwarning(
                "Campo obligatorio",
                "Ingresa el código de la tienda.",
                parent=self
            )

            self.entrada_codigo.focus_set()

            return


        # ----------------------------------------------------
        # VALIDAR NOMBRE
        # ----------------------------------------------------

        if not nombre:

            messagebox.showwarning(
                "Campo obligatorio",
                "Ingresa el nombre de la tienda.",
                parent=self
            )

            self.entrada_nombre.focus_set()

            return


        # ----------------------------------------------------
        # CREAR TIENDA
        # ----------------------------------------------------

        try:

            tienda = crear_tienda(
                codigo,
                nombre
            )

        except ValueError as error:

            messagebox.showwarning(
                "No se puede guardar",
                str(error),
                parent=self
            )

            return

        except Exception as error:

            print(
                "ERROR AL CREAR TIENDA:"
            )

            print(error)

            messagebox.showerror(
                "Error",
                f"No se pudo crear la tienda.\n\n{error}",
                parent=self
            )

            return


        # ----------------------------------------------------
        # ÉXITO
        # ----------------------------------------------------

        messagebox.showinfo(
            "Tienda creada",
            f"La tienda '{tienda.nombre}' fue registrada correctamente.",
            parent=self
        )


        if self.al_guardar is not None:

            self.al_guardar()


        self.destroy()


# ============================================================
# PRUEBA DIRECTA
# ============================================================

if __name__ == "__main__":

    raiz = tk.Tk()

    raiz.title(
        "LLACE CONTROL - Prueba"
    )

    raiz.geometry(
        "1x1+0+0"
    )

    raiz.withdraw()


    ventana = TiendaForm(
        parent=raiz
    )


    raiz.mainloop()