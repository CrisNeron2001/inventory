import flet as ft
from typing import Optional, Callable
from services.user_service import UserService
from services.role_service import RoleService
from core.models.dto.user_dto import UserDTO
from gui.components.form.user_form import UserForm
from gui.validators.user_form_validador import UserFormValidator
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog
from config.settings import log

class CreateUserFormController:
    def __init__(self, page: ft.Page):
        self.user_service = UserService()
        self.role_service = RoleService()
        self.validator = UserFormValidator()
        self.roles = [asdict for asdict in []]
        self.page = page

        try:
            roles = self.role_service.get_all_roles()
            self.roles = [ { 'role_inv_id': r.role_inv_id, 'name': r.name } for r in roles ]
        except Exception as ex:
            log.error(f"Error fatal al cargar datos de usuarios: {ex}")
            self.show_error_dialog([str(ex)])

    def on_submit(self, form_data: dict):
        is_valid, errors = self.validator.validate_form_user(form_data)

        if not is_valid:
              log.error(f"Error al validar el formulario: {errors}")
              self.show_validate_error_dialog(errors)
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

        user_created = self.user_service.create_user(dto)
        if user_created:
            log.info(f"[CreateUserFormController.on_submit] Usuario creado: {getattr(user_created, 'username', '')}.")
            return self.show_success_dialog(f"Usuario creado: {getattr(user_created, 'username', '')}.")
        else:
            log.error("[CreateUserFormController.on_submit] No se pudo crear el usuario. Intente nuevamente.")
            return self.show_validate_error_dialog(["No se pudo crear el usuario. Intente nuevamente."])

    def create_form_layout(self, form_data: dict | None = None) -> ft.Container:
        form = UserForm(self.on_submit, roles=self.roles, is_edit=False)
        controls = form.create_controls(form_data or {})
        return ft.Container(content=ft.Column(controls), width=420)
        
    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/"))
		
    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg) 
        
    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg, on_close=lambda: self.page.go("/"))
