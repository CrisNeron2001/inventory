from gui.components.info.product_info_list import ProductInfoList
from services.product_service import ProductService
from config.settings import log

class ProductDetailController:
    def __init__(self) -> None:
        self.product_service = ProductService()
        self.product_info_list = ProductInfoList()
        
    def on_load_product_by_id(self, product_id: int):
        try:
            product = self.product_service.get_product_by_id(product_id=product_id)
            self.product_info_list.create_controls(info_data=product)
        except Exception as e:
            log.error("Hubo problema al obtener el producto por id: ", e)