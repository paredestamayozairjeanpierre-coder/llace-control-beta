from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QAbstractItemView,
    QMainWindow,
)

from app.admin.services.trabajador_service import (
    listar_trabajadores,
    buscar_trabajadores,
)
from app.admin.views.trabajador.trabajador_form import TrabajadorForm


class TrabajadoresWindow(QWidget):
    """Página de trabajadores integrada al QStackedWidget del Dashboard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pagina_trabajadores")
        self._configurar_estilos()
        self._crear_interfaz()
        self.cargar_trabajadores()

    # =========================================================
    # ESTILOS - COHERENTES CON LLACE CONTROL
    # =========================================================
    def _configurar_estilos(self):
        self.setStyleSheet("""
            QWidget#pagina_trabajadores {
                background-color: #111318;
                color: #E8EAED;
                font-family: "Segoe UI";
                font-size: 10pt;
            }
            QLabel#titulo_pagina {
                color: #F1F1F1;
                font-size: 25px;
                font-weight: 700;
            }
            QLabel#subtitulo_pagina, QLabel#texto_secundario {
                color: #858B96;
                font-size: 11px;
            }
            QLabel#titulo_tarjeta {
                color: #E8EAED;
                font-size: 14px;
                font-weight: 700;
            }
            QLabel#contador {
                color: #858B96;
                font-size: 11px;
            }
            QFrame#barra_superior, QFrame#tarjeta_tabla {
                background-color: #181B21;
                border: 1px solid #2A2F39;
                border-radius: 9px;
            }
            QLineEdit#busqueda {
                background-color: #14171D;
                color: #E8EAED;
                border: 1px solid #343A46;
                border-radius: 7px;
                padding: 9px 12px;
                min-height: 22px;
                selection-background-color: #F4C542;
                selection-color: #111318;
            }
            QLineEdit#busqueda:focus { border: 1px solid #F4C542; }
            QPushButton#btn_nuevo {
                background-color: #F4C542;
                color: #111318;
                border: none;
                border-radius: 7px;
                padding: 10px 16px;
                font-size: 11px;
                font-weight: 700;
                min-height: 22px;
            }
            QPushButton#btn_nuevo:hover { background-color: #FFD95C; }
            QPushButton#btn_buscar {
                background-color: #252A33;
                color: #E8EAED;
                border: 1px solid #343A46;
                border-radius: 7px;
                padding: 9px 15px;
                font-weight: 600;
                min-height: 22px;
            }
            QPushButton#btn_buscar:hover { background-color: #303642; }
            QTableWidget#tabla_trabajadores {
                background-color: #14171D;
                alternate-background-color: #181B21;
                color: #E8EAED;
                gridline-color: #252B35;
                border: 1px solid #2A2F39;
                border-radius: 7px;
                selection-background-color: #34302A;
                selection-color: #FFFFFF;
            }
            QTableWidget#tabla_trabajadores::item {
                padding: 8px 7px;
                border: none;
            }
            QHeaderView::section {
                background-color: #11151B;
                color: #F4C542;
                border: none;
                border-bottom: 1px solid #343A46;
                padding: 11px 8px;
                font-size: 10px;
                font-weight: 700;
            }
            QScrollBar:vertical {
                background: #111318;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #454B56;
                min-height: 25px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

    # =========================================================
    # INTERFAZ
    # =========================================================
    def _crear_interfaz(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(30, 25, 30, 28)
        raiz.setSpacing(16)

        cabecera = QHBoxLayout()
        bloque_titulo = QVBoxLayout()
        bloque_titulo.setSpacing(4)

        titulo = QLabel("Trabajadores")
        titulo.setObjectName("titulo_pagina")
        subtitulo = QLabel("Administra el personal registrado en las tiendas de Grupo LLACE.")
        subtitulo.setObjectName("subtitulo_pagina")
        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(subtitulo)
        cabecera.addLayout(bloque_titulo)
        cabecera.addStretch(1)

        self.btn_nuevo = QPushButton("＋  NUEVO TRABAJADOR")
        self.btn_nuevo.setObjectName("btn_nuevo")
        self.btn_nuevo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nuevo.clicked.connect(self.nuevo_trabajador)
        cabecera.addWidget(self.btn_nuevo, alignment=Qt.AlignmentFlag.AlignVCenter)
        raiz.addLayout(cabecera)

        barra = QFrame()
        barra.setObjectName("barra_superior")
        barra_layout = QHBoxLayout(barra)
        barra_layout.setContentsMargins(14, 12, 14, 12)
        barra_layout.setSpacing(10)

        self.entrada_busqueda = QLineEdit()
        self.entrada_busqueda.setObjectName("busqueda")
        self.entrada_busqueda.setPlaceholderText("⌕  Buscar por nombre, código o DNI...")
        self.entrada_busqueda.setClearButtonEnabled(True)
        self.entrada_busqueda.textChanged.connect(self.buscar)
        barra_layout.addWidget(self.entrada_busqueda, 1)

        self.btn_buscar = QPushButton("BUSCAR")
        self.btn_buscar.setObjectName("btn_buscar")
        self.btn_buscar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar.clicked.connect(self.buscar)
        barra_layout.addWidget(self.btn_buscar)
        raiz.addWidget(barra)

        encabezado_tabla = QHBoxLayout()
        titulo_tabla = QLabel("Lista de trabajadores")
        titulo_tabla.setObjectName("titulo_tarjeta")
        self.lbl_contador = QLabel("0 trabajadores")
        self.lbl_contador.setObjectName("contador")
        encabezado_tabla.addWidget(titulo_tabla)
        encabezado_tabla.addStretch(1)
        encabezado_tabla.addWidget(self.lbl_contador)
        raiz.addLayout(encabezado_tabla)

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta_tabla")
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(0, 0, 0, 0)
        tarjeta_layout.setSpacing(0)

        columnas = ("codigo", "nombre", "dni", "tienda", "sueldo", "estado")
        titulos = ("CÓDIGO", "NOMBRE COMPLETO", "DNI", "TIENDA", "SUELDO SEMANAL", "ESTADO")
        self.tabla = QTableWidget(0, len(columnas))
        self.tabla.setObjectName("tabla_trabajadores")
        self.tabla.setHorizontalHeaderLabels(titulos)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(42)
        self.tabla.horizontalHeader().setHighlightSections(False)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.cellDoubleClicked.connect(self.trabajador_seleccionado)
        tarjeta_layout.addWidget(self.tabla)
        raiz.addWidget(tarjeta, 1)

        pie = QLabel("Selecciona un registro para consultarlo. La edición se gestiona desde el formulario del trabajador.")
        pie.setObjectName("texto_secundario")
        raiz.addWidget(pie)

    # =========================================================
    # CARGAR Y MOSTRAR TRABAJADORES
    # =========================================================
    def cargar_trabajadores(self):
        try:
            trabajadores = listar_trabajadores(activos_solo=True)
            self.mostrar_trabajadores(trabajadores)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los trabajadores.\n\n{error}")

    def mostrar_trabajadores(self, trabajadores):
        self.tabla.setRowCount(0)
        for trabajador in trabajadores:
            tienda = trabajador.tienda.nombre if trabajador.tienda else "Sin tienda"
            sueldo = f"S/ {trabajador.sueldo_semanal:.2f}" if trabajador.sueldo_semanal is not None else "S/ 0.00"
            estado = "ACTIVO" if trabajador.activo else "INACTIVO"
            valores = (trabajador.codigo, trabajador.nombre_completo, trabajador.dni, tienda, sueldo, estado)
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor if valor is not None else ""))
                if columna in (0, 2, 4, 5):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla.setItem(fila, columna, item)
            # El ID se conserva en el primer elemento, sin mostrar una columna adicional.
            self.tabla.item(fila, 0).setData(Qt.ItemDataRole.UserRole, trabajador.id)
            if not trabajador.activo:
                for columna in range(len(valores)):
                    self.tabla.item(fila, columna).setForeground(Qt.GlobalColor.gray)
        self.lbl_contador.setText(f"{len(trabajadores)} trabajadores")

    # =========================================================
    # BUSCAR
    # =========================================================
    def buscar(self, texto=None):
        texto = self.entrada_busqueda.text().strip() if texto is None or isinstance(texto, bool) else str(texto).strip()
        try:
            trabajadores = buscar_trabajadores(texto=texto, activos_solo=True)
            self.mostrar_trabajadores(trabajadores)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo realizar la búsqueda.\n\n{error}")

    # =========================================================
    # NUEVO TRABAJADOR
    # =========================================================
    def nuevo_trabajador(self):
        formulario = TrabajadorForm(parent=self, al_guardar=self.cargar_trabajadores)
        formulario.exec()

    # =========================================================
    # TRABAJADOR SELECCIONADO
    # =========================================================
    def trabajador_seleccionado(self, fila, columna=0):
        item = self.tabla.item(fila, 0)
        if item is None:
            return
        trabajador_id = item.data(Qt.ItemDataRole.UserRole)
        QMessageBox.information(self, "Trabajador seleccionado", f"ID del trabajador: {trabajador_id}")


if __name__ == "__main__":
    app = QApplication([])
    ventana = QMainWindow()
    ventana.setWindowTitle("LLACE CONTROL BETA - Trabajadores")
    ventana.resize(1100, 650)
    pagina = TrabajadoresWindow()
    ventana.setCentralWidget(pagina)
    ventana.show()
    app.exec()
