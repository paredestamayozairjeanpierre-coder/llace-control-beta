from app.core import tiempo
import sys
import subprocess
from pathlib import Path
from datetime import date, datetime, time

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QHeaderView,
    QLineEdit,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from app.services.dashboard_service import obtener_resumen_dashboard
from database.connection import SessionLocal
from database.models import Trabajador, Asistencia, Tienda
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.core.session import sesion_actual
from app.admin.views.usuario.usuario_window import UsuariosWindow
from app.admin.views.descuento.descuentos_window import DescuentosWindow
from app.admin.views.reporte.reportes_window import ReportesWindow
from app.admin.views.trabajador.trabajadores_window import TrabajadoresWindow
from app.admin.views.asistencia.asistencias_window import AsistenciasWindow


class DashboardWindow(QMainWindow):




    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "LLACE CONTROL"
        )

        self.setMinimumSize(
            1200,
            720
        )

        # Página de Usuarios: se crea al ingresar por primera vez.
        self.pagina_usuarios = None
        self.pagina_asistencias = None
        self.ventana_descuentos = None
        self.ventana_reportes = None

        self.crear_interfaz()

    # ==========================================================
    # CREAR INTERFAZ
    # ==========================================================

    def crear_interfaz(self):

        # ======================================================
        # SESIÓN ACTUAL
        # ======================================================

        usuario_actual = sesion_actual.usuario

        if usuario_actual is not None:

            nombre_usuario = usuario_actual.nombre
            usuario = usuario_actual.usuario
            rol = usuario_actual.rol

        else:

            nombre_usuario = "Usuario"
            usuario = ""
            rol = "SIN SESIÓN"

        # ======================================================
        # DATOS DEL DASHBOARD
        # ======================================================

        try:

            resumen_dashboard = (
                obtener_resumen_dashboard()
            )

        except Exception as error:

            print(
                "ERROR AL CARGAR DASHBOARD:"
            )

            print(
                error
            )

            resumen_dashboard = {
                "tiendas": 0,
                "trabajadores": 0,
                "asistencias_hoy": 0,
                "faltas_hoy": 0,
            }

        # ======================================================
        # VENTANA PRINCIPAL
        # ======================================================

        central = QWidget()

        self.setCentralWidget(
            central
        )

        layout_principal = QHBoxLayout(
            central
        )

        layout_principal.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout_principal.setSpacing(
            0
        )

        # ======================================================
        # BARRA LATERAL
        # ======================================================

        sidebar = QFrame()

        sidebar.setObjectName(
            "sidebar"
        )

        sidebar.setFixedWidth(
            235
        )

        layout_sidebar = QVBoxLayout(
            sidebar
        )

        layout_sidebar.setContentsMargins(
            18,
            25,
            18,
            20
        )

        layout_sidebar.setSpacing(
            6
        )

        # ======================================================
        # LOGO
        # ======================================================

        logo = QLabel(
            "LLACE\nCONTROL"
        )

        logo.setObjectName(
            "logo"
        )

        logo.setAlignment(
            Qt.AlignLeft
        )

        layout_sidebar.addWidget(
            logo
        )

        subtitulo_logo = QLabel(
            rol
        )

        subtitulo_logo.setObjectName(
            "subtitulo_logo"
        )

        layout_sidebar.addWidget(
            subtitulo_logo
        )

        layout_sidebar.addSpacing(
            30
        )

        # ======================================================
        # PRINCIPAL
        # ======================================================

        layout_sidebar.addWidget(
            self.crear_titulo_seccion(
                "PRINCIPAL"
            )
        )

        self.btn_inicio = self.crear_boton(
            "⌂   Inicio"
        )
        self.btn_inicio.clicked.connect(
            self.mostrar_inicio
        )

        self.btn_resumen = self.crear_boton(
            "▣   Resumen"
        )
        self.btn_resumen.clicked.connect(
            self.mostrar_resumen
        )

        layout_sidebar.addWidget(
            self.btn_inicio
        )

        layout_sidebar.addWidget(
            self.btn_resumen
        )

        # ======================================================
        # PERSONAL
        # ======================================================

        layout_sidebar.addSpacing(
            18
        )

        layout_sidebar.addWidget(
            self.crear_titulo_seccion(
                "PERSONAL"
            )
        )

        # ------------------------------------------------------
        # TRABAJADORES
        # ------------------------------------------------------

        self.btn_trabajadores = self.crear_boton(
            "♙   Trabajadores"
        )

        self.btn_trabajadores.clicked.connect(
            self.abrir_trabajadores
        )

        layout_sidebar.addWidget(
            self.btn_trabajadores
        )

        # ------------------------------------------------------
        # USUARIOS
        # ------------------------------------------------------

        self.btn_usuarios = self.crear_boton(
            "♙   Usuarios"
        )

        self.btn_usuarios.clicked.connect(
            self.abrir_usuarios
        )

        layout_sidebar.addWidget(
            self.btn_usuarios
        )

        # ======================================================
        # ASISTENCIA
        # ======================================================

        layout_sidebar.addSpacing(
            18
        )

        layout_sidebar.addWidget(
            self.crear_titulo_seccion(
                "ASISTENCIA"
            )
        )

        # ------------------------------------------------------
        # ASISTENCIAS
        # ------------------------------------------------------

        self.btn_asistencias = self.crear_boton(
            "◷   Asistencias"
        )

        self.btn_asistencias.clicked.connect(
            self.abrir_asistencias
        )

        # ------------------------------------------------------
        # JUSTIFICACIONES
        # ------------------------------------------------------

        self.btn_justificaciones = self.crear_boton(
            "✓   Justificaciones"
        )
        
        self.btn_justificaciones.clicked.connect(
        self.abrir_justificaciones
        )

        # ------------------------------------------------------
        # DESCUENTOS
        # ------------------------------------------------------

        self.btn_descuentos = self.crear_boton(
            "S/   Descuentos"
        )

        self.btn_descuentos.clicked.connect(
            self.abrir_descuentos
        )

        layout_sidebar.addWidget(
            self.btn_asistencias
        )

        layout_sidebar.addWidget(
            self.btn_justificaciones
        )

        layout_sidebar.addWidget(
            self.btn_descuentos
        )

        # ======================================================
        # ORGANIZACIÓN
        # ======================================================

        layout_sidebar.addSpacing(
            18
        )

        layout_sidebar.addWidget(
            self.crear_titulo_seccion(
                "ORGANIZACIÓN"
            )
        )

        self.btn_tiendas = self.crear_boton(
            "▣   Tiendas"
        )

        self.btn_tiendas.clicked.connect(
            self.abrir_tiendas
        )

        layout_sidebar.addWidget(
            self.btn_tiendas
        )

        # ======================================================
        # SISTEMA
        # ======================================================

        layout_sidebar.addSpacing(
            18
        )

        layout_sidebar.addWidget(
            self.crear_titulo_seccion(
                "SISTEMA"
            )
        )

        self.btn_reportes = self.crear_boton(
            "▤   Reportes"
        )
        self.btn_reportes.clicked.connect(
        self.abrir_reportes
        )

        self.btn_configuracion = self.crear_boton(
            "⚙   Configuración"
        )

        layout_sidebar.addWidget(
            self.btn_reportes
        )

        layout_sidebar.addWidget(
            self.btn_configuracion
        )

        # ======================================================
        # ESPACIO FLEXIBLE
        # ======================================================

        layout_sidebar.addStretch()

        # ======================================================
        # CERRAR SESIÓN
        # ======================================================

        self.btn_cerrar = self.crear_boton(
            "↪   Cerrar sesión"
        )

        self.btn_cerrar.setObjectName(
            "btn_cerrar"
        )

        self.btn_cerrar.clicked.connect(
            self.cerrar_sesion
        )

        layout_sidebar.addWidget(
            self.btn_cerrar
        )

        # ======================================================
        # CONTENIDO PRINCIPAL
        # ======================================================

        contenido = QWidget()

        contenido.setObjectName(
            "contenido"
        )

        layout_contenido = QVBoxLayout(
            contenido
        )

        layout_contenido.setContentsMargins(
            35,
            25,
            35,
            25
        )

        layout_contenido.setSpacing(
            20
        )

        # ======================================================
        # CABECERA
        # ======================================================

        cabecera = QHBoxLayout()

        bloque_bienvenida = QVBoxLayout()

        titulo = QLabel(
            f"BIENVENIDO, {nombre_usuario.upper()} 👋"
        )

        titulo.setObjectName(
            "titulo_principal"
        )

        subtitulo = QLabel(
            f"{rol}  ·  Centro de control general"
        )

        subtitulo.setObjectName(
            "subtitulo_principal"
        )

        bloque_bienvenida.addWidget(
            titulo
        )

        bloque_bienvenida.addWidget(
            subtitulo
        )

        cabecera.addLayout(
            bloque_bienvenida
        )

        cabecera.addStretch()

        usuario_superior = QLabel(
            f"● {usuario.upper()}\n"
            f"   {rol}"
        )

        usuario_superior.setObjectName(
            "usuario_superior"
        )

        usuario_superior.setAlignment(
            Qt.AlignRight
        )

        cabecera.addWidget(
            usuario_superior
        )

        layout_contenido.addLayout(
            cabecera
        )

        # ======================================================
        # TARJETAS PRINCIPALES
        # ======================================================

        tarjetas = QHBoxLayout()

        tarjetas.setSpacing(
            15
        )

        tarjetas.addWidget(
            self.crear_tarjeta(
                "TIENDAS",
                str(
                    resumen_dashboard[
                        "tiendas"
                    ]
                ),
                "Tiendas registradas",
                "tiendas"
            )
        )

        tarjetas.addWidget(
            self.crear_tarjeta(
                "TRABAJADORES",
                str(
                    resumen_dashboard[
                        "trabajadores"
                    ]
                ),
                "Personal activo",
                "trabajadores"
            )
        )

        tarjetas.addWidget(
            self.crear_tarjeta(
                "ASISTENCIA HOY",
                (
                    f'{resumen_dashboard["asistencias_hoy"]}'
                    f' / '
                    f'{resumen_dashboard["trabajadores"]}'
                ),
                "Marcaciones registradas",
                "asistencia"
            )
        )

        tarjetas.addWidget(
            self.crear_tarjeta(
                "FALTAS",
                str(
                    resumen_dashboard[
                        "faltas_hoy"
                    ]
                ),
                "Faltas de hoy",
                "faltas"
            )
        )

        layout_contenido.addLayout(
            tarjetas
        )

        # ======================================================
        # ASISTENCIAS DE LA SEMANA
        # ======================================================

        titulo_resumen = QLabel(
            "ASISTENCIAS DE LA SEMANA"
        )

        titulo_resumen.setObjectName(
            "titulo_bloque"
        )

        layout_contenido.addWidget(
            titulo_resumen
        )

        resumen = QFrame()

        resumen.setObjectName(
            "bloque"
        )

        layout_resumen = QVBoxLayout(
            resumen
        )

        layout_resumen.setContentsMargins(
            20,
            20,
            20,
            20
        )

        texto_grafico = QLabel(
            "Aquí irá el gráfico semanal de asistencias"
        )

        texto_grafico.setObjectName(
            "placeholder"
        )

        texto_grafico.setAlignment(
            Qt.AlignCenter
        )

        layout_resumen.addWidget(
            texto_grafico
        )

        dias = QHBoxLayout()

        for dia in [
            "LUN",
            "MAR",
            "MIÉ",
            "JUE",
            "VIE",
            "SÁB"
        ]:

            etiqueta = QLabel(
                dia
            )

            etiqueta.setObjectName(
                "dia"
            )

            etiqueta.setAlignment(
                Qt.AlignCenter
            )

            dias.addWidget(
                etiqueta
            )

        layout_resumen.addLayout(
            dias
        )

        layout_contenido.addWidget(
            resumen
        )

        # ======================================================
        # ESTADO POR TIENDA
        # ======================================================

        titulo_tiendas = QLabel(
            "ESTADO POR TIENDA"
        )

        titulo_tiendas.setObjectName(
            "titulo_bloque"
        )

        layout_contenido.addWidget(
            titulo_tiendas
        )

        tiendas_layout = QHBoxLayout()

        tiendas_layout.setSpacing(
            15
        )

        tiendas_layout.addWidget(
            self.crear_tienda(
                "PERU LLAVES",
                "Sin datos todavía"
            )
        )

        tiendas_layout.addWidget(
            self.crear_tienda(
                "EL CERROJO",
                "Sin datos todavía"
            )
        )

        tiendas_layout.addWidget(
            self.crear_tienda(
                "GRUPO LLACE — ALMACÉN",
                "Sin datos todavía"
            )
        )

        layout_contenido.addLayout(
            tiendas_layout
        )

        # ======================================================
        # ACTIVIDAD RECIENTE
        # ======================================================

        titulo_actividad = QLabel(
            "ACTIVIDAD RECIENTE"
        )

        titulo_actividad.setObjectName(
            "titulo_bloque"
        )

        layout_contenido.addWidget(
            titulo_actividad
        )

        actividad = QFrame()

        actividad.setObjectName(
            "bloque"
        )

        layout_actividad = QVBoxLayout(
            actividad
        )

        actividad_texto = QLabel(
            "Todavía no hay actividad registrada."
        )

        actividad_texto.setObjectName(
            "actividad"
        )

        layout_actividad.addWidget(
            actividad_texto
        )

        layout_contenido.addWidget(
            actividad
        )

        # ======================================================
        # ESTILOS
        # ======================================================

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #0F1115;
            }

            QWidget#contenido {
                background-color: #111318;
            }

            QFrame#sidebar {
                background-color: #0B0D10;
                border-right: 1px solid #24272D;
            }

            QLabel#logo {
                color: #F4C542;
                font-size: 25px;
                font-weight: 800;
            }

            QLabel#subtitulo_logo {
                color: #777D87;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#titulo_seccion {
                color: #666C76;
                font-size: 10px;
                font-weight: bold;
                padding-left: 8px;
                padding-bottom: 3px;
            }

            QPushButton#menu {
                background-color: transparent;
                color: #B7BBC3;
                border: none;
                border-radius: 7px;
                text-align: left;
                padding: 10px 12px;
                font-size: 13px;
            }

            QPushButton#menu:hover {
                background-color: #191C22;
                color: white;
            }

            QPushButton#menu_activo {
                background-color: #F4C542;
                color: #111318;
                border: none;
                border-radius: 7px;
                text-align: left;
                padding: 10px 12px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton#btn_cerrar {
                background-color: transparent;
                color: #C75B5B;
                border: none;
                border-radius: 7px;
                text-align: left;
                padding: 10px 12px;
                font-size: 13px;
            }

            QPushButton#btn_cerrar:hover {
                background-color: #281719;
            }

            QLabel#titulo_principal {
                color: #F1F1F1;
                font-size: 25px;
                font-weight: bold;
            }

            QLabel#subtitulo_principal {
                color: #777D87;
                font-size: 12px;
            }

            QLabel#usuario_superior {
                color: #D9DCE1;
                font-size: 12px;
                font-weight: bold;
            }

            QFrame#tarjeta {
                background-color: #181B21;
                border: 1px solid #252932;
                border-radius: 10px;
            }

            QLabel#tarjeta_titulo {
                color: #777D87;
                font-size: 10px;
                font-weight: bold;
            }

            QLabel#tarjeta_numero {
                color: #F4C542;
                font-size: 25px;
                font-weight: bold;
            }

            QLabel#tarjeta_descripcion {
                color: #626872;
                font-size: 10px;
            }

            QLabel#titulo_bloque {
                color: #E4E6E9;
                font-size: 14px;
                font-weight: bold;
            }

            QFrame#bloque {
                background-color: #181B21;
                border: 1px solid #252932;
                border-radius: 10px;
            }

            QLabel#placeholder {
                color: #555B65;
                font-size: 13px;
                padding: 35px;
            }

            QLabel#dia {
                color: #777D87;
                font-size: 10px;
                font-weight: bold;
            }

            QFrame#tienda {
                background-color: #181B21;
                border: 1px solid #252932;
                border-radius: 10px;
            }

            QLabel#tienda_nombre {
                color: #E8EAED;
                font-size: 13px;
                font-weight: bold;
            }

            QLabel#tienda_estado {
                color: #777D87;
                font-size: 11px;
            }

            QLabel#actividad {
                color: #777D87;
                font-size: 12px;
                padding: 10px;
            }

            QWidget#contenido_resumen { background-color: #111318; }
            QFrame#resumen_tarjeta, QFrame#tarjeta_tienda_resumen {
                background-color: #181B21;
                border: 1px solid #2A2F39;
                border-radius: 9px;
            }
            QLineEdit#busqueda_resumen, QComboBox#filtro_resumen,
            QDateEdit#fecha_resumen {
                background-color: #14171D;
                color: #E8EAED;
                border: 1px solid #343A46;
                border-radius: 7px;
                padding: 9px 11px;
                min-height: 20px;
            }
            QComboBox#filtro_resumen QAbstractItemView {
                background-color: #181B21;
                color: #E8EAED;
                selection-background-color: #F4C542;
                selection-color: #111318;
            }
            QPushButton#btn_actualizar_resumen {
                background-color: #F4C542;
                color: #111318;
                border: none;
                border-radius: 7px;
                padding: 10px 16px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton#btn_actualizar_resumen:hover { background-color: #FFD95C; }
            QTableWidget#tabla_resumen {
                background-color: #14171D;
                alternate-background-color: #181B21;
                color: #E8EAED;
                gridline-color: #252B35;
                border: 1px solid #2A2F39;
                border-radius: 8px;
                selection-background-color: #34302A;
                selection-color: #FFFFFF;
            }
            QTableWidget#tabla_resumen::item { padding: 7px; border: none; }
            QHeaderView::section {
                background-color: #11151B;
                color: #F4C542;
                border: none;
                border-bottom: 1px solid #343A46;
                padding: 10px 7px;
                font-size: 10px;
                font-weight: bold;
            }
            QScrollArea { border: none; background-color: #111318; }
            QScrollBar:vertical {
                background: #111318; width: 10px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #454B56; min-height: 25px; border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            """
        )

        # ======================================================
        # INICIO ACTIVO
        # ======================================================

        self.btn_inicio.setObjectName(
            "menu_activo"
        )

        # ======================================================
        # AÑADIR SIDEBAR Y CONTENIDO
        # ======================================================

        self.paginas = QStackedWidget()

        # Página de Inicio
        self.paginas.addWidget(contenido)

        # Página de Resumen
        self.pagina_resumen = self.crear_pagina_resumen(resumen_dashboard)
        self.paginas.addWidget(self.pagina_resumen)

        # Página de Trabajadores (PySide6 QWidget integrada)
        self.pagina_trabajadores = TrabajadoresWindow()
        self.paginas.addWidget(self.pagina_trabajadores)

        # Mostrar Inicio al entrar
        self.paginas.setCurrentWidget(contenido)

        # Mantener fija la barra lateral y cambiar solo el contenido central.
        layout_principal.addWidget(sidebar)
        layout_principal.addWidget(self.paginas, 1)

    # ==========================================================
    # CREAR VISTA DE RESUMEN
    # ==========================================================

    def crear_pagina_resumen(self, resumen):
        """Construye el resumen global de asistencia de todas las tiendas."""
        pagina = QWidget()
        pagina.setObjectName("contenido")

        pagina_layout = QVBoxLayout(pagina)
        pagina_layout.setContentsMargins(0, 0, 0, 0)
        pagina_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        pagina_layout.addWidget(scroll)

        contenido = QWidget()
        contenido.setObjectName("contenido_resumen")
        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(35, 25, 35, 28)
        layout.setSpacing(16)

        # Cabecera: título, fecha de consulta y actualización.
        cabecera = QHBoxLayout()
        bloque_titulo = QVBoxLayout()
        bloque_titulo.setSpacing(4)

        titulo = QLabel("Resumen General")
        titulo.setObjectName("titulo_principal")
        subtitulo = QLabel(
            "Vista completa de la asistencia del personal en todas las tiendas."
        )
        subtitulo.setObjectName("subtitulo_principal")
        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(subtitulo)
        cabecera.addLayout(bloque_titulo)
        cabecera.addStretch()

        self.resumen_fecha = QDateEdit()
        self.resumen_fecha.setObjectName("fecha_resumen")
        self.resumen_fecha.setCalendarPopup(True)
        self.resumen_fecha.setDisplayFormat("dd/MM/yyyy")
        self.resumen_fecha.setDate(QDate.currentDate())
        self.resumen_fecha.setMinimumWidth(145)

        self.btn_actualizar_resumen = QPushButton("⟳  Actualizar")
        self.btn_actualizar_resumen.setObjectName("btn_actualizar_resumen")
        self.btn_actualizar_resumen.setCursor(Qt.PointingHandCursor)
        self.btn_actualizar_resumen.clicked.connect(self.cargar_resumen_global)

        cabecera.addWidget(self.resumen_fecha)
        cabecera.addWidget(self.btn_actualizar_resumen)
        layout.addLayout(cabecera)
        layout.addSpacing(3)

        # Indicadores del día. Los números se calculan desde los registros reales.
        self.resumen_labels = {}
        definiciones = [
            ("PUNTUAL", "PUNTUALES", "Llegaron a tiempo", "#36B879"),
            ("TARDANZA", "TARDANZAS", "Llegaron después de la hora", "#F4C542"),
            ("FALTA", "FALTAS", "No registraron su ingreso", "#EF5350"),
            ("PENDIENTE", "PENDIENTES", "Aún no han marcado", "#98A2AE"),
        ]
        fila_tarjetas = QHBoxLayout()
        fila_tarjetas.setSpacing(14)

        for clave, encabezado, descripcion, color in definiciones:
            tarjeta = QFrame()
            tarjeta.setObjectName("resumen_tarjeta")
            tarjeta.setMinimumHeight(112)
            tarjeta_layout = QVBoxLayout(tarjeta)
            tarjeta_layout.setContentsMargins(16, 12, 15, 12)
            tarjeta_layout.setSpacing(5)

            etiqueta_titulo = QLabel(encabezado)
            etiqueta_titulo.setObjectName("tarjeta_titulo")
            etiqueta_valor = QLabel("0")
            etiqueta_valor.setObjectName("tarjeta_numero")
            etiqueta_valor.setStyleSheet(f"color: {color};")
            etiqueta_descripcion = QLabel(descripcion)
            etiqueta_descripcion.setObjectName("tarjeta_descripcion")
            etiqueta_descripcion.setWordWrap(True)

            tarjeta_layout.addWidget(etiqueta_titulo)
            tarjeta_layout.addWidget(etiqueta_valor)
            tarjeta_layout.addWidget(etiqueta_descripcion)
            tarjeta_layout.addStretch()
            fila_tarjetas.addWidget(tarjeta, 1)
            self.resumen_labels[clave] = etiqueta_valor

        layout.addLayout(fila_tarjetas)

        # Búsqueda y filtros.
        filtros = QHBoxLayout()
        filtros.setSpacing(12)

        self.resumen_busqueda = QLineEdit()
        self.resumen_busqueda.setObjectName("busqueda_resumen")
        self.resumen_busqueda.setPlaceholderText(
            "⌕  Buscar por nombre, código o DNI..."
        )
        self.resumen_busqueda.setClearButtonEnabled(True)
        self.resumen_busqueda.textChanged.connect(self.aplicar_filtros_resumen)

        self.resumen_tienda = QComboBox()
        self.resumen_tienda.setObjectName("filtro_resumen")
        self.resumen_tienda.addItem("Todas las tiendas")
        self.resumen_tienda.currentIndexChanged.connect(
            self.aplicar_filtros_resumen
        )

        self.resumen_estado = QComboBox()
        self.resumen_estado.setObjectName("filtro_resumen")
        self.resumen_estado.addItems([
            "Todos los estados", "Puntual", "Tardanza", "Falta",
            "Justificado", "Pendiente"
        ])
        self.resumen_estado.currentIndexChanged.connect(
            self.aplicar_filtros_resumen
        )

        filtros.addWidget(self.resumen_busqueda, 5)
        filtros.addWidget(self.resumen_tienda, 2)
        filtros.addWidget(self.resumen_estado, 2)
        layout.addLayout(filtros)

        # Tabla general del personal.
        encabezado_tabla = QHBoxLayout()
        titulo_tabla = QLabel("Lista de trabajadores")
        titulo_tabla.setObjectName("titulo_bloque")
        self.resumen_total = QLabel("Total: 0 trabajadores")
        self.resumen_total.setObjectName("subtitulo_principal")
        encabezado_tabla.addWidget(titulo_tabla)
        encabezado_tabla.addStretch()
        encabezado_tabla.addWidget(self.resumen_total)
        layout.addLayout(encabezado_tabla)

        self.tabla_resumen = QTableWidget(0, 7)
        self.tabla_resumen.setObjectName("tabla_resumen")
        self.tabla_resumen.setHorizontalHeaderLabels([
            "#", "CÓDIGO", "NOMBRE COMPLETO", "DNI", "TIENDA",
            "HORA DE INGRESO", "ESTADO"
        ])
        self.tabla_resumen.setAlternatingRowColors(True)
        self.tabla_resumen.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_resumen.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_resumen.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_resumen.verticalHeader().setVisible(False)
        self.tabla_resumen.verticalHeader().setDefaultSectionSize(38)
        self.tabla_resumen.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )
        self.tabla_resumen.horizontalHeader().setStretchLastSection(True)
        for columna, ancho in enumerate([42, 85, 220, 100, 145, 135, 120]):
            self.tabla_resumen.setColumnWidth(columna, ancho)
        self.tabla_resumen.setMinimumHeight(290)
        self.tabla_resumen.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tabla_resumen.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        layout.addWidget(self.tabla_resumen)

        # Conteo por tienda para identificar rápidamente dónde se concentran
        # las puntualidades, tardanzas y ausencias.
        titulo_tiendas = QLabel("Resumen por tienda")
        titulo_tiendas.setObjectName("titulo_bloque")
        layout.addWidget(titulo_tiendas)

        self.resumen_tiendas_contenedor = QWidget()
        self.resumen_tiendas_layout = QHBoxLayout(self.resumen_tiendas_contenedor)
        self.resumen_tiendas_layout.setContentsMargins(0, 0, 0, 0)
        self.resumen_tiendas_layout.setSpacing(14)
        layout.addWidget(self.resumen_tiendas_contenedor)
        layout.addStretch()

        scroll.setWidget(contenido)
        self._filas_resumen = []
        self._tiendas_resumen = []
        self.resumen_fecha.dateChanged.connect(self.cargar_resumen_global)
        return pagina

    def cargar_resumen_global(self, *args):
        """Lee personal y marcaciones de la fecha elegida, sin modificar datos."""
        if not hasattr(self, "resumen_fecha"):
            return

        qfecha = self.resumen_fecha.date()
        fecha_consulta = date(qfecha.year(), qfecha.month(), qfecha.day())

        try:
            with SessionLocal() as session:
                trabajadores = session.scalars(
                    select(Trabajador)
                    .options(joinedload(Trabajador.tienda))
                    .where(Trabajador.activo.is_(True))
                    .order_by(Trabajador.nombre_completo)
                ).unique().all()

                asistencias = session.scalars(
                    select(Asistencia).where(Asistencia.fecha == fecha_consulta)
                ).all()

                tiendas = session.scalars(
                    select(Tienda)
                    .where(Tienda.activa.is_(True))
                    .order_by(Tienda.nombre)
                ).all()

                asistencia_por_trabajador = {
                    asistencia.trabajador_id: {
                        "estado": str(asistencia.estado or "").upper(),
                        "hora": asistencia.hora_marcacion,
                    }
                    for asistencia in asistencias
                }

                filas = []
                ahora = tiempo.ahora()
                for trabajador in trabajadores:
                    if getattr(trabajador, "fecha_ingreso", None) and trabajador.fecha_ingreso > fecha_consulta:
                        continue

                    registro = asistencia_por_trabajador.get(trabajador.id)
                    if registro:
                        estado = registro["estado"] or "PENDIENTE"
                        hora_valor = registro["hora"]
                        hora = hora_valor.strftime("%H:%M") if hora_valor else "—"
                    else:
                        hora = "—"
                        if fecha_consulta > tiempo.hoy():
                            estado = "PENDIENTE"
                        elif fecha_consulta < tiempo.hoy() or ahora.time() >= time(15, 0):
                            # Se refleja como falta en la vista; no se inserta
                            # ni modifica ningún registro de la base de datos.
                            estado = "FALTA"
                        else:
                            estado = "PENDIENTE"

                    filas.append({
                        "codigo": str(trabajador.codigo or "—"),
                        "nombre": str(trabajador.nombre_completo or "Sin nombre"),
                        "dni": str(trabajador.dni or "—"),
                        "tienda": (
                            str(trabajador.tienda.nombre)
                            if trabajador.tienda else "Sin tienda"
                        ),
                        "hora": hora,
                        "estado": estado,
                    })

                self._filas_resumen = filas
                self._tiendas_resumen = [str(tienda.nombre) for tienda in tiendas]

            nombres_tienda_actuales = {
                fila["tienda"] for fila in self._filas_resumen
                if fila["tienda"] != "Sin tienda"
            }
            nombres_tienda = list(dict.fromkeys(
                self._tiendas_resumen + sorted(nombres_tienda_actuales)
            ))
            tienda_seleccionada = self.resumen_tienda.currentText()
            self.resumen_tienda.blockSignals(True)
            self.resumen_tienda.clear()
            self.resumen_tienda.addItem("Todas las tiendas")
            self.resumen_tienda.addItems(nombres_tienda)
            indice = self.resumen_tienda.findText(tienda_seleccionada)
            self.resumen_tienda.setCurrentIndex(max(indice, 0))
            self.resumen_tienda.blockSignals(False)

            self.aplicar_filtros_resumen()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error al cargar resumen",
                "No se pudo cargar la asistencia global.\n\n"
                f"{error}"
            )
            print("ERROR AL CARGAR RESUMEN GLOBAL:")
            print(error)

    def aplicar_filtros_resumen(self, *args):
        """Aplica búsqueda y filtros a la tabla e indicadores del resumen."""
        if not hasattr(self, "tabla_resumen"):
            return

        texto = self.resumen_busqueda.text().strip().casefold()
        tienda_filtro = self.resumen_tienda.currentText()
        estado_filtro = self.resumen_estado.currentText().upper()

        filas = []
        for fila in self._filas_resumen:
            if tienda_filtro != "Todas las tiendas" and fila["tienda"] != tienda_filtro:
                continue
            if estado_filtro != "TODOS LOS ESTADOS":
                if fila["estado"] != estado_filtro:
                    continue
            if texto and not any(
                texto in fila[campo].casefold()
                for campo in ("codigo", "nombre", "dni", "tienda")
            ):
                continue
            filas.append(fila)

        conteos = {"PUNTUAL": 0, "TARDANZA": 0, "FALTA": 0, "PENDIENTE": 0}
        for fila in filas:
            estado = fila["estado"]
            if estado in conteos:
                conteos[estado] += 1
            elif estado == "JUSTIFICADO":
                # Se conserva como estado propio en la tabla; no se suma
                # artificialmente a puntualidad ni a tardanza.
                pass

        for estado, etiqueta in self.resumen_labels.items():
            etiqueta.setText(str(conteos.get(estado, 0)))

        self.resumen_total.setText(f"Total: {len(filas)} trabajadores")
        self.tabla_resumen.setRowCount(len(filas))
        colores = {
            "PUNTUAL": "#36B879",
            "TARDANZA": "#F4C542",
            "FALTA": "#EF5350",
            "JUSTIFICADO": "#69A9E8",
            "PENDIENTE": "#98A2AE",
        }
        etiquetas_estado = {
            "PUNTUAL": "●  Puntual",
            "TARDANZA": "●  Tardanza",
            "FALTA": "●  Falta",
            "JUSTIFICADO": "●  Justificado",
            "PENDIENTE": "●  Pendiente",
        }

        for indice, fila in enumerate(filas):
            valores = [
                str(indice + 1), fila["codigo"], fila["nombre"],
                fila["dni"], fila["tienda"], fila["hora"],
                etiquetas_estado.get(fila["estado"], fila["estado"]),
            ]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(valor)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if columna in (0, 1, 3, 5):
                    item.setTextAlignment(Qt.AlignCenter)
                if columna == 6:
                    item.setForeground(QColor(colores.get(fila["estado"], "#D1D5DB")))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.tabla_resumen.setItem(indice, columna, item)

        self._actualizar_tarjetas_tiendas(filas, self._tiendas_resumen)

    def _actualizar_tarjetas_tiendas(self, filas, tiendas):
        """Reconstruye los contadores agrupados por tienda."""
        while self.resumen_tiendas_layout.count():
            elemento = self.resumen_tiendas_layout.takeAt(0)
            widget = elemento.widget()
            if widget is not None:
                widget.deleteLater()

        nombres = list(dict.fromkeys(
            tiendas + sorted({fila["tienda"] for fila in filas if fila["tienda"] != "Sin tienda"})
        ))
        if not nombres:
            etiqueta = QLabel("No hay tiendas activas registradas.")
            etiqueta.setObjectName("subtitulo_principal")
            self.resumen_tiendas_layout.addWidget(etiqueta)
            return

        for nombre in nombres:
            grupo = [fila for fila in filas if fila["tienda"] == nombre]
            conteos = {"PUNTUAL": 0, "TARDANZA": 0, "FALTA": 0, "PENDIENTE": 0, "JUSTIFICADO": 0}
            for fila in grupo:
                if fila["estado"] in conteos:
                    conteos[fila["estado"]] += 1

            tarjeta = QFrame()
            tarjeta.setObjectName("tarjeta_tienda_resumen")
            tarjeta_layout = QVBoxLayout(tarjeta)
            tarjeta_layout.setContentsMargins(15, 12, 15, 12)
            tarjeta_layout.setSpacing(7)

            nombre_label = QLabel(nombre.upper())
            nombre_label.setObjectName("tienda_nombre")
            total_label = QLabel(f"{len(grupo)} trabajadores")
            total_label.setObjectName("tienda_estado")
            tarjeta_layout.addWidget(nombre_label)
            tarjeta_layout.addWidget(total_label)

            conteo_layout = QHBoxLayout()
            for clave, texto, color in [
                ("PUNTUAL", "Puntuales", "#36B879"),
                ("TARDANZA", "Tardanzas", "#F4C542"),
                ("FALTA", "Faltas", "#EF5350"),
                ("PENDIENTE", "Pendientes", "#98A2AE"),
            ]:
                mini = QVBoxLayout()
                valor = QLabel(str(conteos[clave]))
                valor.setStyleSheet(f"color: {color}; font-size: 17px; font-weight: bold;")
                texto_label = QLabel(texto)
                texto_label.setObjectName("tienda_estado")
                mini.addWidget(valor, alignment=Qt.AlignLeft)
                mini.addWidget(texto_label, alignment=Qt.AlignLeft)
                conteo_layout.addLayout(mini)
            tarjeta_layout.addLayout(conteo_layout)
            self.resumen_tiendas_layout.addWidget(tarjeta, 1)

    # ==========================================================
    # NAVEGACIÓN: INICIO Y RESUMEN
    # ==========================================================

    def mostrar_inicio(self):
        """Regresa a la vista principal del dashboard."""

        self.paginas.setCurrentIndex(0)

        self.btn_inicio.setObjectName("menu_activo")
        self.btn_resumen.setObjectName("menu")
        self.btn_trabajadores.setObjectName("menu")
        self.btn_usuarios.setObjectName("menu")
        self.btn_asistencias.setObjectName("menu")

        for boton in (
            self.btn_inicio,
            self.btn_resumen,
            self.btn_trabajadores,
            self.btn_usuarios,
            self.btn_asistencias,
        ):
            boton.style().unpolish(boton)
            boton.style().polish(boton)


    def mostrar_resumen(self):
        """Muestra el Resumen Global."""

        self.paginas.setCurrentWidget(self.pagina_resumen)

        self.btn_inicio.setObjectName("menu")
        self.btn_resumen.setObjectName("menu_activo")
        self.btn_trabajadores.setObjectName("menu")
        self.btn_usuarios.setObjectName("menu")
        self.btn_asistencias.setObjectName("menu")

        for boton in (
            self.btn_inicio,
            self.btn_resumen,
            self.btn_trabajadores,
            self.btn_usuarios,
            self.btn_asistencias,
        ):
            boton.style().unpolish(boton)
            boton.style().polish(boton)

        self.cargar_resumen_global()

    # ==========================================================
    # ABRIR USUARIOS
    # ==========================================================

    def abrir_usuarios(self):
        """Muestra Usuarios en el área central del Dashboard."""
        try:
            if self.pagina_usuarios is None:
                self.pagina_usuarios = UsuariosWindow(parent=self)
                self.paginas.addWidget(self.pagina_usuarios)

            self.paginas.setCurrentWidget(self.pagina_usuarios)

            self.btn_inicio.setObjectName("menu")
            self.btn_resumen.setObjectName("menu")
            self.btn_trabajadores.setObjectName("menu")
            self.btn_usuarios.setObjectName("menu_activo")
            self.btn_asistencias.setObjectName("menu")

            for boton in (
                self.btn_inicio, self.btn_resumen,
                self.btn_trabajadores, self.btn_usuarios, self.btn_asistencias,
            ):
                boton.style().unpolish(boton)
                boton.style().polish(boton)

            self.pagina_usuarios.cargar_usuarios(
                self.pagina_usuarios.entrada_busqueda.text()
            )

        except PermissionError as error:
            QMessageBox.warning(self, "Acceso denegado", str(error))
        except Exception as error:
            QMessageBox.critical(
                self, "Error",
                f"No se pudo mostrar Usuarios dentro del Dashboard.\n\n{error}"
            )
            print("ERROR AL MOSTRAR USUARIOS:")
            print(error)

    # ==========================================================
    # USUARIOS CERRADA
    # ==========================================================

    def usuario_window_cerrada(
        self
    ):
        # Compatibilidad con versiones anteriores: Usuarios ahora es una página.
        self.pagina_usuarios = None

    # ==========================================================
    # ABRIR DESCUENTOS
    # ==========================================================

    def abrir_descuentos(self):

        try:

            # La ventana se abre dentro del mismo proceso del Dashboard.
            # Así conserva la sesión ADMIN/SUPERADMIN actual.
            if (
                self.ventana_descuentos is not None
                and self.ventana_descuentos.isVisible()
            ):
                self.ventana_descuentos.raise_()
                self.ventana_descuentos.activateWindow()
                return

            self.ventana_descuentos = DescuentosWindow(self)

            self.ventana_descuentos.setAttribute(
                Qt.WA_DeleteOnClose
            )

            self.ventana_descuentos.destroyed.connect(
                self.descuentos_window_cerrada
            )

            self.ventana_descuentos.showMaximized()
            self.ventana_descuentos.raise_()
            self.ventana_descuentos.activateWindow()

        except PermissionError as error:

            QMessageBox.warning(
                self,
                "Permisos",
                str(error)
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudo abrir la ventana de "
                    "Descuentos.\n\n"
                    f"{error}"
                )
            )

            print("ERROR AL ABRIR DESCUENTOS:")
            print(error)

    # ==========================================================
    # DESCUENTOS CERRADA
    # ==========================================================

    def descuentos_window_cerrada(self):
        self.ventana_descuentos = None
        
    # ==========================================================
    # ABRIR REPORTES
    # ==========================================================

    def abrir_reportes(self):

        try:
            # Si ya está abierta, la mostramos al frente.
            if (
                self.ventana_reportes is not None
                and self.ventana_reportes.isVisible()
            ):
                self.ventana_reportes.raise_()
                self.ventana_reportes.activateWindow()
                return

            # Crear ventana de reportes.
            self.ventana_reportes = ReportesWindow()

            self.ventana_reportes.setAttribute(
                Qt.WA_DeleteOnClose
            )

            self.ventana_reportes.destroyed.connect(
                self.reportes_window_cerrada
            )

            self.ventana_reportes.showMaximized()
            self.ventana_reportes.raise_()
            self.ventana_reportes.activateWindow()

        except PermissionError as error:
            QMessageBox.warning(
                self,
                "Permisos",
                str(error)
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudo abrir la ventana de "
                    "Reportes.\n\n"
                    f"{error}"
                )
            )

            print("ERROR AL ABRIR REPORTES:")
            print(error)

    # ==========================================================
    # REPORTES CERRADA
    # ==========================================================

    def reportes_window_cerrada(self):
        self.ventana_reportes = None

    # ==========================================================
    # ABRIR TRABAJADORES
    # ==========================================================

    def abrir_trabajadores(self):
        """Muestra Trabajadores dentro del Dashboard."""

        try:
            self.paginas.setCurrentWidget(self.pagina_trabajadores)

            self.btn_inicio.setObjectName("menu")
            self.btn_resumen.setObjectName("menu")
            self.btn_trabajadores.setObjectName("menu_activo")
            self.btn_usuarios.setObjectName("menu")
            self.btn_asistencias.setObjectName("menu")

            for boton in (
                self.btn_inicio,
                self.btn_resumen,
                self.btn_trabajadores,
                self.btn_usuarios,
                self.btn_asistencias,
            ):
                boton.style().unpolish(boton)
                boton.style().polish(boton)

            self.pagina_trabajadores.cargar_trabajadores()

        except Exception as error:
            QMessageBox.critical(
               self,
               "Error",
               f"No se pudo mostrar Trabajadores.\n\n{error}"
            )

            print("ERROR AL MOSTRAR TRABAJADORES:")
            print(error)

    # ==========================================================
    # ABRIR ASISTENCIAS
    # ==========================================================

    def abrir_asistencias(self):
        """Muestra Asistencias en el área central del Dashboard."""
        try:
            if self.pagina_asistencias is None:
                self.pagina_asistencias = AsistenciasWindow(parent=self)
                self.paginas.addWidget(self.pagina_asistencias)

            self.paginas.setCurrentWidget(self.pagina_asistencias)

            self.btn_inicio.setObjectName("menu")
            self.btn_resumen.setObjectName("menu")
            self.btn_trabajadores.setObjectName("menu")
            self.btn_usuarios.setObjectName("menu")
            self.btn_asistencias.setObjectName("menu_activo")

            for boton in (
                self.btn_inicio,
                self.btn_resumen,
                self.btn_trabajadores,
                self.btn_usuarios,
                self.btn_asistencias,
            ):
                boton.style().unpolish(boton)
                boton.style().polish(boton)

            self.pagina_asistencias.cargar_asistencias()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo mostrar Asistencias dentro del Dashboard.\n\n{error}"
            )
            print("ERROR AL MOSTRAR ASISTENCIAS:")
            print(error)

    # ==========================================================
    # ABRIR JUSTIFICACIONES
    # ==========================================================

    def abrir_justificaciones(self):

        try:

            proyecto = (
                Path(__file__)
                .resolve()
                .parents[4]
            )

            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "app.admin.views.asistencia.justificaciones_window"
                ],
                cwd=str(
                    proyecto
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudo abrir la ventana de "
                    "Justificaciones.\n\n"
                    f"{error}"
                )
            )

            print(
                "ERROR AL ABRIR JUSTIFICACIONES:"
            )

            print(
                error
            )
    # ==========================================================
    # ABRIR TIENDAS
    # ==========================================================

    def abrir_tiendas(self):

        try:

            proyecto = (
                Path(__file__)
                .resolve()
                .parents[4]
            )

            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "app.admin.views.tienda.tiendas_window"
                ],
                cwd=str(
                    proyecto
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudo abrir la ventana de "
                    "Tiendas.\n\n"
                    f"{error}"
                )
            )

            print(
                "ERROR AL ABRIR TIENDAS:"
            )

            print(
                error
            )

    # ==========================================================
    # CERRAR SESIÓN
    # ==========================================================

    def cerrar_sesion(self):

        respuesta = QMessageBox.question(
            self,
            "Cerrar sesión",
            "¿Deseas cerrar la sesión actual?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        try:

            sesion_actual.cerrar()

            self.close()

            from app.admin.views.login.login_window import LoginWindow

            self.login_window = LoginWindow()

            self.login_window.show()
            self.login_window.raise_()
            self.login_window.activateWindow()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudo cerrar la sesión.\\n\\n"
                    f"{error}"
                )
            )

            print(
                "ERROR AL CERRAR SESIÓN:"
            )

            print(
                error
            )

    # ==========================================================
    # TÍTULO DE SECCIÓN
    # ==========================================================

    def crear_titulo_seccion(
        self,
        texto
    ):

        etiqueta = QLabel(
            texto
        )

        etiqueta.setObjectName(
            "titulo_seccion"
        )

        return etiqueta

    # ==========================================================
    # BOTÓN
    # ==========================================================

    def crear_boton(
        self,
        texto
    ):

        boton = QPushButton(
            texto
        )

        boton.setObjectName(
            "menu"
        )

        boton.setCursor(
            Qt.PointingHandCursor
        )

        boton.setMinimumHeight(
            38
        )

        return boton

    # ==========================================================
    # TARJETA
    # ==========================================================

    def crear_tarjeta(
        self,
        titulo,
        numero,
        descripcion,
        identificador
    ):

        tarjeta = QFrame()

        tarjeta.setObjectName(
            "tarjeta"
        )

        tarjeta.setMinimumHeight(
            105
        )

        layout = QVBoxLayout(
            tarjeta
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        etiqueta_titulo = QLabel(
            titulo
        )

        etiqueta_titulo.setObjectName(
            "tarjeta_titulo"
        )

        etiqueta_numero = QLabel(
            numero
        )

        etiqueta_numero.setObjectName(
            "tarjeta_numero"
        )

        etiqueta_descripcion = QLabel(
            descripcion
        )

        etiqueta_descripcion.setObjectName(
            "tarjeta_descripcion"
        )

        layout.addWidget(
            etiqueta_titulo
        )

        layout.addWidget(
            etiqueta_numero
        )

        layout.addWidget(
            etiqueta_descripcion
        )

        return tarjeta

    # ==========================================================
    # TIENDA
    # ==========================================================

    def crear_tienda(
        self,
        nombre,
        estado
    ):

        tarjeta = QFrame()

        tarjeta.setObjectName(
            "tienda"
        )

        tarjeta.setMinimumHeight(
            85
        )

        layout = QVBoxLayout(
            tarjeta
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14
        )

        etiqueta_nombre = QLabel(
            nombre
        )

        etiqueta_nombre.setObjectName(
            "tienda_nombre"
        )

        etiqueta_estado = QLabel(
            estado
        )

        etiqueta_estado.setObjectName(
            "tienda_estado"
        )

        layout.addWidget(
            etiqueta_nombre
        )

        layout.addWidget(
            etiqueta_estado
        )

        return tarjeta


# ==============================================================
# EJECUCIÓN DIRECTA
# ==============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    ventana = DashboardWindow()

    ventana.showMaximized()

    sys.exit(
        app.exec()
    )