from gui.components.info.category_info_table import CategoryInfoTable
from services.category_service import CategoryService
from config.settings import log

class CategoryRegistrationsController:
	def __init__(self) -> None:
		self.category_service = CategoryService()
		self.category_info_table = CategoryInfoTable()

	def on_load_categories(self):
		try:
			categories = self.category_service.get_all_categories()
			self.category_info_table.create_controls(info_data=categories)
		except Exception as e:
			log.error("Hubo un problema al cargar todas las categorias: ", e)