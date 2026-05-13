from gui.components.info.user_info_table import UserInfoTable
from services.user_service import UserService
from config.settings import log
from gui.components.dialog.validate.error.error_dialog import error_dialog
import flet as ft


class UserRegistrationsController:
    def __init__(self, page: ft.Page) -> None:
        self.user_service = UserService()
        self.page = page
        self.user_info_table = UserInfoTable(page)

    def on_load_users(self) -> ft.Control:
        try:
            users = self.user_service.get_all_users()
            user_control = self.user_info_table.create_controls(info_data=users)
            return ft.Column(controls=user_control, expand=True)
        except Exception as e:
            log.error(
                f"[UserRegistrationsController.on_load_users] Hubo un problema al cargar todos los usuarios: {e}."
            )
            self.show_error_dialog(
                [f"Hubo un problema al cargar todos los usuarios: {str(e)}."]
            )
            return ft.Container()

    def create_table_layout(self) -> ft.Container:
        loaded_users = self.on_load_users()
        return ft.Container(content=loaded_users, expand=True)

    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/"))

