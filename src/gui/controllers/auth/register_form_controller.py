from gui.components.form.register_form import RegisterForm
from services.user_service import UserService
from services.role_service import RoleService
from core.models.dto.user_dto import UserDTO
from config.settings import log
from typing import Optional, Callable, cast
import flet as ft


class RegisterFormController:
    def __init__(self, router_callback: Optional[Callable[[str], None]] = None):
        self.user_service = UserService()
        self.role_service = RoleService()
        self.router_callback = router_callback
        roles = [r.__dict__ for r in self.role_service.get_all_roles()]
        self.register_form = RegisterForm(self.on_submit, roles=roles)

    def on_submit(self, form_data: dict):
        try:
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
                log.info(f"Usuario creado: {created}")
                if self.router_callback:
                    self.router_callback("/")
                return created
            else:
                log.error("No se pudo crear el usuario.")
                return None
        except Exception as e:
            log.error(f"Error al registrar usuario: {e}")
            return None

    def create_form_layout(self) -> ft.Container:
        form_controls = self.register_form.create_controls({})
        main_content = ft.Row([
            ft.Container(
                content=ft.Column(form_controls),
                width=420,
                padding=ft.Padding(20, 20, 20, 20),
                border_radius=10,
            )
        ], alignment=ft.MainAxisAlignment.CENTER)
        return ft.Container(content=main_content, expand=True)
