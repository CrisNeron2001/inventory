import flet as ft
from gui.controllers.user.edit_user_form_controller import EditUserFormController

def edit_user_view(user_id: int, page: ft.Page) -> ft.Container:
    controller = EditUserFormController(user_id=user_id, page=page)
    return controller.create_form_layout()
