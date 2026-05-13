from gui.components.info.product_info_list import ProductInfoList
from services.product_service import ProductService
from config.settings import log
from gui.components.dialog.validate.error.error_dialog import error_dialog
import flet as ft


class ProductDetailController:
    def __init__(self, page: ft.Page) -> None:
        self.product_service = ProductService()
        self.product_info_list = ProductInfoList()
        self.page = page
        self.payload = {}

    def on_load_product_by_id(self, product_id: int) -> ft.Control:
        try:
            product = self.product_service.get_product_by_id(product_id=product_id)
            product_control = self.product_info_list.create_controls(info_data=product)
            return ft.Column(controls=product_control, expand=True)
        except Exception as e:
            log.error(
                f"[ProductDetailController.on_load_product_by_id] Hubo problema al obtener el producto por id: {e}."
            )
            self.show_error_dialog(
                [f"Hubo problema al obtener el producto por id: {str(e)}."]
            )
            return ft.Container()

    def create_list_layout(self, product_id: int) -> ft.Container:
        loaded_products = self.on_load_product_by_id(product_id)
        return ft.Container(content=loaded_products, expand=True)

    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/"))

