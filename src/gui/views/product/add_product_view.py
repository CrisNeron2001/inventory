from gui.controllers.product.add_product_form_controller import AddProductFormController
import flet as ft

def add_product_view() -> ft.Container:
    controller = AddProductFormController()
    return controller.create_layout()