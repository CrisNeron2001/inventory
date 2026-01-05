import flet as ft
from gui.controllers.product.product_import_controller import ProductImportController

def product_import_view(page: ft.Page):
    controller = ProductImportController(page)
    return controller.create_layout()
