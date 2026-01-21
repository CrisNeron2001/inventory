import flet as ft
from gui.controllers.category.category_registrations_controller import CategoryRegistrationsController

def category_registrations_view(page:ft.Page) -> ft.Container:
	controller = CategoryRegistrationsController(page)
	return controller.create_table_layout()