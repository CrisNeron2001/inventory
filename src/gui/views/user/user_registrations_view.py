import flet as ft
from gui.controllers.user.user_registrations_controller import UserRegistrationsController

def user_registrations_view(page: ft.Page) -> ft.Container:
	controller = UserRegistrationsController(page)
	return controller.create_table_layout()