import flet as ft
from services.user_service import UserService
from core.models.dto.user_dto import UserDTO
from gui.components.form.user_form import UserForm
from gui.validators.user_form_validador import UserFormValidator
from gui.components.dialog.validate.success.success_dialog import success_dialog
from gui.components.dialog.validate.error.error_dialog import error_dialog
from config.settings import log


class EditUserFormController:
    def __init__(self, page: ft.Page, user_id: int):
        self.user_service = UserService()
        self.validator = UserFormValidator()
        self.user_id = user_id
        self.page = page

    def load_user(self) -> dict:
        user = self.user_service.get_user_by_id(self.user_id)
        if user is None:
            return {}
        return {
            "user_inv_id": getattr(user, "user_inv_id", None),
            "first_name": getattr(user, "first_name", ""),
            "middle_name": getattr(user, "middle_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "rut": getattr(user, "rut", ""),
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

        if not is_valid:
            log.error(
                f"[EditUserFormController.on_submit] Error al validar el formulario: {errors}"
            )
            self.show_validate_error_dialog(errors)
            return

        dto = UserDTO(
            user_inv_id=resolved_user_inv,
            first_name=form_data.get("first_name") or "",
            middle_name=form_data.get("middle_name") or "",
            last_name=form_data.get("last_name") or "",
            rut=form_data.get("rut") or "",
            password=form_data.get("password") or "",
        )

        user_updated = self.user_service.update_user(dto)
        if user_updated:
            log.info(
                f"[EditUserFormController.on_submit] Usuario editado: {getattr(user_updated, 'username', '')}."
            )
            return self.show_success_dialog(
                f"Usuario editado: {getattr(user_updated, 'username', '')}."
            )
        else:
            log.error(
                "[EditUserFormController.on_submit] No se pudo editar el usuario. Intente nuevamente."
            )
            return self.show_validate_error_dialog(
                ["No se pudo editar el usuario. Intente nuevamente."]
            )

    def create_form_layout(self) -> ft.Container:
        data = self.load_user()
        form = UserForm(self.on_submit, is_edit=True)
        controls = form.create_controls(data)
        return ft.Container(content=ft.Column(controls), width=420)

    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/"))

    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg)

    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg, on_close=lambda: self.page.go("/"))
