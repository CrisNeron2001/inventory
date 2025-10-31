from gui.controllers.brand.add_brand_form_controller import AddBrandFormController
import flet as ft

def add_brand_view() -> ft.Container:
    controller = AddBrandFormController()
    return controller.create_form_layout()