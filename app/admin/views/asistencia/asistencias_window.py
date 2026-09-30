"""Página de Asistencias para integrar en el QStackedWidget de LLACE CONTROL."""
from app.core import tiempo
from datetime import date, datetime, time

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QDateEdit, QComboBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFrame, QMessageBox, QTextEdit, QDialogButtonBox, QSizePolicy,
)

from app.admin.services.asistencia_service import (
    listar_asistencias,
    obtener_resumen_asistencias,
    actualizar_estado_asistencia,
    cerrar_asistencias_del_dia,
)


FONDO = "#111318"
PANEL = "#171A22"
PANEL_ALT = "#14171E"
BORDE = "#2B303B"
TEXTO = "#F3F4F6"
SECUNDARIO = "#8D98A8"
AMARILLO = "#F4C542"


class AsistenciasWindow(QWidget):
    """Vista central de asistencia; no crea una ventana de nivel superior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fecha_actual = tiempo.hoy()
        self.asistencias = []
        self.asistencias_mostradas = []
        self.setObjectName("pagina_asistencias")
        self.setStyleSheet(f"""
            QWidget#pagina_asistencias {{ background: {FONDO}; color: {TEXTO}; }}
            QLabel {{ color: {TEXTO}; background: transparent; }}
            QLabel#subtitulo {{ color: {SECUNDARIO}; font-size: 11px; }}
            QLabel#seccion {{ color: {TEXTO}; font-size: 13px; font-weight: 600; }}
            QLineEdit, QComboBox, QDateEdit, QTextEdit {{
                background: {PANEL_ALT}; color: {TEXTO}; border: 1px solid {BORDE};
                border-radius: 6px; padding: 8px 10px; selection-background-color: {AMARILLO};
            }}
            QComboBox QAbstractItemView {{ background: {PANEL}; color: {TEXTO};
                selection-background-color: #343A46; border: 1px solid {BORDE}; }}
            QPushButton {{ background: #242934; color: {TEXTO}; border: 1px solid {BORDE};
                border-radius: 6px; padding: 9px 14px; font-weight: 600; }}
            QPushButton:hover {{ background: #303644; }}
            QPushButton#amarillo {{ background: {AMARILLO}; color: #111318; border: none; }}
            QPushButton#amarillo:hover {{ background: #EAB308; }}
            QTableWidget {{ background: {PANEL_ALT}; alternate-background-color: {PANEL};
                color: {TEXTO}; border: 1px solid {BORDE}; gridline-color: {BORDE};
                selection-background-color: #343A46; selection-color: {TEXTO}; }}
            QHeaderView::section {{ background: {FONDO}; color: {AMARILLO}; border: none;
                border-bottom: 1px solid {BORDE}; padding: 10px 7px; font-size: 10px; font-weight: bold; }}
            QScrollBar:vertical {{ background: {FONDO}; width: 10px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: #454B56; min-height: 25px; border-radius: 4px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        self.crear_interfaz()
        self.cargar_asistencias()

    @staticmethod
    def crear_boton(texto, amarillo=False, parent=None):
        boton = QPushButton(texto, parent)
        if amarillo:
            boton.setObjectName("amarillo")
        boton.setCursor(Qt.PointingHandCursor)
        return boton

    def crear_interfaz(self):
        principal = QVBoxLayout(self)
        principal.setContentsMargins(24, 20, 24, 16)
        principal.setSpacing(14)

        # Cabecera
        cabecera = QHBoxLayout()
        bloque_titulo = QVBoxLayout()
        titulo = QLabel("ASISTENCIAS")
        titulo.setStyleSheet("font-size: 23px; font-weight: 700;")
        subtitulo = QLabel("Control diario de asistencia del personal")
        subtitulo.setObjectName("subtitulo")
        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(subtitulo)
        cabecera.addLayout(bloque_titulo)
        cabecera.addStretch(1)

        self.entrada_fecha = QDateEdit()
        self.entrada_fecha.setCalendarPopup(True)
        self.entrada_fecha.setDisplayFormat("yyyy-MM-dd")
        self.entrada_fecha.setDate(QDate.currentDate())
        self.entrada_fecha.setFixedWidth(126)
        self.entrada_fecha.dateChanged.connect(self.buscar_por_fecha)
        boton_hoy = self.crear_boton("HOY")
        boton_hoy.clicked.connect(self.ir_a_hoy)
        boton_cierre = self.crear_boton("●  CERRAR DÍA (3:00 PM)", True)
        boton_cierre.clicked.connect(self.cerrar_dia)
        cabecera.addWidget(self.entrada_fecha)
        cabecera.addWidget(boton_hoy)
        cabecera.addWidget(boton_cierre)
        principal.addLayout(cabecera)

        # Filtros
        filtros = QHBoxLayout()
        self.combo_tienda = QComboBox()
        self.combo_tienda.addItem("Todas las tiendas")
        self.combo_tienda.setMinimumWidth(155)
        self.combo_estado = QComboBox()
        self.combo_estado.addItems([
            "Todos los estados", "PUNTUAL", "TARDANZA", "FALTA", "JUSTIFICADO"
        ])
        self.combo_estado.setMinimumWidth(155)
        self.entrada_busqueda = QLineEdit()
        self.entrada_busqueda.setPlaceholderText("⌕  Buscar por nombre, código o DNI...")
        self.boton_buscar = self.crear_boton("BUSCAR")
        self.boton_buscar.clicked.connect(self.aplicar_filtros)
        self.combo_tienda.currentIndexChanged.connect(self.aplicar_filtros)
        self.combo_estado.currentIndexChanged.connect(self.aplicar_filtros)
        self.entrada_busqueda.textChanged.connect(self.aplicar_filtros)
        filtros.addWidget(self.combo_tienda)
        filtros.addWidget(self.combo_estado)
        filtros.addWidget(self.entrada_busqueda, 1)
        filtros.addWidget(self.boton_buscar)
        principal.addLayout(filtros)

        # Tarjetas de resumen
        tarjetas = QGridLayout()
        tarjetas.setHorizontalSpacing(12)
        tarjetas.setVerticalSpacing(8)
        self.card_puntuales = self.crear_card_resumen("PUNTUALES", "0", "#39C786")
        self.card_tardanzas = self.crear_card_resumen("TARDANZAS", "0", AMARILLO)
        self.card_faltas = self.crear_card_resumen("FALTAS", "0", "#F05B64")
        self.card_justificados = self.crear_card_resumen("JUSTIFICADOS", "0", "#68A7F5")
        for col, card in enumerate((self.card_puntuales, self.card_tardanzas,
                                    self.card_faltas, self.card_justificados)):
            tarjetas.addWidget(card, 0, col)
        principal.addLayout(tarjetas)

        label_lista = QLabel("Lista de asistencias")
        label_lista.setObjectName("seccion")
        principal.addWidget(label_lista)

        # Tabla
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels([
            "CÓDIGO", "NOMBRE", "TIENDA", "HORA", "ESTADO", "TARDANZA"
        ])
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.verticalHeader().setDefaultSectionSize(34)
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabla.doubleClicked.connect(self.abrir_detalle)
        principal.addWidget(self.tabla, 1)

        pie = QHBoxLayout()
        self.etiqueta_pie = QLabel("0 registros")
        self.etiqueta_pie.setObjectName("subtitulo")
        pie.addWidget(self.etiqueta_pie)
        pie.addStretch(1)
        boton_detalle = self.crear_boton("◉  VER DETALLE")
        boton_detalle.clicked.connect(self.abrir_detalle)
        pie.addWidget(boton_detalle)
        principal.addLayout(pie)

    def crear_card_resumen(self, titulo, valor, color):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaResumen")
        tarjeta.setStyleSheet(f"QFrame#tarjetaResumen {{ background: {PANEL}; border: 1px solid {BORDE}; border-radius: 8px; }}")
        tarjeta.setMinimumHeight(82)
        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(15, 10, 12, 10)
        layout.setSpacing(3)
        nombre = QLabel(titulo)
        nombre.setStyleSheet(f"color: {SECUNDARIO}; font-size: 10px; font-weight: 600; border: none;")
        numero = QLabel(valor)
        numero.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 700; border: none;")
        layout.addWidget(nombre)
        layout.addWidget(numero)
        layout.addStretch(1)
        tarjeta.etiqueta_valor = numero
        return tarjeta

    def cargar_asistencias(self):
        try:
            self.asistencias = listar_asistencias(self.fecha_actual)
            self.actualizar_tiendas()
            self.actualizar_resumen()
            self.aplicar_filtros()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las asistencias.\n\n{error}")

    def actualizar_tiendas(self):
        tiendas = sorted({
            asistencia.trabajador.tienda.nombre
            for asistencia in self.asistencias
            if asistencia.trabajador and asistencia.trabajador.tienda
        })
        seleccion = self.combo_tienda.currentText()
        self.combo_tienda.blockSignals(True)
        self.combo_tienda.clear()
        self.combo_tienda.addItems(["Todas las tiendas"] + tiendas)
        idx = self.combo_tienda.findText(seleccion)
        self.combo_tienda.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_tienda.blockSignals(False)

    def actualizar_resumen(self):
        resumen = obtener_resumen_asistencias(self.fecha_actual)
        self.card_puntuales.etiqueta_valor.setText(str(resumen["puntuales"]))
        self.card_tardanzas.etiqueta_valor.setText(str(resumen["tardanzas"]))
        self.card_faltas.etiqueta_valor.setText(str(resumen["faltas"]))
        self.card_justificados.etiqueta_valor.setText(str(resumen["justificados"]))

    def aplicar_filtros(self, *_):
        tienda = self.combo_tienda.currentText()
        estado = self.combo_estado.currentText()
        texto = self.entrada_busqueda.text().strip().lower()
        resultados = []
        for asistencia in self.asistencias:
            trabajador = asistencia.trabajador
            if trabajador is None:
                continue
            nombre = (trabajador.nombre_completo or "").lower()
            codigo = str(trabajador.codigo or "").lower()
            dni = str(getattr(trabajador, "dni", "") or "").lower()
            nombre_tienda = trabajador.tienda.nombre if trabajador.tienda else "Sin tienda"
            if tienda != "Todas las tiendas" and nombre_tienda != tienda:
                continue
            if estado != "Todos los estados" and asistencia.estado != estado:
                continue
            if texto and texto not in nombre and texto not in codigo and texto not in dni:
                continue
            resultados.append(asistencia)
        self.asistencias_mostradas = resultados
        self.mostrar_tabla(resultados)

    def mostrar_tabla(self, asistencias):
        self.tabla.setRowCount(0)
        colores = {
            "PUNTUAL": QColor("#39C786"),
            "TARDANZA": QColor(AMARILLO),
            "FALTA": QColor("#F05B64"),
            "JUSTIFICADO": QColor("#68A7F5"),
        }
        for asistencia in asistencias:
            trabajador = asistencia.trabajador
            nombre = trabajador.nombre_completo if trabajador else "Sin trabajador"
            codigo = str(trabajador.codigo) if trabajador else "-"
            tienda = trabajador.tienda.nombre if trabajador and trabajador.tienda else "Sin tienda"
            hora = asistencia.hora_marcacion.strftime("%H:%M:%S") if asistencia.hora_marcacion else "—"
            tardanza = f"{asistencia.minutos_tardanza or 0} min"
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            valores = (codigo, nombre, tienda, hora, asistencia.estado, tardanza)
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if columna in (0, 3, 4, 5):
                    item.setTextAlignment(Qt.AlignCenter)
                if columna == 4:
                    item.setForeground(colores.get(asistencia.estado, QColor(TEXTO)))
                if columna == 0:
                    item.setData(Qt.UserRole, asistencia.id)
                self.tabla.setItem(fila, columna, item)
        n = len(asistencias)
        self.etiqueta_pie.setText(f"{n} registro" if n == 1 else f"{n} registros")

    def abrir_detalle(self, *_):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Selecciona una asistencia", "Selecciona una asistencia de la lista.")
            return
        item = self.tabla.item(fila, 0)
        if item is None:
            return
        asistencia_id = item.data(Qt.UserRole)
        asistencia = next((a for a in self.asistencias if a.id == asistencia_id), None)
        if asistencia is not None:
            self.mostrar_detalle(asistencia)

    def mostrar_detalle(self, asistencia):
        trabajador = asistencia.trabajador
        detalle = QDialog(self)
        detalle.setWindowTitle("LLACE CONTROL - Detalle de asistencia")
        detalle.setMinimumWidth(440)
        detalle.setStyleSheet(f"""
            QDialog {{ background: {PANEL}; color: {TEXTO}; }}
            QLabel {{ color: {TEXTO}; }}
            QComboBox, QTextEdit {{ background: {PANEL_ALT}; color: {TEXTO}; border: 1px solid {BORDE}; border-radius: 5px; padding: 7px; }}
            QPushButton {{ background: #242934; color: {TEXTO}; border: 1px solid {BORDE}; border-radius: 5px; padding: 8px 14px; }}
            QPushButton#guardar {{ background: {AMARILLO}; color: #111318; border: none; font-weight: bold; }}
        """)
        layout = QVBoxLayout(detalle)
        layout.setContentsMargins(22, 20, 22, 20)
        title = QLabel("DETALLE DE ASISTENCIA")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        subtitle = QLabel("Información de la marcación")
        subtitle.setStyleSheet(f"color: {SECUNDARIO};")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        tarjeta = QFrame()
        tarjeta.setStyleSheet(f"QFrame {{ background: {PANEL_ALT}; border: 1px solid {BORDE}; border-radius: 7px; }}")
        tarjeta_layout = QVBoxLayout(tarjeta)
        nombre = QLabel(trabajador.nombre_completo if trabajador else "Sin trabajador")
        nombre.setStyleSheet("font-size: 14px; font-weight: 700; border: none;")
        cod_dni = QLabel(f"Código: {trabajador.codigo if trabajador else '-'}  |  DNI: {trabajador.dni if trabajador else '-'}")
        cod_dni.setStyleSheet(f"color: {SECUNDARIO}; border: none;")
        tarjeta_layout.addWidget(nombre)
        tarjeta_layout.addWidget(cod_dni)
        layout.addWidget(tarjeta)
        fecha = asistencia.fecha.strftime("%d/%m/%Y") if asistencia.fecha else "-"
        hora = asistencia.hora_marcacion.strftime("%H:%M:%S") if asistencia.hora_marcacion else "—"
        tienda = trabajador.tienda.nombre if trabajador and trabajador.tienda else "Sin tienda"
        for etiqueta, valor in (
            ("Fecha", fecha), ("Hora de marcación", hora),
            ("Tienda", tienda), ("Minutos de tardanza", f"{asistencia.minutos_tardanza or 0} minutos"),
        ):
            linea = QHBoxLayout()
            lbl = QLabel(etiqueta)
            lbl.setMinimumWidth(160)
            lbl.setStyleSheet(f"color: {SECUNDARIO}; font-weight: 600;")
            val = QLabel(valor)
            linea.addWidget(lbl)
            linea.addWidget(val, 1)
            layout.addLayout(linea)
        estado_label = QLabel("CAMBIAR ESTADO")
        estado_label.setStyleSheet(f"color: {SECUNDARIO}; font-size: 10px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(estado_label)
        combo_estado = QComboBox()
        combo_estado.addItems(["PUNTUAL", "TARDANZA", "FALTA", "JUSTIFICADO"])
        combo_estado.setCurrentText(asistencia.estado)
        layout.addWidget(combo_estado)
        # El servicio actual actualizar_estado_asistencia solo recibe id y estado.
        nota_info = QLabel("La actualización disponible en el servicio guarda el estado de asistencia.")
        nota_info.setStyleSheet(f"color: {SECUNDARIO}; font-size: 10px;")
        nota_info.setWordWrap(True)
        layout.addWidget(nota_info)
        botones = QDialogButtonBox()
        cancelar = botones.addButton("CANCELAR", QDialogButtonBox.RejectRole)
        guardar = botones.addButton("GUARDAR CAMBIOS", QDialogButtonBox.AcceptRole)
        guardar.setObjectName("guardar")
        cancelar.clicked.connect(detalle.reject)
        def guardar_cambios():
            nuevo_estado = combo_estado.currentText()
            confirmar = QMessageBox.question(
                detalle, "Confirmar cambios",
                "¿Deseas guardar los cambios de esta asistencia?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if confirmar != QMessageBox.Yes:
                return
            try:
                actualizar_estado_asistencia(asistencia.id, nuevo_estado)
                QMessageBox.information(detalle, "Cambios guardados", "La asistencia fue actualizada correctamente.")
                detalle.accept()
                self.cargar_asistencias()
            except Exception as error:
                QMessageBox.critical(detalle, "Error", f"No se pudo actualizar la asistencia.\n\n{error}")
        guardar.clicked.connect(guardar_cambios)
        layout.addWidget(botones)
        detalle.exec()

    def ir_a_hoy(self):
        self.fecha_actual = tiempo.hoy()
        self.entrada_fecha.blockSignals(True)
        self.entrada_fecha.setDate(QDate.currentDate())
        self.entrada_fecha.blockSignals(False)
        self.cargar_asistencias()

    def buscar_por_fecha(self, *_):
        qdate = self.entrada_fecha.date()
        self.fecha_actual = date(qdate.year(), qdate.month(), qdate.day())
        self.cargar_asistencias()

    def cerrar_dia(self):
        if tiempo.ahora().time() < time(15, 0):
            QMessageBox.warning(self, "Cierre no disponible", "El cierre automático corresponde a las 3:00 PM.")
            return
        confirmar = QMessageBox.question(
            self, "Cerrar día",
            f"¿Deseas cerrar el día {self.fecha_actual.strftime('%d/%m/%Y')}?\n\n"
            "Los trabajadores activos que no tengan marcación serán registrados como FALTA.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirmar != QMessageBox.Yes:
            return
        try:
            cantidad = cerrar_asistencias_del_dia(self.fecha_actual)
            QMessageBox.information(self, "Día cerrado", f"El día fue cerrado correctamente.\n\nFaltas generadas: {cantidad}")
            self.cargar_asistencias()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo cerrar el día.\n\n{error}")
