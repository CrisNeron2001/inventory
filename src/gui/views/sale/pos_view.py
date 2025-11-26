import flet as ft
from typing import Callable, Optional
from gui.controllers.sale.pos_controller import POSController


def pos_view(router_callback: Optional[Callable[[str], None]] = None) -> ft.Container:
    controller = POSController(page=None, router_callback=router_callback)
    return controller.create_steps_layout()
