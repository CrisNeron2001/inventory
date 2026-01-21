import flet as ft
from gui.controllers.product.edit_product_stock_form_controller import EditProductStockTableController

def edit_product_stock_view(page: ft.Page) -> ft.Container:
	controller = EditProductStockTableController(page)
	return controller.create_layout()