import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.auth_service import autenticar_usuario
from app.core.session import sesion_actual
from app.admin.views.dashboard.dashboard_window import DashboardWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.usuario_autenticado = None
        self.dashboard = None

        self.setWindowTitle("LLACE CONTROL BETA")
        self.setFixedSize(500, 500)

        self.crear_interfaz()

    def crear_interfaz(self):

        self.setStyleSheet("""
            QWidget {
                background-color: #F4F4F4;
                font-family: "Segoe UI";
            }

            QFrame#panel {
                background-color: white;
                border-radius: 12px;
            }

            QLabel#titulo {
                color: #222222;
                font-size: 28px;
                font-weight: bold;
            }

            QLabel#subtitulo {
                color: #777777;
                font-size: 14px;
            }

            QLabel#label {
                color: #333333;
                font-size: 13px;
                font-weight: bold;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 2px solid #F2C94C;
            }

            QPushButton {
                background-color: #F2C94C;
                color: #222222;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #E5B93F;
            }

            QPushButton:pressed {
                background-color: #D4A72F;
            }

            QLabel#estado {
                color: #C0392B;
                font-size: 13px;
            }
        """)

        panel = QFrame()
        panel.setObjectName("panel")

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(
            45,
            35,
            45,
            35
        )

        layout.setSpacing(12)

        # ==========================================================
        # TÍTULO
        # ==========================================================

        titulo = QLabel(
            "LLACE CONTROL"
        )

        titulo.setObjectName(
            "titulo"
        )

        titulo.setAlignment(
            Qt.AlignCenter
        )

        subtitulo = QLabel(
            "BETA"
        )

        subtitulo.setObjectName(
            "subtitulo"
        )

        subtitulo.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            subtitulo
        )

        layout.addSpacing(
            25
        )

        # ==========================================================
        # USUARIO
        # ==========================================================

        label_usuario = QLabel(
            "Usuario"
        )

        label_usuario.setObjectName(
            "label"
        )

        self.usuario_input = QLineEdit()

        self.usuario_input.setPlaceholderText(
            "Ingresa tu usuario"
        )

        layout.addWidget(
            label_usuario
        )

        layout.addWidget(
            self.usuario_input
        )

        # ==========================================================
        # CONTRASEÑA
        # ==========================================================

        label_password = QLabel(
            "Contraseña"
        )

        label_password.setObjectName(
            "label"
        )

        self.password_input = QLineEdit()

        self.password_input.setPlaceholderText(
            "Ingresa tu contraseña"
        )

        self.password_input.setEchoMode(
            QLineEdit.Password
        )

        layout.addWidget(
            label_password
        )

        layout.addWidget(
            self.password_input
        )

        layout.addSpacing(
            20
        )

        # ==========================================================
        # BOTÓN INGRESAR
        # ==========================================================

        self.boton_ingresar = QPushButton(
            "INGRESAR"
        )

        self.boton_ingresar.setCursor(
            Qt.PointingHandCursor
        )

        self.boton_ingresar.clicked.connect(
            self.iniciar_sesion
        )

        layout.addWidget(
            self.boton_ingresar
        )

        # ==========================================================
        # ESTADO
        # ==========================================================

        self.estado = QLabel(
            ""
        )

        self.estado.setObjectName(
            "estado"
        )

        self.estado.setAlignment(
            Qt.AlignCenter
        )

        self.estado.setWordWrap(
            True
        )

        layout.addWidget(
            self.estado
        )

        # ==========================================================
        # LAYOUT PRINCIPAL
        # ==========================================================

        ventana_layout = QVBoxLayout(
            self
        )

        ventana_layout.setContentsMargins(
            60,
            50,
            60,
            50
        )

        ventana_layout.addWidget(
            panel
        )

        # ==========================================================
        # ENTER PARA INGRESAR
        # ==========================================================

        self.password_input.returnPressed.connect(
            self.iniciar_sesion
        )

    # ==============================================================
    # LOGIN
    # ==============================================================

    def iniciar_sesion(self):

        usuario = self.usuario_input.text().strip()

        password = self.password_input.text()

        # ----------------------------------------------------------
        # VALIDACIÓN
        # ----------------------------------------------------------

        if not usuario:

            self.estado.setStyleSheet(
                "color: #C0392B; font-size: 13px;"
            )

            self.estado.setText(
                "Ingresa tu usuario."
            )

            self.usuario_input.setFocus()

            return

        if not password:

            self.estado.setStyleSheet(
                "color: #C0392B; font-size: 13px;"
            )

            self.estado.setText(
                "Ingresa tu contraseña."
            )

            self.password_input.setFocus()

            return

        # ----------------------------------------------------------
        # DESACTIVAR BOTÓN
        # ----------------------------------------------------------

        self.boton_ingresar.setEnabled(
            False
        )

        self.estado.setStyleSheet(
            "color: #777777; font-size: 13px;"
        )

        self.estado.setText(
            "Verificando..."
        )

        try:

            # ------------------------------------------------------
            # AUTENTICAR CONTRA LA BASE DE DATOS
            # ------------------------------------------------------

            usuario_db = autenticar_usuario(
                usuario,
                password
            )

            # ------------------------------------------------------
            # LOGIN INCORRECTO
            # ------------------------------------------------------

            if usuario_db is None:

                self.estado.setStyleSheet(
                    "color: #C0392B; font-size: 13px;"
                )

                self.estado.setText(
                    "Usuario o contraseña incorrectos."
                )

                self.password_input.clear()

                self.password_input.setFocus()

                return

            # ------------------------------------------------------
            # GUARDAR USUARIO AUTENTICADO
            # ------------------------------------------------------

            self.usuario_autenticado = usuario_db

            # ------------------------------------------------------
            # INICIAR SESIÓN GLOBAL
            # ------------------------------------------------------

            sesion_actual.iniciar(
                usuario_db
            )

            print(
                "LOGIN CORRECTO"
            )

            print(
                f"Usuario: {usuario_db.usuario}"
            )

            print(
                f"Nombre: {usuario_db.nombre}"
            )

            print(
                f"Rol: {usuario_db.rol}"
            )

            print(
                f"SESION ACTIVA: "
                f"{sesion_actual.esta_activa()}"
            )

            # ------------------------------------------------------
            # MENSAJE VISUAL
            # ------------------------------------------------------

            self.estado.setStyleSheet(
                "color: #27AE60; font-size: 13px;"
            )

            self.estado.setText(
                f"Acceso correcto\n"
                f"Rol: {usuario_db.rol}"
            )

            # ------------------------------------------------------
            # ABRIR DASHBOARD
            # ------------------------------------------------------

            self.dashboard = DashboardWindow()

            self.dashboard.showMaximized()

            # ------------------------------------------------------
            # OCULTAR LOGIN
            # ------------------------------------------------------

            self.hide()

        except Exception as error:

            self.estado.setStyleSheet(
                "color: #C0392B; font-size: 13px;"
            )

            self.estado.setText(
                "No se pudo conectar con el servidor."
            )

            print(
                "ERROR DE LOGIN:"
            )

            print(
                error
            )

        finally:

            self.boton_ingresar.setEnabled(
                True
            )


# ==============================================================
# EJECUCIÓN
# ==============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    ventana = LoginWindow()

    ventana.show()

    sys.exit(
        app.exec()
    )