from gui.components.form.login_form import LoginForm
from gui.controllers.main.main_controller import MainController
from services.user_service import UserService
from config.settings import log
import flet as ft
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog


class LoginFormController:
    def __init__(self, page: ft.Page):
        self.user_service = UserService()
        self.login_form = LoginForm(self.on_submit, self.to_register)
        self.page = page
        self.main_controller = MainController()

    def on_submit(self, form_data: dict):
        rut = form_data.get("rut")
        password = form_data.get("password")
        if not isinstance(rut, str) or not isinstance(password, str):
            log.info(
                "[LoginFormController.on_submit] Credenciales inválidas recibidas (tipos incorrectos)."
            )
            self.show_validate_error_dialog(["Credenciales inválidas."])
            return

        user = self.user_service.login(rut, password)
        if user:
            log.info(f"[LoginFormController.on_submit] Login correcto para {rut}.")
            self.page.session.set("user_inv", user)

            if hasattr(self.page, "main_controller"):
                self.main_controller.user_inv_id = user.user_inv_id

            self.show_success_dialog("Inicio de sesión exitoso")
        else:
            log.info(f"[LoginFormController.on_submit] Login fallido para {rut}.")
            self.show_error_dialog(["Usuario o contraseña incorrectos"])

    def to_register(self):
        return self.page.go("/register")

    def create_form_layout(self) -> ft.Container:
        form_controls = self.login_form.create_controls({})
        main_content = ft.Row(
            [
                ft.Container(
                    content=ft.Column(form_controls),
                    width=360,
                    padding=ft.Padding(20, 20, 20, 20),
                    border_radius=10,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        return ft.Container(content=main_content, expand=True)

    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/login"))

    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg)

    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg, on_close=lambda: self.page.go("/"))
