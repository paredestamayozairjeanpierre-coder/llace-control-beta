
from datetime import date
from decimal import Decimal

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLabel,
    QPushButton,
    QComboBox,
    QDateEdit,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QFileDialog,
)

from app.admin.services.reporte_service import (
    obtener_liquidacion_semanal,
)
from app.admin.services.tienda_service import (
    listar_tiendas,
)
from app.core.permisos import (
    puede_ver_reportes,
)
from app.core.session import sesion_actual


class ReportesWindow(QWidget):
    """
    Reportes y liquidación semanal estimada.

    - Consulta PostgreSQL mediante reporte_service.
    - Respeta la sesión ADMIN/SUPERADMIN activa.
    - Filtra por semana, tienda y trabajador.
    - Muestra totales y detalle por trabajador.
    - Exporta el resultado visible a CSV compatible con Excel.
    - No registra pagos ni modifica datos.
    """

    def __init__(self, parent=None):
        if not puede_ver_reportes():
            raise PermissionError(
                "No tienes permisos para consultar los reportes."
            )

        super().__init__(parent)

        self.setWindowTitle(
            "LLACE CONTROL BETA - Reportes"
        )

        self.setWindowFlags(
            Qt.Window
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )

        self.setAttribute(
            Qt.WA_DeleteOnClose,
            True,
        )

        self.setMinimumSize(1150, 680)
        self.resize(1450, 820)

        self.reporte_actual = None
        self.filas_originales = []
        self.tiendas = []

        self.crear_interfaz()
        self.cargar_tiendas()
        self.cargar_reporte()

    # ======================================================
    # ESTILO
    # ======================================================

    def aplicar_estilos(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #101216;
                color: #E8EAED;
                font-family: "Segoe UI";
                font-size: 11px;
            }

            QFrame#cabecera {
                background-color: #101216;
            }

            QLabel#titulo {
                color: #F5F5F5;
                font-size: 27px;
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
            QFrame#tarjeta,
            QFrame#nota {
                background-color: #181B21;
                border: 1px solid #282D35;
                border-radius: 9px;
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

            QLabel#valor_tarjeta {
                color: #F5F5F5;
                font-size: 19px;
                font-weight: 700;
            }

            QLabel#detalle_tarjeta {
                color: #8D939D;
                font-size: 10px;
            }

            QLabel#amarillo {
                color: #F4C542;
                font-weight: 700;
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

            QPushButton#secundario {
                background-color: #252A32;
                color: #E8EAED;
                border: 1px solid #363C46;
            }

            QPushButton#secundario:hover {
                background-color: #303641;
            }

            QPushButton#exportar {
                background-color: #F4C542;
                color: #111419;
                border: none;
            }

            QPushButton#exportar:hover {
                background-color: #FFD75A;
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
                padding: 9px 5px;
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

            QScrollBar:horizontal {
                background: #111419;
                height: 10px;
            }

            QScrollBar::handle:horizontal {
                background: #3A404A;
                border-radius: 5px;
                min-width: 25px;
            }
            """
        )

    # ======================================================
    # INTERFAZ
    # ======================================================

    def crear_interfaz(self):
        self.aplicar_estilos()

        principal = QVBoxLayout(self)
        principal.setContentsMargins(22, 18, 22, 18)
        principal.setSpacing(12)

        # --------------------------------------------------
        # CABECERA
        # --------------------------------------------------

        cabecera = QFrame()
        cabecera.setObjectName("cabecera")

        layout_cabecera = QHBoxLayout(cabecera)
        layout_cabecera.setContentsMargins(0, 0, 0, 0)

        bloque_titulo = QVBoxLayout()
        bloque_titulo.setSpacing(3)

        titulo = QLabel("REPORTES")
        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Liquidación semanal estimada del personal"
        )
        subtitulo.setObjectName("subtitulo")

        bloque_titulo.addWidget(titulo)
        bloque_titulo.addWidget(subtitulo)

        layout_cabecera.addLayout(bloque_titulo)
        layout_cabecera.addStretch()

        usuario = sesion_actual.usuario
        texto_usuario = (
            f"{usuario.nombre}  ·  {usuario.rol}"
            if usuario is not None
            else "Sin sesión"
        )

        etiqueta_usuario = QLabel(texto_usuario)
        etiqueta_usuario.setObjectName("usuario")
        etiqueta_usuario.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        layout_cabecera.addWidget(etiqueta_usuario)

        principal.addWidget(cabecera)

        # --------------------------------------------------
        # FILTROS
        # --------------------------------------------------

        filtros = QFrame()
        filtros.setObjectName("filtros")

        layout_filtros = QGridLayout(filtros)
        layout_filtros.setContentsMargins(14, 12, 14, 12)
        layout_filtros.setHorizontalSpacing(10)
        layout_filtros.setVerticalSpacing(5)

        titulo_filtros = QLabel("Filtros del reporte")
        titulo_filtros.setObjectName("seccion")
        layout_filtros.addWidget(
            titulo_filtros, 0, 0, 1, 5
        )

        self.fecha_referencia = QDateEdit()
        self.fecha_referencia.setCalendarPopup(True)
        self.fecha_referencia.setDisplayFormat("dd/MM/yyyy")
        self.fecha_referencia.setDate(
            QDate.currentDate()
        )

        self.filtro_tienda = QComboBox()
        self.filtro_tienda.addItem(
            "Todas las tiendas",
            None,
        )

        self.filtro_trabajador = QComboBox()
        self.filtro_trabajador.addItem(
            "Todos los trabajadores",
            None,
        )

        self.buscar_texto = QLineEdit()
        self.buscar_texto.setPlaceholderText(
            "Buscar por nombre o código"
        )

        layout_filtros.addWidget(
            self.crear_etiqueta("Fecha de la semana"),
            1, 0,
        )
        layout_filtros.addWidget(
            self.fecha_referencia, 2, 0
        )

        layout_filtros.addWidget(
            self.crear_etiqueta("Tienda"),
            1, 1,
        )
        layout_filtros.addWidget(
            self.filtro_tienda, 2, 1
        )

        layout_filtros.addWidget(
            self.crear_etiqueta("Trabajador"),
            1, 2,
        )
        layout_filtros.addWidget(
            self.filtro_trabajador, 2, 2
        )

        layout_filtros.addWidget(
            self.crear_etiqueta("Búsqueda"),
            1, 3,
        )
        layout_filtros.addWidget(
            self.buscar_texto, 2, 3
        )

        botones = QHBoxLayout()
        botones.setSpacing(6)

        self.btn_buscar = QPushButton("BUSCAR")
        self.btn_buscar.setObjectName("buscar")
        self.btn_buscar.clicked.connect(
            self.cargar_reporte
        )

        self.btn_limpiar = QPushButton("LIMPIAR")
        self.btn_limpiar.setObjectName("secundario")
        self.btn_limpiar.clicked.connect(
            self.limpiar_filtros
        )

        botones.addWidget(self.btn_buscar)
        botones.addWidget(self.btn_limpiar)

        layout_filtros.addLayout(
            botones, 2, 4
        )

        principal.addWidget(filtros)

        # --------------------------------------------------
        # PERIODO
        # --------------------------------------------------

        self.etiqueta_periodo = QLabel(
            "Periodo: pendiente de consulta"
        )
        self.etiqueta_periodo.setObjectName("amarillo")

        principal.addWidget(self.etiqueta_periodo)

        # --------------------------------------------------
        # TARJETAS RESUMEN
        # --------------------------------------------------

        resumen = QGridLayout()
        resumen.setHorizontalSpacing(10)
        resumen.setVerticalSpacing(10)

        self.tarjeta_trabajadores, self.valor_trabajadores = (
            self.crear_tarjeta(
                "Trabajadores",
                "0",
            )
        )

        self.tarjeta_sueldo, self.valor_sueldo = (
            self.crear_tarjeta(
                "Sueldos proporcionales",
                "S/ 0.00",
            )
        )

        self.tarjeta_descuentos, self.valor_descuentos = (
            self.crear_tarjeta(
                "Total descuentos",
                "S/ 0.00",
            )
        )

        self.tarjeta_neto, self.valor_neto = (
            self.crear_tarjeta(
                "Neto estimado",
                "S/ 0.00",
            )
        )

        self.tarjeta_revision, self.valor_revision = (
            self.crear_tarjeta(
                "Requieren revisión",
                "0",
            )
        )

        resumen.addWidget(
            self.tarjeta_trabajadores, 0, 0
        )
        resumen.addWidget(
            self.tarjeta_sueldo, 0, 1
        )
        resumen.addWidget(
            self.tarjeta_descuentos, 0, 2
        )
        resumen.addWidget(
            self.tarjeta_neto, 0, 3
        )
        resumen.addWidget(
            self.tarjeta_revision, 0, 4
        )

        principal.addLayout(resumen)

        # --------------------------------------------------
        # TABLA
        # --------------------------------------------------

        tabla_frame = QFrame()
        tabla_frame.setObjectName("tabla_frame")

        layout_tabla = QVBoxLayout(tabla_frame)
        layout_tabla.setContentsMargins(12, 12, 12, 12)
        layout_tabla.setSpacing(8)

        encabezado_tabla = QHBoxLayout()

        titulo_tabla = QLabel(
            "Liquidación por trabajador"
        )
        titulo_tabla.setObjectName("seccion")

        encabezado_tabla.addWidget(titulo_tabla)
        encabezado_tabla.addStretch()

        self.etiqueta_registros = QLabel("0 registros")
        self.etiqueta_registros.setObjectName("subtitulo")

        encabezado_tabla.addWidget(
            self.etiqueta_registros
        )

        self.btn_actualizar = QPushButton("ACTUALIZAR")
        self.btn_actualizar.setObjectName("secundario")
        self.btn_actualizar.clicked.connect(
            self.cargar_reporte
        )

        encabezado_tabla.addWidget(
            self.btn_actualizar
        )

        self.btn_exportar = QPushButton(
            "EXPORTAR EXCEL"
        )
        self.btn_exportar.setObjectName("exportar")
        self.btn_exportar.clicked.connect(
            self.exportar_excel
        )

        encabezado_tabla.addWidget(
            self.btn_exportar
        )

        layout_tabla.addLayout(encabezado_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(15)

        self.tabla.setHorizontalHeaderLabels(
            [
                "CÓDIGO",
                "TRABAJADOR",
                "TIENDA",
                "ESTADO",
                "PUNTUAL",
                "TARDANZAS",
                "FALTAS",
                "JUSTIF.",
                "DÍAS",
                "SUELDO SEMANAL",
                "SUELDO PROPORCIONAL",
                "DESC. FALTAS",
                "DESC. TARDANZAS",
                "TOTAL DESC.",
                "NETO ESTIMADO",
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
        header.setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        header.setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )

        self.tabla.setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )

        layout_tabla.addWidget(self.tabla, 1)

        principal.addWidget(tabla_frame, 1)

        # --------------------------------------------------
        # NOTA
        # --------------------------------------------------

        nota = QFrame()
        nota.setObjectName("nota")

        layout_nota = QHBoxLayout(nota)
        layout_nota.setContentsMargins(12, 8, 12, 8)

        texto_nota = QLabel(
            "Importante: este reporte es una estimación. "
            "No registra pagos ni reemplaza la revisión "
            "administrativa antes de liquidar."
        )
        texto_nota.setObjectName("subtitulo")
        texto_nota.setWordWrap(True)

        layout_nota.addWidget(texto_nota)

        principal.addWidget(nota)

    # ======================================================
    # COMPONENTES
    # ======================================================

    def crear_etiqueta(self, texto):
        etiqueta = QLabel(texto)
        etiqueta.setObjectName("etiqueta")
        return etiqueta

    def crear_tarjeta(self, titulo, valor):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("detalle_tarjeta")

        valor_label = QLabel(valor)
        valor_label.setObjectName("valor_tarjeta")

        layout.addWidget(etiqueta)
        layout.addWidget(valor_label)

        return tarjeta, valor_label

    @staticmethod
    def formato_dinero(valor):
        try:
            monto = Decimal(str(valor or 0))
        except Exception:
            monto = Decimal("0")

        return f"S/ {monto:,.2f}"

    @staticmethod
    def crear_item(valor, alineacion=None):
        item = QTableWidgetItem(str(valor))

        if alineacion is not None:
            item.setTextAlignment(alineacion)

        return item

    # ======================================================
    # CARGA DE TIENDAS
    # ======================================================

    def cargar_tiendas(self):
        try:
            self.tiendas = list(
                listar_tiendas() or []
            )

            self.filtro_tienda.blockSignals(True)
            self.filtro_tienda.clear()
            self.filtro_tienda.addItem(
                "Todas las tiendas",
                None,
            )

            for tienda in self.tiendas:
                self.filtro_tienda.addItem(
                    tienda.nombre,
                    tienda.id,
                )

            self.filtro_tienda.blockSignals(False)

        except Exception as error:
            self.filtro_tienda.blockSignals(False)

            QMessageBox.warning(
                self,
                "Tiendas",
                "No se pudieron cargar las tiendas.\n\n"
                f"{error}",
            )

            print(
                "ERROR AL CARGAR TIENDAS:",
                repr(error),
            )

    # ======================================================
    # CONSULTAR REPORTE
    # ======================================================

    def cargar_reporte(self):
        if not puede_ver_reportes():
            QMessageBox.warning(
                self,
                "Permisos",
                "Tu sesión no tiene permiso para consultar reportes.",
            )
            return

        fecha = self.fecha_referencia.date().toPython()
        tienda_id = self.filtro_tienda.currentData()

        self.btn_buscar.setEnabled(False)
        self.btn_actualizar.setEnabled(False)

        try:
            resultado = obtener_liquidacion_semanal(
                fecha_referencia=fecha,
                tienda_id=tienda_id,
            )

            if not isinstance(resultado, dict):
                raise ValueError(
                    "El servicio devolvió un resultado inesperado."
                )

            self.reporte_actual = resultado
            self.filas_originales = list(
                resultado.get("trabajadores", [])
            )

            inicio = resultado.get("fecha_inicio")
            fin = resultado.get("fecha_fin")

            self.etiqueta_periodo.setText(
                f"Periodo: {inicio:%d/%m/%Y} "
                f"al {fin:%d/%m/%Y}"
            )

            self.actualizar_filtro_trabajadores()
            self.aplicar_filtros_locales()

        except PermissionError as error:
            QMessageBox.warning(
                self,
                "Permisos",
                str(error),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error al consultar",
                "No se pudo generar el reporte.\n\n"
                "Los datos anteriores se mantienen en pantalla "
                "si ya había un reporte cargado.\n\n"
                f"Detalle: {error}",
            )

            print(
                "ERROR AL CARGAR REPORTE:",
                repr(error),
            )

        finally:
            self.btn_buscar.setEnabled(True)
            self.btn_actualizar.setEnabled(True)

    # ======================================================
    # FILTRO DE TRABAJADORES
    # ======================================================

    def actualizar_filtro_trabajadores(self):
        trabajador_anterior = (
            self.filtro_trabajador.currentData()
        )

        self.filtro_trabajador.blockSignals(True)
        self.filtro_trabajador.clear()

        self.filtro_trabajador.addItem(
            "Todos los trabajadores",
            None,
        )

        trabajadores = sorted(
            self.filas_originales,
            key=lambda fila: fila.get("nombre", "").casefold(),
        )

        for trabajador in trabajadores:
            etiqueta = (
                f'{trabajador.get("codigo", "")} - '
                f'{trabajador.get("nombre", "")}'
            )

            self.filtro_trabajador.addItem(
                etiqueta,
                trabajador.get("trabajador_id"),
            )

        indice = self.filtro_trabajador.findData(
            trabajador_anterior
        )

        if indice >= 0:
            self.filtro_trabajador.setCurrentIndex(indice)

        self.filtro_trabajador.blockSignals(False)

    # ======================================================
    # APLICAR FILTROS LOCALES
    # ======================================================

    def aplicar_filtros_locales(self):
        trabajador_id = (
            self.filtro_trabajador.currentData()
        )

        texto = self.buscar_texto.text().strip().casefold()

        filas = []

        for fila in self.filas_originales:
            if (
                trabajador_id is not None
                and fila.get("trabajador_id") != trabajador_id
            ):
                continue

            nombre = str(
                fila.get("nombre", "")
            ).casefold()

            codigo = str(
                fila.get("codigo", "")
            ).casefold()

            if texto and texto not in nombre and texto not in codigo:
                continue

            filas.append(fila)

        self.mostrar_filas(filas)
        self.actualizar_resumen(filas)

    # ======================================================
    # MOSTRAR TABLA
    # ======================================================

    def mostrar_filas(self, filas):
        self.tabla.setUpdatesEnabled(False)

        try:
            self.tabla.setRowCount(0)

            for fila in filas:
                indice = self.tabla.rowCount()
                self.tabla.insertRow(indice)

                activo = (
                    "ACTIVO"
                    if fila.get("activo")
                    else "INACTIVO"
                )

                valores = [
                    fila.get("codigo", ""),
                    fila.get("nombre", ""),
                    fila.get("tienda", "Sin tienda"),
                    activo,
                    fila.get("puntuales", 0),
                    fila.get("tardanzas", 0),
                    fila.get("faltas", 0),
                    fila.get("justificados", 0),
                    fila.get("dias_corresponden", 0),
                    self.formato_dinero(
                        fila.get("sueldo_semanal", 0)
                    ),
                    self.formato_dinero(
                        fila.get("sueldo_proporcional", fila.get("sueldo_semanal", 0))
                    ),
                    self.formato_dinero(
                        fila.get("descuento_faltas", 0)
                    ),
                    self.formato_dinero(
                        fila.get("descuento_tardanzas", 0)
                    ),
                    self.formato_dinero(
                        fila.get("total_descuentos", 0)
                    ),
                    self.formato_dinero(
                        fila.get("neto_estimado", 0)
                    ),
                ]

                for columna, valor in enumerate(valores):
                    alineacion = (
                        Qt.AlignCenter
                        if columna in (0, 3, 4, 5, 6, 7, 8)
                        else Qt.AlignVCenter | Qt.AlignLeft
                    )

                    item = self.crear_item(
                        valor,
                        alineacion,
                    )

                    if columna == 8:
                        item.setToolTip(
                            "Días laborables que corresponden en el periodo, de lunes a sábado."
                        )
                    if columna == 10:
                        item.setToolTip(
                            "Sueldo proporcional: sueldo semanal dividido entre 6 y multiplicado por los días que corresponden."
                        )
                    if columna == 14:
                        item.setToolTip(
                            "Monto neto estimado, sujeto a revisión."
                        )

                    if fila.get("requiere_revision") and columna == 14:
                        item.setForeground(
                            Qt.GlobalColor.red
                        )

                    self.tabla.setItem(
                        indice,
                        columna,
                        item,
                    )

            self.etiqueta_registros.setText(
                f"{len(filas)} registros"
            )

        finally:
            self.tabla.setUpdatesEnabled(True)

    # ======================================================
    # RESUMEN
    # ======================================================

    def actualizar_resumen(self, filas):
        cantidad = len(filas)

        sueldo = sum(
            (
                Decimal(str(fila.get("sueldo_proporcional", fila.get("sueldo_semanal", 0))))
                for fila in filas
            ),
            Decimal("0.00"),
        )

        descuentos = sum(
            (
                Decimal(str(fila.get("total_descuentos", 0)))
                for fila in filas
            ),
            Decimal("0.00"),
        )

        neto = sum(
            (
                Decimal(str(fila.get("neto_estimado", 0)))
                for fila in filas
            ),
            Decimal("0.00"),
        )

        revision = sum(
            1
            for fila in filas
            if fila.get("requiere_revision")
        )

        self.valor_trabajadores.setText(
            str(cantidad)
        )

        self.valor_sueldo.setText(
            self.formato_dinero(sueldo)
        )

        self.valor_descuentos.setText(
            self.formato_dinero(descuentos)
        )

        self.valor_neto.setText(
            self.formato_dinero(neto)
        )

        self.valor_revision.setText(
            str(revision)
        )

    # ======================================================
    # LIMPIAR FILTROS
    # ======================================================

    def limpiar_filtros(self):
        self.fecha_referencia.setDate(
            QDate.currentDate()
        )

        self.filtro_tienda.setCurrentIndex(0)
        self.buscar_texto.clear()

        self.cargar_reporte()

    # ======================================================
    # EXPORTAR EXCEL PROFESIONAL
    # ======================================================

    def exportar_excel(self):
        """Exporta el reporte visible a XLSX con formato corporativo LLACE."""
        if self.tabla.rowCount() == 0:
            QMessageBox.information(
                self, "Sin datos", "No hay registros para exportar."
            )
            return

        if not self.reporte_actual:
            QMessageBox.warning(
                self, "Reporte", "Primero debes consultar un reporte."
            )
            return

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
            from openpyxl.utils import get_column_letter
            from openpyxl.worksheet.properties import PageSetupProperties
        except ImportError:
            QMessageBox.critical(
                self,
                "Falta una dependencia",
                "Para exportar a Excel instala openpyxl desde la terminal de VS Code:\n\n"
                "python -m pip install openpyxl",
            )
            return

        inicio = self.reporte_actual["fecha_inicio"]
        fin = self.reporte_actual["fecha_fin"]
        nombre_archivo = f"liquidacion_LLACE_{inicio:%Y%m%d}_{fin:%Y%m%d}.xlsx"
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar liquidación en Excel", nombre_archivo,
            "Libro de Excel (*.xlsx)"
        )
        if not ruta:
            return
        if not ruta.lower().endswith(".xlsx"):
            ruta += ".xlsx"

        # Identidad visual Grupo LLACE: carbón, amarillo y blanco.
        negro = "17191F"
        negro_sec = "242832"
        amarillo = "F5C928"
        blanco = "FFFFFF"
        gris = "F2F4F7"
        gris_borde = "D5D9E0"
        verde = "E5F3E8"
        borde_fino = Side(style="thin", color=gris_borde)

        libro = Workbook()
        hoja = libro.active
        hoja.title = "Liquidación semanal"
        hoja.sheet_view.showGridLines = False

        # Título y periodo.
        hoja.merge_cells("A1:O1")
        titulo = hoja["A1"]
        titulo.value = "GRUPO LLACE | LIQUIDACIÓN SEMANAL ESTIMADA"
        titulo.font = Font(name="Aptos Display", size=18, bold=True, color=amarillo)
        titulo.fill = PatternFill("solid", fgColor=negro)
        titulo.alignment = Alignment(vertical="center")
        for row in hoja["A1:O1"]:
            for celda in row:
                celda.fill = PatternFill("solid", fgColor=negro)
        hoja.row_dimensions[1].height = 36

        hoja.merge_cells("A2:O2")
        hoja["A2"] = f"PERÍODO: {inicio:%d/%m/%Y} AL {fin:%d/%m/%Y}    |    REPORTE ADMINISTRATIVO"
        hoja["A2"].font = Font(name="Aptos", size=10, bold=True, color=blanco)
        hoja["A2"].fill = PatternFill("solid", fgColor=negro_sec)
        hoja["A2"].alignment = Alignment(vertical="center")
        for row in hoja["A2:O2"]:
            for celda in row:
                celda.fill = PatternFill("solid", fgColor=negro_sec)
        hoja.row_dimensions[2].height = 24

        # Tarjetas de resumen.
        resumen = [
            ("TRABAJADORES", self.valor_trabajadores.text()),
            ("SUELDOS PROPORCIONALES", self.valor_sueldo.text()),
            ("TOTAL DESCUENTOS", self.valor_descuentos.text()),
            ("NETO ESTIMADO", self.valor_neto.text()),
            ("REQUIEREN REVISIÓN", self.valor_revision.text()),
        ]
        grupos = [(1,3),(4,6),(7,9),(10,12),(13,15)]
        for (etiqueta, valor), (col_ini, col_fin) in zip(resumen, grupos):
            hoja.merge_cells(start_row=4, start_column=col_ini, end_row=4, end_column=col_fin)
            hoja.merge_cells(start_row=5, start_column=col_ini, end_row=5, end_column=col_fin)
            celda_titulo = hoja.cell(4, col_ini, etiqueta)
            celda_titulo.font = Font(name="Aptos", size=9, bold=True, color=blanco)
            celda_titulo.fill = PatternFill("solid", fgColor=negro_sec)
            celda_titulo.alignment = Alignment(horizontal="center", vertical="center")
            celda_valor = hoja.cell(5, col_ini, valor)
            celda_valor.font = Font(name="Aptos Display", size=14, bold=True, color=negro)
            celda_valor.fill = PatternFill("solid", fgColor=amarillo)
            celda_valor.alignment = Alignment(horizontal="center", vertical="center")
        hoja.row_dimensions[4].height = 20
        hoja.row_dimensions[5].height = 30

        encabezados = [
            self.tabla.horizontalHeaderItem(i).text()
            for i in range(self.tabla.columnCount())
        ]
        fila_encabezado = 8
        for col, encabezado in enumerate(encabezados, start=1):
            celda = hoja.cell(fila_encabezado, col, encabezado)
            celda.font = Font(name="Aptos", size=9, bold=True, color=amarillo)
            celda.fill = PatternFill("solid", fgColor=negro)
            celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            celda.border = Border(bottom=Side(style="medium", color=amarillo))
        hoja.row_dimensions[fila_encabezado].height = 32

        # La exportación respeta exactamente las filas visibles (incluidos filtros/búsqueda).
        primera_fila_datos = fila_encabezado + 1
        columnas_monetarias = {9, 10, 11, 12, 13, 14}  # índices de tabla, base cero
        columnas_enteras = {4, 5, 6, 7, 8}
        for indice_fila in range(self.tabla.rowCount()):
            num_fila = primera_fila_datos + indice_fila
            for col in range(self.tabla.columnCount()):
                item = self.tabla.item(indice_fila, col)
                texto = item.text().strip() if item is not None else ""
                valor = texto
                if col in columnas_monetarias:
                    limpio = texto.replace("S/", "").replace(" ", "").replace(",", "")
                    try:
                        valor = float(limpio) if limpio else 0.0
                    except ValueError:
                        valor = texto
                elif col in columnas_enteras:
                    try:
                        valor = int(texto) if texto else 0
                    except ValueError:
                        valor = texto
                celda = hoja.cell(num_fila, col + 1, valor)
                celda.font = Font(name="Aptos", size=9, color=negro)
                celda.fill = PatternFill("solid", fgColor=blanco if indice_fila % 2 == 0 else gris)
                celda.border = Border(bottom=borde_fino)
                celda.alignment = Alignment(
                    horizontal="center" if col in {0,3,4,5,6,7,8} else ("right" if col in columnas_monetarias else "left"),
                    vertical="center",
                )
                if col in columnas_monetarias and isinstance(valor, (int, float)):
                    celda.number_format = '"S/ "#,##0.00;[Red]-"S/ "#,##0.00'
                if col == 14 and isinstance(valor, (int, float)) and valor > 0:
                    celda.fill = PatternFill("solid", fgColor=verde)
            hoja.row_dimensions[num_fila].height = 22

        ultima_fila_datos = primera_fila_datos + self.tabla.rowCount() - 1
        fila_total = ultima_fila_datos + 1
        hoja.merge_cells(start_row=fila_total, start_column=1, end_row=fila_total, end_column=4)
        celda_total = hoja.cell(fila_total, 1, "TOTAL GENERAL")
        celda_total.font = Font(name="Aptos", size=10, bold=True, color=amarillo)
        celda_total.fill = PatternFill("solid", fgColor=negro)
        celda_total.alignment = Alignment(horizontal="right", vertical="center")
        for col in range(5, 16):
            celda = hoja.cell(fila_total, col)
            if col - 1 in columnas_enteras or col - 1 in columnas_monetarias:
                letra = get_column_letter(col)
                celda.value = f"=SUM({letra}{primera_fila_datos}:{letra}{ultima_fila_datos})"
            celda.font = Font(name="Aptos", size=9, bold=True, color=amarillo)
            celda.fill = PatternFill("solid", fgColor=negro)
            celda.alignment = Alignment(horizontal="center" if col <= 9 else "right", vertical="center")
            celda.border = Border(top=Side(style="medium", color=amarillo))
            if col - 1 in columnas_monetarias:
                celda.number_format = '"S/ "#,##0.00;[Red]-"S/ "#,##0.00'
        hoja.row_dimensions[fila_total].height = 26

        # Presentación, filtros e impresión.
        anchos = [12, 30, 25, 13, 11, 13, 11, 11, 9, 17, 20, 16, 18, 15, 17]
        for col, ancho in enumerate(anchos, start=1):
            hoja.column_dimensions[get_column_letter(col)].width = ancho
        hoja.freeze_panes = "A9"
        hoja.auto_filter.ref = f"A{fila_encabezado}:O{ultima_fila_datos}"
        hoja.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True, autoPageBreaks=False)
        hoja.page_setup.orientation = "landscape"
        hoja.page_setup.paperSize = hoja.PAPERSIZE_A4
        hoja.page_setup.fitToWidth = 1
        hoja.page_setup.fitToHeight = 0
        hoja.page_margins.left = 0.25
        hoja.page_margins.right = 0.25
        hoja.page_margins.top = 0.5
        hoja.page_margins.bottom = 0.5
        hoja.print_title_rows = "1:8"
        hoja.print_area = f"A1:O{fila_total}"
        hoja.oddFooter.center.text = "Grupo LLACE | Documento de liquidación estimada"
        hoja.oddFooter.right.text = "Página &P de &N"

        try:
            libro.save(ruta)
            QMessageBox.information(
                self, "Exportación completada",
                "El reporte profesional se exportó correctamente.\n\n"
                f"Archivo:\n{ruta}",
            )
        except (OSError, PermissionError, ValueError) as error:
            QMessageBox.critical(
                self, "Error al exportar",
                "No se pudo guardar el archivo. Si está abierto en Excel, ciérralo e inténtalo de nuevo.\n\n"
                f"Detalle: {error}",
            )
            print("ERROR AL EXPORTAR REPORTE:", repr(error))

