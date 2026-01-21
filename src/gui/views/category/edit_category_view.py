import flet as ft
from gui.controllers.category.edit_category_form_controller import EditCategoryFormController

def edit_category_view(category_id: int, page: ft.Page):
    controller = EditCategoryFormController(category_id=category_id, page=page)
    return controller.create_form_layout()