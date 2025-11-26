from gui.components.form.login_form import LoginForm
from services.user_service import UserService
from config.settings import log
from typing import Optional, Callable, cast
import flet as ft
from services.session_service import SessionService


class LoginFormController:
    def __init__(self, router_callback: Optional[Callable[[str], None]] = None):
        self.user_service = UserService()
        self.login_form = LoginForm(self.on_submit)
        self.router_callback = router_callback

    def on_submit(self, form_data: dict):
        navigate = form_data.get("_navigate")
        if navigate:
            if self.router_callback and isinstance(navigate, str):
                self.router_callback(navigate)
            return

        username = form_data.get("username")
        password = form_data.get("password")
        if not isinstance(username, str) or not isinstance(password, str):
            log.info("Credenciales inválidas recibidas (tipos incorrectos).")
            return None

        user = self.user_service.login(username, password)
        if user:
            log.info(f"Usuario {username} autenticado correctamente.")
            try:
                SessionService().set_current_user(user)
            except Exception:
                log.error("No se pudieron cargar permisos en la sesión.")
            if self.router_callback:
                self.router_callback("/")
            return user
        else:
            log.info(f"Fallo de autenticación para {username}")
            return None

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
