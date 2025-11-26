from core.abstracts.form import Form
from typing import Any, Callable, Optional, List, cast
import flet as ft


class UserForm(Form):
    def __init__(self, on_submit: Callable, roles: List[dict] | None = None, is_edit: bool = False) -> None:
        title = "Editar usuario" if is_edit else "Crear usuario"
        super().__init__(title, "user_form")
        self.field_first_name: Optional[ft.TextField] = None
        self.field_last_name: Optional[ft.TextField] = None
        self.field_username: Optional[ft.TextField] = None
        self.field_password: Optional[ft.TextField] = None
        self.field_role: Optional[ft.Dropdown] = None
        self.on_submit = on_submit
        self.roles = roles or []
        self.is_edit = is_edit

    def create_controls(self, form_data: dict) -> list[ft.Control]:
        self.field_first_name = ft.TextField(label="Nombre", value=form_data.get("first_name", ""))
        self.field_last_name = ft.TextField(label="Apellido", value=form_data.get("last_name", ""))
        self.field_username = ft.TextField(label="Usuario", value=form_data.get("username", ""))
        self.field_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, value=form_data.get("password", "") if self.is_edit else "")

        options = [ft.DropdownOption(key=str(r.get('role_inv_id')), text=r.get('name')) for r in self.roles]
        selected = None
        if form_data.get("role_inv_id"):
            selected = str(form_data.get("role_inv_id"))
        elif options:
            selected = options[0].key

        self.field_role = ft.Dropdown(label="Rol", options=cast(List[ft.dropdown.Option], options), value=selected)

        submit_text = "Guardar" if self.is_edit else "Crear"
        button_submit = ft.ElevatedButton(text=submit_text, on_click=lambda e: self.on_submit(self.get_data()))

        controls = [
            ft.Text(self.title, size=18),
            self.field_first_name,
            self.field_last_name,
            self.field_username,
        ]
        if not self.is_edit:
            controls.append(self.field_password)
        else:
            controls.append(self.field_password)

        controls.append(self.field_role)
        controls.append(ft.Container(content=button_submit, margin=ft.Margin(0, 20, 0, 0)))
        return controls

    def get_data(self) -> dict[str, Any]:
        return {
            "first_name": getattr(self.field_first_name, "value", "") or "",
            "last_name": getattr(self.field_last_name, "value", "") or "",
            "username": getattr(self.field_username, "value", "") or "",
            "password": getattr(self.field_password, "value", "") or "",
            "role_inv_id": int(getattr(self.field_role, "value", 0)) if getattr(self.field_role, "value", None) else None,
        }

    def validate(self) -> tuple[bool, list[str]]:
        data = self.get_data()
        errors = []
        if not data["username"]:
            errors.append("username is required")
        if not self.is_edit and not data["password"]:
            errors.append("password is required")
        if not data["first_name"]:
            errors.append("first_name is required")
        if not data["role_inv_id"]:
            errors.append("role is required")
        return (len(errors) == 0, errors)

    def reset(self) -> None:
        if self.field_first_name:
            self.field_first_name.value = ""
        if self.field_last_name:
            self.field_last_name.value = ""
        if self.field_username:
            self.field_username.value = ""
        if self.field_password:
            self.field_password.value = ""
