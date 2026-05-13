import flet as ft
from gui.controllers.product.menu_create_product_controller import MenuProductController


def menu_create_product_view(page: ft.Page) -> ft.Container:
    controller = MenuProductController(page)
    return controller.create_layout()
