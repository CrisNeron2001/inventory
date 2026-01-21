import flet as ft
from gui.controllers.brand.add_brand_form_controller import AddBrandFormController

def add_brand_view(page: ft.Page) -> ft.Container:
    controller = AddBrandFormController(page)
    return controller.create_form_layout()