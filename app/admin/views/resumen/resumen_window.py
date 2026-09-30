
from app.core import tiempo
from datetime import date, datetime, time

from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.admin.services.asistencia_service import listar_asistencias


class ResumenWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("LLACE CONTROL - Resumen")
        self.setMinimumSize(1000, 650)

        self.asistencias = []

        self.crear_interfaz()
        self.cargar_datos()

    def crear_interfaz(self):

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(18)

        # ENCABEZADO
        titulo = QLabel("RESUMEN DE ASISTENCIAS")
        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Consulta y seguimiento de asistencia del personal"
        )
        subtitulo.setObjectName("subtitulo")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        # FILTROS
        filtros = QHBoxLayout()
        filtros.setSpacing(12)

        etiqueta_fecha = QLabel("Fecha:")

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.setDate(tiempo.hoy())
        self.fecha.dateChanged.connect(self.cargar_datos)

        etiqueta_tienda = QLabel("Tienda:")

        self.combo_tienda = QComboBox()
        self.combo_tienda.addItem("Todas las tiendas")
        self.combo_tienda.currentTextChanged.connect(
            self.actualizar_vista
        )

        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.cargar_datos)

        filtros.addWidget(etiqueta_fecha)
        filtros.addWidget(self.fecha)
        filtros.addSpacing(15)
        filtros.addWidget(etiqueta_tienda)
        filtros.addWidget(self.combo_tienda)
        filtros.addStretch()
        filtros.addWidget(self.btn_actualizar)

        layout.addLayout(filtros)

        # TARJETAS DE RESUMEN
        tarjetas = QHBoxLayout()
        tarjetas.setSpacing(12)

        self.valores = {}

        datos_tarjetas = [
            ("total", "TOTAL", "tarjeta_total"),
            ("puntuales", "PUNTUALES", "tarjeta_puntual"),
            ("tardanzas", "TARDANZAS", "tarjeta_tardanza"),
            ("faltas", "FALTAS", "tarjeta_falta"),
            ("justificados", "JUSTIFICADOS", "tarjeta_justificado"),
        ]

        for clave, nombre, estilo in datos_tarjetas:
            tarjeta = self.crear_tarjeta(nombre, estilo)
            self.valores[clave] = tarjeta.findChild(
                QLabel, "valor_tarjeta"
            )
            tarjetas.addWidget(tarjeta)

        layout.addLayout(tarjetas)

        # TABLA
        titulo_tabla = QLabel("DETALLE DE ASISTENCIAS")
        titulo_tabla.setObjectName("titulo_seccion")
        layout.addWidget(titulo_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "Código",
            "Trabajador",
            "DNI",
            "Tienda",
            "Estado",
            "Hora",
        ])

        self.tabla.setEditTriggers(
            QTableWidget.NoEditTriggers
        )
        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self.tabla.setSelectionMode(
            QTableWidget.SingleSelection
        )
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(self.tabla)

        self.mensaje = QLabel("")
        self.mensaje.setObjectName("mensaje")
        layout.addWidget(self.mensaje)

        # ESTILOS
        self.setStyleSheet("""
            QMainWindow {
                background-color: #111318;
            }

            QWidget {
                color: #E8EAED;
                font-size: 12px;
            }

            QLabel#titulo {
                color: #F4C542;
                font-size: 23px;
                font-weight: bold;
            }

            QLabel#subtitulo, QLabel#mensaje {
                color: #858B96;
            }

            QLabel#titulo_seccion {
                font-size: 14px;
                font-weight: bold;
                padding-top: 8px;
            }

            QFrame#tarjeta_total,
            QFrame#tarjeta_puntual,
            QFrame#tarjeta_tardanza,
            QFrame#tarjeta_falta,
            QFrame#tarjeta_justificado {
                background-color: #181B21;
                border: 1px solid #292D36;
                border-radius: 9px;
            }

            QLabel#nombre_tarjeta {
                color: #9298A3;
                font-size: 10px;
                font-weight: bold;
            }

            QLabel#valor_tarjeta {
                color: #F4C542;
                font-size: 24px;
                font-weight: bold;
            }

            QComboBox, QDateEdit {
                background-color: #181B21;
                border: 1px solid #343945;
                border-radius: 6px;
                padding: 7px;
                min-width: 110px;
            }

            QPushButton {
                background-color: #F4C542;
                color: #111318;
                border: none;
                border-radius: 6px;
                padding: 9px 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #FFDA62;
            }

            QTableWidget {
                background-color: #181B21;
                alternate-background-color: #1D2027;
                border: 1px solid #292D36;
                border-radius: 8px;
                gridline-color: #292D36;
                selection-background-color: #343944;
            }

            QHeaderView::section {
                background-color: #222630;
                color: #F4C542;
                border: none;
                padding: 10px;
                font-weight: bold;
            }
        """)

        self.tabla.setAlternatingRowColors(True)

    def crear_tarjeta(self, nombre, estilo):

        tarjeta = QFrame()
        tarjeta.setObjectName(estilo)
        tarjeta.setMinimumHeight(90)

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(14, 12, 14, 12)

        etiqueta = QLabel(nombre)
        etiqueta.setObjectName("nombre_tarjeta")

        valor = QLabel("0")
        valor.setObjectName("valor_tarjeta")

        layout.addWidget(etiqueta)
        layout.addWidget(valor)
        layout.addStretch()

        return tarjeta

    def cargar_datos(self, *_):

        fecha = self.fecha.date().toPython()

        try:
            self.asistencias = listar_asistencias(fecha)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar las asistencias.\n\n{error}",
            )
            return

        # Cargar tiendas encontradas en los registros
        tiendas = set()

        for asistencia in self.asistencias:
            trabajador = asistencia.trabajador

            if trabajador and trabajador.tienda:
                tiendas.add(trabajador.tienda.nombre)
            else:
                tiendas.add("Sin tienda")

        seleccion = self.combo_tienda.currentText()
        bloqueo = QSignalBlocker(self.combo_tienda)

        self.combo_tienda.clear()
        self.combo_tienda.addItem("Todas las tiendas")
        self.combo_tienda.addItems(sorted(tiendas))

        indice = self.combo_tienda.findText(seleccion)

        if indice >= 0:
            self.combo_tienda.setCurrentIndex(indice)

        del bloqueo

        self.actualizar_vista()

    def actualizar_vista(self, *_):

        tienda_seleccionada = self.combo_tienda.currentText()

        resultados = []

        for asistencia in self.asistencias:
            trabajador = asistencia.trabajador

            if trabajador is None:
                continue

            nombre_tienda = (
                trabajador.tienda.nombre
                if trabajador.tienda
                else "Sin tienda"
            )

            if (
                tienda_seleccionada != "Todas las tiendas"
                and nombre_tienda != tienda_seleccionada
            ):
                continue

            resultados.append(asistencia)

        resumen = {
            "total": len(resultados),
            "puntuales": 0,
            "tardanzas": 0,
            "faltas": 0,
            "justificados": 0,
        }

        for asistencia in resultados:
            estado = (asistencia.estado or "").upper()

            if estado == "PUNTUAL":
                resumen["puntuales"] += 1
            elif estado == "TARDANZA":
                resumen["tardanzas"] += 1
            elif estado == "FALTA":
                resumen["faltas"] += 1
            elif estado == "JUSTIFICADO":
                resumen["justificados"] += 1

        for clave, valor in resumen.items():
            self.valores[clave].setText(str(valor))

        self.mostrar_tabla(resultados)

        if not resultados:
            self.mensaje.setText(
                "No hay asistencias registradas para estos filtros."
            )
        else:
            self.mensaje.setText(
                f"Se encontraron {len(resultados)} registros."
            )

    def mostrar_tabla(self, asistencias):

        self.tabla.setRowCount(0)

        for asistencia in asistencias:
            trabajador = asistencia.trabajador
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)

            tienda = (
                trabajador.tienda.nombre
                if trabajador.tienda
                else "Sin tienda"
            )

            hora = asistencia.hora_marcacion

            if isinstance(hora, (datetime, time)):
                hora = hora.strftime("%H:%M")
            elif hora is None:
                hora = "--"
            else:
                hora = str(hora)

            datos = [
                trabajador.codigo or "-",
                trabajador.nombre_completo or "-",
                trabajador.dni or "-",
                tienda,
                asistencia.estado or "-",
                hora,
            ]

            for columna, dato in enumerate(datos):
                item = QTableWidgetItem(str(dato))

                if columna in (0, 2, 4, 5):
                    item.setTextAlignment(Qt.AlignCenter)

                self.tabla.setItem(fila, columna, item)