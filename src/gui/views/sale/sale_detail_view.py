import flet as ft
from gui.controllers.sale.sale_detail_controller import SaleDetailController

def sale_detail_view(sale_id: int, page: ft.Page) -> ft.Container:
	controller = SaleDetailController(page)
	return controller.create_list_layout(sale_id)