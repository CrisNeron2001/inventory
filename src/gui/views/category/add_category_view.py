import flet as ft
from gui.controllers.category.add_category_form_controller import AddCategoryFormController

def add_category_view(page:ft.Page) -> ft.Container:
    controller = AddCategoryFormController(page)
    return controller.create_form_layout()