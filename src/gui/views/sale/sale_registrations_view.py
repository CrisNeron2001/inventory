import flet as ft
from gui.controllers.sale.sale_registrations_controller import SaleRegistrationsController

def sale_registrations_view(page: ft.Page) -> ft.Container:
	controller = SaleRegistrationsController(page)
	return controller.create_table_layout()