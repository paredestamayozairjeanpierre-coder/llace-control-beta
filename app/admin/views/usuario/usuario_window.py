import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
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
)

from app.admin.services.usuario_service import (
    listar_usuarios,
    buscar_usuarios,
)

from app.admin.views.usuario.usuario_form import (
    UsuarioForm,
)

from app.core.session import sesion_actual

from app.core.permisos import (
    puede_gestionar_usuarios,
)


class UsuariosWindow(QWidget):

    def __init__(
        self,
        parent=None
    ):

        # ======================================================
        # SEGURIDAD
        # ======================================================

        if not puede_gestionar_usuarios():
            raise PermissionError(
                "No tienes permisos para gestionar usuarios."
            )

        super().__init__(parent)

        # Esta vista se integra como página dentro del QStackedWidget
        # del Dashboard. No debe crear una ventana independiente.
        self.setObjectName("pagina_usuarios")

        # ======================================================
        # REFERENCIA AL FORMULARIO
        # ======================================================

        self.formulario_usuario = None

        # ======================================================
        # INTERFAZ
        # ======================================================

        self.crear_interfaz()

        # ======================================================
        # CARGAR DATOS
        # ======================================================

        self.cargar_usuarios()

    # ==========================================================
    # INTERFAZ
    # ==========================================================

    def crear_interfaz(self):

        self.setStyleSheet(
            """
            QWidget#pagina_usuarios, QWidget {
                background-color: #111318;
                color: #E8EAED;
                font-family: "Segoe UI";
                font-size: 12px;
            }
            QFrame#cabecera { background-color: #111318; border: none; }
            QLabel#titulo { color: #F1F1F1; font-size: 25px; font-weight: bold; }
            QLabel#subtitulo { color: #858B96; font-size: 12px; }
            QLabel#sesion { color: #858B96; font-size: 11px; }
            QLineEdit {
                background-color: #14171D; color: #E8EAED;
                border: 1px solid #343A46; border-radius: 7px;
                padding: 8px 10px; font-size: 11px;
            }
            QLineEdit:focus { border: 1px solid #F4C542; }
            QPushButton#boton_nuevo {
                background-color: #F4C542; color: #111318; border: none;
                border-radius: 7px; padding: 12px 18px;
                font-size: 10px; font-weight: bold;
            }
            QPushButton#boton_nuevo:hover { background-color: #FFD95C; }
            QPushButton#boton_limpiar {
                background-color: #252A34; color: #D5D8DE; border: 1px solid #343A46;
                border-radius: 7px; padding: 9px 18px;
                font-size: 10px; font-weight: bold;
            }
            QPushButton#boton_limpiar:hover { background-color: #303641; }
            QPushButton#boton_gestionar {
                background-color: #F4C542; color: #111318; border: none;
                border-radius: 5px; padding: 6px 12px;
                font-size: 9px; font-weight: bold;
            }
            QPushButton#boton_gestionar:hover { background-color: #FFD95C; }
            QTableWidget {
                background-color: #14171D; alternate-background-color: #181B21;
                border: 1px solid #2A2F39; gridline-color: #252B35;
                color: #E8EAED; font-size: 11px;
                selection-background-color: #34302A; selection-color: #FFFFFF;
            }
            QTableWidget::item { padding: 7px; border: none; }
            QHeaderView::section {
                background-color: #11151B; color: #F4C542; border: none;
                border-bottom: 1px solid #343A46; padding: 10px 7px;
                font-size: 10px; font-weight: bold;
            }
            QScrollBar:vertical { background: #111318; width: 10px; margin: 0; }
            QScrollBar::handle:vertical { background: #454B56; min-height: 25px; border-radius: 4px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            """
        )

        # ======================================================
        # LAYOUT PRINCIPAL
        # ======================================================

        layout_principal = QVBoxLayout(
            self
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
        # CABECERA
        # ======================================================

        cabecera = QFrame()

        cabecera.setObjectName(
            "cabecera"
        )

        cabecera.setMinimumHeight(
            105
        )

        layout_cabecera = QHBoxLayout(
            cabecera
        )

        layout_cabecera.setContentsMargins(
            30,
            20,
            30,
            20
        )

        layout_cabecera.setSpacing(
            20
        )

        # ------------------------------------------------------
        # TÍTULO
        # ------------------------------------------------------

        bloque_titulo = QVBoxLayout()

        bloque_titulo.setSpacing(
            3
        )

        titulo = QLabel(
            "USUARIOS"
        )

        titulo.setObjectName(
            "titulo"
        )

        subtitulo = QLabel(
            "Gestión de usuarios y permisos del sistema"
        )

        subtitulo.setObjectName(
            "subtitulo"
        )

        bloque_titulo.addWidget(
            titulo
        )

        bloque_titulo.addWidget(
            subtitulo
        )

        layout_cabecera.addLayout(
            bloque_titulo
        )

        layout_cabecera.addStretch()

        # ------------------------------------------------------
        # NUEVO USUARIO
        # ------------------------------------------------------

        self.boton_nuevo = QPushButton(
            "+ NUEVO USUARIO"
        )

        self.boton_nuevo.setObjectName(
            "boton_nuevo"
        )

        self.boton_nuevo.setCursor(
            Qt.PointingHandCursor
        )

        self.boton_nuevo.setMinimumHeight(
            42
        )

        self.boton_nuevo.clicked.connect(
            self.nuevo_usuario
        )

        layout_cabecera.addWidget(
            self.boton_nuevo
        )

        layout_principal.addWidget(
            cabecera
        )

        # ======================================================
        # CONTENIDO
        # ======================================================

        contenido = QWidget()

        layout_contenido = QVBoxLayout(
            contenido
        )

        layout_contenido.setContentsMargins(
            30,
            20,
            30,
            25
        )

        layout_contenido.setSpacing(
            10
        )

        # ======================================================
        # BÚSQUEDA
        # ======================================================

        barra_busqueda = QHBoxLayout()

        barra_busqueda.setSpacing(
            10
        )

        etiqueta_buscar = QLabel(
            "Buscar:"
        )

        etiqueta_buscar.setStyleSheet(
            """
            QLabel {
                color: #374151;
                font-size: 10px;
                font-weight: bold;
            }
            """
        )

        barra_busqueda.addWidget(
            etiqueta_buscar
        )

        self.entrada_busqueda = QLineEdit()

        self.entrada_busqueda.setPlaceholderText(
            "Buscar por nombre, usuario o rol..."
        )

        self.entrada_busqueda.setMinimumHeight(
            36
        )

        self.entrada_busqueda.textChanged.connect(
            self.buscar
        )

        barra_busqueda.addWidget(
            self.entrada_busqueda
        )

        self.boton_limpiar = QPushButton(
            "LIMPIAR"
        )

        self.boton_limpiar.setObjectName(
            "boton_limpiar"
        )

        self.boton_limpiar.setCursor(
            Qt.PointingHandCursor
        )

        self.boton_limpiar.setMinimumHeight(
            36
        )

        self.boton_limpiar.clicked.connect(
            self.limpiar_busqueda
        )

        barra_busqueda.addWidget(
            self.boton_limpiar
        )

        layout_contenido.addLayout(
            barra_busqueda
        )

        # ======================================================
        # INFORMACIÓN DE SESIÓN
        # ======================================================

        self.label_sesion = QLabel()

        self.label_sesion.setObjectName(
            "sesion"
        )

        layout_contenido.addWidget(
            self.label_sesion
        )

        self.actualizar_info_sesion()

        # ======================================================
        # TABLA
        # ======================================================

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(
            6
        )

        self.tabla.setHorizontalHeaderLabels(
            [
                "ID",
                "NOMBRE",
                "USUARIO",
                "ROL",
                "ESTADO",
                "ACCIONES",
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

        self.tabla.verticalHeader().setVisible(
            False
        )

        self.tabla.setMinimumHeight(
            350
        )

        # ------------------------------------------------------
        # DOBLE CLIC PARA GESTIONAR
        # ------------------------------------------------------

        self.tabla.cellDoubleClicked.connect(
            self.gestionar_usuario_por_fila
        )

        # ------------------------------------------------------
        # CONFIGURACIÓN DE COLUMNAS
        # ------------------------------------------------------

        header = self.tabla.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        layout_contenido.addWidget(
            self.tabla
        )

        layout_principal.addWidget(
            contenido
        )

    # ==========================================================
    # SESIÓN
    # ==========================================================

    def actualizar_info_sesion(self):

        usuario = sesion_actual.usuario

        if usuario is None:

            self.label_sesion.setText(
                "Sin sesión activa."
            )

            return

        if usuario.rol == "SUPERADMIN":

            self.label_sesion.setText(
                "Sesión: SUPERADMIN  ·  "
                "Gestión completa de usuarios."
            )

        elif usuario.rol == "ADMIN":

            self.label_sesion.setText(
                "Sesión: ADMIN  ·  "
                "Gestión operativa."
            )

        else:

            self.label_sesion.setText(
                f"Sesión: {usuario.rol}"
            )

    # ==========================================================
    # CARGAR USUARIOS
    # ==========================================================

    def cargar_usuarios(
        self,
        texto=""
    ):

        try:

            texto = str(
                texto
            ).strip()

            if texto:

                usuarios = buscar_usuarios(
                    texto
                )

            else:

                usuarios = listar_usuarios()

            self.mostrar_usuarios(
                usuarios
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudieron cargar los usuarios.\n\n"
                    f"{error}"
                )
            )

            print(
                "ERROR AL CARGAR USUARIOS:"
            )

            print(
                error
            )

    # ==========================================================
    # MOSTRAR USUARIOS
    # ==========================================================

    def mostrar_usuarios(
        self,
        usuarios
    ):

        self.tabla.setRowCount(
            0
        )

        for usuario in usuarios:

            fila = self.tabla.rowCount()

            self.tabla.insertRow(
                fila
            )

            # ==================================================
            # ID
            # ==================================================

            item_id = QTableWidgetItem(
                str(
                    usuario.id
                )
            )

            item_id.setTextAlignment(
                Qt.AlignCenter
            )

            self.tabla.setItem(
                fila,
                0,
                item_id
            )

            # ==================================================
            # NOMBRE
            # ==================================================

            item_nombre = QTableWidgetItem(
                usuario.nombre or ""
            )

            self.tabla.setItem(
                fila,
                1,
                item_nombre
            )

            # ==================================================
            # USUARIO
            # ==================================================

            item_usuario = QTableWidgetItem(
                usuario.usuario or ""
            )

            self.tabla.setItem(
                fila,
                2,
                item_usuario
            )

            # ==================================================
            # ROL
            # ==================================================

            item_rol = QTableWidgetItem(
                usuario.rol or ""
            )

            item_rol.setTextAlignment(
                Qt.AlignCenter
            )

            self.tabla.setItem(
                fila,
                3,
                item_rol
            )

            # ==================================================
            # ESTADO
            # ==================================================

            estado = (
                "ACTIVO"
                if usuario.activo
                else "INACTIVO"
            )

            item_estado = QTableWidgetItem(
                estado
            )

            item_estado.setTextAlignment(
                Qt.AlignCenter
            )

            self.tabla.setItem(
                fila,
                4,
                item_estado
            )

            # ==================================================
            # ACCIONES
            # ==================================================

            contenedor_accion = QWidget()

            layout_accion = QHBoxLayout(
                contenedor_accion
            )

            layout_accion.setContentsMargins(
                4,
                3,
                4,
                3
            )

            layout_accion.setSpacing(
                0
            )

            boton_gestionar = QPushButton(
                "GESTIONAR"
            )

            boton_gestionar.setObjectName(
                "boton_gestionar"
            )

            boton_gestionar.setCursor(
                Qt.PointingHandCursor
            )

            # Guardamos el ID del usuario
            # directamente en el botón.

            boton_gestionar.setProperty(
                "usuario_id",
                usuario.id
            )

            boton_gestionar.clicked.connect(
                self.gestionar_usuario_por_boton
            )

            layout_accion.addWidget(
                boton_gestionar
            )

            self.tabla.setCellWidget(
                fila,
                5,
                contenedor_accion
            )

        self.tabla.resizeRowsToContents()

    # ==========================================================
    # BUSCAR
    # ==========================================================

    def buscar(
        self,
        texto
    ):

        self.cargar_usuarios(
            texto
        )

    # ==========================================================
    # LIMPIAR
    # ==========================================================

    def limpiar_busqueda(self):

        self.entrada_busqueda.clear()

        self.entrada_busqueda.setFocus()

    # ==========================================================
    # NUEVO USUARIO
    # ==========================================================

    def nuevo_usuario(self):

        if not puede_gestionar_usuarios():

            QMessageBox.warning(
                self,
                "Acceso denegado",
                "No tienes permisos para gestionar usuarios."
            )

            return

        try:

            # --------------------------------------------------
            # Evitar múltiples formularios
            # --------------------------------------------------

            if (
                self.formulario_usuario is not None
                and self.formulario_usuario.isVisible()
            ):

                self.formulario_usuario.raise_()

                self.formulario_usuario.activateWindow()

                return

            # --------------------------------------------------
            # Crear formulario
            # --------------------------------------------------

            self.formulario_usuario = UsuarioForm(
                parent=self,
                al_guardar=self.usuario_guardado
            )

            resultado = (
                self.formulario_usuario.exec()
            )

            self.formulario_usuario = None

            if resultado == UsuarioForm.Accepted:

                self.cargar_usuarios(
                    self.entrada_busqueda.text()
                )

        except Exception as error:

            self.formulario_usuario = None

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudo abrir el formulario "
                    "de nuevo usuario.\n\n"
                    f"{error}"
                )
            )

            print(
                "ERROR AL ABRIR FORMULARIO:"
            )

            print(
                error
            )

    # ==========================================================
    # GESTIONAR POR BOTÓN
    # ==========================================================

    def gestionar_usuario_por_boton(self):

        boton = self.sender()

        if boton is None:
            return

        usuario_id = boton.property(
            "usuario_id"
        )

        if usuario_id is None:
            return

        self.abrir_gestion_usuario(
            usuario_id
        )

    # ==========================================================
    # GESTIONAR POR DOBLE CLIC
    # ==========================================================

    def gestionar_usuario_por_fila(
        self,
        fila,
        columna
    ):

        # ------------------------------------------------------
        # La columna ACCIONES ya tiene su propio botón.
        # El doble clic funciona sobre cualquier otra columna.
        # ------------------------------------------------------

        if columna == 5:
            return

        item_id = self.tabla.item(
            fila,
            0
        )

        if item_id is None:
            return

        try:

            usuario_id = int(
                item_id.text()
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Usuario inválido",
                "No se pudo identificar el usuario seleccionado."
            )

            return

        self.abrir_gestion_usuario(
            usuario_id
        )

    # ==========================================================
    # ABRIR GESTIÓN DE USUARIO
    # ==========================================================

    def abrir_gestion_usuario(
        self,
        usuario_id
    ):

        if not puede_gestionar_usuarios():

            QMessageBox.warning(
                self,
                "Acceso denegado",
                "No tienes permisos para gestionar usuarios."
            )

            return

        try:

            # --------------------------------------------------
            # Evitar múltiples formularios
            # --------------------------------------------------

            if (
                self.formulario_usuario is not None
                and self.formulario_usuario.isVisible()
            ):

                self.formulario_usuario.raise_()

                self.formulario_usuario.activateWindow()

                return

            # --------------------------------------------------
            # Buscar usuario actual
            # --------------------------------------------------

            usuario = None

            for fila in range(
                self.tabla.rowCount()
            ):

                item_id = self.tabla.item(
                    fila,
                    0
                )

                if item_id is None:
                    continue

                try:

                    id_fila = int(
                        item_id.text()
                    )

                except ValueError:

                    continue

                if id_fila == int(usuario_id):

                    # ------------------------------------------
                    # Obtener el objeto nuevamente desde BD
                    # ------------------------------------------

                    from app.admin.services.usuario_service import (
                        obtener_usuario_por_id,
                    )

                    usuario = obtener_usuario_por_id(
                        usuario_id
                    )

                    break

            if usuario is None:

                # --------------------------------------------------
                # Por seguridad, intentar directamente desde BD.
                # --------------------------------------------------

                from app.admin.services.usuario_service import (
                    obtener_usuario_por_id,
                )

                usuario = obtener_usuario_por_id(
                    usuario_id
                )

            if usuario is None:

                QMessageBox.warning(
                    self,
                    "Usuario no encontrado",
                    "El usuario seleccionado ya no existe."
                )

                self.cargar_usuarios(
                    self.entrada_busqueda.text()
                )

                return

            # --------------------------------------------------
            # Abrir formulario
            # --------------------------------------------------

            self.formulario_usuario = UsuarioForm(
                parent=self,
                usuario=usuario,
                al_guardar=self.usuario_guardado
            )

            resultado = (
                self.formulario_usuario.exec()
            )

            self.formulario_usuario = None

            if resultado == UsuarioForm.Accepted:

                self.cargar_usuarios(
                    self.entrada_busqueda.text()
                )

        except Exception as error:

            self.formulario_usuario = None

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudo abrir la gestión del usuario.\n\n"
                    f"{error}"
                )
            )

            print(
                "ERROR AL GESTIONAR USUARIO:"
            )

            print(
                error
            )

    # ==========================================================
    # USUARIO GUARDADO
    # ==========================================================

    def usuario_guardado(self):

        self.cargar_usuarios(
            self.entrada_busqueda.text()
        )

    # ==========================================================
    # CERRAR
    # ==========================================================

    def closeEvent(
        self,
        event
    ):

        self.formulario_usuario = None

        event.accept()


# ==============================================================
# EJECUCIÓN DIRECTA
# ==============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    ventana = UsuariosWindow()

    ventana.show()

    sys.exit(
        app.exec()
    )