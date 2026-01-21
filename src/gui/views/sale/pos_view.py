import flet as ft
from gui.controllers.sale.pos_controller import POSController

def pos_view(page: ft.Page) -> ft.Container:
    controller = POSController(page=page)
    return controller.create_steps_layout()
