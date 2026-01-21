import flet as ft
from gui.controllers.product.product_detail_controller import ProductDetailController

def product_detail_view(page: ft.Page, product_id: int) -> ft.Container:
	controller = ProductDetailController(page=page)
	return controller.create_list_layout(product_id)
