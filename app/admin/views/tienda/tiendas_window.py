import tkinter as tk
from tkinter import ttk, messagebox

from app.admin.services.tienda_service import (
    listar_tiendas,
    buscar_tiendas,
    contar_trabajadores_tienda,
)

from app.admin.views.tienda.tienda_form import TiendaForm
from app.admin.views.tienda.tienda_gestion_form import TiendaGestionForm


# ============================================================
# VENTANA DE TIENDAS
# ============================================================

class TiendasWindow(tk.Toplevel):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.title("LLACE CONTROL BETA - Tiendas")

        self.geometry("1150x700")
        self.minsize(950, 600)

        self.configure(
            bg="#F4F5F7"
        )

        self.crear_interfaz()
        self.cargar_tiendas()


    # ========================================================
    # INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        # ====================================================
        # ENCABEZADO
        # ====================================================

        encabezado = tk.Frame(
            self,
            bg="#FFFFFF"
        )

        encabezado.pack(
            fill="x"
        )


        titulo = tk.Label(
            encabezado,
            text="TIENDAS",
            font=("Arial", 26, "bold"),
            fg="#111827",
            bg="#FFFFFF"
        )

        titulo.pack(
            side="left",
            padx=35,
            pady=(25, 5)
        )


        boton_nueva = tk.Button(
            encabezado,
            text="+  NUEVA TIENDA",
            font=("Arial", 10, "bold"),
            bg="#FACC15",
            fg="#111827",
            activebackground="#EAB308",
            activeforeground="#111827",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            command=self.nueva_tienda
        )

        boton_nueva.pack(
            side="right",
            padx=35,
            pady=25
        )


        subtitulo = tk.Label(
            encabezado,
            text="Gestiona las tiendas registradas en LLACE CONTROL",
            font=("Arial", 10),
            fg="#6B7280",
            bg="#FFFFFF"
        )

        subtitulo.pack(
            anchor="w",
            padx=38,
            pady=(0, 20)
        )


        # ====================================================
        # CONTENIDO PRINCIPAL
        # ====================================================

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


        # ====================================================
        # CONFIGURACIÓN GRID
        # ====================================================

        contenido.grid_rowconfigure(
            1,
            weight=1
        )

        contenido.grid_columnconfigure(
            0,
            weight=1
        )


        # ====================================================
        # BUSCADOR
        # ====================================================

        buscador_frame = tk.Frame(
            contenido,
            bg="#F4F5F7"
        )

        buscador_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )


        buscador_frame.grid_columnconfigure(
            0,
            weight=1
        )


        self.entrada_busqueda = tk.Entry(
            buscador_frame,
            font=("Arial", 11),
            relief="solid",
            bd=1
        )

        self.entrada_busqueda.grid(
            row=0,
            column=0,
            sticky="ew",
            ipady=9
        )

        self.entrada_busqueda.insert(
            0,
            "Buscar por código o nombre..."
        )

        self.entrada_busqueda.configure(
            fg="#9CA3AF"
        )

        self.entrada_busqueda.bind(
            "<FocusIn>",
            self.limpiar_placeholder
        )

        self.entrada_busqueda.bind(
            "<Return>",
            lambda event: self.buscar()
        )


        boton_buscar = tk.Button(
            buscador_frame,
            text="BUSCAR",
            font=("Arial", 10, "bold"),
            bg="#111827",
            fg="#FFFFFF",
            activebackground="#1F2937",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=10,
            command=self.buscar
        )

        boton_buscar.grid(
            row=0,
            column=1,
            padx=(10, 0)
        )


        # ====================================================
        # CONTENEDOR DE TABLA
        # ====================================================

        tabla_frame = tk.Frame(
            contenido,
            bg="#FFFFFF",
            highlightbackground="#D1D5DB",
            highlightthickness=1
        )

        tabla_frame.grid(
            row=1,
            column=0,
            sticky="nsew"
        )


        tabla_frame.grid_rowconfigure(
            0,
            weight=1
        )

        tabla_frame.grid_columnconfigure(
            0,
            weight=1
        )


        # ====================================================
        # TREEVIEW
        # ====================================================

        columnas = (
            "codigo",
            "nombre",
            "trabajadores",
            "estado",
            "acciones"
        )


        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )


        # ====================================================
        # ENCABEZADOS
        # ====================================================

        self.tabla.heading(
            "codigo",
            text="CÓDIGO"
        )

        self.tabla.heading(
            "nombre",
            text="NOMBRE"
        )

        self.tabla.heading(
            "trabajadores",
            text="TRABAJADORES"
        )

        self.tabla.heading(
            "estado",
            text="ESTADO"
        )

        self.tabla.heading(
            "acciones",
            text="ACCIONES"
        )


        # ====================================================
        # COLUMNAS
        # ====================================================

        self.tabla.column(
            "codigo",
            width=130,
            anchor="center"
        )

        self.tabla.column(
            "nombre",
            width=420,
            anchor="w"
        )

        self.tabla.column(
            "trabajadores",
            width=180,
            anchor="center"
        )

        self.tabla.column(
            "estado",
            width=180,
            anchor="center"
        )

        self.tabla.column(
            "acciones",
            width=180,
            anchor="center"
        )


        # ====================================================
        # COLOCAR TREEVIEW
        # ====================================================

        self.tabla.grid(
            row=0,
            column=0,
            sticky="nsew"
        )


        # ====================================================
        # SCROLLBAR
        # ====================================================

        scrollbar = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self.tabla.yview
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.tabla.configure(
            yscrollcommand=scrollbar.set
        )


        # ====================================================
        # DOBLE CLIC
        # ====================================================

        self.tabla.bind(
            "<Double-1>",
            self.gestionar_tienda
        )


        # ====================================================
        # ESTILO
        # ====================================================

        estilo = ttk.Style()

        try:

            estilo.theme_use(
                "clam"
            )

        except Exception:

            pass


        estilo.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#111827",
            rowheight=58,
            fieldbackground="#FFFFFF",
            font=("Arial", 10)
        )


        estilo.configure(
            "Treeview.Heading",
            background="#F3F4F6",
            foreground="#374151",
            font=("Arial", 9, "bold"),
            padding=10
        )


        estilo.map(
            "Treeview",
            background=[
                ("selected", "#FEF3C7")
            ],
            foreground=[
                ("selected", "#111827")
            ]
        )


        # ====================================================
        # ZONA DE ACCIONES
        # ====================================================

        acciones_frame = tk.Frame(
            contenido,
            bg="#F4F5F7"
        )

        acciones_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(12, 0)
        )


        self.boton_gestionar = tk.Button(
            acciones_frame,
            text="GESTIONAR TIENDA",
            font=("Arial", 10, "bold"),
            bg="#111827",
            fg="#FFFFFF",
            activebackground="#1F2937",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=22,
            pady=10,
            command=self.gestionar_tienda
        )

        self.boton_gestionar.pack(
            side="left"
        )


        tk.Label(
            acciones_frame,
            text="Selecciona una tienda o haz doble clic sobre ella para gestionarla.",
            font=("Arial", 9),
            fg="#6B7280",
            bg="#F4F5F7"
        ).pack(
            side="left",
            padx=15
        )


        # ====================================================
        # PIE
        # ====================================================

        pie = tk.Frame(
            contenido,
            bg="#F4F5F7"
        )

        pie.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(10, 0)
        )


        self.label_total = tk.Label(
            pie,
            text="0 tiendas registradas",
            font=("Arial", 10),
            fg="#6B7280",
            bg="#F4F5F7"
        )

        self.label_total.pack(
            side="left"
        )


    # ========================================================
    # CARGAR TIENDAS
    # ========================================================

    def cargar_tiendas(
        self,
        texto=""
    ):

        try:

            if texto:

                tiendas = buscar_tiendas(
                    texto
                )

            else:

                tiendas = listar_tiendas()


            # ------------------------------------------------
            # LIMPIAR
            # ------------------------------------------------

            for item in self.tabla.get_children():

                self.tabla.delete(
                    item
                )


            # ------------------------------------------------
            # CARGAR
            # ------------------------------------------------

            for tienda in tiendas:

                trabajadores = contar_trabajadores_tienda(
                    tienda.id
                )


                if tienda.activa:

                    estado = "●  ACTIVA"

                else:

                    estado = "●  INACTIVA"


                self.tabla.insert(
                    "",
                    "end",
                    iid=str(tienda.id),
                    values=(
                        tienda.codigo,
                        tienda.nombre,
                        trabajadores,
                        estado,
                        "Editar / Gestionar"
                    )
                )


            # ------------------------------------------------
            # TOTAL
            # ------------------------------------------------

            cantidad = len(tiendas)


            if cantidad == 1:

                texto_total = "1 tienda registrada"

            else:

                texto_total = (
                    f"{cantidad} tiendas registradas"
                )


            self.label_total.config(
                text=texto_total
            )


        except Exception as error:

            messagebox.showerror(
                "Error",
                f"No se pudieron cargar las tiendas.\n\n{error}",
                parent=self
            )

            print(
                "ERROR AL CARGAR TIENDAS:"
            )

            print(error)


    # ========================================================
    # BUSCAR
    # ========================================================

    def buscar(self):

        texto = self.entrada_busqueda.get().strip()


        if texto == "Buscar por código o nombre...":

            texto = ""


        self.cargar_tiendas(
            texto
        )


    # ========================================================
    # PLACEHOLDER
    # ========================================================

    def limpiar_placeholder(
        self,
        event=None
    ):

        if self.entrada_busqueda.get() == "Buscar por código o nombre...":

            self.entrada_busqueda.delete(
                0,
                tk.END
            )

            self.entrada_busqueda.configure(
                fg="#111827"
            )


    # ========================================================
    # NUEVA TIENDA
    # ========================================================

    def nueva_tienda(self):

        TiendaForm(
            parent=self,
            al_guardar=self.recargar_tiendas
        )


    # ========================================================
    # GESTIONAR TIENDA
    # ========================================================

    def gestionar_tienda(
        self,
        event=None
    ):

        seleccion = self.tabla.selection()


        if not seleccion:

            messagebox.showwarning(
                "Selecciona una tienda",
                "Primero selecciona una tienda de la lista.",
                parent=self
            )

            return


        try:

            tienda_id = int(
                seleccion[0]
            )


            TiendaGestionForm(
                parent=self,
                tienda_id=tienda_id,
                al_guardar=self.recargar_tiendas
            )


        except Exception as error:

            messagebox.showerror(
                "Error",
                f"No se pudo abrir la gestión de la tienda.\n\n{error}",
                parent=self
            )

            print(
                "ERROR AL GESTIONAR TIENDA:"
            )

            print(error)


    # ========================================================
    # RECARGAR
    # ========================================================

    def recargar_tiendas(self):

        texto = self.entrada_busqueda.get().strip()


        if texto == "Buscar por código o nombre...":

            texto = ""


        self.cargar_tiendas(
            texto
        )


# ============================================================
# EJECUCIÓN DIRECTA
# ============================================================

if __name__ == "__main__":

    raiz = tk.Tk()

    raiz.withdraw()


    ventana = TiendasWindow(
        parent=raiz
    )


    ventana.protocol(
        "WM_DELETE_WINDOW",
        raiz.destroy
    )


    raiz.mainloop()