from core.abstracts.form import Form
from typing import Any, Callable, Optional
import flet as ft


class LoginForm(Form):
    def __init__(self, on_submit: Callable) -> None:
        super().__init__("Iniciar sesión", "login_form")
        self.field_username: Optional[ft.TextField] = None
        self.field_password: Optional[ft.TextField] = None
        self.on_submit = on_submit

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        self.field_username = ft.TextField(
            label="Nombre de usuario",
            hint_text="Ingrese su usuario",
            value=form_data.get("username", "")
        )
        self.field_password = ft.TextField(
            label="Contraseña",
            hint_text="Ingrese su contraseña",
            password=True,
            can_reveal_password=True,
            value=""
        )

        button_submit = ft.ElevatedButton(
            text="Ingresar",
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.LIGHT_BLUE_600),
            on_click=lambda e: self.on_submit(self.get_data())
        )

        return [
            ft.Text(self.title, size=18),
            self.field_username,
            self.field_password,
            ft.Row([button_submit], spacing=20)
        ]

    def get_data(self) -> dict[Any, str]:
        return {
            "username": getattr(self.field_username, "value", "") or "",
            "password": getattr(self.field_password, "value", "") or "",
        }

    def validate(self) -> tuple[bool, list[str]]:
        data = self.get_data()
        errors = []
        if not data["username"]:
            errors.append("username is required")
        if not data["password"]:
            errors.append("password is required")
        return (len(errors) == 0, errors)

    def reset(self) -> None:
        if self.field_username:
            self.field_username.value = ""
        if self.field_password:
            self.field_password.value = ""
