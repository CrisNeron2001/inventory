import flet as ft
from typing import Optional, Callable
from services.user_service import UserService
from services.role_service import RoleService
from core.models.dto.user_dto import UserDTO
from gui.components.form.user_form import UserForm
from gui.validators.user_form_validador import UserFormValidator
from config.settings import log

class CreateUserFormController:
    def __init__(self, router_callback: Optional[Callable[[str], None]] = None):
        self.user_service = UserService()
        self.role_service = RoleService()
        self.validator = UserFormValidator()
        self.router_callback = router_callback
        self.roles = [asdict for asdict in []]
        try:
            roles = self.role_service.get_all_roles()
            self.roles = [ { 'role_inv_id': r.role_inv_id, 'name': r.name } for r in roles ]
        except Exception as ex:
            log.error(f"Failed to load roles for user form: {ex}")

    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_form_user(form_data)
        navigate = form_data.get("_navigate")
        if navigate and self.router_callback:
            self.router_callback(navigate)
            return
        if not is_valid:
              log.error(f"Error al validar el formulario: {errors}")
              return

        dto = UserDTO(
            user_inv_id=None,
            role_inv_id=int(form_data.get("role_inv_id") or 0),
            first_name=form_data.get("first_name") or "",
            last_name=form_data.get("last_name") or "",
            username=form_data.get("username") or "",
            password=form_data.get("password") or "",
            role_inv=None,
        )

        created = self.user_service.create_user(dto)
        if created:
            if self.router_callback:
                self.router_callback("/users")
        return created

    def create_form_layout(self, form_data: dict | None = None) -> ft.Container:
        form = UserForm(self.on_submit, roles=self.roles, is_edit=False)
        controls = form.create_controls(form_data or {})
        return ft.Container(content=ft.Column(controls), width=420)
