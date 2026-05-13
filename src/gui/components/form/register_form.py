from core.abstracts.form import Form
from typing import Any, Callable, Optional
import flet as ft


class RegisterForm(Form):
    def __init__(self, on_submit: Callable, to_login: Callable) -> None:
        super().__init__("Crear cuenta", "register_form")
        self.field_first_name: Optional[ft.TextField] = None
        self.field_middle_name: Optional[ft.TextField] = None
        self.field_last_name: Optional[ft.TextField] = None
        self.field_rut: Optional[ft.TextField] = None
        self.field_password: Optional[ft.TextField] = None
        self.on_submit = on_submit
        self.to_login = to_login

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        self.field_first_name = ft.TextField(
            label="Primer Nombre", value=form_data.get("first_name", "")
        )
        self.field_middle_name = ft.TextField(
            label="Segundo Nombre", value=form_data.get("middle_name", "")
        )
        self.field_last_name = ft.TextField(
            label="Apellidos", value=form_data.get("last_name", "")
        )
        self.field_rut = ft.TextField(label="Rut", value=form_data.get("rut", ""))
        self.field_password = ft.TextField(
            label="Contraseña", password=True, can_reveal_password=True
        )

        button_submit = ft.ElevatedButton(
            text="Registrar", on_click=lambda e: self.on_submit(self.get_data())
        )

        text_question = ft.Text("¿Ya tienes una cuenta?", size=12)

        button_to_login = ft.ElevatedButton(
            text="Ir ingresar sesión", on_click=lambda e: self.to_login()
        )

        return [
            ft.Text(self.title, size=18),
            self.field_first_name,
            self.field_middle_name,
            self.field_last_name,
            self.field_rut,
            self.field_password,
            ft.Row([button_submit], spacing=20),
            ft.Row(
                [text_question, button_to_login],
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ]

    def get_data(self) -> dict[str, Any]:
        return {
            "first_name": getattr(self.field_first_name, "value", "") or "",
            "middle_name": getattr(self.field_middle_name, "value", "") or "",
            "last_name": getattr(self.field_last_name, "value", "") or "",
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
        if not data["first_name"]:
            errors.append("first_name is required")
        if not data["last_name"]:
            errors.append("last_name is required")
        return (len(errors) == 0, errors)

    def reset(self) -> None:
        if self.field_first_name:
            self.field_first_name.value = ""
        if self.field_middle_name:
            self.field_middle_name.value = ""
        if self.field_last_name:
            self.field_last_name.value = ""
        if self.field_rut:
            self.field_rut.value = ""
        if self.field_password:
            self.field_password.value = ""
