from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.admin.services.usuario_service import guardar_usuario_completo


class UsuarioForm(QDialog):

    def __init__(
        self,
        parent=None,
        usuario=None,
        al_guardar=None,
    ):
        super().__init__(parent)

        self.usuario = usuario
        self.al_guardar = al_guardar

        self.es_edicion = usuario is not None

        self.setWindowTitle(
            "LLACE CONTROL BETA - "
            + (
                "Editar Usuario"
                if self.es_edicion
                else "Nuevo Usuario"
            )
        )

        self.setMinimumSize(620, 570)
        self.setModal(True)

        self.crear_interfaz()

        if self.es_edicion:
            self.cargar_datos()

    # ==========================================================
    # INTERFAZ
    # ==========================================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(
            28,
            24,
            28,
            24
        )

        layout_principal.setSpacing(18)

        # ======================================================
        # CABECERA
        # ======================================================

        titulo = QLabel(
            "EDITAR USUARIO"
            if self.es_edicion
            else "NUEVO USUARIO"
        )

        titulo.setObjectName("titulo")

        subtitulo = QLabel(
            "Actualiza los datos de la cuenta."
            if self.es_edicion
            else "Registra una nueva cuenta para acceder al sistema."
        )

        subtitulo.setObjectName("subtitulo")

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)

        # ======================================================
        # TARJETA
        # ======================================================

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")

        layout_tarjeta = QVBoxLayout(tarjeta)

        layout_tarjeta.setContentsMargins(
            24,
            24,
            24,
            24
        )

        layout_tarjeta.setSpacing(15)

        # ======================================================
        # FORMULARIO
        # ======================================================

        formulario = QFormLayout()

        formulario.setLabelAlignment(Qt.AlignLeft)
        formulario.setFormAlignment(Qt.AlignTop)

        formulario.setVerticalSpacing(15)
        formulario.setHorizontalSpacing(20)

        # ======================================================
        # NOMBRE
        # ======================================================

        self.entrada_nombre = QLineEdit()

        self.entrada_nombre.setPlaceholderText(
            "Ejemplo: Juan Pérez"
        )

        self.entrada_nombre.setMinimumHeight(40)

        formulario.addRow(
            self.crear_etiqueta("NOMBRE COMPLETO"),
            self.entrada_nombre
        )

        # ======================================================
        # USUARIO
        # ======================================================

        self.entrada_usuario = QLineEdit()

        self.entrada_usuario.setPlaceholderText(
            "Ejemplo: jperez"
        )

        self.entrada_usuario.setMinimumHeight(40)
        self.entrada_usuario.setMaxLength(50)

        formulario.addRow(
            self.crear_etiqueta("USUARIO"),
            self.entrada_usuario
        )

        # ======================================================
        # CONTRASEÑA
        # ======================================================

        self.entrada_password = QLineEdit()

        self.entrada_password.setPlaceholderText(
            "Ingresa una contraseña"
        )

        self.entrada_password.setEchoMode(
            QLineEdit.Password
        )

        self.entrada_password.setMinimumHeight(40)

        formulario.addRow(
            self.crear_etiqueta("CONTRASEÑA"),
            self.entrada_password
        )

        # ======================================================
        # CONFIRMAR CONTRASEÑA
        # ======================================================

        self.entrada_password_confirmacion = QLineEdit()

        self.entrada_password_confirmacion.setPlaceholderText(
            "Repite la contraseña"
        )

        self.entrada_password_confirmacion.setEchoMode(
            QLineEdit.Password
        )

        self.entrada_password_confirmacion.setMinimumHeight(40)

        formulario.addRow(
            self.crear_etiqueta("CONFIRMAR CONTRASEÑA"),
            self.entrada_password_confirmacion
        )

        # ======================================================
        # ROL
        # ======================================================

        self.combo_rol = QComboBox()
        self.combo_rol.setMinimumHeight(40)

        self.combo_rol.addItem(
            "ADMIN",
            "ADMIN"
        )

        self.combo_rol.addItem(
            "SUPERADMIN",
            "SUPERADMIN"
        )

        formulario.addRow(
            self.crear_etiqueta("ROL"),
            self.combo_rol
        )

        # ======================================================
        # ESTADO
        # ======================================================

        self.combo_estado = QComboBox()
        self.combo_estado.setMinimumHeight(40)

        self.combo_estado.addItem(
            "ACTIVO",
            True
        )

        self.combo_estado.addItem(
            "INACTIVO",
            False
        )

        formulario.addRow(
            self.crear_etiqueta("ESTADO"),
            self.combo_estado
        )

        layout_tarjeta.addLayout(formulario)

        # ======================================================
        # AVISO
        # ======================================================

        aviso = QFrame()
        aviso.setObjectName("aviso")

        layout_aviso = QHBoxLayout(aviso)

        layout_aviso.setContentsMargins(
            14,
            12,
            14,
            12
        )

        texto_aviso = QLabel(
            "🔐 La contraseña se almacenará mediante "
            "hash seguro y no se guardará en texto plano."
        )

        texto_aviso.setWordWrap(True)
        texto_aviso.setObjectName("texto_aviso")

        layout_aviso.addWidget(texto_aviso)

        layout_tarjeta.addWidget(aviso)

        layout_principal.addWidget(tarjeta)

        # ======================================================
        # BOTONES
        # ======================================================

        botones = QHBoxLayout()

        botones.addStretch()

        self.btn_cancelar = QPushButton("CANCELAR")

        self.btn_cancelar.setObjectName("btn_cancelar")

        self.btn_cancelar.setMinimumHeight(42)
        self.btn_cancelar.setMinimumWidth(120)

        self.btn_cancelar.clicked.connect(
            self.reject
        )

        botones.addWidget(self.btn_cancelar)

        self.btn_guardar = QPushButton("GUARDAR")

        self.btn_guardar.setObjectName("btn_guardar")

        self.btn_guardar.setMinimumHeight(42)
        self.btn_guardar.setMinimumWidth(120)

        self.btn_guardar.clicked.connect(
            self.guardar
        )

        botones.addWidget(self.btn_guardar)

        layout_principal.addLayout(botones)

        # ======================================================
        # ESTILOS
        # ======================================================

        self.setStyleSheet(
            """
            QDialog { background-color: #111318; }
            QLabel#titulo { color: #F1F1F1; font-size: 24px; font-weight: bold; }
            QLabel#subtitulo { color: #858B96; font-size: 11px; }
            QFrame#tarjeta { background-color: #181B21; border: 1px solid #2A2F39; border-radius: 8px; }
            QLabel#campo { color: #C5CAD2; font-size: 10px; font-weight: bold; }
            QLineEdit, QComboBox {
                background-color: #14171D; color: #E8EAED;
                border: 1px solid #343A46; border-radius: 5px;
                padding: 7px 10px; font-size: 11px;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #F4C542; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView { background-color: #181B21; color: #E8EAED; selection-background-color: #F4C542; selection-color: #111318; }
            QFrame#aviso { background-color: #292515; border: 1px solid #806A20; border-radius: 5px; }
            QLabel#texto_aviso { color: #E8D58A; font-size: 10px; }
            QPushButton#btn_cancelar { background-color: #252A34; color: #D5D8DE; border: 1px solid #343A46; border-radius: 5px; font-size: 10px; font-weight: bold; }
            QPushButton#btn_cancelar:hover { background-color: #303641; }
            QPushButton#btn_guardar { background-color: #F4C542; color: #111318; border: none; border-radius: 5px; font-size: 10px; font-weight: bold; }
            QPushButton#btn_guardar:hover { background-color: #FFD95C; }
            QPushButton#btn_guardar:pressed { background-color: #D7AA28; }
            """
        )

    # ==========================================================
    # ETIQUETA
    # ==========================================================

    def crear_etiqueta(self, texto):

        etiqueta = QLabel(texto)

        etiqueta.setObjectName("campo")

        return etiqueta

    # ==========================================================
    # CARGAR DATOS
    # ==========================================================

    def cargar_datos(self):

        if self.usuario is None:
            return

        self.entrada_nombre.setText(
            self.usuario.nombre or ""
        )

        self.entrada_usuario.setText(
            self.usuario.usuario or ""
        )

        # El username no se modifica
        self.entrada_usuario.setEnabled(False)

        indice_rol = self.combo_rol.findData(
            self.usuario.rol
        )

        if indice_rol >= 0:
            self.combo_rol.setCurrentIndex(
                indice_rol
            )

        indice_estado = self.combo_estado.findData(
            self.usuario.activo
        )

        if indice_estado >= 0:
            self.combo_estado.setCurrentIndex(
                indice_estado
            )

        self.entrada_password.setPlaceholderText(
            "Dejar vacío para conservar la contraseña"
        )

        self.entrada_password_confirmacion.setPlaceholderText(
            "Repite solo si deseas cambiarla"
        )

    # ==========================================================
    # VALIDAR
    # ==========================================================

    def validar_formulario(self):

        nombre = (
            self.entrada_nombre
            .text()
            .strip()
        )

        usuario = (
            self.entrada_usuario
            .text()
            .strip()
            .lower()
        )

        password = (
            self.entrada_password
            .text()
        )

        confirmacion = (
            self.entrada_password_confirmacion
            .text()
        )

        rol = (
            self.combo_rol
            .currentData()
        )

        activo = (
            self.combo_estado
            .currentData()
        )

        # ======================================================
        # NOMBRE
        # ======================================================

        if not nombre:

            QMessageBox.warning(
                self,
                "Dato requerido",
                "Ingresa el nombre completo."
            )

            self.entrada_nombre.setFocus()

            return None

        if len(nombre) < 3:

            QMessageBox.warning(
                self,
                "Nombre inválido",
                "El nombre debe tener al menos 3 caracteres."
            )

            self.entrada_nombre.setFocus()

            return None

        # ======================================================
        # USUARIO
        # ======================================================

        if not usuario:

            QMessageBox.warning(
                self,
                "Dato requerido",
                "Ingresa el nombre de usuario."
            )

            self.entrada_usuario.setFocus()

            return None

        if " " in usuario:

            QMessageBox.warning(
                self,
                "Usuario inválido",
                "El usuario no puede contener espacios."
            )

            self.entrada_usuario.setFocus()

            return None

        if len(usuario) < 3:

            QMessageBox.warning(
                self,
                "Usuario inválido",
                "El usuario debe tener al menos 3 caracteres."
            )

            self.entrada_usuario.setFocus()

            return None

        # ======================================================
        # ROL
        # ======================================================

        if rol not in (
            "ADMIN",
            "SUPERADMIN"
        ):

            QMessageBox.warning(
                self,
                "Rol inválido",
                "Selecciona un rol válido."
            )

            return None

        # ======================================================
        # CONTRASEÑA
        # ======================================================

        if not self.es_edicion:

            if not password:

                QMessageBox.warning(
                    self,
                    "Contraseña requerida",
                    "Ingresa una contraseña."
                )

                self.entrada_password.setFocus()

                return None

            if len(password) < 6:

                QMessageBox.warning(
                    self,
                    "Contraseña débil",
                    "La contraseña debe tener al menos 6 caracteres."
                )

                self.entrada_password.setFocus()

                return None

            if password != confirmacion:

                QMessageBox.warning(
                    self,
                    "Contraseñas diferentes",
                    "Las contraseñas no coinciden."
                )

                self.entrada_password_confirmacion.setFocus()

                return None

        else:

            # En edición, ambos campos vacíos significa
            # conservar la contraseña actual.

            if password or confirmacion:

                if len(password) < 6:

                    QMessageBox.warning(
                        self,
                        "Contraseña débil",
                        "La nueva contraseña debe tener al menos 6 caracteres."
                    )

                    self.entrada_password.setFocus()

                    return None

                if password != confirmacion:

                    QMessageBox.warning(
                        self,
                        "Contraseñas diferentes",
                        "Las contraseñas no coinciden."
                    )

                    self.entrada_password_confirmacion.setFocus()

                    return None

        return {
            "nombre": nombre,
            "usuario": usuario,
            "password": password,
            "rol": rol,
            "activo": activo,
        }

    # ==========================================================
    # GUARDAR
    # ==========================================================

    def guardar(self):

        datos = self.validar_formulario()

        if datos is None:
            return

        # ======================================================
        # NUEVO USUARIO
        # ======================================================

        if not self.es_edicion:

            confirmar = QMessageBox.question(
                self,
                "Confirmar registro",
                (
                    "¿Deseas crear este usuario?\n\n"
                    f"Nombre: {datos['nombre']}\n"
                    f"Usuario: {datos['usuario']}\n"
                    f"Rol: {datos['rol']}\n"
                    f"Estado: "
                    f"{'ACTIVO' if datos['activo'] else 'INACTIVO'}"
                ),
                QMessageBox.Yes
                | QMessageBox.No,
                QMessageBox.No
            )

            if confirmar != QMessageBox.Yes:
                return

            try:

                nuevo_usuario = guardar_usuario_completo(
                    nombre=datos["nombre"],
                    usuario=datos["usuario"],
                    password=datos["password"],
                    rol=datos["rol"],
                    activo=datos["activo"],
                )

                if not nuevo_usuario:
                    QMessageBox.warning(
                        self,
                        "No se pudo crear",
                        "El usuario no pudo ser creado."
                    )
                    return

                QMessageBox.information(
                    self,
                    "Usuario creado",
                    (
                        "El usuario se creó correctamente.\n\n"
                        f"Usuario: {nuevo_usuario.usuario}\n"
                        f"Rol: {nuevo_usuario.rol}\n"
                        f"Estado: "
                        f"{'ACTIVO' if datos['activo'] else 'INACTIVO'}"
                    )
                )

                if self.al_guardar:
                    self.al_guardar()

                self.accept()

            except ValueError as error:

                QMessageBox.warning(
                    self,
                    "No se pudo crear",
                    str(error)
                )

            except Exception as error:

                QMessageBox.critical(
                    self,
                    "Error",
                    (
                        "Ocurrió un error al crear el usuario.\n\n"
                        f"{error}"
                    )
                )

            return

        # ======================================================
        # EDICIÓN
        # ======================================================

        if self.usuario is None:

            QMessageBox.warning(
                self,
                "Error",
                "No se encontró el usuario que deseas editar."
            )

            return

        confirmar = QMessageBox.question(
            self,
            "Confirmar cambios",
            (
                "¿Deseas guardar los cambios de este usuario?\n\n"
                f"Nombre: {datos['nombre']}\n"
                f"Usuario: {datos['usuario']}\n"
                f"Rol: {datos['rol']}\n"
                f"Estado: "
                f"{'ACTIVO' if datos['activo'] else 'INACTIVO'}"
            ),
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No
        )

        if confirmar != QMessageBox.Yes:
            return

        try:

            # Todos los cambios se aplican en una sola transaccion.
            usuario_actualizado = guardar_usuario_completo(
                usuario_id=self.usuario.id,
                nombre=datos["nombre"],
                usuario=datos["usuario"],
                rol=datos["rol"],
                activo=datos["activo"],
                password=datos["password"],
            )

            if usuario_actualizado is None:
                QMessageBox.warning(
                    self,
                    "No se pudo actualizar",
                    "El usuario no pudo ser actualizado."
                )
                return

            QMessageBox.information(
                self,
                "Usuario actualizado",
                (
                    "Los cambios se guardaron correctamente.\n\n"
                    f"Usuario: {datos['usuario']}"
                )
            )

            if self.al_guardar:
                self.al_guardar()

            self.accept()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "No se pudo actualizar",
                str(error)
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "Ocurrió un error al actualizar el usuario.\n\n"
                    f"{error}"
                )
            )