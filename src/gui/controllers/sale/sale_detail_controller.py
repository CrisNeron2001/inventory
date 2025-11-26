from gui.components.info.sale_info_list import SaleInfoList
from services.sale_service import SaleService
from config.settings import log

class SaleDetailController:
    def __init__(self) -> None:
        self.sale_service = SaleService()
        self.sale_info_list = SaleInfoList()
        
    def on_load_sale_by_id(self, sale_id: int):
        try:
            sale = self.sale_service.get_sale_by_id(sale_id=sale_id)
            self.sale_info_list.create_controls(info_data=sale)
        except Exception as e:
            log.error("Hubo problema al obtener la venta por id: ", e)