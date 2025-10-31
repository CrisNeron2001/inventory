from gui.controllers.category.add_category_form_controller import AddCategoryFormController
import flet as ft

def add_category_view() -> ft.Container:
    controller = AddCategoryFormController()
    return controller.create_form_layout()