import flet as ft
from gui.controllers.auth.register_form_controller import RegisterFormController

def register_view(page: ft.Page) -> ft.Container:
    controller = RegisterFormController(page)
    return controller.create_form_layout()
