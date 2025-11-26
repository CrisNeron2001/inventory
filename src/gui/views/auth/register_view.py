import flet as ft
from typing import Callable, Optional
from gui.controllers.auth.register_form_controller import RegisterFormController


def register_view(router_callback: Optional[Callable[[str], None]] = None) -> ft.Container:
    controller = RegisterFormController(router_callback=router_callback)
    return controller.create_form_layout()
