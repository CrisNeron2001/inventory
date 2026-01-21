import flet as ft
from gui.controllers.auth.login_form_controller import LoginFormController

def login_view(page: ft.Page) -> ft.Container:
    controller = LoginFormController(page)
    return controller.create_form_layout()
