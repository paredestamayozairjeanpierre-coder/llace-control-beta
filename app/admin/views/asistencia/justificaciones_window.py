
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt


class JustificacionesWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("LLACE CONTROL - Justificaciones")
        self.setMinimumSize(1050, 650)
        self.resize(1250, 760)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #101116;
                color: #F1F3F5;
                font-family: Segoe UI;
                font-size: 12px;
            }

            QFrame#Card {
                background-color: #181A22;
                border: 1px solid #292C37;
                border-radius: 9px;
            }

            QLabel#Title {
                font-size: 23px;
                font-weight: bold;
                color: #F5F5F5;
            }

            QLabel#Subtitle {
                color: #9299A9;
                font-size: 11px;
            }

            QLabel#Count {
                font-size: 26px;
                font-weight: bold;
                color: #F6C83E;
            }

            QLineEdit, QComboBox {
                background-color: #181A22;
                color: #F1F3F5;
                border: 1px solid #303441;
                border-radius: 6px;
                padding: 9px;
                min-height: 20px;
            }

            QTableWidget {
                background-color: #181A22;
                alternate-background-color: #1D2029;
                border: 1px solid #292C37;
                border-radius: 8px;
                gridline-color: #292C37;
                selection-background-color: #34313A;
                selection-color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: #20232D;
                color: #AEB5C4;
                border: none;
                border-bottom: 1px solid #343744;
                padding: 12px 6px;
                font-weight: bold;
            }

            QTableWidget::item {
                padding: 7px;
            }

            QPushButton {
                background-color: #20232D;
                color: #E9EBF0;
                border: 1px solid #343744;
                border-radius: 6px;
                padding: 9px 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #2B2E39;
            }

            QPushButton#Yellow {
                background-color: #F6C83E;
                color: #111111;
                border: none;
            }

            QPushButton#Yellow:hover {
                background-color: #FFD957;
            }

            QPushButton#Green {
                background-color: #163C2B;
                color: #61D69A;
                border: 1px solid #246443;
            }

            QPushButton#Red {
                background-color: #421F25;
                color: #FF808A;
                border: 1px solid #6B3039;
            }
        """)

        self.crear_interfaz()

    def crear_interfaz(self):

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(28, 22, 28, 24)
        layout.setSpacing(20)

        # ENCABEZADO
        encabezado = QHBoxLayout()

        titulos = QVBoxLayout()

        titulo = QLabel("Justificaciones")
        titulo.setObjectName("Title")

        subtitulo = QLabel(
            "Revisión y control de solicitudes del personal"
        )
        subtitulo.setObjectName("Subtitle")

        titulos.addWidget(titulo)
        titulos.addWidget(subtitulo)

        encabezado.addLayout(titulos)
        encabezado.addStretch()

        self.btn_actualizar = QPushButton("↻  Actualizar")
        self.btn_actualizar.clicked.connect(
            self.actualizar
        )

        encabezado.addWidget(self.btn_actualizar)
        layout.addLayout(encabezado)

        # TARJETAS DE ESTADO
        tarjetas = QHBoxLayout()
        tarjetas.setSpacing(14)

        self.lbl_pendientes = self.crear_tarjeta(
            tarjetas, "PENDIENTES", "0", "#F6C83E"
        )

        self.lbl_aprobadas = self.crear_tarjeta(
            tarjetas, "APROBADAS", "0", "#43C982"
        )

        self.lbl_rechazadas = self.crear_tarjeta(
            tarjetas, "RECHAZADAS", "0", "#F16B75"
        )

        layout.addLayout(tarjetas)

        # FILTROS
        filtros = QHBoxLayout()
        filtros.setSpacing(10)

        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText(
            "Buscar trabajador..."
        )

        self.filtro_estado = QComboBox()
        self.filtro_estado.addItems([
            "Todos los estados",
            "Pendiente",
            "Aprobada",
            "Rechazada",
        ])

        self.filtro_tienda = QComboBox()
        self.filtro_tienda.addItems([
            "Todas las tiendas",
            "Peru Llaves",
            "El Cerrojo",
            "Grupo LLACE - Almacén",
        ])

        filtros.addWidget(self.buscar, 2)
        filtros.addWidget(self.filtro_estado, 1)
        filtros.addWidget(self.filtro_tienda, 1)

        layout.addLayout(filtros)

        # TABLA
        tabla_card = QFrame()
        tabla_card.setObjectName("Card")

        tabla_layout = QVBoxLayout(tabla_card)
        tabla_layout.setContentsMargins(14, 14, 14, 14)
        tabla_layout.setSpacing(10)

        titulo_tabla = QLabel("SOLICITUDES DE JUSTIFICACIÓN")
        titulo_tabla.setStyleSheet(
            "font-weight: bold; color: #F1F3F5;"
        )

        tabla_layout.addWidget(titulo_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "TRABAJADOR",
            "TIENDA",
            "FECHA",
            "MOTIVO",
            "ESTADO",
        ])

        self.tabla.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.tabla.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        tabla_layout.addWidget(self.tabla)

        self.lbl_vacio = QLabel(
            "Las solicitudes aparecerán aquí cuando "
            "conectemos la base de datos."
        )
        self.lbl_vacio.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.lbl_vacio.setStyleSheet(
            "color: #9299A9; padding: 12px;"
        )

        tabla_layout.addWidget(self.lbl_vacio)

        layout.addWidget(tabla_card, 1)

        # ACCIONES
        acciones = QHBoxLayout()
        acciones.addStretch()

        self.btn_detalle = QPushButton("Ver detalle")
        self.btn_detalle.clicked.connect(
            self.ver_detalle
        )

        self.btn_aprobar = QPushButton("✓  Aprobar")
        self.btn_aprobar.setObjectName("Green")
        self.btn_aprobar.clicked.connect(
            self.aprobar
        )

        self.btn_rechazar = QPushButton("✕  Rechazar")
        self.btn_rechazar.setObjectName("Red")
        self.btn_rechazar.clicked.connect(
            self.rechazar
        )

        acciones.addWidget(self.btn_detalle)
        acciones.addWidget(self.btn_aprobar)
        acciones.addWidget(self.btn_rechazar)

        layout.addLayout(acciones)

    def crear_tarjeta(self, contenedor, titulo, valor, color):

        tarjeta = QFrame()
        tarjeta.setObjectName("Card")
        tarjeta.setMinimumHeight(100)

        contenido = QVBoxLayout(tarjeta)
        contenido.setContentsMargins(16, 12, 16, 12)
        contenido.setSpacing(5)

        nombre = QLabel(titulo)
        nombre.setStyleSheet(
            "color: #9BA3B4; font-size: 10px; "
            "font-weight: bold;"
        )

        cantidad = QLabel(valor)
        cantidad.setObjectName("Count")
        cantidad.setStyleSheet(
            f"font-size: 26px; font-weight: bold; color: {color};"
        )

        contenido.addWidget(nombre)
        contenido.addWidget(cantidad)
        contenido.addStretch()

        contenedor.addWidget(tarjeta)

        return cantidad

    def actualizar(self):

        QMessageBox.information(
            self,
            "Base de datos",
            "La interfaz está creada. "
            "La conexión para cargar solicitudes "
            "se implementará en el siguiente paso."
        )

    def ver_detalle(self):

        QMessageBox.information(
            self,
            "Detalle",
            "Primero debemos conectar las solicitudes "
            "con PostgreSQL."
        )

    def aprobar(self):

        QMessageBox.information(
            self,
            "Aprobación",
            "La aprobación se habilitará cuando "
            "conectemos el servicio de justificaciones."
        )

    def rechazar(self):

        QMessageBox.information(
            self,
            "Rechazo",
            "El rechazo se habilitará cuando "
            "conectemos el servicio de justificaciones."
        )


if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)

    ventana = JustificacionesWindow()
    ventana.show()

    sys.exit(app.exec())