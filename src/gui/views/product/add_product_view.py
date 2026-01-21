from gui.controllers.product.add_product_form_controller import AddProductFormController
import flet as ft

def add_product_view(page: ft.Page) -> ft.Container:
    controller = AddProductFormController(page)
    return controller.create_layout()