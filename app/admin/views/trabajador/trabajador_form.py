from app.core import tiempo
from datetime import date
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sqlalchemy import select

from database.connection import SessionLocal
from database.models import Tienda
from app.admin.services.trabajador_service import (
    generar_codigo_trabajador,
    crear_trabajador,
    obtener_trabajador,
    actualizar_trabajador,
)


class TrabajadorForm(QDialog):
    """Formulario PySide6 para registrar o editar un trabajador."""

    def __init__(self, parent=None, al_guardar=None, trabajador_id=None):
        super().__init__(parent)

        self.al_guardar = al_guardar
        self.trabajador_id = trabajador_id
        self.es_edicion = trabajador_id is not None
        self.tiendas = []

        titulo = "Editar trabajador" if self.es_edicion else "Nuevo trabajador"
        self.setWindowTitle(f"LLACE CONTROL BETA - {titulo}")
        self.setModal(True)
        self.setFixedSize(720, 570)

        self.setStyleSheet("""
            QDialog {
                background: #F5F6F8;
                color: #111827;
                font-family: "Segoe UI";
                font-size: 10pt;
            }
            QWidget#cabecera { background: #FFFFFF; }
            QLabel#titulo { color: #111827; font-size: 20pt; font-weight: 700; }
            QLabel#subtitulo { color: #6B7280; font-size: 9pt; }
            QLabel.campo { color: #374151; font-size: 8pt; font-weight: 700; }
            QLineEdit, QComboBox {
                background: #FFFFFF;
                color: #111827;
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 8px;
                min-height: 20px;
            }
            QLineEdit:read-only { background: #F3F4F6; color: #374151; }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #EAB308; }
            QPushButton {
                border: 0;
                border-radius: 4px;
                padding: 9px 18px;
                font-weight: 700;
            }
            QPushButton#guardar { background: #FACC15; color: #111827; }
            QPushButton#guardar:hover { background: #EAB308; }
            QPushButton#cancelar { background: #E5E7EB; color: #374151; }
            QPushButton#cancelar:hover { background: #D1D5DB; }
            QPushButton#foto { background: #111827; color: #FFFFFF; font-size: 8pt; }
        """)

        self.crear_interfaz()
        self.cargar_tiendas()

        if self.es_edicion:
            self.cargar_trabajador()
        else:
            self.cargar_codigo()
            self.entrada_fecha.setText(tiempo.hoy().isoformat())

    def crear_interfaz(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        cabecera = QWidget()
        cabecera.setObjectName("cabecera")
        cabecera.setFixedHeight(92)
        cab_layout = QVBoxLayout(cabecera)
        cab_layout.setContentsMargins(28, 15, 24, 12)
        cab_layout.setSpacing(2)

        titulo = QLabel("EDITAR TRABAJADOR" if self.es_edicion else "NUEVO TRABAJADOR")
        titulo.setObjectName("titulo")
        subtitulo = QLabel(
            "Actualiza los datos del trabajador" if self.es_edicion
            else "Registra los datos del trabajador"
        )
        subtitulo.setObjectName("subtitulo")
        cab_layout.addWidget(titulo)
        cab_layout.addWidget(subtitulo)
        raiz.addWidget(cabecera)

        cuerpo = QWidget()
        cuerpo_layout = QHBoxLayout(cuerpo)
        cuerpo_layout.setContentsMargins(24, 20, 24, 14)
        cuerpo_layout.setSpacing(22)

        foto_layout = QVBoxLayout()
        foto_layout.setContentsMargins(0, 25, 0, 0)
        avatar = QLabel("●")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(125, 125)
        avatar.setStyleSheet(
            "background:#F3F4F6; color:#9CA3AF; border:1px solid #D1D5DB; font-size:42pt;"
        )
        foto_texto = QLabel("FOTO OPCIONAL")
        foto_texto.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        foto_texto.setStyleSheet("color:#9CA3AF; font-size:8pt; font-weight:700;")
        btn_foto = QPushButton("SELECCIONAR FOTO")
        btn_foto.setObjectName("foto")
        btn_foto.clicked.connect(self.foto_proximamente)
        foto_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignHCenter)
        foto_layout.addWidget(foto_texto)
        foto_layout.addWidget(btn_foto)
        foto_layout.addStretch()
        cuerpo_layout.addLayout(foto_layout)

        datos = QGridLayout()
        datos.setHorizontalSpacing(16)
        datos.setVerticalSpacing(10)
        datos.setColumnStretch(0, 1)
        datos.setColumnStretch(1, 1)

        self.entrada_codigo = QLineEdit()
        self.entrada_codigo.setReadOnly(True)
        self.combo_tienda = QComboBox()
        self.combo_tienda.setMinimumHeight(38)
        self._agregar_campo(datos, 0, 0, "CÓDIGO DE TRABAJADOR", self.entrada_codigo)
        self._agregar_campo(datos, 0, 1, "TIENDA", self.combo_tienda)

        self.entrada_nombre = QLineEdit()
        self._agregar_campo(datos, 1, 0, "NOMBRE COMPLETO", self.entrada_nombre, 2)

        self.entrada_dni = QLineEdit()
        self.entrada_dni.setMaxLength(8)
        self.entrada_dni.setPlaceholderText("8 dígitos")

        sueldo_widget = QWidget()
        sueldo_layout = QHBoxLayout(sueldo_widget)
        sueldo_layout.setContentsMargins(0, 0, 0, 0)
        sueldo_layout.setSpacing(6)
        prefijo = QLabel("S/")
        prefijo.setStyleSheet("font-weight:700; color:#374151;")
        self.entrada_sueldo = QLineEdit()
        self.entrada_sueldo.setPlaceholderText("0.00")
        sueldo_layout.addWidget(prefijo)
        sueldo_layout.addWidget(self.entrada_sueldo)
        self._agregar_campo(datos, 2, 0, "DNI", self.entrada_dni)
        self._agregar_campo(datos, 2, 1, "SUELDO SEMANAL", sueldo_widget)

        self.entrada_fecha = QLineEdit()
        self.entrada_fecha.setPlaceholderText("AAAA-MM-DD")
        self._agregar_campo(datos, 3, 0, "FECHA DE INGRESO", self.entrada_fecha, 2)
        datos.setRowStretch(4, 1)
        cuerpo_layout.addLayout(datos, 1)
        raiz.addWidget(cuerpo, 1)

        botones = QHBoxLayout()
        botones.setContentsMargins(24, 0, 24, 20)
        botones.addStretch()

        btn_cancelar = QPushButton("CANCELAR")
        btn_cancelar.setObjectName("cancelar")
        btn_cancelar.clicked.connect(self.reject)

        btn_guardar = QPushButton("GUARDAR CAMBIOS" if self.es_edicion else "REGISTRAR")
        btn_guardar.setObjectName("guardar")
        btn_guardar.setDefault(True)
        btn_guardar.clicked.connect(self.guardar_trabajador)

        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_guardar)
        raiz.addLayout(botones)

    @staticmethod
    def _agregar_campo(layout, fila, columna, texto, widget, colspan=1):
        etiqueta = QLabel(texto)
        etiqueta.setProperty("class", "campo")
        bloque = QVBoxLayout()
        bloque.setSpacing(5)
        bloque.addWidget(etiqueta)
        bloque.addWidget(widget)
        contenedor = QWidget()
        contenedor.setLayout(bloque)
        layout.addWidget(contenedor, fila, columna, 1, colspan)

    def cargar_codigo(self):
        try:
            self.entrada_codigo.setText(str(generar_codigo_trabajador()))
        except Exception as error:
            QMessageBox.critical(
                self, "Error", f"No se pudo generar el código.\n\n{error}"
            )

    def cargar_tiendas(self):
        try:
            with SessionLocal() as session:
                tiendas = session.scalars(
                    select(Tienda)
                    .where(Tienda.activa.is_(True))
                    .order_by(Tienda.nombre)
                ).all()
                # Guardar solo valores simples; no conservar objetos detached.
                self.tiendas = [(tienda.id, tienda.nombre) for tienda in tiendas]

            self.combo_tienda.clear()
            for tienda_id, nombre in self.tiendas:
                self.combo_tienda.addItem(nombre, tienda_id)

            if self.combo_tienda.count() and not self.es_edicion:
                self.combo_tienda.setCurrentIndex(0)
        except Exception as error:
            QMessageBox.critical(
                self, "Error", f"No se pudieron cargar las tiendas.\n\n{error}"
            )

    def cargar_trabajador(self):
        try:
            trabajador = obtener_trabajador(self.trabajador_id)
            if trabajador is None:
                QMessageBox.critical(self, "Error", "El trabajador no existe.")
                self.reject()
                return

            self.entrada_codigo.setText(str(trabajador.codigo or ""))
            self.entrada_nombre.setText(trabajador.nombre_completo or "")
            self.entrada_dni.setText(str(trabajador.dni or ""))

            if trabajador.sueldo_semanal is not None:
                self.entrada_sueldo.setText(str(trabajador.sueldo_semanal))
            if trabajador.fecha_ingreso:
                self.entrada_fecha.setText(trabajador.fecha_ingreso.isoformat())

            tienda_id = trabajador.tienda_id
            indice = self.combo_tienda.findData(tienda_id)
            if indice >= 0:
                self.combo_tienda.setCurrentIndex(indice)
        except Exception as error:
            QMessageBox.critical(
                self, "Error", f"No se pudo cargar el trabajador.\n\n{error}"
            )
            self.reject()

    def guardar_trabajador(self):
        nombre = self.entrada_nombre.text().strip()
        dni = self.entrada_dni.text().strip()
        sueldo_texto = self.entrada_sueldo.text().strip().replace(",", ".")
        fecha_texto = self.entrada_fecha.text().strip()
        tienda_id = self.combo_tienda.currentData()
        tienda_nombre = self.combo_tienda.currentText().strip()

        if not nombre:
            QMessageBox.warning(self, "Dato requerido", "Ingresa el nombre completo.")
            self.entrada_nombre.setFocus()
            return
        if not dni:
            QMessageBox.warning(self, "Dato requerido", "Ingresa el DNI.")
            self.entrada_dni.setFocus()
            return
        if not dni.isdigit() or len(dni) != 8:
            QMessageBox.warning(
                self, "DNI inválido", "El DNI debe contener exactamente 8 dígitos."
            )
            self.entrada_dni.setFocus()
            return
        if tienda_id is None or not tienda_nombre:
            QMessageBox.warning(self, "Dato requerido", "Selecciona una tienda.")
            self.combo_tienda.setFocus()
            return
        if not sueldo_texto:
            QMessageBox.warning(self, "Dato requerido", "Ingresa el sueldo semanal.")
            self.entrada_sueldo.setFocus()
            return
        try:
            sueldo = Decimal(sueldo_texto)
            if not sueldo.is_finite() or sueldo < 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            QMessageBox.warning(self, "Sueldo inválido", "Ingresa un sueldo válido.")
            self.entrada_sueldo.setFocus()
            return
        try:
            fecha_ingreso = date.fromisoformat(fecha_texto)
        except ValueError:
            QMessageBox.warning(self, "Fecha inválida", "Usa el formato AAAA-MM-DD.")
            self.entrada_fecha.setFocus()
            return

        if self.es_edicion:
            confirmar = QMessageBox.question(
                self,
                "Confirmar cambios",
                "¿Deseas guardar los cambios?\n\n"
                f"Trabajador: {nombre}\nCódigo: {self.entrada_codigo.text()}\n"
                f"Tienda: {tienda_nombre}\nSueldo semanal: S/ {sueldo:.2f}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if confirmar != QMessageBox.StandardButton.Yes:
                return
            try:
                actualizar_trabajador(
                    trabajador_id=self.trabajador_id,
                    nombre_completo=nombre,
                    dni=dni,
                    tienda_id=tienda_id,
                    sueldo_semanal=sueldo,
                    fecha_ingreso=fecha_ingreso,
                )
                QMessageBox.information(
                    self, "Cambios guardados",
                    "Los datos del trabajador fueron actualizados correctamente.",
                )
                if self.al_guardar:
                    self.al_guardar()
                self.accept()
            except ValueError as error:
                QMessageBox.warning(self, "No se pudo actualizar", str(error))
            except Exception as error:
                QMessageBox.critical(
                    self, "Error", f"Ocurrió un error inesperado.\n\n{error}"
                )
            return

        confirmar = QMessageBox.question(
            self,
            "Confirmar registro",
            "¿Deseas registrar este trabajador?\n\n"
            f"Nombre: {nombre}\nDNI: {dni}\nTienda: {tienda_nombre}\n"
            f"Sueldo semanal: S/ {sueldo:.2f}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmar != QMessageBox.StandardButton.Yes:
            return

        try:
            trabajador = crear_trabajador(
                nombre_completo=nombre,
                dni=dni,
                tienda_id=tienda_id,
                sueldo_semanal=sueldo,
                codigo=self.entrada_codigo.text(),
                fecha_ingreso=fecha_ingreso,
            )
            QMessageBox.information(
                self, "Trabajador registrado",
                "Trabajador registrado correctamente.\n\n"
                f"Código: {trabajador.codigo}\nNombre: {trabajador.nombre_completo}",
            )
            if self.al_guardar:
                self.al_guardar()
            self.accept()
        except ValueError as error:
            QMessageBox.warning(self, "No se pudo registrar", str(error))
        except Exception as error:
            QMessageBox.critical(
                self, "Error", f"Ocurrió un error inesperado.\n\n{error}"
            )

    def foto_proximamente(self):
        QMessageBox.information(
            self, "Foto del trabajador",
            "La carga de fotos estará disponible en una próxima versión.",
        )


if __name__ == "__main__":
    app = QApplication([])
    formulario = TrabajadorForm()
    formulario.show()
    app.exec()
