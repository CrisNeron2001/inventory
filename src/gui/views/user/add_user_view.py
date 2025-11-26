import flet as ft
from typing import Optional, Callable
from gui.controllers.user.create_user_form_controller import CreateUserFormController


def add_user_view(router_callback: Optional[Callable[[str], None]] = None) -> ft.Container:
    controller = CreateUserFormController(router_callback=router_callback)
    return controller.create_form_layout()
