from core.abstracts.form import Form
from typing import Any, Callable, Optional
import flet as ft


class LoginForm(Form):
    def __init__(self, on_submit: Callable, to_register: Callable) -> None:
        super().__init__("Iniciar sesión", "login_form")
        self.field_rut: Optional[ft.TextField] = None
        self.field_password: Optional[ft.TextField] = None
        self.on_submit = on_submit
        self.to_register = to_register

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        self.field_rut = ft.TextField(
            label="Rut",
            hint_text="Ingrese su rut",
            value=form_data.get("rut", ""),
        )
        self.field_password = ft.TextField(
            label="Contraseña",
            hint_text="Ingrese su contraseña",
            password=True,
            can_reveal_password=True,
            value="",
        )

        button_submit = ft.ElevatedButton(
            text="Ingresar",
            on_click=lambda e: self.on_submit(self.get_data()),
        )

        question_text = ft.Text("¿No tienes una cuenta?", size=12)

        button_to_register = ft.ElevatedButton(
            text="Ir Registrarse",
            on_click=lambda e: self.to_register(),
        )

        return [
            ft.Text(self.title, size=18),
            self.field_rut,
            self.field_password,
            ft.Row([button_submit], spacing=20),
            ft.Row(
                [question_text, button_to_register],
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ]

    def get_data(self) -> dict[Any, str]:
        return {
            "rut": getattr(self.field_rut, "value", "") or "",
            "password": getattr(self.field_password, "value", "") or "",
        }

    def validate(self) -> tuple[bool, list[str]]:
        data = self.get_data()
        errors = []
        if not data["rut"]:
            errors.append("rut is required")
        if not data["password"]:
            errors.append("password is required")
        return (len(errors) == 0, errors)

    def reset(self) -> None:
        if self.field_rut:
            self.field_rut.value = ""
        if self.field_password:
            self.field_password.value = ""
