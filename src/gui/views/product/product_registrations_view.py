import flet as ft
from gui.controllers.product.product_registrations_controller import ProductRegistrationsController

def product_registrations_view(page: ft.Page) -> ft.Container:
	controller = ProductRegistrationsController(page)
	return controller.create_table_layout()