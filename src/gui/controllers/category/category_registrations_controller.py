from gui.components.info.category_info_table import CategoryInfoTable
from services.category_service import CategoryService
from config.settings import log
from gui.components.dialog.validate.error.error_dialog import error_dialog
import flet as ft


class CategoryRegistrationsController:
    def __init__(self, page: ft.Page) -> None:
        self.category_service = CategoryService()
        self.page = page
        self.category_info_table = CategoryInfoTable(page)

    def on_load_categories(self):
        try:
            categories = self.category_service.get_all_categories()
            category_control = self.category_info_table.create_controls(
                info_data=categories
            )
            return ft.Column(controls=category_control, expand=True)
        except Exception as e:
            log.error(
                f"[CategoryRegistrationsController.on_load_categories] Hubo un problema al cargar todas las categorias: {e}."
            )
            self.show_error_dialog(
                [f"Hubo un problema al cargar todas las categorias: {str(e)}."]
            )

    def create_table_layout(self) -> ft.Container:
        loaded_categories = self.on_load_categories()
        return ft.Container(content=loaded_categories, expand=True)

    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/"))
