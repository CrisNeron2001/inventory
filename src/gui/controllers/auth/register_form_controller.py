from gui.components.form.register_form import RegisterForm
from services.user_service import UserService
from core.models.dto.user_dto import UserDTO
from config.settings import log
import flet as ft
from gui.components.dialog.validate.error.error_dialog import error_dialog
from gui.components.dialog.validate.success.success_dialog import success_dialog


class RegisterFormController:
    def __init__(self, page: ft.Page):
        self.user_service = UserService()
        self.register_form = RegisterForm(self.on_submit, self.to_login)
        self.page = page

    def on_submit(self, form_data: dict):
        dto = UserDTO(
            user_inv_id=None,
            first_name=form_data.get("first_name") or "",
            middle_name=form_data.get("middle_name") or "",
            last_name=form_data.get("last_name") or "",
            rut=form_data.get("rut") or "",
            password=form_data.get("password") or "",
        )

        user_created = self.user_service.create_user(dto)
        if user_created:
            log.info(
                f"[RegisterFormController.on_submit] Usuario creado: {getattr(user_created, 'first_name', '')}."
            )
            self.show_success_dialog(
                f"Usuario creado: {getattr(user_created, 'first_name', '')}."
            )
        else:
            log.error("[RegisterFormController.on_submit] No se pudo crear el usuario.")
            self.show_validate_error_dialog(["No se pudo crear el usuario."])
            return None

    def to_login(self):
        return self.page.go("/login")

    def create_form_layout(self) -> ft.Container:
        form_controls = self.register_form.create_controls({})
        main_content = ft.Row(
            [
                ft.Container(
                    content=ft.Column(form_controls),
                    width=420,
                    padding=ft.Padding(20, 20, 20, 20),
                    border_radius=10,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        return ft.Container(content=main_content, expand=True)

    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/register"))

    def show_validate_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg)

    def show_success_dialog(self, msg: str):
        success_dialog(self.page, msg, on_close=lambda: self.page.go("/"))
