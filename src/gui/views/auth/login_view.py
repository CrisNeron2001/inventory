import flet as ft
from typing import Callable, Optional
from gui.controllers.auth.login_form_controller import LoginFormController


def login_view(router_callback: Optional[Callable[[str], None]] = None) -> ft.Container:
    controller = LoginFormController(router_callback=router_callback)
    return controller.create_form_layout()
