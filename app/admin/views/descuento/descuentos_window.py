from app.core import tiempo
import sys
from datetime import date
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QGridLayout,
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
)

from app.admin.services.descuento_service import (
    listar_descuentos,
)
from app.admin.views.descuento.descuento_form import (
    DescuentoForm,
)
from app.core.permisos import (
    puede_registrar_descuentos,
)
from app.core.session import sesion_actual


class DescuentosWindow(QWidget):
    """
    Ventana principal del módulo de Descuentos.

    Presenta descuentos reales de PostgreSQL, filtros locales, resumen
    y apertura del formulario en el mismo proceso/sesión.
    """

    def __init__(self, parent=None):
        if not puede_registrar_descuentos():
            raise PermissionError(
                "No tienes permisos para consultar y gestionar descuentos."
            )

        super().__init__(parent)

        self.setWindowTitle("LLACE CONTROL BETA - Descuentos")
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.setMinimumSize(1180, 700)
        self.resize(1380, 780)

        self.descuentos = []
        self.formulario_descuento = None
        self.filtros_aplicados = False

        self.crear_interfaz()
        self.cargar_descuentos()

    # ==========================================================
    # INTERFAZ
    # ==========================================================

    def crear_interfaz(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #101216;
                color: #E8EAED;
                font-family: "Segoe UI";
            }

            QFrame#contenedor_principal {
                background-color: #101216;
            }

            QFrame#cabecera {
                background-color: #101216;
            }

            QLabel#titulo {
                color: #F5F5F5;
                font-size: 26px;
                font-weight: 700;
            }

            QLabel#subtitulo {
                color: #8D939D;
                font-size: 12px;
            }

            QLabel#usuario {
                color: #C9CDD3;
                font-size: 11px;
            }

            QFrame#filtros,
            QFrame#tabla_frame,
            QFrame#registro_frame,
            QFrame#tarjeta {
                background-color: #181B21;
                border: 1px solid #282D35;
                border-radius: 10px;
            }

            QLabel#seccion {
                color: #F5F5F5;
                font-size: 13px;
                font-weight: 700;
            }

            QLabel#etiqueta {
                color: #9BA1AA;
                font-size: 10px;
                font-weight: 600;
            }

            QLineEdit,
            QComboBox,
            QDateEdit {
                background-color: #111419;
                color: #E8EAED;
                border: 1px solid #303640;
                border-radius: 6px;
                padding: 8px 10px;
                min-height: 18px;
                font-size: 11px;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QDateEdit:focus {
                border: 1px solid #F4C542;
            }

            QComboBox QAbstractItemView {
                background-color: #181B21;
                color: #E8EAED;
                selection-background-color: #F4C542;
                selection-color: #111419;
            }

            QPushButton {
                border-radius: 6px;
                padding: 9px 14px;
                font-size: 10px;
                font-weight: 700;
            }

            QPushButton#buscar {
                background-color: #F4C542;
                color: #111419;
                border: none;
            }

            QPushButton#buscar:hover {
                background-color: #FFD75A;
            }

            QPushButton#limpiar {
                background-color: #252A32;
                color: #D5D8DD;
                border: 1px solid #363C46;
            }

            QPushButton#limpiar:hover {
                background-color: #303641;
            }

            QPushButton#nuevo {
                background-color: #F4C542;
                color: #111419;
                border: none;
                padding: 10px 16px;
            }

            QPushButton#nuevo:hover {
                background-color: #FFD75A;
            }

            QPushButton#actualizar {
                background-color: #252A32;
                color: #E8EAED;
                border: 1px solid #363C46;
            }

            QTableWidget {
                background-color: #111419;
                alternate-background-color: #15181D;
                border: none;
                gridline-color: #242932;
                color: #E8EAED;
                font-size: 10px;
                selection-background-color: #3A3216;
                selection-color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: #242932;
                color: #F4C542;
                border: none;
                border-bottom: 1px solid #363C46;
                padding: 9px 6px;
                font-size: 10px;
                font-weight: 700;
            }

            QScrollBar:vertical {
                background: #111419;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background: #3A404A;
                border-radius: 5px;
                min-height: 25px;
            }

            QLabel#valor_tarjeta {
                color: #F5F5F5;
                font-size: 19px;
                font-weight: 700;
            }

            QLabel#detalle_tarjeta {
                color: #8D939D;
                font-size: 10px;
            }

            QLabel#tipo_falta {
                background-color: #4A1F23;
                color: #FF777F;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: 700;
            }

            QLabel#tipo_tardanza {
                background-color: #4A3B14;
                color: #F4C542;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: 700;
            }

            QFrame#panel_registro {
                background-color: #181B21;
                border: 1px solid #3A3216;
                border-radius: 10px;
            }

            QLabel#panel_titulo {
                color: #F4C542;
                font-size: 14px;
                font-weight: 700;
            }

            QLabel#panel_texto {
                color: #8D939D;
                font-size: 11px;
            }
            """
        )

        principal = QVBoxLayout(self)
        principal.setContentsMargins(24, 20, 24, 20)
        principal.setSpacing(14)

        # ------------------------------------------------------
        # CABECERA
        # ------------------------------------------------------

        cabecera = QFrame()
        cabecera.setObjectName("cabecera")

        cabecera_layout = QHBoxLayout(cabecera)
        cabecera_layout.setContentsMargins(0, 0, 0, 0)

        textos = QVBoxLayout()
        textos.setSpacing(2)

        titulo = QLabel("Descuentos")
        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Registra y gestiona los descuentos por faltas y tardanzas."
        )
        subtitulo.setObjectName("subtitulo")

        textos.addWidget(titulo)
        textos.addWidget(subtitulo)

        cabecera_layout.addLayout(textos)
        cabecera_layout.addStretch()

        usuario = sesion_actual.usuario

        if usuario is not None:
            texto_usuario = f"{usuario.nombre}  ·  {usuario.rol}"
        else:
            texto_usuario = "Sin sesión"

        etiqueta_usuario = QLabel(texto_usuario)
        etiqueta_usuario.setObjectName("usuario")
        etiqueta_usuario.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        cabecera_layout.addWidget(etiqueta_usuario)

        principal.addWidget(cabecera)

        # ------------------------------------------------------
        # FILTROS
        # ------------------------------------------------------

        filtros = QFrame()
        filtros.setObjectName("filtros")

        filtros_layout = QGridLayout(filtros)
        filtros_layout.setContentsMargins(14, 12, 14, 12)
        filtros_layout.setHorizontalSpacing(10)
        filtros_layout.setVerticalSpacing(6)

        titulo_filtros = QLabel("Filtros de búsqueda")
        titulo_filtros.setObjectName("seccion")

        filtros_layout.addWidget(titulo_filtros, 0, 0, 1, 6)

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDate(tiempo.hoy().replace(day=1))
        self.fecha_inicio.setDisplayFormat("dd/MM/yyyy")

        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDate(tiempo.hoy())
        self.fecha_fin.setDisplayFormat("dd/MM/yyyy")

        self.filtro_trabajador = QLineEdit()
        self.filtro_trabajador.setPlaceholderText(
            "Nombre o código"
        )

        self.filtro_tienda = QLineEdit()
        self.filtro_tienda.setPlaceholderText(
            "Tienda"
        )

        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItems(
            ["Todos", "FALTA", "TARDANZA"]
        )

        filtros_layout.addWidget(
            self.crear_etiqueta("Fecha inicio"), 1, 0
        )
        filtros_layout.addWidget(self.fecha_inicio, 2, 0)

        filtros_layout.addWidget(
            self.crear_etiqueta("Fecha fin"), 1, 1
        )
        filtros_layout.addWidget(self.fecha_fin, 2, 1)

        filtros_layout.addWidget(
            self.crear_etiqueta("Trabajador"), 1, 2
        )
        filtros_layout.addWidget(self.filtro_trabajador, 2, 2)

        filtros_layout.addWidget(
            self.crear_etiqueta("Tienda"), 1, 3
        )
        filtros_layout.addWidget(self.filtro_tienda, 2, 3)

        filtros_layout.addWidget(
            self.crear_etiqueta("Tipo"), 1, 4
        )
        filtros_layout.addWidget(self.filtro_tipo, 2, 4)

        botones_filtro = QHBoxLayout()
        botones_filtro.setSpacing(6)

        boton_buscar = QPushButton("Buscar")
        boton_buscar.setObjectName("buscar")
        boton_buscar.clicked.connect(self.aplicar_filtros)

        boton_limpiar = QPushButton("Limpiar")
        boton_limpiar.setObjectName("limpiar")
        boton_limpiar.clicked.connect(self.limpiar_filtros)

        botones_filtro.addWidget(boton_buscar)
        botones_filtro.addWidget(boton_limpiar)

        filtros_layout.addLayout(
            botones_filtro, 2, 5
        )

        principal.addWidget(filtros)

        # ------------------------------------------------------
        # CONTENIDO CENTRAL
        # ------------------------------------------------------

        contenido = QHBoxLayout()
        contenido.setSpacing(12)

        # TABLA
        tabla_frame = QFrame()
        tabla_frame.setObjectName("tabla_frame")

        tabla_layout = QVBoxLayout(tabla_frame)
        tabla_layout.setContentsMargins(12, 12, 12, 12)
        tabla_layout.setSpacing(8)

        encabezado_tabla = QHBoxLayout()

        titulo_tabla = QLabel("Descuentos registrados")
        titulo_tabla.setObjectName("seccion")

        encabezado_tabla.addWidget(titulo_tabla)
        encabezado_tabla.addStretch()

        boton_actualizar = QPushButton("Actualizar")
        boton_actualizar.setObjectName("actualizar")
        boton_actualizar.clicked.connect(self.cargar_descuentos)

        encabezado_tabla.addWidget(boton_actualizar)

        tabla_layout.addLayout(encabezado_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels(
            [
                "#",
                "Fecha incidencia",
                "Fecha registro",
                "Trabajador",
                "Tienda",
                "Tipo",
                "Monto",
                "Observación",
                "Usuario ID",
            ]
        )

        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.tabla.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.tabla.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        tabla_layout.addWidget(self.tabla)

        contenido.addWidget(tabla_frame, 7)

        # PANEL DERECHO
        panel = QFrame()
        panel.setObjectName("panel_registro")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.setSpacing(12)

        titulo_panel = QLabel("Registrar descuento")
        titulo_panel.setObjectName("panel_titulo")

        panel_layout.addWidget(titulo_panel)

        texto_panel = QLabel(
            "El registro de faltas y tardanzas se realizará "
            "desde el formulario del módulo."
        )
        texto_panel.setObjectName("panel_texto")
        texto_panel.setWordWrap(True)

        panel_layout.addWidget(texto_panel)

        panel_layout.addSpacing(8)

        boton_nuevo = QPushButton("＋  Nuevo descuento")
        boton_nuevo.setObjectName("nuevo")
        boton_nuevo.clicked.connect(self.nuevo_descuento)

        panel_layout.addWidget(boton_nuevo)

        panel_layout.addSpacing(8)

        panel_layout.addWidget(
            self.crear_etiqueta("Trabajador")
        )

        trabajador_preview = QLineEdit()
        trabajador_preview.setPlaceholderText(
            "Se seleccionará en el formulario"
        )
        trabajador_preview.setReadOnly(True)
        panel_layout.addWidget(trabajador_preview)

        panel_layout.addWidget(
            self.crear_etiqueta("Tipo")
        )

        tipo_preview = QComboBox()
        tipo_preview.addItems(
            ["FALTA", "TARDANZA"]
        )
        tipo_preview.setEnabled(False)
        panel_layout.addWidget(tipo_preview)

        panel_layout.addWidget(
            self.crear_etiqueta("Monto")
        )

        monto_preview = QLineEdit()
        monto_preview.setPlaceholderText(
            "Calculado o ingresado manualmente"
        )
        monto_preview.setReadOnly(True)
        panel_layout.addWidget(monto_preview)

        panel_layout.addSpacing(8)

        aviso = QLabel(
            "FALTA: sueldo semanal ÷ 6.\n"
            "TARDANZA: monto definido por ADMIN/SUPERADMIN."
        )
        aviso.setObjectName("panel_texto")
        aviso.setWordWrap(True)

        panel_layout.addWidget(aviso)
        panel_layout.addStretch()

        contenido.addWidget(panel, 3)

        principal.addLayout(contenido, 1)

        # ------------------------------------------------------
        # TARJETAS DE RESUMEN
        # ------------------------------------------------------

        resumen = QHBoxLayout()
        resumen.setSpacing(12)

        self.tarjeta_total, self.valor_total = (
            self.crear_tarjeta(
                "Total de descuentos",
                "S/ 0.00",
            )
        )

        self.tarjeta_faltas, self.valor_faltas = (
            self.crear_tarjeta(
                "Faltas registradas",
                "0",
            )
        )

        self.tarjeta_tardanzas, self.valor_tardanzas = (
            self.crear_tarjeta(
                "Tardanzas registradas",
                "0",
            )
        )

        resumen.addWidget(self.tarjeta_total)
        resumen.addWidget(self.tarjeta_faltas)
        resumen.addWidget(self.tarjeta_tardanzas)

        principal.addLayout(resumen)

    # ==========================================================
    # ELEMENTOS AUXILIARES
    # ==========================================================

    def crear_etiqueta(self, texto):
        etiqueta = QLabel(texto)
        etiqueta.setObjectName("etiqueta")
        return etiqueta

    def crear_tarjeta(self, titulo, valor):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(3)

        titulo_label = QLabel(titulo)
        titulo_label.setObjectName("detalle_tarjeta")

        valor_label = QLabel(valor)
        valor_label.setObjectName("valor_tarjeta")

        layout.addWidget(titulo_label)
        layout.addWidget(valor_label)

        return tarjeta, valor_label

    # ==========================================================
    # DATOS
    # ==========================================================

    def cargar_descuentos(self):
        """Recarga los datos; si falla, conserva la última vista válida."""
        try:
            nuevos_descuentos = listar_descuentos()
            self.descuentos = list(nuevos_descuentos or [])

            if self.filtros_aplicados:
                self.aplicar_filtros(mostrar_error=False)
            else:
                self.mostrar_descuentos(self.descuentos)
                self.actualizar_resumen(self.descuentos)

        except PermissionError as error:
            QMessageBox.warning(self, "Permisos", str(error))
        except Exception as error:
            # No vaciar la tabla: un error de conexión no significa cero descuentos.
            QMessageBox.critical(
                self,
                "Error de conexión",
                "No se pudieron actualizar los descuentos.\n"
                "Se conserva la información que ya estaba cargada.\n\n"
                f"Detalle: {error}",
            )
            print("ERROR AL CARGAR DESCUENTOS:", repr(error))

    @staticmethod
    def obtener_fecha_incidencia(descuento):
        """Fecha real de la falta/tardanza; usa fecha de registro si no hay asistencia."""
        asistencia = getattr(descuento, "asistencia", None)
        fecha = getattr(asistencia, "fecha", None) if asistencia else None
        return fecha or getattr(descuento, "fecha", None)

    @staticmethod
    def obtener_tienda_trabajador(trabajador):
        """Usa la relación cargada, evitando una consulta SQL por fila."""
        if trabajador is None:
            return None
        return getattr(trabajador, "tienda", None)

    def mostrar_descuentos(self, descuentos):
        """Pinta registros de forma segura y sin consultas individuales por fila."""
        self.tabla.setUpdatesEnabled(False)
        try:
            self.tabla.setRowCount(0)
            for descuento in descuentos:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)

                trabajador = getattr(descuento, "trabajador", None)
                asistencia = getattr(descuento, "asistencia", None)
                tienda = self.obtener_tienda_trabajador(trabajador)

                nombre = str(getattr(trabajador, "nombre_completo", "") or "—")
                codigo = str(getattr(trabajador, "codigo", "") or "")
                nombre_mostrar = f"{codigo} - {nombre}" if codigo else nombre
                tienda_nombre = str(getattr(tienda, "nombre", "—") or "—")
                tienda_codigo = str(getattr(tienda, "codigo", "") or "")

                fecha_incidencia = self.obtener_fecha_incidencia(descuento)
                fecha_registro = getattr(descuento, "fecha", None)
                fecha_incidencia_txt = fecha_incidencia.strftime("%d/%m/%Y") if fecha_incidencia else "—"
                fecha_registro_txt = fecha_registro.strftime("%d/%m/%Y") if fecha_registro else "—"

                tipo = str(getattr(descuento, "tipo", "") or "—").upper()
                try:
                    monto = Decimal(str(getattr(descuento, "monto", 0) or 0))
                    monto_txt = f"S/ {monto:,.2f}"
                except Exception:
                    monto_txt = "S/ —"

                observacion = str(getattr(descuento, "observacion", "") or "—")
                usuario_id = getattr(descuento, "registrado_por", None)
                usuario_txt = str(usuario_id) if usuario_id is not None else "—"
                valores = [
                    str(getattr(descuento, "id", "")),
                    fecha_incidencia_txt,
                    fecha_registro_txt,
                    nombre_mostrar,
                    tienda_nombre,
                    tipo,
                    monto_txt,
                    observacion,
                    usuario_txt,
                ]

                for columna, valor in enumerate(valores):
                    item = QTableWidgetItem(valor)
                    item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignCenter if columna in (0, 1, 2, 5, 6, 8) else Qt.AlignLeft))
                    if columna == 4 and tienda_codigo:
                        item.setToolTip(f"Código de tienda: {tienda_codigo}")
                    if columna == 7:
                        item.setToolTip(observacion)
                    if columna == 5:
                        item.setData(Qt.UserRole, tipo)
                    self.tabla.setItem(fila, columna, item)
        finally:
            self.tabla.setUpdatesEnabled(True)

    def actualizar_resumen(self, descuentos):
        total = Decimal("0.00")
        faltas = 0
        tardanzas = 0

        for descuento in descuentos:
            monto = getattr(
                descuento,
                "monto",
                Decimal("0.00"),
            )

            try:
                importe = Decimal(str(monto or 0))
                if importe.is_finite():
                    total += importe
            except Exception:
                # Se ignora el importe inválido, pero se sigue contando el tipo.
                importe = Decimal("0.00")

            tipo = str(
                getattr(
                    descuento,
                    "tipo",
                    "",
                )
            ).upper()

            if tipo == "FALTA":
                faltas += 1

            elif tipo == "TARDANZA":
                tardanzas += 1

        self.valor_total.setText(
            f"S/ {total:.2f}"
        )
        self.valor_faltas.setText(
            str(faltas)
        )
        self.valor_tardanzas.setText(
            str(tardanzas)
        )

    # ==========================================================
    # FILTROS
    # ==========================================================

    @staticmethod
    def _normalizar_busqueda(valor):
        return " ".join(str(valor or "").casefold().split())

    def aplicar_filtros(self, _checked=False, mostrar_error=True):
        fecha_inicio = self.fecha_inicio.date().toPython()
        fecha_fin = self.fecha_fin.date().toPython()

        if fecha_inicio > fecha_fin:
            if mostrar_error:
                QMessageBox.warning(
                    self, "Fechas inválidas",
                    "La fecha inicial no puede ser posterior a la fecha final.",
                )
            return

        trabajador_texto = self._normalizar_busqueda(self.filtro_trabajador.text())
        tienda_texto = self._normalizar_busqueda(self.filtro_tienda.text())
        tipo = self.filtro_tipo.currentText().strip().upper()
        filtrados = []

        for descuento in self.descuentos:
            fecha = self.obtener_fecha_incidencia(descuento)
            if fecha is None or not (fecha_inicio <= fecha <= fecha_fin):
                continue

            tipo_descuento = str(getattr(descuento, "tipo", "") or "").upper()
            if tipo != "TODOS" and tipo_descuento != tipo:
                continue

            trabajador = getattr(descuento, "trabajador", None)
            nombre = self._normalizar_busqueda(getattr(trabajador, "nombre_completo", ""))
            codigo = self._normalizar_busqueda(getattr(trabajador, "codigo", ""))
            if trabajador_texto and trabajador_texto not in nombre and trabajador_texto not in codigo:
                continue

            tienda = self.obtener_tienda_trabajador(trabajador)
            nombre_tienda = self._normalizar_busqueda(getattr(tienda, "nombre", ""))
            codigo_tienda = self._normalizar_busqueda(getattr(tienda, "codigo", ""))
            tienda_id = str(getattr(trabajador, "tienda_id", "") or "")
            if tienda_texto and all(tienda_texto not in dato for dato in (nombre_tienda, codigo_tienda, tienda_id)):
                continue

            filtrados.append(descuento)

        filtrados.sort(
            key=lambda d: (self.obtener_fecha_incidencia(d) or date.min, getattr(d, "id", 0) or 0),
            reverse=True,
        )
        self.filtros_aplicados = True
        self.mostrar_descuentos(filtrados)
        self.actualizar_resumen(filtrados)

    def limpiar_filtros(self):
        self.fecha_inicio.setDate(
            tiempo.hoy().replace(day=1)
        )
        self.fecha_fin.setDate(
            tiempo.hoy()
        )
        self.filtro_trabajador.clear()
        self.filtro_tienda.clear()
        self.filtro_tipo.setCurrentIndex(0)
        self.filtros_aplicados = False

        self.mostrar_descuentos(
            self.descuentos
        )
        self.actualizar_resumen(
            self.descuentos
        )

    # ==========================================================
    # NUEVO DESCUENTO
    # ==========================================================

    def nuevo_descuento(self):
        try:
            formulario = DescuentoForm(self)

            resultado = formulario.exec()

            if resultado == QDialog.Accepted:
                self.cargar_descuentos()

        except PermissionError as error:
            QMessageBox.warning(
                self,
                "Permisos",
                str(error),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo abrir el formulario de descuento.\n\n"
                f"{error}",
            )

            print(
                "ERROR AL ABRIR FORMULARIO DE DESCUENTO:"
            )
            print(error)


# ==========================================================
# EJECUCIÓN DIRECTA
# ==========================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        ventana = DescuentosWindow()
        ventana.showMaximized()
        sys.exit(app.exec())

    except PermissionError as error:
        QMessageBox.critical(
            None,
            "Permisos",
            str(error),
        )
        sys.exit(1)
