from gui.components.info.product_info_table import ProductInfoTable
from services.product_service import ProductService
from config.settings import log

class ProductRegistrationsController:
	def __init__(self) -> None:
		self.product_service = ProductService()
		self.product_info_table = ProductInfoTable()

	def on_load_products(self):
		try:
			products = self.product_service.get_all_products()
			self.product_info_table.create_controls(info_data=products)
		except Exception as e:
			log.error("Hubo un problema al cargar todos los productos: ", e)