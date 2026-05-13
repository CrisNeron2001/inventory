import flet as ft
from gui.controllers.sale.pos_controller import POSController


def pos_view(page: ft.Page, user_inv_id: int | None = None) -> ft.Container:
    controller = POSController(page=page, user_inv_id=user_inv_id)
    return controller.create_steps_layout()
