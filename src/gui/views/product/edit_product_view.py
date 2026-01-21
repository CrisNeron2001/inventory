import flet as ft
from gui.controllers.product.edit_product_form_controller import EditProductFormController

def edit_product_view(product_id: int, page: ft.Page) -> ft.Container:
    controller = EditProductFormController(product_id, page=page)
    return controller.create_form_layout()