from gui.components.form.login_form import LoginForm
from services.user_service import UserService
from config.settings import log
import flet as ft
from services.session_service import SessionService
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog

class LoginFormController:
    def __init__(self, page: ft.Page):
        self.user_service = UserService()
        self.login_form = LoginForm(self.on_submit)
        self.page = page

    def on_submit(self, form_data: dict):
        username = form_data.get("username")
        password = form_data.get("password")
        if not isinstance(username, str) or not isinstance(password, str):
            log.info("[LoginFormController.on_submit] Credenciales inválidas recibidas (tipos incorrectos).")
            self.show_validate_error_dialog(["Credenciales inválidas."])
            return

        user = self.user_service.login(username, password)
        if user:
            SessionService().set_current_user(user)
            log.info(f"[LoginFormController.on_submit] Login correcto para {username}.")
            self.show_success_dialog("Inicio de sesión exitoso")
        else:
            log.info(f"[LoginFormController.on_submit] Login fallido para {username}.")
            self.show_error_dialog(["Usuario o contraseña incorrectos"])

    def create_form_layout(self) -> ft.Container:
        form_controls = self.login_form.create_controls({})
        main_content = ft.Row([
            ft.Container(
                content=ft.Column(form_controls),
                width=360,
                padding=ft.Padding(20, 20, 20, 20),
                border_radius=10,
            )
        ], alignment=ft.MainAxisAlignment.CENTER)
        return ft.Container(content=main_content, expand=True)

    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/login"))
        
    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg) 
        
    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg, on_close=lambda: self.page.go("/"))