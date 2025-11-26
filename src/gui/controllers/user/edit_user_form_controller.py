import flet as ft
from typing import Optional, Callable
from services.user_service import UserService
from services.role_service import RoleService
from core.models.dto.user_dto import UserDTO
from gui.components.form.user_form import UserForm
from gui.validators.user_form_validador import UserFormValidator
from config.settings import log

class EditUserFormController:
    def __init__(self, user_id: int, router_callback: Optional[Callable[[str], None]] = None):
        self.user_service = UserService()
        self.role_service = RoleService()
        self.validator = UserFormValidator()
        self.user_id = user_id
        self.router_callback = router_callback
        self.roles = []
        roles = self.role_service.get_all_roles()
        self.roles = [ { 'role_inv_id': r.role_inv_id, 'name': r.name } for r in roles ]

    def load_user(self) -> dict:
        user = self.user_service.get_user_by_id(self.user_id)
        if user is None:
            return {}
        return {
            "user_inv_id": getattr(user, "user_inv_id", None),
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "username": getattr(user, "username", ""),
            "role_inv_id": getattr(user, "role_inv_id", None),
        }

    def on_submit(self, form_data: dict):
        user_inv_raw = form_data.get("user_inv_id")
        is_valid, errors = self.validator.validate_form_user(form_data)
        if user_inv_raw is None or user_inv_raw == "":
            resolved_user_inv = self.user_id
        else:
            try:
                resolved_user_inv = int(user_inv_raw)
            except (TypeError, ValueError):
                resolved_user_inv = self.user_id

        role_raw = form_data.get("role_inv_id")
        if role_raw is None or role_raw == "":
            resolved_role_inv = 0
        else:
            try:
                resolved_role_inv = int(role_raw)
            except (TypeError, ValueError):
                resolved_role_inv = 0
                
        if not is_valid:
            log.error(f"Error al validar el formulario: {errors}")
            return

        dto = UserDTO(
            user_inv_id=resolved_user_inv,
            role_inv_id=resolved_role_inv,
            first_name=form_data.get("first_name") or "",
            last_name=form_data.get("last_name") or "",
            username=form_data.get("username") or "",
            password=form_data.get("password") or "",
            role_inv=None,
        )

        updated = self.user_service.update_user(dto)
        if updated and self.router_callback:
            self.router_callback("/users")
        return updated

    def create_form_layout(self) -> ft.Container:
        data = self.load_user()
        form = UserForm(self.on_submit, roles=self.roles, is_edit=True)
        controls = form.create_controls(data)
        return ft.Container(content=ft.Column(controls), width=420)