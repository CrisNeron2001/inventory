from gui.components.info.sale_info_table import SaleInfoTable
from services.sale_service import SaleService
from config.settings import log
from gui.components.dialog.validate.error.error_dialog import error_dialog
import flet as ft

class SaleRegistrationsController:
	def __init__(self, page: ft.Page) -> None:
		self.sale_service = SaleService()
		self.page = page
		self.sale_info_table = SaleInfoTable(page)

	def on_load_sales(self) -> ft.Control:
		try:
			sales = self.sale_service.get_all_sales()
			sale_control = self.sale_info_table.create_controls(info_data=sales)
			return ft.Column(controls=sale_control, expand=True)
		except Exception as e:
			log.error(f"[SaleRegistrationsController.on_load_sales] Hubo un problema al cargar todos los ventas: {e}.")
			self.show_error_dialog([f"Hubo un problema al cargar todos los ventas: {str(e)}."])
			return ft.Container()

	def create_table_layout(self) -> ft.Container:
		loaded_sales = self.on_load_sales()
		return ft.Container(
            content=loaded_sales,
            expand=True
        )
			
	def show_error_dialog(self, errors: list[str]):
		error_msg = "\n".join(errors)
		error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/")) 