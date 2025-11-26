import flet as ft
from typing import Callable, Optional
from services.user_service import UserService
from gui.components.info.user_info_table import UserInfoTable


def user_registrations_view(router_callback: Optional[Callable[[str], None]] = None) -> ft.Container:
    svc = UserService()
    users = svc.get_all_users()
    table = UserInfoTable(router_callback)
    controls = table.create_controls(users)
    return ft.Container(content=ft.Column(controls), expand=True)
