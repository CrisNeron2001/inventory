from gui.components.info.brand_info_table import BrandInfoTable
from services.brand_service import BrandService
from config.settings import log
import flet as ft
from gui.components.dialog.validate.error.error_dialog import error_dialog

class BrandRegistrationsController:
	def __init__(self, page: ft.Page) -> None:
		self.brand_service = BrandService()
		self.page = page
		self.brand_info_table = BrandInfoTable(page)

	def on_load_brands(self) -> ft.Control:
		try:
			brands = self.brand_service.get_all_brands()
			brand_control = self.brand_info_table.create_controls(info_data=brands)
			return ft.Column(controls=brand_control, expand=True)
		except Exception as e:
			log.error(f"[BrandRegistrationsController.on_load_brands] Hubo un problema al cargar todas las marcas: {e}.")
			self.show_error_dialog([f"Hubo un problema al cargar todas las marcas: {str(e)}."])
			return ft.Container()

	def create_table_layout(self) -> ft.Container:
		loaded_brands = self.on_load_brands()
		return ft.Container(
            content=loaded_brands,
            expand=True
        )

	def show_error_dialog(self, errors: list[str]):
		error_msg = "\n".join(errors)
		error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/")) 