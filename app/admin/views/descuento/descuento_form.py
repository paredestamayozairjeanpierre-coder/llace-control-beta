import sys
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QTextEdit,
    QVBoxLayout,
)

from app.admin.services.descuento_service import (
    calcular_descuento_por_falta,
    obtener_asistencia_del_trabajador_en_fecha,
    obtener_trabajadores_activos,
    registrar_descuento_por_falta,
    registrar_descuento_por_tardanza,
)
from app.admin.services.tienda_service import (
    obtener_tienda_por_id,
)
from app.core.permisos import (
    puede_registrar_descuentos,
)


class DescuentoForm(QDialog):
    """
    Formulario para registrar descuentos.

    Reglas:
    - FALTA: monto automático = sueldo semanal / 6.
    - TARDANZA: monto manual.
    - Se recomienda vincular el descuento a una asistencia existente.
    - El servicio de descuentos vuelve a validar permisos y datos
      antes de guardar.
    """

    def __init__(self, parent=None):
        if not puede_registrar_descuentos():
            raise PermissionError(
                "No tienes permisos para registrar descuentos."
            )

        super().__init__(parent)

        self.trabajadores = []
        self.asistencia_actual = None
        self.tienda_actual = None

        self.setWindowTitle(
            "LLACE CONTROL BETA - Registrar descuento"
        )
        self.setModal(True)
        self.setMinimumSize(540, 620)
        self.resize(580, 680)

        self.crear_interfaz()
        self.cargar_trabajadores()
        self.actualizar_tipo()

    # ==========================================================
    # INTERFAZ
    # ==========================================================

    def crear_interfaz(self):
        self.setStyleSheet(
            """
            QDialog {
                background-color: #101216;
            }

            QLabel#titulo {
                color: #F5F5F5;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#subtitulo {
                color: #8D939D;
                font-size: 11px;
            }

            QLabel#seccion {
                color: #F4C542;
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#etiqueta {
                color: #AEB3BB;
                font-size: 10px;
                font-weight: 600;
            }

            QLabel#dato {
                color: #E8EAED;
                background-color: #15181D;
                border: 1px solid #303640;
                border-radius: 6px;
                padding: 9px 10px;
                font-size: 11px;
            }

            QLabel#estado_ok {
                color: #67D58A;
                background-color: #14251B;
                border: 1px solid #245536;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 10px;
            }

            QLabel#estado_error {
                color: #FF777F;
                background-color: #291619;
                border: 1px solid #5A292F;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 10px;
            }

            QComboBox,
            QDateEdit,
            QLineEdit,
            QTextEdit {
                background-color: #111419;
                color: #E8EAED;
                border: 1px solid #303640;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 11px;
            }

            QComboBox:focus,
            QDateEdit:focus,
            QLineEdit:focus,
            QTextEdit:focus {
                border: 1px solid #F4C542;
            }

            QComboBox QAbstractItemView {
                background-color: #181B21;
                color: #E8EAED;
                selection-background-color: #F4C542;
                selection-color: #111419;
            }

            QFrame#bloque {
                background-color: #181B21;
                border: 1px solid #282D35;
                border-radius: 10px;
            }

            QRadioButton {
                background-color: #15181D;
                color: #DCE0E5;
                border: 1px solid #303640;
                border-radius: 7px;
                padding: 12px;
                font-size: 11px;
                font-weight: 700;
            }

            QRadioButton:hover {
                border: 1px solid #6A5A1D;
            }

            QRadioButton::indicator {
                width: 0px;
                height: 0px;
            }

            QRadioButton:checked {
                background-color: #3A3216;
                color: #F4C542;
                border: 1px solid #F4C542;
            }

            QPushButton {
                border-radius: 6px;
                padding: 9px 16px;
                font-size: 10px;
                font-weight: 700;
            }

            QPushButton#cancelar {
                background-color: #252A32;
                color: #D5D8DD;
                border: 1px solid #363C46;
            }

            QPushButton#guardar {
                background-color: #F4C542;
                color: #111419;
                border: none;
            }

            QPushButton#guardar:hover {
                background-color: #FFD75A;
            }

            QPushButton#guardar:disabled {
                background-color: #4B4630;
                color: #77715B;
            }
            """
        )

        principal = QVBoxLayout(self)
        principal.setContentsMargins(22, 20, 22, 20)
        principal.setSpacing(12)

        titulo = QLabel("Registrar descuento")
        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Registra una falta injustificada o un descuento por tardanza."
        )
        subtitulo.setObjectName("subtitulo")

        principal.addWidget(titulo)
        principal.addWidget(subtitulo)

        # ------------------------------------------------------
        # BLOQUE PRINCIPAL
        # ------------------------------------------------------

        bloque = QFrame()
        bloque.setObjectName("bloque")

        layout = QVBoxLayout(bloque)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(
            self.crear_etiqueta("TRABAJADOR")
        )

        self.trabajador_combo = QComboBox()
        self.trabajador_combo.currentIndexChanged.connect(
            self.trabajador_cambiado
        )
        layout.addWidget(self.trabajador_combo)

        datos_grid = QFormLayout()
        datos_grid.setHorizontalSpacing(12)
        datos_grid.setVerticalSpacing(8)

        self.tienda_label = QLabel("—")
        self.tienda_label.setObjectName("dato")

        self.sueldo_label = QLabel("—")
        self.sueldo_label.setObjectName("dato")

        datos_grid.addRow(
            self.crear_etiqueta("Tienda"),
            self.tienda_label,
        )
        datos_grid.addRow(
            self.crear_etiqueta("Sueldo semanal"),
            self.sueldo_label,
        )

        layout.addLayout(datos_grid)

        layout.addWidget(
            self.crear_etiqueta("FECHA DE LA INCIDENCIA")
        )

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(
            QDate.currentDate()
        )
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.dateChanged.connect(
            self.actualizar_asistencia
        )
        layout.addWidget(self.fecha)

        layout.addWidget(
            self.crear_etiqueta("ASISTENCIA RELACIONADA")
        )

        self.asistencia_label = QLabel(
            "Selecciona un trabajador y una fecha."
        )
        self.asistencia_label.setObjectName(
            "estado_error"
        )
        self.asistencia_label.setWordWrap(True)
        layout.addWidget(self.asistencia_label)

        layout.addWidget(
            self.crear_etiqueta("TIPO DE DESCUENTO")
        )

        tipos = QHBoxLayout()
        tipos.setSpacing(8)

        self.radio_falta = QRadioButton(
            "FALTA\nDescuento por día"
        )
        self.radio_tardanza = QRadioButton(
            "TARDANZA\nMonto manual"
        )

        self.radio_falta.setChecked(True)

        self.grupo_tipo = QButtonGroup(self)
        self.grupo_tipo.addButton(
            self.radio_falta
        )
        self.grupo_tipo.addButton(
            self.radio_tardanza
        )

        self.radio_falta.toggled.connect(
            self.actualizar_tipo
        )
        self.radio_tardanza.toggled.connect(
            self.actualizar_tipo
        )

        tipos.addWidget(self.radio_falta)
        tipos.addWidget(self.radio_tardanza)

        layout.addLayout(tipos)

        layout.addWidget(
            self.crear_etiqueta("MONTO (S/)")
        )

        self.monto = QLineEdit()
        self.monto.setPlaceholderText(
            "Ejemplo: 10.00"
        )
        self.monto.textChanged.connect(
            self.validar_formulario
        )
        layout.addWidget(self.monto)

        self.monto_info = QLabel()
        self.monto_info.setObjectName("subtitulo")
        layout.addWidget(self.monto_info)

        layout.addWidget(
            self.crear_etiqueta("OBSERVACIÓN")
        )

        self.observacion = QTextEdit()
        self.observacion.setPlaceholderText(
            "Indica el motivo del descuento..."
        )
        self.observacion.setMaximumHeight(85)
        self.observacion.textChanged.connect(
            self.validar_formulario
        )
        layout.addWidget(self.observacion)

        principal.addWidget(bloque)

        # ------------------------------------------------------
        # BOTONES
        # ------------------------------------------------------

        botones = QHBoxLayout()
        botones.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("cancelar")
        cancelar.clicked.connect(self.reject)

        self.guardar = QPushButton(
            "Guardar descuento"
        )
        self.guardar.setObjectName("guardar")
        self.guardar.clicked.connect(
            self.guardar_descuento
        )

        botones.addWidget(cancelar)
        botones.addWidget(self.guardar)

        principal.addLayout(botones)

    # ==========================================================
    # AUXILIARES
    # ==========================================================

    def crear_etiqueta(self, texto):
        etiqueta = QLabel(texto)
        etiqueta.setObjectName("etiqueta")
        return etiqueta

    def cargar_trabajadores(self):
        try:
            self.trabajadores = (
                obtener_trabajadores_activos()
            )

            self.trabajador_combo.blockSignals(True)
            self.trabajador_combo.clear()

            if not self.trabajadores:
                self.trabajador_combo.addItem(
                    "No hay trabajadores activos",
                    None,
                )
            else:
                for trabajador in self.trabajadores:
                    texto = (
                        f"{trabajador.codigo} - "
                        f"{trabajador.nombre_completo}"
                    )

                    self.trabajador_combo.addItem(
                        texto,
                        trabajador.id,
                    )

            self.trabajador_combo.blockSignals(False)

            if self.trabajadores:
                self.trabajador_combo.setCurrentIndex(0)
                self.trabajador_cambiado(0)
            else:
                self.trabajador_combo.setEnabled(False)
                self.guardar.setEnabled(False)

        except Exception as error:
            self.trabajador_combo.addItem(
                "No se pudieron cargar trabajadores"
            )
            self.trabajador_combo.setEnabled(False)
            self.guardar.setEnabled(False)

            QMessageBox.critical(
                self,
                "Error",
                "No se pudieron cargar los trabajadores.\n\n"
                f"{error}",
            )

    def obtener_trabajador_seleccionado(self):
        trabajador_id = (
            self.trabajador_combo.currentData()
        )

        if trabajador_id is None:
            return None

        for trabajador in self.trabajadores:
            if trabajador.id == trabajador_id:
                return trabajador

        return None

    # ==========================================================
    # TRABAJADOR
    # ==========================================================

    def trabajador_cambiado(self, indice):
        trabajador = (
            self.obtener_trabajador_seleccionado()
        )

        self.asistencia_actual = None
        self.tienda_actual = None

        if trabajador is None:
            self.tienda_label.setText("—")
            self.sueldo_label.setText("—")
            self.asistencia_label.setText(
                "No hay trabajador seleccionado."
            )
            self.asistencia_label.setObjectName(
                "estado_error"
            )
            self.asistencia_label.style().unpolish(
                self.asistencia_label
            )
            self.asistencia_label.style().polish(
                self.asistencia_label
            )
            self.validar_formulario()
            return

        self.sueldo_label.setText(
            f"S/ {Decimal(str(trabajador.sueldo_semanal or 0)):.2f}"
        )

        try:
            self.tienda_actual = (
                obtener_tienda_por_id(
                    trabajador.tienda_id
                )
            )

            if self.tienda_actual is not None:
                self.tienda_label.setText(
                    self.tienda_actual.nombre
                )
            else:
                self.tienda_label.setText(
                    "Tienda no encontrada"
                )

        except Exception:
            self.tienda_label.setText(
                "No disponible"
            )

        self.actualizar_tipo()
        self.actualizar_asistencia()

    # ==========================================================
    # ASISTENCIA
    # ==========================================================

    def actualizar_asistencia(self):
        trabajador = (
            self.obtener_trabajador_seleccionado()
        )

        if trabajador is None:
            return

        fecha = self.fecha.date().toPython()

        try:
            asistencia = (
                obtener_asistencia_del_trabajador_en_fecha(
                    trabajador.id,
                    fecha,
                )
            )

            self.asistencia_actual = asistencia

            if asistencia is None:
                self.asistencia_label.setText(
                    "No existe una asistencia registrada "
                    "para este trabajador en esta fecha."
                )
                self.asistencia_label.setObjectName(
                    "estado_error"
                )
            else:
                estado = str(
                    asistencia.estado
                ).upper()

                hora = getattr(
                    asistencia,
                    "hora_marcacion",
                    None,
                )

                hora_texto = (
                    hora.strftime("%H:%M:%S")
                    if hora is not None
                    else "—"
                )

                self.asistencia_label.setText(
                    f"Asistencia encontrada: {estado}  ·  "
                    f"Hora: {hora_texto}"
                )

                if (
                    self.radio_falta.isChecked()
                    and estado == "FALTA"
                ):
                    self.asistencia_label.setObjectName(
                        "estado_ok"
                    )
                elif (
                    self.radio_tardanza.isChecked()
                    and estado == "TARDANZA"
                ):
                    self.asistencia_label.setObjectName(
                        "estado_ok"
                    )
                else:
                    self.asistencia_label.setObjectName(
                        "estado_error"
                    )

            self.asistencia_label.style().unpolish(
                self.asistencia_label
            )
            self.asistencia_label.style().polish(
                self.asistencia_label
            )

        except Exception as error:
            self.asistencia_actual = None
            self.asistencia_label.setText(
                "No se pudo consultar la asistencia."
            )
            self.asistencia_label.setObjectName(
                "estado_error"
            )
            print(
                "ERROR AL CONSULTAR ASISTENCIA:"
            )
            print(error)

        self.validar_formulario()

    # ==========================================================
    # TIPO
    # ==========================================================

    def actualizar_tipo(self):
        trabajador = (
            self.obtener_trabajador_seleccionado()
        )

        if self.radio_falta.isChecked():
            self.monto.setReadOnly(True)
            self.monto.setPlaceholderText(
                "Se calculará automáticamente"
            )

            if trabajador is not None:
                try:
                    monto = (
                        calcular_descuento_por_falta(
                            trabajador.id
                        )
                    )
                    self.monto.setText(
                        f"{Decimal(str(monto)):.2f}"
                    )
                    self.monto_info.setText(
                        "Fórmula: sueldo semanal ÷ 6 días."
                    )
                except Exception as error:
                    self.monto.clear()
                    self.monto_info.setText(
                        str(error)
                    )
            else:
                self.monto.clear()
                self.monto_info.setText(
                    "Selecciona un trabajador."
                )

        else:
            self.monto.setReadOnly(False)
            self.monto.setPlaceholderText(
                "Ejemplo: 10.00"
            )
            self.monto_info.setText(
                "El monto lo define manualmente ADMIN/SUPERADMIN."
            )

        self.actualizar_asistencia()
        self.validar_formulario()

    # ==========================================================
    # VALIDACIÓN
    # ==========================================================

    def obtener_monto(self):
        texto = (
            self.monto.text()
            .strip()
            .replace(",", ".")
        )

        try:
            monto = Decimal(texto)
        except (InvalidOperation, ValueError):
            raise ValueError(
                "El monto no es válido."
            )

        if monto <= 0:
            raise ValueError(
                "El monto debe ser mayor que 0."
            )

        return monto.quantize(
            Decimal("0.01")
        )

    def validar_formulario(self):
        trabajador = (
            self.obtener_trabajador_seleccionado()
        )

        if trabajador is None:
            self.guardar.setEnabled(False)
            return

        observacion = (
            self.observacion.toPlainText()
            .strip()
        )

        if not observacion:
            self.guardar.setEnabled(False)
            return

        try:
            monto = self.obtener_monto()
        except ValueError:
            self.guardar.setEnabled(False)
            return

        if monto <= 0:
            self.guardar.setEnabled(False)
            return

        asistencia = self.asistencia_actual

        if asistencia is None:
            self.guardar.setEnabled(False)
            return

        estado = str(
            asistencia.estado
        ).upper()

        if (
            self.radio_falta.isChecked()
            and estado != "FALTA"
        ):
            self.guardar.setEnabled(False)
            return

        if (
            self.radio_tardanza.isChecked()
            and estado != "TARDANZA"
        ):
            self.guardar.setEnabled(False)
            return

        self.guardar.setEnabled(True)

    # ==========================================================
    # GUARDAR
    # ==========================================================

    def guardar_descuento(self):
        trabajador = (
            self.obtener_trabajador_seleccionado()
        )

        if trabajador is None:
            QMessageBox.warning(
                self,
                "Trabajador",
                "Selecciona un trabajador.",
            )
            return

        asistencia = self.asistencia_actual

        if asistencia is None:
            QMessageBox.warning(
                self,
                "Asistencia",
                "No existe una asistencia relacionada "
                "con la fecha seleccionada.",
            )
            return

        observacion = (
            self.observacion.toPlainText()
            .strip()
        )

        if not observacion:
            QMessageBox.warning(
                self,
                "Observación",
                "Debes indicar una observación.",
            )
            self.observacion.setFocus()
            return

        try:
            monto = self.obtener_monto()
        except ValueError as error:
            QMessageBox.warning(
                self,
                "Monto",
                str(error),
            )
            self.monto.setFocus()
            return

        if self.radio_falta.isChecked():
            tipo_texto = "FALTA"
        else:
            tipo_texto = "TARDANZA"

        respuesta = QMessageBox.question(
            self,
            "Confirmar descuento",
            (
                "¿Deseas registrar este descuento?\n\n"
                f"Trabajador: {trabajador.nombre_completo}\n"
                f"Tipo: {tipo_texto}\n"
                f"Monto: S/ {monto:.2f}\n"
                f"Fecha: {self.fecha.date().toString('dd/MM/yyyy')}"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if respuesta != QMessageBox.Yes:
            return

        try:
            if tipo_texto == "FALTA":
                descuento = (
                    registrar_descuento_por_falta(
                        trabajador_id=trabajador.id,
                        asistencia_id=asistencia.id,
                        observacion=observacion,
                    )
                )
            else:
                descuento = (
                    registrar_descuento_por_tardanza(
                        trabajador_id=trabajador.id,
                        monto=monto,
                        asistencia_id=asistencia.id,
                        observacion=observacion,
                    )
                )

            QMessageBox.information(
                self,
                "Descuento registrado",
                (
                    "El descuento se registró correctamente.\n\n"
                    f"ID: {descuento.id}\n"
                    f"Monto: S/ {Decimal(str(descuento.monto)):.2f}"
                ),
            )

            self.accept()

        except PermissionError as error:
            QMessageBox.warning(
                self,
                "Permisos",
                str(error),
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "No se pudo registrar",
                str(error),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                "Ocurrió un error al registrar el descuento.\n\n"
                f"{error}",
            )

            print(
                "ERROR AL REGISTRAR DESCUENTO:"
            )
            print(error)


# ==========================================================
# EJECUCIÓN DIRECTA
# ==========================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        ventana = DescuentoForm()
        ventana.exec()

    except PermissionError as error:
        QMessageBox.critical(
            None,
            "Permisos",
            str(error),
        )
        sys.exit(1)
