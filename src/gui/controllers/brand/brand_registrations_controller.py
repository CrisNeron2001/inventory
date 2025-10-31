from gui.components.info.brand_info_table import BrandInfoTable
from services.brand_service import BrandService
from config.settings import log

class BrandRegistrationsController:
	def __init__(self) -> None:
		self.brand_service = BrandService()
		self.brand_info_table = BrandInfoTable()

	def on_load_brands(self):
		try:
			brands = self.brand_service.get_all_brands()
			self.brand_info_table.create_controls(info_data=brands)
		except Exception as e:
			log.error("Hubo un problema al cargar todas las marcas: ", e)