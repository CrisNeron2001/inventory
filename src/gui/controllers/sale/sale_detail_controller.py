from gui.components.info.sale_info_list import SaleInfoList
from services.sale_service import SaleService
from config.settings import log
from gui.components.dialog.validate.error.error_dialog import error_dialog
from dataclasses import is_dataclass, asdict
import flet as ft

class SaleDetailController:
    def __init__(self, page: ft.Page) -> None:
        self.sale_service = SaleService()
        self.sale_info_list = SaleInfoList()
        self.page = page
        
    def on_load_sale_by_id(self, sale_id: int) -> ft.Control:
        try:
            sale = self.sale_service.get_sale_by_id(sale_id=sale_id)
            sale_control = self.sale_info_list.create_controls(info_data=sale)
            return ft.Column(controls=sale_control, expand=True)
        except Exception as e:
            log.error(f"[SaleDetailController.on_load_sale_by_id] Hubo problema al obtener la venta por id: {e}.")
            self.show_error_dialog([f"Hubo problema al obtener la venta por id: {str(e)}."])
            return ft.Container()
	
    def create_list_layout(self, sale_id: int) -> ft.Container:
        loaded_sales = self.on_load_sale_by_id(sale_id)
        return ft.Container(
            content=loaded_sales,
            expand=True
        )
            
    def show_error_dialog(self, errors: list[str]):
        error_msg = "\n".join(errors)
        error_dialog(self.page, error_msg, on_close=lambda: self.page.go("/")) 