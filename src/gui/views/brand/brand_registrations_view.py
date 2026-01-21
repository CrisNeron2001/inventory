import flet as ft
from gui.controllers.brand.brand_registrations_controller import BrandRegistrationsController

def brand_registrations_view(page: ft.Page) -> ft.Container:
	controller = BrandRegistrationsController(page=page)
	return controller.create_table_layout()