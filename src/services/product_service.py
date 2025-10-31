from core.models.dao.product_dao import ProductDAO
from core.models.dto.product_dto import ProductDTO
from core.models.mapper.product_mapper import dto_to_entity, entity_to_dto
from typing import List
from config.settings import log

class ProductService:
    def __init__(self):
        self.dao = ProductDAO()
    def create_product(self, product_dto: ProductDTO) -> ProductDTO | None:
        product = dto_to_entity(product_dto)
        new_product = self.dao.create_product(product=product)
        log.info(f"Nuevo producto creado: {new_product}")
        return entity_to_dto(new_product) if new_product else None
    
    def get_product_by_id(self, product_id: int) -> ProductDTO | None:
        product = self.dao.get_product_by_id(product_id=product_id)
        log.info(f"Producto obtenido por id: {product}")
        return entity_to_dto(product) if product else None
    
    def get_all_products(self) -> List[ProductDTO]:
        products = self.dao.get_all_products()
        log.info(f"Obtenido todos los productos: {products}")
        return [entity_to_dto(product) for product in products]
    
    def update_product(self, product_dto: ProductDTO) -> ProductDTO | None:
        product = dto_to_entity(product_dto)
        updated_product = self.dao.edit_product(product=product)
        log.info(f"Produco modificado: {updated_product}")
        return entity_to_dto(updated_product) if updated_product else None
    
    def delete_product(self, product_id: int) -> bool | None:
        product = self.dao.delete_product(product_id=product_id)
        log.info(f"Producto eliminado: {product}")
        return True if product else False 