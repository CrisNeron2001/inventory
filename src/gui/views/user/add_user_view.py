import flet as ft
from gui.controllers.user.create_user_form_controller import CreateUserFormController

def add_user_view(page: ft.Page) -> ft.Container:
    controller = CreateUserFormController(page=page)
    return controller.create_form_layout()
