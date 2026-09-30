import tkinter as tk
from tkinter import messagebox

from app.admin.services.tienda_service import (
    obtener_tienda_por_id,
    contar_trabajadores_tienda,
    actualizar_tienda,
    cambiar_estado_tienda,
)


class TiendaGestionForm(tk.Toplevel):
    def __init__(self, parent=None, tienda_id=None, al_guardar=None):
        super().__init__(parent)

        self.parent = parent
        self.tienda_id = tienda_id
        self.al_guardar = al_guardar

        self.title("LLACE CONTROL BETA - Gestionar tienda")
        self.geometry("560x500")
        self.minsize(560, 500)
        self.maxsize(560, 500)

        self.configure(bg="#f5f5f5")

        self.tienda = obtener_tienda_por_id(self.tienda_id)

        if self.tienda is None:
            messagebox.showerror(
                "Error",
                "La tienda seleccionada no existe.",
                parent=self,
            )
            self.destroy()
            return

        self.crear_interfaz()
        self.cargar_datos()

        self.after(100, self.mostrar_ventana)

    # ---------------------------------------------------------
    # VENTANA
    # ---------------------------------------------------------

    def mostrar_ventana(self):
        self.deiconify()
        self.lift()
        self.focus_force()

        try:
            self.grab_set()
        except tk.TclError:
            pass

        self.entrada_codigo.focus_set()

    # ---------------------------------------------------------
    # INTERFAZ
    # ---------------------------------------------------------

    def crear_interfaz(self):

        # TÍTULO
        frame_titulo = tk.Frame(
            self,
            bg="#111111",
            height=75
        )
        frame_titulo.pack(fill="x")
        frame_titulo.pack_propagate(False)

        tk.Label(
            frame_titulo,
            text="GESTIONAR TIENDA",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#111111"
        ).pack(pady=(14, 2))

        tk.Label(
            frame_titulo,
            text="Editar información y estado de la tienda",
            font=("Arial", 10),
            fg="#cccccc",
            bg="#111111"
        ).pack()

        # CONTENEDOR
        contenido = tk.Frame(
            self,
            bg="#f5f5f5"
        )
        contenido.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        # INFORMACIÓN
        tk.Label(
            contenido,
            text="INFORMACIÓN DE LA TIENDA",
            font=("Arial", 11, "bold"),
            bg="#f5f5f5",
            fg="#222222"
        ).pack(anchor="w", pady=(0, 12))

        # CÓDIGO
        tk.Label(
            contenido,
            text="Código:",
            font=("Arial", 10, "bold"),
            bg="#f5f5f5"
        ).pack(anchor="w")

        self.entrada_codigo = tk.Entry(
            contenido,
            font=("Arial", 12),
            relief="solid",
            bd=1
        )
        self.entrada_codigo.pack(
            fill="x",
            ipady=6,
            pady=(5, 12)
        )

        # NOMBRE
        tk.Label(
            contenido,
            text="Nombre de la tienda:",
            font=("Arial", 10, "bold"),
            bg="#f5f5f5"
        ).pack(anchor="w")

        self.entrada_nombre = tk.Entry(
            contenido,
            font=("Arial", 12),
            relief="solid",
            bd=1
        )
        self.entrada_nombre.pack(
            fill="x",
            ipady=6,
            pady=(5, 15)
        )

        # TRABAJADORES
        frame_info = tk.Frame(
            contenido,
            bg="white",
            relief="solid",
            bd=1
        )
        frame_info.pack(
            fill="x",
            pady=(0, 15)
        )

        tk.Label(
            frame_info,
            text="TRABAJADORES ACTIVOS",
            font=("Arial", 9, "bold"),
            bg="white",
            fg="#666666"
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 2)
        )

        self.label_trabajadores = tk.Label(
            frame_info,
            text="0",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#222222"
        )
        self.label_trabajadores.pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        # ESTADO
        frame_estado = tk.Frame(
            contenido,
            bg="white",
            relief="solid",
            bd=1
        )
        frame_estado.pack(
            fill="x",
            pady=(0, 20)
        )

        tk.Label(
            frame_estado,
            text="ESTADO DE LA TIENDA",
            font=("Arial", 9, "bold"),
            bg="white",
            fg="#666666"
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 2)
        )

        self.label_estado = tk.Label(
            frame_estado,
            text="",
            font=("Arial", 11, "bold"),
            bg="white"
        )
        self.label_estado.pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        # BOTONES
        frame_botones = tk.Frame(
            contenido,
            bg="#f5f5f5"
        )
        frame_botones.pack(
            fill="x",
            side="bottom"
        )

        self.boton_estado = tk.Button(
            frame_botones,
            text="",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8,
            command=self.cambiar_estado
        )
        self.boton_estado.pack(
            side="left"
        )

        tk.Button(
            frame_botones,
            text="CANCELAR",
            font=("Arial", 10, "bold"),
            bg="#dddddd",
            fg="#222222",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=8,
            command=self.destroy
        ).pack(
            side="right",
            padx=(8, 0)
        )

        tk.Button(
            frame_botones,
            text="GUARDAR CAMBIOS",
            font=("Arial", 10, "bold"),
            bg="#f2c300",
            fg="#111111",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=8,
            command=self.guardar_cambios
        ).pack(
            side="right"
        )

    # ---------------------------------------------------------
    # CARGAR DATOS
    # ---------------------------------------------------------

    def cargar_datos(self):

        self.entrada_codigo.delete(0, tk.END)
        self.entrada_codigo.insert(0, self.tienda.codigo)

        self.entrada_nombre.delete(0, tk.END)
        self.entrada_nombre.insert(0, self.tienda.nombre)

        cantidad = contar_trabajadores_tienda(self.tienda.id)

        self.label_trabajadores.config(
            text=str(cantidad)
        )

        self.actualizar_estado_visual()

    # ---------------------------------------------------------
    # ESTADO
    # ---------------------------------------------------------

    def actualizar_estado_visual(self):

        if self.tienda.activa:
            self.label_estado.config(
                text="● ACTIVA",
                fg="#16803c"
            )

            self.boton_estado.config(
                text="DESACTIVAR TIENDA",
                bg="#eeeeee",
                fg="#b00020"
            )

        else:
            self.label_estado.config(
                text="● INACTIVA",
                fg="#b00020"
            )

            self.boton_estado.config(
                text="ACTIVAR TIENDA",
                bg="#eeeeee",
                fg="#16803c"
            )

    # ---------------------------------------------------------
    # GUARDAR CAMBIOS
    # ---------------------------------------------------------

    def guardar_cambios(self):

        codigo = self.entrada_codigo.get().strip()
        nombre = self.entrada_nombre.get().strip()

        if not codigo:
            messagebox.showwarning(
                "Dato requerido",
                "Ingresa el código de la tienda.",
                parent=self
            )
            self.entrada_codigo.focus_set()
            return

        if not nombre:
            messagebox.showwarning(
                "Dato requerido",
                "Ingresa el nombre de la tienda.",
                parent=self
            )
            self.entrada_nombre.focus_set()
            return

        try:
            actualizar_tienda(
                self.tienda.id,
                codigo,
                nombre
            )

            messagebox.showinfo(
                "Guardado",
                "Los cambios de la tienda se guardaron correctamente.",
                parent=self
            )

            if self.al_guardar:
                self.al_guardar()

            self.destroy()

        except ValueError as error:

            messagebox.showwarning(
                "No se pudo guardar",
                str(error),
                parent=self
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Ocurrió un error al guardar la tienda:\n\n{error}",
                parent=self
            )

    # ---------------------------------------------------------
    # CAMBIAR ESTADO
    # ---------------------------------------------------------

    def cambiar_estado(self):

        nuevo_estado = not self.tienda.activa

        if nuevo_estado:
            mensaje = (
                f"¿Deseas activar la tienda '{self.tienda.nombre}'?"
            )
        else:
            mensaje = (
                f"¿Deseas desactivar la tienda '{self.tienda.nombre}'?"
            )

        confirmar = messagebox.askyesno(
            "Confirmar cambio de estado",
            mensaje,
            parent=self
        )

        if not confirmar:
            return

        try:

            cambiar_estado_tienda(
                self.tienda.id,
                nuevo_estado
            )

            self.tienda.activa = nuevo_estado

            self.actualizar_estado_visual()

            if self.al_guardar:
                self.al_guardar()

            if nuevo_estado:
                messagebox.showinfo(
                    "Tienda activada",
                    "La tienda ahora está activa.",
                    parent=self
                )
            else:
                messagebox.showinfo(
                    "Tienda desactivada",
                    "La tienda ahora está inactiva.",
                    parent=self
                )

        except ValueError as error:

            messagebox.showwarning(
                "No se pudo cambiar el estado",
                str(error),
                parent=self
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Ocurrió un error:\n\n{error}",
                parent=self
            )


# -------------------------------------------------------------
# PRUEBA DIRECTA
# -------------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()
    root.withdraw()

    ventana = TiendaGestionForm(
        parent=root,
        tienda_id=1
    )

    root.wait_window(ventana)
    root.destroy()