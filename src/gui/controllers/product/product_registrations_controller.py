from gui.components.info.product_info_table import ProductInfoTable
from services.product_service import ProductService
from config.settings import log
from gui.components.dialog.validate.error.error_dialog import error_dialog
import flet as ft

class ProductRegistrationsController:
	def __init__(self, page: ft.Page) -> None:
		self.product_service = ProductService()
		self.page = page
		self.product_info_table = ProductInfoTable(page)
		
	def on_load_products(self) -> ft.Control:
		try:
			products = self.product_service.get_all_products()
			product_controls = self.product_info_table.create_controls(info_data=products)
			return ft.Column(controls=product_controls, expand=True)
		except Exception as e:
			log.error(f"[ProductRegistrationsController.on_load_products] Hubo un problema al cargar todos los productos: {e}.")
			self.show_error_dialog([f"Hubo un problema al cargar todos los productos: {str(e)}."])
			return ft.Container()

	def create_table_layout(self) -> ft.Container:
		loaded_products = self.on_load_products()
		return ft.Container(
            content=loaded_products,
            expand=True
        )
			
	def show_error_dialog(self, errors: list[str]):
		error_msg = "\n".join(errors)
		error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/")) 